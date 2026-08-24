"use client";

import "./globals.css";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">
        <nav className="border-b border-slate-800 bg-slate-900/50 backdrop-blur sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
            <a href="/" className="text-xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
              CodeBattle
            </a>
            <div className="flex gap-4 text-sm text-slate-400">
              <a href="/" className="hover:text-emerald-400 transition">Home</a>
              <a href="/dashboard" className="hover:text-emerald-400 transition">Dashboard</a>
            </div>
          </div>
        </nav>
        {children}
      </body>
    </html>
  );
}
