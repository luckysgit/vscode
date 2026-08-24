const express = require("express");
const http = require("http");
const { Server } = require("socket.io");
const cors = require("cors");
const { Queue, Worker } = require("bullmq");
const { v4: uuidv4 } = require("uuid");
require("dotenv").config();

const db = require("./services/db");
const redis = require("./services/redis");
const { submitCode } = require("./services/judge0");

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: { origin: "*", methods: ["GET", "POST"] },
});

app.use(cors());
app.use(express.json({ limit: "50kb" }));

// ─── UTILS ───
function generateRoomCode() {
  return Math.random().toString(36).substring(2, 8).toUpperCase();
}

function generateAlias() {
  const names = ["SwiftFox", "CodeNinja", "ByteMaster", "NullPointer", "StackOverflow", "Recursion", "BinaryBeast", "PixelPioneer", "CyberWolf", "DataDragon"];
  return names[Math.floor(Math.random() * names.length)];
}

// ─── BULLMQ QUEUE ───
const submissionQueue = new Queue("submissions", {
  connection: redis.options,
});

// ─── HTTP API ───
app.get("/api/health", (req, res) => res.json({ status: "ok" }));

app.post("/api/rooms", async (req, res) => {
  try {
    const code = generateRoomCode();
    // Pick a random problem for MVP
    const problemResult = await db.query("SELECT id FROM problems ORDER BY RANDOM() LIMIT 1");
    const problemId = problemResult.rows[0]?.id;

    await db.query(
      `INSERT INTO rooms (id, unique_code, status, problem_id, created_at) VALUES ($1, $2, $3, $4, NOW())`,
      [uuidv4(), code, "lobby", problemId]
    );

    // Initialize Redis room state
    await redis.hset(`room:${code}`, "status", "lobby", "problemId", problemId || "", "hostId", "");
    await redis.expire(`room:${code}`, 86400);

    res.json({ code, message: "Room created" });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to create room" });
  }
});

app.get("/api/rooms/:code", async (req, res) => {
  try {
    const { code } = req.params;
    const result = await db.query(`SELECT * FROM rooms WHERE unique_code = $1`, [code]);
    if (!result.rows.length) return res.status(404).json({ error: "Room not found" });
    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: "Server error" });
  }
});

// ─── SOCKET.IO ───
const rooms = new Map(); // In-memory room tracking for MVP

