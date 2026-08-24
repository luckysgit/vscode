"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Swords, Users, Zap, Trophy, ArrowRight } from "lucide-react";
import axios from "axios";

export default function Home() {
  const router = useRouter();
  const [joinCode, setJoinCode] = useState("");
  const [loading, setLoading] = useState(false);

  const createRoom = async () => {
    setLoading(true);
    try {
      const { data } = await axios.post("/api/rooms");
      router.push(`/room/${data.code}`);
    } catch (e) {
      alert("Failed to create room");
    } finally {
      setLoading(false);
    }
  };

  const joinRoom = async () => {
    if (!joinCode.trim()) return;
    router.push(`/room/${joinCode.trim().toUpperCase()}`);
  };

  return (
    <main className="max-w-5xl mx-auto px-4 py-16">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-16"
      >
        <h1 className="text-5xl md:text-7xl font-extrabold mb-6">
          <span className="bg-gradient-to-r from-emerald-400 via-cyan-400 to-blue-500 bg-clip-text text-transparent">
            Battle. Code. Win.
          </span>
        </h1>
        <p className="text-slate-400 text-lg max-w-2xl mx-auto">
          Real-time competitive coding. Create a room, share the code, and race your friends to solve problems.
        </p>
      </motion.div>

      <div className="grid md:grid-cols-2 gap-8 max-w-3xl mx-auto mb-20">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={createRoom}
          disabled={loading}
          className="group relative overflow-hidden rounded-2xl bg-emerald-500/10 border border-emerald-500/20 p-8 text-left hover:border-emerald-500/40 transition"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-cyan-500/5 opacity-0 group-hover:opacity-100 transition" />
          <Swords className="w-10 h-10 text-emerald-400 mb-4" />
          <h3 className="text-xl font-bold mb-2 flex items-center gap-2">
            Create Room <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition" />
          </h3>
          <p className="text-slate-400 text-sm">Host a battle and invite friends with a room code.</p>
        </motion.button>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="rounded-2xl bg-slate-900 border border-slate-800 p-8"
        >
          <Users className="w-10 h-10 text-cyan-400 mb-4" />
          <h3 className="text-xl font-bold mb-4">Join Room</h3>
          <div className="flex gap-3">
            <input
              value={joinCode}
              onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
              placeholder="ENTER CODE"
              maxLength={6}
              className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-center font-mono tracking-widest uppercase focus:outline-none focus:border-cyan-500 transition"
            />
            <button
              onClick={joinRoom}
              className="bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold px-6 py-3 rounded-lg transition"
            >
              Join
            </button>
          </div>
        </motion.div>
      </div>

      <div className="grid md:grid-cols-3 gap-6 text-center">
        {[
          { icon: Zap, title: "Real-time", desc: "Live leaderboard updates as you code" },
          { icon: Trophy, title: "Ranked", desc: "Speed + correctness scoring system" },
          { icon: Users, title: "Multiplayer", desc: "Up to 100 players per room" },
        ].map((f, i) => (
          <motion.div
            key={f.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 + i * 0.1 }}
            className="p-6 rounded-xl bg-slate-900/50 border border-slate-800"
          >
            <f.icon className="w-8 h-8 text-emerald-400 mx-auto mb-3" />
            <h4 className="font-bold mb-1">{f.title}</h4>
            <p className="text-slate-400 text-sm">{f.desc}</p>
          </motion.div>
        ))}
      </div>
    </main>
  );
}
