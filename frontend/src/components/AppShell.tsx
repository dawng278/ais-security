import React from "react";
import Link from "next/link";
import { ShieldCheck, Terminal, LayoutDashboard, BarChart3, Swords, GitBranch, Trophy } from "lucide-react";

interface AppShellProps {
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-tr from-emerald-500 to-cyan-500 rounded-lg text-slate-950 font-bold">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-lg font-bold bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                GradingGuard AI
              </h1>
              <p className="text-xs text-emerald-400 font-mono">IELTS AI Grading Security Gateway</p>
            </div>
          </div>

          <nav className="flex items-center space-x-1 sm:space-x-3 text-sm">
            <Link
              href="/judge-view"
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-amber-950/60 hover:bg-amber-900/80 text-amber-300 font-bold border border-amber-800/80 transition"
            >
              <Trophy className="w-4 h-4 text-amber-400" />
              <span>Judge View</span>
            </Link>
            <Link
              href="/attack-arena"
              className="flex items-center space-x-1.5 px-2.5 py-1.5 rounded-md hover:bg-slate-800 text-rose-400 font-medium hover:text-rose-300 transition"
            >
              <Swords className="w-4 h-4 text-rose-400" />
              <span>Attack Arena</span>
            </Link>
            <Link
              href="/playground"
              className="flex items-center space-x-1.5 px-2.5 py-1.5 rounded-md hover:bg-slate-800 text-slate-300 hover:text-white transition"
            >
              <Terminal className="w-4 h-4 text-cyan-400" />
              <span>Playground</span>
            </Link>
            <Link
              href="/dashboard"
              className="flex items-center space-x-1.5 px-2.5 py-1.5 rounded-md hover:bg-slate-800 text-slate-300 hover:text-white transition"
            >
              <LayoutDashboard className="w-4 h-4 text-emerald-400" />
              <span>Dashboard</span>
            </Link>
            <Link
              href="/benchmark"
              className="flex items-center space-x-1.5 px-2.5 py-1.5 rounded-md hover:bg-slate-800 text-slate-300 hover:text-white transition"
            >
              <BarChart3 className="w-4 h-4 text-teal-400" />
              <span>Benchmark</span>
            </Link>
            <Link
              href="/data-lineage"
              className="flex items-center space-x-1.5 px-2.5 py-1.5 rounded-md hover:bg-slate-800 text-indigo-400 font-medium hover:text-indigo-300 transition"
            >
              <GitBranch className="w-4 h-4 text-indigo-400" />
              <span>Data Lineage</span>
            </Link>
          </nav>
        </div>
      </header>



      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-4 text-center text-xs text-slate-500">
        GradingGuard AI — Robustness Layer Against Prompt Injection & Score Manipulation in LLM Assessment
      </footer>
    </div>
  );
};