io.on("connection", (socket) => {
  console.log("Socket connected:", socket.id);

  socket.on("room:join", async ({ code, alias }) => {
    try {
      const roomCode = code.toUpperCase();
      const roomKey = `room:${roomCode}`;
      const roomData = await redis.hgetall(roomKey);

      if (!roomData || !roomData.status) {
        socket.emit("error", { message: "Room not found" });
        return;
      }

      if (roomData.status === "ended") {
        socket.emit("error", { message: "Room has ended" });
        return;
      }

      socket.join(roomCode);
      socket.roomCode = roomCode;
      socket.alias = alias || generateAlias();

      // Set host if first player
      let isHost = false;
      const existingPlayers = await redis.smembers(`${roomKey}:players`);
      if (existingPlayers.length === 0) {
        await redis.hset(roomKey, "hostId", socket.id);
        isHost = true;
      }

      await redis.sadd(`${roomKey}:players`, socket.id);
      await redis.hset(`${roomKey}:player:${socket.id}`, "alias", socket.alias, "score", "0", "status", "waiting");

      // Notify room
      socket.to(roomCode).emit("room:player_joined", {
        id: socket.id,
        alias: socket.alias,
        isHost,
      });

      // Send current state to joining player
      const players = [];
      const playerIds = await redis.smembers(`${roomKey}:players`);
      for (const pid of playerIds) {
        const pdata = await redis.hgetall(`${roomKey}:player:${pid}`);
        const h = await redis.hget(roomKey, "hostId");
        players.push({ id: pid, alias: pdata.alias || "Player", isHost: pid === h });
      }

      socket.emit("room:state", {
        status: roomData.status,
        players,
        problem: null,
      });
    } catch (err) {
      console.error(err);
      socket.emit("error", { message: "Failed to join room" });
    }
  });

  socket.on("room:start", async ({ code }) => {
    try {
      const roomCode = code.toUpperCase();
      const roomKey = `room:${roomCode}`;
      const roomData = await redis.hgetall(roomKey);

      if (roomData.hostId !== socket.id) {
        socket.emit("error", { message: "Only host can start" });
        return;
      }

      if (roomData.status !== "lobby") {
        socket.emit("error", { message: "Room already started" });
        return;
      }

      // Get problem
      const problemResult = await db.query(
        `SELECT p.*, json_agg(json_build_object('input', tc.input, 'output', tc.expected) ORDER BY tc.order_index) as examples
         FROM problems p
         LEFT JOIN test_cases tc ON tc.problem_id = p.id AND tc.is_hidden = false
         WHERE p.id = $1
         GROUP BY p.id`,
        [roomData.problemId]
      );
      const problem = problemResult.rows[0];
      if (problem.examples && problem.examples[0] === null) problem.examples = [];

      // Countdown
      await redis.hset(roomKey, "status", "countdown");
      io.to(roomCode).emit("room:state", { status: "countdown", players: [] });

      for (let i = 5; i >= 1; i--) {
        io.to(roomCode).emit("room:countdown", i);
        await new Promise((r) => setTimeout(r, 1000));
      }

      // Start active
      const timeLimit = 300; // 5 minutes
      await redis.hset(roomKey, "status", "active", "startedAt", Date.now(), "timeLimit", timeLimit);
      await redis.del(`${roomKey}:leaderboard`);

      io.to(roomCode).emit("room:started", {
        problem: {
          id: problem.id,
          title: problem.title,
          description: problem.description,
          difficulty: problem.difficulty,
          examples: problem.examples || [],
        },
        timeLimit,
      });

      // Auto-end after time limit
      setTimeout(async () => {
        await endRoom(roomCode);
      }, timeLimit * 1000);
    } catch (err) {
      console.error(err);
      socket.emit("error", { message: "Failed to start room" });
    }
  });

  socket.on("room:activity", async ({ code }) => {
    socket.to(code.toUpperCase()).emit("room:activity_pulse", socket.id);
  });

  socket.on("submission:submit", async ({ code: roomCode, language, problemId }) => {
    try {
      const rc = roomCode.toUpperCase();
      const roomKey = `room:${rc}`;
      const roomData = await redis.hgetall(roomKey);

      if (roomData.status !== "active") {
        socket.emit("submission:result", { passed: false, error: "Room not active" });
        return;
      }

      const sourceCode = socket.handshake.query.code || ""; // For MVP, we'll handle this differently
      // Actually, we need the code from the event. Let me fix:
      // The frontend sends code in the event, let me adjust
    } catch (err) {
      console.error(err);
    }
  });

  socket.on("disconnect", async () => {
    if (socket.roomCode) {
      const roomKey = `room:${socket.roomCode}`;
      await redis.srem(`${roomKey}:players`, socket.id);
      await redis.del(`${roomKey}:player:${socket.id}`);
      socket.to(socket.roomCode).emit("room:player_left", socket.id);
    }
  });
});

// Fix: handle submission with code properly
io.on("connection", (socket) => {
  // Re-attach submission handler with correct signature
  socket.on("submission:submit", async (data) => {
    try {
      const { code: roomCode, language, problemId, sourceCode } = data;
      const rc = roomCode.toUpperCase();
      const roomKey = `room:${rc}`;
      const roomData = await redis.hgetall(roomKey);

      if (roomData.status !== "active") {
        socket.emit("submission:result", { userId: socket.id, passed: false, error: "Room not active" });
        return;
      }

      // Get test cases
      const testResult = await db.query(
        `SELECT input, expected, is_hidden FROM test_cases WHERE problem_id = $1 ORDER BY order_index`,
        [problemId]
      );
      const tests = testResult.rows;

      // Add to BullMQ
      await submissionQueue.add("judge", {
        submissionId: uuidv4(),
        socketId: socket.id,
        roomCode: rc,
        sourceCode,
        language: language || "python",
        tests,
        problemId,
        userId: socket.id,
        alias: socket.alias,
        startedAt: parseInt(roomData.startedAt),
      });

      socket.emit("submission:result", { userId: socket.id, passed: false, status: "pending" });
    } catch (err) {
      console.error(err);
      socket.emit("submission:result", { userId: socket.id, passed: false, error: "Submission failed" });
    }
  });
});

