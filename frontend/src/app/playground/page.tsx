"use client";

import React, { useState } from "react";
import { AppShell } from "@/components/AppShell";
import { api } from "@/lib/api";
import { AttackType, FirewallResult, GradingResult, SecureGradeResponse, TaskType } from "@/lib/types";
import { ShieldAlert, Play, AlertTriangle, CheckCircle2, RefreshCw } from "lucide-react";

const DEFAULT_ESSAY = `Some people believe that technology has made education more accessible than ever before. I partly agree with this view because online resources allow students to study anywhere and at any time.

However, technology also creates distractions. Many students spend too much time on social media instead of focusing on their lessons. Therefore, schools should combine digital tools with traditional teaching methods.

In conclusion, technology can improve education if it is used carefully and responsibly.`;

export default function PlaygroundPage() {
  const [taskType, setTaskType] = useState<TaskType>("writing");
  const [attackType, setAttackType] = useState<AttackType>("direct_vietnamese");
  const [originalText, setOriginalText] = useState(DEFAULT_ESSAY);
  const [injectedText, setInjectedText] = useState("");
  const [injectedSpan, setInjectedSpan] = useState("");

  const [loading, setLoading] = useState(false);
  const [firewallRes, setFirewallRes] = useState<FirewallResult | null>(null);
  const [baselineScore, setBaselineScore] = useState<GradingResult | null>(null);
  const [secureRes, setSecureRes] = useState<SecureGradeResponse | null>(null);

  const handleGenerateAttack = async () => {
    setLoading(true);
    try {
      const res = await api.generateAttack({
        text: originalText,
        task_type: taskType,
        attack_type: attackType,
      });
      setInjectedText(res.injected_text);
      setInjectedSpan(res.injected_span);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunBaseline = async () => {
    setLoading(true);
    try {
      const targetText = injectedText || originalText;
      const res = await api.baselineGrade({ text: targetText, task_type: taskType });
      setBaselineScore(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunSecure = async () => {
    setLoading(true);
    try {
      const targetText = injectedText || originalText;
      const res = await api.secureGrade({ text: targetText, task_type: taskType });
      setSecureRes(res);
      setFirewallRes(res.firewall);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-cyan-400" /> Security Playground
            </h2>
            <p className="text-sm text-slate-400">
              Test prompt injection attacks against unprotected LLM baseline vs. GradingGuard AI.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <select
              value={taskType}
              onChange={(e) => setTaskType(e.target.value as TaskType)}
              className="bg-slate-950 border border-slate-700 text-sm rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500"
            >
              <option value="writing">Task: IELTS Writing</option>
              <option value="speaking">Task: Speaking Transcript</option>
            </select>

            <select
              value={attackType}
              onChange={(e) => setAttackType(e.target.value as AttackType)}
              className="bg-slate-950 border border-slate-700 text-sm rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500"
            >
              <option value="direct_vietnamese">Attack: Direct Vietnamese</option>
              <option value="direct_english">Attack: Direct English</option>
              <option value="unicode_obfuscation">Attack: Unicode Spacing</option>
              <option value="markdown_role_spoofing">Attack: Role Spoofing</option>
            </select>

            <button
              onClick={handleGenerateAttack}
              disabled={loading}
              className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-sm font-semibold rounded-lg shadow transition flex items-center gap-2"
            >
              {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
              Generate Attack
            </button>
          </div>
        </div>

        {/* 3 Columns Editor & Firewall Result */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Column 1: Original Essay */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-slate-300">Clean Student Essay</label>
              <span className="text-xs text-slate-500">Original</span>
            </div>
            <textarea
              value={originalText}
              onChange={(e) => setOriginalText(e.target.value)}
              rows={12}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-200 focus:outline-none focus:border-slate-600 font-mono resize-none"
            />
          </div>

          {/* Column 2: Injected Essay */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-amber-400 flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4" /> Injected Payload Essay
              </label>
              <span className="text-xs text-amber-500/80 font-mono">Red-team Output</span>
            </div>
            <textarea
              value={injectedText}
              onChange={(e) => setInjectedText(e.target.value)}
              placeholder="Click 'Generate Attack' to inject payload..."
              rows={12}
              className="w-full bg-slate-950 border border-amber-900/50 text-amber-200/90 rounded-lg p-3 text-sm focus:outline-none focus:border-amber-600 font-mono resize-none"
            />
            {injectedSpan && (
              <div className="p-2.5 bg-amber-950/40 border border-amber-800/40 rounded-lg text-xs text-amber-300">
                <span className="font-semibold text-amber-400">Injected Span: </span>
                {injectedSpan}
              </div>
            )}
          </div>

          {/* Column 3: Firewall & Verifier Result */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col space-y-4">
            <h3 className="text-sm font-medium text-slate-300 flex items-center gap-1.5">
              <ShieldAlert className="w-4 h-4 text-emerald-400" /> Firewall Telemetry
            </h3>

            {firewallRes ? (
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-slate-950 border border-slate-800 p-3 rounded-lg">
                    <div className="text-xs text-slate-500">Risk Score</div>
                    <div className="text-xl font-bold text-amber-400">
                      {(firewallRes.risk_score * 100).toFixed(0)}%
                    </div>
                  </div>
                  <div className="bg-slate-950 border border-slate-800 p-3 rounded-lg">
                    <div className="text-xs text-slate-500">Action</div>
                    <div className="text-sm font-semibold capitalize text-emerald-400">
                      {firewallRes.action.replace("_", " ")}
                    </div>
                  </div>
                </div>

                <div className="bg-slate-950 border border-slate-800 p-3 rounded-lg text-xs space-y-1.5">
                  <div className="text-slate-400 font-medium">Attack Classification:</div>
                  <div className="text-amber-300 font-mono">{firewallRes.attack_type}</div>
                </div>

                {secureRes?.sanitizer.removed_spans.length ? (
                  <div className="bg-emerald-950/30 border border-emerald-800/40 p-3 rounded-lg text-xs space-y-1">
                    <div className="text-emerald-400 font-semibold flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Removed Malicious Spans
                    </div>
                    <div className="text-emerald-200/80 font-mono italic">
                      {secureRes.sanitizer.removed_spans.join(", ")}
                    </div>
                  </div>
                ) : null}

                <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-400 leading-relaxed">
                  {firewallRes.explanation}
                </div>
              </div>
            ) : (
              <div className="flex-1 flex items-center justify-center border border-dashed border-slate-800 rounded-lg p-6 text-center text-xs text-slate-500">
                Run Secure Grading to view live security firewall telemetry.
              </div>
            )}
          </div>
        </div>

        {/* Action Controls & Benchmark Comparison Results */}
        <div className="flex flex-wrap items-center justify-center gap-4 py-2">
          <button
            onClick={handleRunBaseline}
            disabled={loading}
            className="px-6 py-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 font-semibold text-sm rounded-xl transition"
          >
            Run Baseline Grader (Unprotected)
          </button>

          <button
            onClick={handleRunSecure}
            disabled={loading}
            className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-emerald-900/40 transition"
          >
            Run Secure Grader (GradingGuard Protected)
          </button>
        </div>

        {/* Score Comparison Cards */}
        {(baselineScore || secureRes) && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
            {/* Baseline Result Card */}
            <div className="bg-slate-900 border border-rose-900/40 rounded-xl p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold text-rose-400">Baseline Grader (Vulnerable)</span>
                {baselineScore && (
                  <span className="text-2xl font-black text-rose-400">Band {baselineScore.overall_band}</span>
                )}
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                {baselineScore?.feedback || "Click 'Run Baseline Grader' to simulate unprotected LLM response."}
              </p>
            </div>

            {/* Secure Result Card */}
            <div className="bg-slate-900 border border-emerald-800/40 rounded-xl p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold text-emerald-400">GradingGuard Secure Grader</span>
                {secureRes && (
                  <span className="text-2xl font-black text-emerald-400">
                    Band {secureRes.grading.overall_band}
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                {secureRes?.grading.feedback || "Click 'Run Secure Grader' to evaluate under Firewall protection."}
              </p>
              {secureRes?.verifier && (
                <div className="pt-2 text-xs text-emerald-300 font-medium">
                  Status: {secureRes.verifier.integrity_status.toUpperCase()} — {secureRes.verifier.recommendation}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
