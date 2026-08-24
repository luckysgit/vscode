"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { useParams } from "next/navigation";
import dynamic from "next/dynamic";
import { motion, AnimatePresence } from "framer-motion";
import { QRCodeSVG } from "qrcode.react";
import {
  Copy, Play, Clock, Trophy, CheckCircle2, XCircle,
  Loader2, Send, Users, Zap, Crown, Flame
} from "lucide-react";
import { getSocket, disconnectSocket } from "@/lib/socket";
import api from "@/lib/api";

const Editor = dynamic(() => import("@monaco-editor/react"), { ssr: false });

type RoomStatus = "lobby" | "countdown" | "active" | "ended";

interface Player {
  id: string;
  alias: string;
  isHost: boolean;
}

interface Problem {
  id: string;
  title: string;
  description: string;
  difficulty: string;
  examples: { input: string; output: string }[];
}

interface LeaderboardEntry {
  rank: number;
  alias: string;
  score: number;
  status: string;
  timeMs: number;
}

export default function RoomPage() {
  const { code } = useParams() as { code: string };
  const [status, setStatus] = useState<RoomStatus>("lobby");
  const [players, setPlayers] = useState<Player[]>([]);
  const [problem, setProblem] = useState<Problem | null>(null);
  const [codeEditor, setCodeEditor] = useState("# Write your solution here\n");
  const [countdown, setCountdown] = useState(5);
  const [timeLeft, setTimeLeft] = useState(0);
  const [submissionStatus, setSubmissionStatus] = useState<"idle" | "submitting" | "accepted" | "wrong" | "error">("idle");
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [myAlias, setMyAlias] = useState("");
  const [copied, setCopied] = useState(false);
  const [activityPulses, setActivityPulses] = useState<Record<string, boolean>>({});
  const [results, setResults] = useState<any>(null);
  const socketRef = useRef<any>(null);
  const timerRef = useRef<any>(null);

  // Generate alias on mount
  useEffect(() => {
    const aliases = ["SwiftFox", "CodeNinja", "ByteMaster", "NullPointer", "StackOverflow", "Recursion", "BinaryBeast", "PixelPioneer"];
    setMyAlias(aliases[Math.floor(Math.random() * aliases.length)]);
  }, []);

  // Connect socket
  useEffect(() => {
    const socket = getSocket();
    socketRef.current = socket;

    socket.emit("room:join", { code, alias: myAlias || "Player" });

    socket.on("room:state", (data: any) => {
      setStatus(data.status);
      setPlayers(data.players || []);
      if (data.problem) setProblem(data.problem);
      if (data.timeLeft) setTimeLeft(data.timeLeft);
    });

    socket.on("room:player_joined", (p: Player) => {
      setPlayers((prev) => [...prev.filter((x) => x.id !== p.id), p]);
    });

    socket.on("room:player_left", (id: string) => {
      setPlayers((prev) => prev.filter((p) => p.id !== id));
    });

    socket.on("room:countdown", (sec: number) => {
      setStatus("countdown");
      setCountdown(sec);
    });

    socket.on("room:started", (data: any) => {
      setStatus("active");
      setProblem(data.problem);
      setTimeLeft(data.timeLimit);
      setCodeEditor(`# ${data.problem.title}\n# Difficulty: ${data.problem.difficulty}\n\ndef solve():\n    pass\n`);
    });

    socket.on("room:activity_pulse", (userId: string) => {
      setActivityPulses((prev) => ({ ...prev, [userId]: true }));
      setTimeout(() => {
        setActivityPulses((prev) => ({ ...prev, [userId]: false }));
      }, 2000);
    });

    socket.on("submission:result", (data: any) => {
      if (data.userId === socket.id) {
        setSubmissionStatus(data.passed ? "accepted" : "wrong");
      }
    });

    socket.on("room:leaderboard", (data: LeaderboardEntry[]) => {
      setLeaderboard(data);
    });

    socket.on("room:ended", (data: any) => {
      setStatus("ended");
      setResults(data);
    });

    return () => {
      disconnectSocket();
    };
  }, [code, myAlias]);

  // Timer
  useEffect(() => {
    if (status === "active" && timeLeft > 0) {
      timerRef.current = setInterval(() => {
        setTimeLeft((t) => {
          if (t <= 1) {
            clearInterval(timerRef.current);
            return 0;
          }
          return t - 1;
        });
      }, 1000);
    }
    return () => clearInterval(timerRef.current);
  }, [status, timeLeft]);

  const copyCode = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const startRoom = () => {
    socketRef.current?.emit("room:start", { code });
  };

  const submitCode = async () => {
    if (!problem || submissionStatus === "submitting") return;
    setSubmissionStatus("submitting");
    socketRef.current?.emit("submission:submit", {
      code,
      language: "python",
      problemId: problem.id,
    });
  };

  const isHost = players.find((p) => p.id === socketRef.current?.id)?.isHost;
  const roomUrl = typeof window !== "undefined" ? `${window.location.origin}/room/${code}` : "";

  return (
    <main className="max-w-7xl mx-auto px-4 py-6 h-[calc(100vh-3.5rem)] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <div className="bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 flex items-center gap-3">
            <span className="text-slate-400 text-sm">Room Code</span>
            <span className="font-mono text-xl font-bold text-emerald-400 tracking-widest">{code}</span>
            <button onClick={copyCode} className="text-slate-500 hover:text-emerald-400 transition">
              {copied ? <CheckCircle2 className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            </button>
          </div>
          <div className="flex items-center gap-2 text-slate-400 text-sm">
            <Users className="w-4 h-4" />
            {players.length} player{players.length !== 1 ? "s" : ""}
          </div>
        </div>

        {status === "active" && (
          <div className="flex items-center gap-2 bg-slate-900 border border-slate-700 rounded-lg px-4 py-2">
            <Clock className="w-4 h-4 text-cyan-400" />
            <span className={`font-mono font-bold ${timeLeft < 60 ? "text-red-400" : "text-slate-200"}`}>
              {Math.floor(timeLeft / 60)}:{String(timeLeft % 60).padStart(2, "0")}
            </span>
          </div>
        )}
      </div>

      {/* LOBBY */}
      {status === "lobby" && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex-1 flex flex-col items-center justify-center gap-8"
        >
          <div className="bg-white p-4 rounded-xl">
            <QRCodeSVG value={roomUrl} size={180} />
          </div>
          <p className="text-slate-400">Scan to join or share code: <span className="text-emerald-400 font-mono font-bold">{code}</span></p>

          <div className="w-full max-w-md">
            <h3 className="text-sm font-bold text-slate-400 mb-3 uppercase tracking-wider">Players</h3>
            <div className="space-y-2">
              <AnimatePresence>
                {players.map((p) => (
                  <motion.div
                    key={p.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0 }}
                    className="flex items-center gap-3 bg-slate-900 border border-slate-800 rounded-lg px-4 py-3"
                  >
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center text-xs font-bold">
                      {p.alias[0]}
                    </div>
                    <span className="font-medium">{p.alias}</span>
                    {p.isHost && <Crown className="w-4 h-4 text-amber-400 ml-auto" />}
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </div>

          {isHost && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={startRoom}
              className="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold px-8 py-4 rounded-xl text-lg transition"
            >
              <Play className="w-5 h-5" /> Start Battle
            </motion.button>
          )}
        </motion.div>
      )}

      {/* COUNTDOWN */}
      {status === "countdown" && (
        <div className="flex-1 flex items-center justify-center">
          <motion.div
            key={countdown}
            initial={{ scale: 2, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            className="text-9xl font-black text-emerald-400"
          >
            {countdown}
          </motion.div>
        </div>
      )}

      {/* ACTIVE */}
      {status === "active" && problem && (
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-4 min-h-0">
          {/* Problem Panel */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 overflow-auto">
            <div className="flex items-center gap-3 mb-4">
              <h2 className="text-xl font-bold">{problem.title}</h2>
              <span className={`text-xs font-bold px-2 py-1 rounded ${
                problem.difficulty === "easy" ? "bg-emerald-500/20 text-emerald-400" :
                problem.difficulty === "medium" ? "bg-amber-500/20 text-amber-400" :
                "bg-red-500/20 text-red-400"
              }`}>
                {problem.difficulty.toUpperCase()}
              </span>
            </div>
            <div className="prose prose-invert max-w-none mb-6 text-slate-300 leading-relaxed">
              {problem.description}
            </div>
            <div className="space-y-4">
              {problem.examples?.map((ex, i) => (
                <div key={i} className="bg-slate-950 rounded-lg p-4 border border-slate-800">
                  <p className="text-xs text-slate-500 mb-2 font-bold uppercase">Example {i + 1}</p>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-slate-500">Input:</span>
                      <pre className="mt-1 text-emerald-400 font-mono">{ex.input}</pre>
                    </div>
                    <div>
                      <span className="text-slate-500">Output:</span>
                      <pre className="mt-1 text-cyan-400 font-mono">{ex.output}</pre>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Live Activity */}
            <div className="mt-6 pt-4 border-t border-slate-800">
              <p className="text-xs text-slate-500 mb-2 flex items-center gap-2">
                <Zap className="w-3 h-3" /> Live Activity
              </p>
              <div className="flex gap-2 flex-wrap">
                {players.filter((p) => p.id !== socketRef.current?.id).map((p) => (
                  <motion.div
                    key={p.id}
                    animate={{ opacity: activityPulses[p.id] ? 1 : 0.5 }}
                    className="flex items-center gap-1 text-xs bg-slate-800 px-2 py-1 rounded"
                  >
                    <Flame className="w-3 h-3 text-orange-400" />
                    {p.alias} {activityPulses[p.id] && "is typing..."}
                  </motion.div>
                ))}
              </div>
            </div>
          </div>

          {/* Editor Panel */}
          <div className="flex flex-col gap-4 min-h-0">
            <div className="flex-1 border border-slate-800 rounded-xl overflow-hidden bg-slate-950">
              <Editor
                height="100%"
                defaultLanguage="python"
                value={codeEditor}
                onChange={(v) => {
                  setCodeEditor(v || "");
                  socketRef.current?.emit("room:activity", { code });
                }}
                theme="vs-dark"
                options={{
                  fontSize: 14,
                  minimap: { enabled: false },
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                  padding: { top: 16 },
                }}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {submissionStatus === "accepted" && (
                  <span className="flex items-center gap-1 text-emerald-400 text-sm font-bold">
                    <CheckCircle2 className="w-4 h-4" /> Accepted!
                  </span>
                )}
                {submissionStatus === "wrong" && (
                  <span className="flex items-center gap-1 text-red-400 text-sm font-bold">
                    <XCircle className="w-4 h-4" /> Wrong Answer
                  </span>
                )}
                {submissionStatus === "submitting" && (
                  <span className="flex items-center gap-1 text-amber-400 text-sm">
                    <Loader2 className="w-4 h-4 animate-spin" /> Judging...
                  </span>
                )}
              </div>
              <button
                onClick={submitCode}
                disabled={submissionStatus === "submitting"}
                className="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-slate-950 font-bold px-6 py-3 rounded-lg transition"
              >
                <Send className="w-4 h-4" /> Submit
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ENDED */}
      {status === "ended" && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex-1 flex flex-col items-center justify-center"
        >
          <Trophy className="w-16 h-16 text-amber-400 mb-4" />
          <h2 className="text-3xl font-bold mb-8">Battle Complete!</h2>
          <div className="w-full max-w-lg space-y-3">
            {leaderboard.map((entry, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                className={`flex items-center gap-4 p-4 rounded-xl border ${
                  i === 0 ? "bg-amber-500/10 border-amber-500/30" :
                  i === 1 ? "bg-slate-400/10 border-slate-400/30" :
                  i === 2 ? "bg-orange-700/10 border-orange-700/30" :
                  "bg-slate-900 border-slate-800"
                }`}
              >
                <span className="text-2xl font-black w-8 text-center">{entry.rank}</span>
                <div className="flex-1">
                  <p className="font-bold">{entry.alias}</p>
                  <p className="text-xs text-slate-400">{entry.status}</p>
                </div>
                <div className="text-right">
                  <p className="font-bold text-emerald-400">{entry.score} pts</p>
                  <p className="text-xs text-slate-500">{Math.floor(entry.timeMs / 1000)}s</p>
                </div>
              </motion.div>
            ))}
          </div>
          <button
            onClick={() => window.location.href = "/"}
            className="mt-8 bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold px-6 py-3 rounded-lg transition"
          >
            Back to Home
          </button>
        </motion.div>
      )}
    </main>
  );
}