// ─── BULLMQ WORKER ───
const submissionWorker = new Worker("submissions", async (job) => {
  const { socketId, roomCode, sourceCode, language, tests, userId, alias, startedAt } = job.data;

  let passedCount = 0;
  let totalCount = tests.length;
  let firstFail = null;

  // Run visible tests first
  const visibleTests = tests.filter((t) => !t.is_hidden);
  const hiddenTests = tests.filter((t) => t.is_hidden);

  for (const test of visibleTests) {
    const result = await submitCode({
      sourceCode,
      language,
      stdin: test.input,
      expectedOutput: test.expected,
    });

    const passed = result.statusId === 3 && result.stdout?.trim() === test.expected?.trim();
    if (passed) passedCount++;
    else if (!firstFail) firstFail = { test: "visible", error: result.statusDescription || "Wrong answer" };
  }

  // If visible tests pass, run hidden
  if (passedCount === visibleTests.length && hiddenTests.length > 0) {
    for (const test of hiddenTests) {
      const result = await submitCode({
        sourceCode,
        language,
        stdin: test.input,
        expectedOutput: test.expected,
      });
      const passed = result.statusId === 3 && result.stdout?.trim() === test.expected?.trim();
      if (passed) passedCount++;
      else if (!firstFail) firstFail = { test: "hidden", error: "Hidden test failed" };
    }
  }

  const allPassed = passedCount === totalCount;
  const timeTaken = Date.now() - startedAt;
  const score = allPassed ? Math.max(100, 100 + Math.floor((300000 - timeTaken) / 1000)) : 0;

  // Update Redis leaderboard
  await redis.zadd(`room:${roomCode}:leaderboard`, score, userId);
  await redis.hset(`room:${roomCode}:player:${userId}`, "score", score, "status", allPassed ? "finished" : "failed");

  // Get updated leaderboard
  const lb = await redis.zrevrange(`room:${roomCode}:leaderboard`, 0, -1, "WITHSCORES");
  const leaderboard = [];
  for (let i = 0; i < lb.length; i += 2) {
    const pid = lb[i];
    const pdata = await redis.hgetall(`room:${roomCode}:player:${pid}`);
    leaderboard.push({
      rank: Math.floor(i / 2) + 1,
      alias: pdata.alias || "Player",
      score: parseInt(lb[i + 1]),
      status: allPassed && pid === userId ? "Accepted" : pdata.status,
      timeMs: timeTaken,
    });
  }

  // Broadcast
  io.to(roomCode).emit("submission:result", {
    userId,
    passed: allPassed,
    score,
    testsPassed: passedCount,
    testsTotal: totalCount,
  });

  io.to(roomCode).emit("room:leaderboard", leaderboard);

  // Save to DB
  await db.query(
    `INSERT INTO submissions (id, room_id, user_id, code, status, score, time_taken_ms, submitted_at)
     VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())`,
    [job.data.submissionId, roomCode, userId, sourceCode, allPassed ? "accepted" : "wrong_answer", score, timeTaken]
  );
}, { connection: redis.options });

// ─── END ROOM ───
async function endRoom(roomCode) {
  const roomKey = `room:${roomCode}`;
  const roomData = await redis.hgetall(roomKey);
  if (roomData.status === "ended") return;

  await redis.hset(roomKey, "status", "ended");

  const lb = await redis.zrevrange(`${roomKey}:leaderboard`, 0, -1, "WITHSCORES");
  const leaderboard = [];
  for (let i = 0; i < lb.length; i += 2) {
    const pid = lb[i];
    const pdata = await redis.hgetall(`${roomKey}:player:${pid}`);
    leaderboard.push({
      rank: Math.floor(i / 2) + 1,
      alias: pdata.alias || "Player",
      score: parseInt(lb[i + 1]),
      status: pdata.status || "DNF",
      timeMs: 0,
    });
  }

  io.to(roomCode).emit("room:ended", { leaderboard });
  await db.query(`UPDATE rooms SET status = 'ended', ended_at = NOW() WHERE unique_code = $1`, [roomCode]);
}

// ─── START ───
const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
  console.log(`CodeBattle API + WS running on port ${PORT}`);
});
