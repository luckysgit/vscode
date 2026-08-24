"use client";

import { motion } from "framer-motion";
import { Trophy, Flame, Code2, Zap } from "lucide-react";

export default function Dashboard() {
  return (
    <main className="max-w-5xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>

      <div className="grid md:grid-cols-3 gap-4 mb-8">
        {[
          { label: "Rooms Created", value: 0, icon: Zap, color: "text-emerald-400" },
          { label: "Submissions", value: 0, icon: Code2, color: "text-cyan-400" },
          { label: "Problems", value: 3, icon: Trophy, color: "text-amber-400" },
        ].map((stat) => (
          <motion.div
            key={stat.label}
            whileHover={{ scale: 1.02 }}
            className="bg-slate-900 border border-slate-800 rounded-xl p-6"
          >
            <stat.icon className={`w-8 h-8 ${stat.color} mb-3`} />
            <p className="text-3xl font-bold">{stat.value}</p>
            <p className="text-slate-400 text-sm">{stat.label}</p>
          </motion.div>
        ))}
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <Flame className="w-5 h-5 text-orange-400" /> Quick Start
        </h2>
        <div className="space-y-3 text-slate-300">
          <p>1. Click <strong>Create Room</strong> on the home page</p>
          <p>2. Share the 6-digit code or QR with friends</p>
          <p>3. Click <strong>Start Battle</strong> when everyone is ready</p>
          <p>4. Solve the problem and hit <strong>Submit</strong>!</p>
        </div>
      </div>
    </main>
  );
}
