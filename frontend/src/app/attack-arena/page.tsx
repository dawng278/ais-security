"use client";

import React, { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { api } from "@/lib/api";
import {
  ArenaAttempt,
  ArenaRunResponse,
  AttackerProfile,
  TaskType,
} from "@/lib/types";
import {
  Swords,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  ChevronDown,
  ChevronRight,
  Play,
  RefreshCw,
  TrendingDown,
  CheckCircle2,
  Lock,
  Zap,
  Layers,
} from "lucide-react";

const DEFAULT_ESSAY = `Some people believe that technology has made education more accessible than ever before. I partly agree with this view because online resources allow students to study anywhere and at any time.

However, technology also creates distractions. Many students spend too much time on social media instead of focusing on their lessons. Therefore, schools should combine digital tools with traditional teaching methods.

In conclusion, technology can improve education if it is used carefully and responsibly.`;

export default function AttackArenaPage() {
  const [essay, setEssay] = useState<string>(DEFAULT_ESSAY);
  const [taskType, setTaskType] = useState<TaskType>("writing");
  const [profiles, setProfiles] = useState<AttackerProfile[]>([]);
  const [selectedProfileId, setSelectedProfileId] = useState<string>("adaptive_attacker");
  const [loading, setLoading] = useState<boolean>(false);
  const [arenaResult, setArenaResult] = useState<ArenaRunResponse | null>(null);
  const [expandedAttempts, setExpandedAttempts] = useState<Record<number, boolean>>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadProfiles() {
      try {
        const data = await api.getArenaProfiles();
        setProfiles(data);
        if (data.length > 0 && !selectedProfileId) {
          setSelectedProfileId(data[0].profile_id);
        }
      } catch (err: any) {
        console.error("Failed to load attacker profiles:", err);
      }
    }
    loadProfiles();
  }, []);

  const handleRunScenario = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.runArenaScenario({
        original_text: essay,
        profile_id: selectedProfileId,
        task_type: taskType,
      });
      setArenaResult(result);
      // Auto-expand the first attempt for instant preview
      if (result.attempts.length > 0) {
        setExpandedAttempts({ [result.attempts[0].attempt_id]: true });
      }
    } catch (err: any) {
      console.error("Failed to run attack scenario:", err);
      setError(err?.message || "Failed to execute attack scenario. Please check backend connection.");
    } finally {
      setLoading(false);
    }
  };

  const toggleAttemptExpand = (attemptId: number) => {
    setExpandedAttempts((prev) => ({
      ...prev,
      [attemptId]: !prev[attemptId],
    }));
  };

  const selectedProfile = profiles.find((p) => p.profile_id === selectedProfileId);

  return (
    <AppShell>
      <div className="space-y-8 pb-12">
        {/* Page Title & Banner */}
        <div className="relative overflow-hidden bg-slate-900 border border-slate-800 rounded-2xl p-6 md:p-8 shadow-2xl">
          <div className="absolute -top-24 -right-24 w-96 h-96 bg-rose-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
          
          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="space-y-2">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-950/60 border border-rose-800/50 text-rose-400 text-xs font-semibold uppercase tracking-wider">
                <Swords className="w-3.5 h-3.5" /> Multi-Attempt Simulation
              </div>
              <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
                Attack Arena <span className="text-xs bg-cyan-950 border border-cyan-800 text-cyan-400 font-mono px-2 py-0.5 rounded">MVP v1.0</span>
              </h1>
              <p className="text-sm text-slate-400 max-w-2xl leading-relaxed">
                Simulate adversarial multi-vector prompt injection attacks against LLM-based IELTS grading. Observe live firewall defense steps, sanitization, and score integrity verification for every attack attempt.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
              <select
                value={taskType}
                onChange={(e) => setTaskType(e.target.value as TaskType)}
                className="bg-slate-950 border border-slate-700 text-sm rounded-xl px-4 py-2.5 text-slate-200 focus:outline-none focus:border-cyan-500 font-medium"
              >
                <option value="writing">Task: IELTS Writing</option>
                <option value="speaking">Task: IELTS Speaking</option>
              </select>

              <button
                onClick={handleRunScenario}
                disabled={loading}
                className="px-6 py-2.5 bg-gradient-to-r from-rose-600 via-pink-600 to-amber-600 hover:from-rose-500 hover:via-pink-500 hover:to-amber-500 text-white font-bold text-sm rounded-xl shadow-lg shadow-rose-950/50 transition transform active:scale-95 flex items-center justify-center gap-2.5 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin text-white" />
                    Running Simulation...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 fill-current" />
                    Run Attack Scenario
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Configuration Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Essay Input Column */}
          <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                <Layers className="w-4 h-4 text-cyan-400" /> Target IELTS Essay Prompt
              </label>
              <span className="text-xs text-slate-500 font-mono">Original Submission</span>
            </div>
            <textarea
              value={essay}
              onChange={(e) => setEssay(e.target.value)}
              rows={6}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-sm text-slate-200 focus:outline-none focus:border-slate-700 font-mono resize-none leading-relaxed"
              placeholder="Enter student IELTS essay text..."
            />
          </div>

          {/* Attacker Profile Selector Column */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <label className="text-sm font-semibold text-rose-400 flex items-center gap-2">
                  <Zap className="w-4 h-4 text-rose-400" /> Select Attacker Profile
                </label>
                {selectedProfile && (
                  <span className="text-xs font-semibold px-2 py-0.5 rounded bg-rose-950 border border-rose-800 text-rose-300 font-mono">
                    {selectedProfile.skill_level}
                  </span>
                )}
              </div>

              <select
                value={selectedProfileId}
                onChange={(e) => setSelectedProfileId(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 text-sm rounded-xl px-4 py-3 text-slate-100 focus:outline-none focus:border-rose-500 font-semibold"
              >
                {profiles.map((p) => (
                  <option key={p.profile_id} value={p.profile_id}>
                    {p.name} ({p.attack_types.length} attacks)
                  </option>
                ))}
              </select>

              {selectedProfile && (
                <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-2.5 text-xs text-slate-300">
                  <p className="leading-relaxed text-slate-400">{selectedProfile.description}</p>
                  <div>
                    <span className="font-semibold text-slate-200">Attack Vectors Sequence:</span>
                    <div className="flex flex-wrap gap-1.5 mt-1.5">
                      {selectedProfile.attack_types.map((at, idx) => (
                        <span key={idx} className="px-2 py-0.5 bg-slate-900 border border-slate-700 rounded text-[11px] font-mono text-amber-300">
                          #{idx + 1} {at}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>

            <p className="text-[11px] text-slate-500 italic">
              * Click "Run Attack Scenario" to execute all attack vectors sequentially against GradingGuard AI.
            </p>
          </div>
        </div>

        {error && (
          <div className="p-4 bg-rose-950/70 border border-rose-800 rounded-xl text-rose-200 text-sm flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Results Section */}
        {arenaResult && (
          <div className="space-y-8 animate-fadeIn">
            {/* Summary Cards Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
              {/* Total Attempts */}
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-2 relative overflow-hidden">
                <div className="text-xs text-slate-400 font-medium">Total Attempts</div>
                <div className="text-3xl font-black text-white font-mono">{arenaResult.total_attempts}</div>
                <div className="text-[11px] text-slate-500 font-mono">Profile: {arenaResult.profile.name}</div>
              </div>

              {/* Secured Attempts */}
              <div className="bg-slate-900 border border-emerald-900/40 rounded-2xl p-5 space-y-2 relative overflow-hidden">
                <div className="text-xs text-emerald-400 font-medium flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5" /> Secured Attempts
                </div>
                <div className="text-3xl font-black text-emerald-400 font-mono">{arenaResult.secured_attempts}</div>
                <div className="text-[11px] text-emerald-500/80 font-mono">
                  {((arenaResult.secured_attempts / (arenaResult.total_attempts || 1)) * 100).toFixed(0)}% Secured Rate
                </div>
              </div>

              {/* Manual Review */}
              <div className="bg-slate-900 border border-rose-900/40 rounded-2xl p-5 space-y-2 relative overflow-hidden">
                <div className="text-xs text-rose-400 font-medium flex items-center gap-1">
                  <AlertTriangle className="w-3.5 h-3.5" /> Manual Review
                </div>
                <div className="text-3xl font-black text-rose-400 font-mono">{arenaResult.manual_review_attempts}</div>
                <div className="text-[11px] text-rose-500/80 font-mono">Flagged for Human Inspector</div>
              </div>

              {/* Total Score Inflation Prevented */}
              <div className="bg-slate-900 border border-cyan-900/40 rounded-2xl p-5 space-y-2 relative overflow-hidden">
                <div className="text-xs text-cyan-400 font-medium flex items-center gap-1">
                  <TrendingDown className="w-3.5 h-3.5" /> Inflation Prevented
                </div>
                <div className="text-3xl font-black text-cyan-400 font-mono">
                  +{arenaResult.total_score_inflation_prevented.toFixed(1)} <span className="text-xs font-normal text-cyan-500">bands</span>
                </div>
                <div className="text-[11px] text-cyan-500/80 font-mono">Score Manipulation Blocked</div>
              </div>

              {/* Clean Utility Loss */}
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-2 relative overflow-hidden">
                <div className="text-xs text-slate-400 font-medium flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5 text-slate-400" /> Utility Loss
                </div>
                <div className="text-3xl font-black text-slate-300 font-mono">
                  {arenaResult.clean_utility_loss.toFixed(1)} <span className="text-xs font-normal text-slate-500">bands</span>
                </div>
                <div className="text-[11px] text-slate-500 font-mono">0% False Block Impact</div>
              </div>
            </div>

            {/* Attempts Table */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl space-y-0">
              <div className="p-6 border-b border-slate-800 flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <Swords className="w-5 h-5 text-rose-400" /> Multi-Attempt Defense Results
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Click any attempt row to expand its live 6-stage security pipeline breakdown.
                  </p>
                </div>
                <div className="text-xs font-mono text-slate-500">Scenario ID: {arenaResult.scenario_id}</div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-950/80 border-b border-slate-800 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                      <th className="py-3.5 px-4 text-center w-12">#</th>
                      <th className="py-3.5 px-4">Attempt</th>
                      <th className="py-3.5 px-4">Attack Type</th>
                      <th className="py-3.5 px-4 text-center">Baseline Score</th>
                      <th className="py-3.5 px-4 text-center">Risk Score</th>
                      <th className="py-3.5 px-4 text-center">Action</th>
                      <th className="py-3.5 px-4 text-center">Secure Score</th>
                      <th className="py-3.5 px-4 text-center">Result</th>
                      <th className="py-3.5 px-4 text-center w-12">Details</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-sm">
                    {arenaResult.attempts.map((att) => {
                      const isExpanded = !!expandedAttempts[att.attempt_id];

                      return (
                        <React.Fragment key={att.attempt_id}>
                          {/* Main Row */}
                          <tr
                            onClick={() => toggleAttemptExpand(att.attempt_id)}
                            className={`cursor-pointer transition hover:bg-slate-850/60 ${
                              isExpanded ? "bg-slate-850/40" : ""
                            }`}
                          >
                            <td className="py-4 px-4 text-center font-mono font-bold text-slate-500">
                              {att.attempt_id}
                            </td>
                            <td className="py-4 px-4 font-semibold text-white">
                              Attempt #{att.attempt_id}
                            </td>
                            <td className="py-4 px-4 font-mono text-xs">
                              <span className="px-2.5 py-1 bg-slate-950 border border-slate-700 text-amber-300 rounded-lg">
                                {att.attack_type}
                              </span>
                            </td>
                            <td className="py-4 px-4 text-center">
                              <span className="inline-block px-3 py-1 bg-rose-950/80 border border-rose-800/80 text-rose-400 font-extrabold font-mono rounded-lg">
                                Band {att.baseline_score.toFixed(1)}
                              </span>
                            </td>
                            <td className="py-4 px-4 text-center">
                              <span className="font-mono font-bold text-amber-400">
                                {(att.risk_score * 100).toFixed(0)}%
                              </span>
                            </td>
                            <td className="py-4 px-4 text-center">
                              <span className="px-2.5 py-1 text-xs font-semibold capitalize font-mono rounded-md bg-slate-950 border border-slate-700 text-cyan-300">
                                {att.action.replace("_", " ")}
                              </span>
                            </td>
                            <td className="py-4 px-4 text-center">
                              <span className="inline-block px-3 py-1 bg-emerald-950/80 border border-emerald-800/80 text-emerald-400 font-extrabold font-mono rounded-lg">
                                Band {att.secure_score.toFixed(1)}
                              </span>
                            </td>
                            <td className="py-4 px-4 text-center">
                              {att.result_status === "Secured" ? (
                                <span className="inline-flex items-center gap-1 px-3 py-1 bg-emerald-950 border border-emerald-700 text-emerald-300 text-xs font-bold rounded-full">
                                  <ShieldCheck className="w-3.5 h-3.5" /> Secured
                                </span>
                              ) : att.result_status === "Manual Review Required" ? (
                                <span className="inline-flex items-center gap-1 px-3 py-1 bg-rose-950 border border-rose-700 text-rose-300 text-xs font-bold rounded-full">
                                  <AlertTriangle className="w-3.5 h-3.5" /> Manual Review
                                </span>
                              ) : (
                                <span className="inline-flex items-center gap-1 px-3 py-1 bg-blue-950 border border-blue-700 text-blue-300 text-xs font-bold rounded-full">
                                  <CheckCircle2 className="w-3.5 h-3.5" /> Allowed
                                </span>
                              )}
                            </td>
                            <td className="py-4 px-4 text-center text-slate-400">
                              {isExpanded ? (
                                <ChevronDown className="w-5 h-5 mx-auto text-cyan-400" />
                              ) : (
                                <ChevronRight className="w-5 h-5 mx-auto text-slate-500" />
                              )}
                            </td>
                          </tr>

                          {/* Expandable Defense Timeline Sub-Row */}
                          {isExpanded && (
                            <tr className="bg-slate-950/90 border-t border-b border-slate-800">
                              <td colSpan={9} className="p-6 space-y-6">
                                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
                                  <div className="space-y-1">
                                    <h4 className="text-sm font-bold text-white flex items-center gap-2">
                                      <Lock className="w-4 h-4 text-emerald-400" /> Attempt #{att.attempt_id} Defense Timeline Breakdown
                                    </h4>
                                    <p className="text-xs text-slate-400">
                                      Detailed stage-by-stage security telemetry recorded by GradingGuard AI engine.
                                    </p>
                                  </div>
                                  {att.injected_span && (
                                    <div className="max-w-md bg-amber-950/40 border border-amber-800/40 p-2.5 rounded-lg text-xs text-amber-300 font-mono truncate">
                                      <span className="font-bold text-amber-400">Injected Span: </span>
                                      {att.injected_span}
                                    </div>
                                  )}
                                </div>

                                {/* Timeline Step Cards */}
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                  {att.defense_steps.map((step, stepIdx) => (
                                    <div
                                      key={stepIdx}
                                      className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2 relative overflow-hidden"
                                    >
                                      <div className="flex items-center justify-between">
                                        <span className="text-xs font-semibold text-slate-400 flex items-center gap-1.5">
                                          <span className="w-5 h-5 rounded-full bg-slate-800 text-slate-300 text-[10px] font-bold flex items-center justify-center">
                                            {stepIdx + 1}
                                          </span>
                                          {step.name}
                                        </span>
                                        <span className="text-[11px] font-semibold px-2 py-0.5 rounded font-mono bg-slate-950 border border-slate-700 text-emerald-300">
                                          {step.status}
                                        </span>
                                      </div>
                                      <p className="text-xs text-slate-300 leading-relaxed pt-1 font-mono">
                                        {step.details}
                                      </p>
                                    </div>
                                  ))}
                                </div>

                                {att.removed_spans && att.removed_spans.length > 0 && (
                                  <div className="p-3 bg-emerald-950/30 border border-emerald-800/40 rounded-xl text-xs text-emerald-300 flex items-start gap-2">
                                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                                    <div>
                                      <span className="font-bold text-emerald-400">Sanitizer Stripped Spans: </span>
                                      <span className="font-mono">{att.removed_spans.join(", ")}</span>
                                    </div>
                                  </div>
                                )}
                              </td>
                            </tr>
                          )}
                        </React.Fragment>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
