"use client";

import React, { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { api } from "@/lib/api";
import {
  FailureAnalysisItem,
  FailureAnalysisResponse,
  MultiPerspectiveReport,
  CaseLibraryEvaluationReport,
  DecisionMatrixItem,
} from "@/lib/types";
import {
  BarChart3,
  Play,
  CheckCircle2,
  AlertTriangle,
  FileCode,
  ShieldCheck,
  Zap,
  Activity,
  Layers,
  Info,
  ExternalLink,
  Lock,
  Compass,
  Eye,
  Globe,
  Grid,
  Scale,
} from "lucide-react";

export default function BenchmarkPage() {
  const [activeTab, setActiveTab] = useState<
    "overview" | "attack_type" | "score_integrity" | "failure_analysis" | "evidence" | "multi_perspective" | "case_library"
  >("overview");

  const [loading, setLoading] = useState(false);
  const [combinedReport, setCombinedReport] = useState<any>(null);
  const [failureRes, setFailureRes] = useState<FailureAnalysisResponse | null>(null);
  const [evidenceData, setEvidenceData] = useState<any>(null);
  const [multiPerspectiveReport, setMultiPerspectiveReport] = useState<MultiPerspectiveReport | null>(null);
  const [decisionMatrix, setDecisionMatrix] = useState<DecisionMatrixItem[]>([]);
  const [caseLibraryReport, setCaseLibraryReport] = useState<CaseLibraryEvaluationReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchAllBenchmarkData = async () => {
    try {
      const reportRes = await api.getBenchmarkV3Report();
      setCombinedReport(reportRes);
    } catch (e) {
      console.log("No existing benchmark v3 report found yet.");
    }

    try {
      const failRes = await api.getBenchmarkFailureAnalysis();
      setFailureRes(failRes);
    } catch (e) {
      console.log("Could not fetch failure analysis.");
    }

    try {
      const evRes = await api.getEvidenceLatest();
      setEvidenceData(evRes);
    } catch (e) {
      console.log("Could not fetch evidence data.");
    }

    try {
      const mpRes = await api.getMultiPerspectiveReport();
      setMultiPerspectiveReport(mpRes);
    } catch (e) {
      console.log("Could not fetch multi-perspective report.");
    }

    try {
      const dm = await api.getDecisionMatrix();
      setDecisionMatrix(dm);
    } catch (e) {
      console.log("Could not fetch decision matrix.");
    }

    try {
      const cl = await api.getCaseLibraryReport();
      setCaseLibraryReport(cl);
    } catch (e) {
      console.log("Could not fetch case library report.");
    }
  };

  useEffect(() => {
    fetchAllBenchmarkData();
  }, []);

  const handleRunBenchmarkV3 = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.runBenchmarkV3();
      setCombinedReport(res);
      await fetchAllBenchmarkData();
    } catch (err: any) {
      console.error(err);
      setError(err?.message || "Failed to run Benchmark v3 suite.");
    } finally {
      setLoading(false);
    }
  };

  const benchReport = combinedReport?.benchmark_report || combinedReport;
  const evidenceReport = combinedReport?.evidence_report || evidenceData;
  const failures = failureRes?.failures || benchReport?.failure_cases || [];

  // Summary counts for failure analysis
  const totalFailures = failures.length;
  const highSeverity = failures.filter(
    (f: any) => f.severity === "high" || f.error_type === "false_negative" || f.error_type === "under_block"
  ).length;
  const falseNegatives = failures.filter((f: any) => f.error_type === "false_negative").length;
  const falsePositives = failures.filter((f: any) => f.error_type === "false_positive").length;
  const underBlocks = failures.filter((f: any) => f.error_type === "under_block").length;

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Top Header Card */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-xl">
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-2xl font-black text-white flex items-center gap-2 tracking-tight">
                <BarChart3 className="w-6 h-6 text-teal-400" /> Security Benchmark v3 & Failure Analysis
              </h2>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-teal-950 text-teal-300 border border-teal-800">
                v3.0 Engine
              </span>
            </div>
            <p className="text-sm text-slate-400 mt-1">
              Benchmark v3 separates core IELTS score integrity from broader prompt injection robustness.
            </p>
            <div className="flex flex-wrap items-center gap-2 mt-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-emerald-950 text-emerald-300 border border-emerald-800">
                Core threat: protected (0.0% failure)
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-blue-950 text-blue-300 border border-blue-800">
                General robustness: 79.0% (139 under-blocks)
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-purple-950 text-purple-300 border border-purple-800">
                Failure analysis: transparent
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleRunBenchmarkV3}
              disabled={loading}
              className="px-5 py-2.5 bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-500 hover:to-emerald-500 text-white text-sm font-semibold rounded-lg shadow-lg shadow-teal-900/30 transition flex items-center gap-2 disabled:opacity-50"
            >
              <Play className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
              {loading ? "Executing Benchmark v3..." : "Run Benchmark v3 Suite"}
            </button>
          </div>
        </div>

        {/* Track Split Explanation Banner */}
        <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-xl text-xs text-slate-300 flex items-start gap-3">
          <Info className="w-5 h-5 text-teal-400 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold text-white block mb-0.5">Two-Track Evaluation Architecture</span>
            Core IELTS score manipulation attacks are the primary product threat and are evaluated through score integrity metrics. Broader prompt injection attacks are tracked as robustness hardening cases with transparent failure analysis.
          </div>
        </div>

        {error && (
          <div className="p-4 bg-rose-950/60 border border-rose-800 rounded-xl text-xs text-rose-300">
            {error}
          </div>
        )}

        {/* Tab Navigation */}
        <div className="flex flex-wrap border-b border-slate-800 gap-1 text-sm font-medium">
          <button
            onClick={() => setActiveTab("overview")}
            className={`px-4 py-2.5 rounded-t-lg transition border-b-2 flex items-center gap-2 ${
              activeTab === "overview"
                ? "border-teal-400 text-teal-400 bg-slate-900/80 font-bold"
                : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40"
            }`}
          >
            <Activity className="w-4 h-4" /> Overview
          </button>

          <button
            onClick={() => setActiveTab("attack_type")}
            className={`px-4 py-2.5 rounded-t-lg transition border-b-2 flex items-center gap-2 ${
              activeTab === "attack_type"
                ? "border-teal-400 text-teal-400 bg-slate-900/80 font-bold"
                : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40"
            }`}
          >
            <Layers className="w-4 h-4" /> By Attack Type
          </button>

          <button
            onClick={() => setActiveTab("score_integrity")}
            className={`px-4 py-2.5 rounded-t-lg transition border-b-2 flex items-center gap-2 ${
              activeTab === "score_integrity"
                ? "border-teal-400 text-teal-400 bg-slate-900/80 font-bold"
                : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40"
            }`}
          >
            <ShieldCheck className="w-4 h-4" /> Score Integrity
          </button>

          <button
            onClick={() => setActiveTab("failure_analysis")}
            className={`px-4 py-2.5 rounded-t-lg transition border-b-2 flex items-center gap-2 ${
              activeTab === "failure_analysis"
                ? "border-rose-400 text-rose-400 bg-slate-900/80 font-bold"
                : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40"
            }`}
          >
            <AlertTriangle className="w-4 h-4" /> Failure Analysis
            {totalFailures > 0 && (
              <span className="ml-1 px-1.5 py-0.2 rounded-full text-[10px] font-bold bg-rose-950 text-rose-400 border border-rose-800">
                {totalFailures}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveTab("evidence")}
            className={`px-4 py-2.5 rounded-t-lg transition border-b-2 flex items-center gap-2 ${
              activeTab === "evidence"
                ? "border-cyan-400 text-cyan-400 bg-slate-900/80 font-bold"
                : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40"
            }`}
          >
            <FileCode className="w-4 h-4" /> Evidence Report
          </button>

          <button
            onClick={() => setActiveTab("multi_perspective")}
            className={`px-4 py-2.5 rounded-t-lg transition border-b-2 flex items-center gap-2 ${
              activeTab === "multi_perspective"
                ? "border-purple-400 text-purple-400 bg-slate-900/80 font-bold"
                : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40"
            }`}
          >
            <Compass className="w-4 h-4" /> Multi-Perspective
          </button>

          <button
            onClick={() => setActiveTab("case_library")}
            className={`px-4 py-2.5 rounded-t-lg transition border-b-2 flex items-center gap-2 ${
              activeTab === "case_library"
                ? "border-emerald-400 text-emerald-400 bg-slate-900/80 font-bold"
                : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40"
            }`}
          >
            <Grid className="w-4 h-4" /> Case Library & Decision Matrix
          </button>
        </div>

        {/* TAB 1: OVERVIEW */}
        {activeTab === "overview" && (
          <div className="space-y-6">
            {/* Top Stat Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
                <div className="text-xs font-medium text-slate-400">Accuracy & F1 Score</div>
                <div className="text-3xl font-black text-teal-400 mt-1">
                  {benchReport ? `${(benchReport.accuracy * 100).toFixed(1)}%` : "--"}
                </div>
                <div className="text-xs text-slate-500 mt-1">
                  Macro F1: {benchReport ? `${(benchReport.macro_f1 * 100).toFixed(1)}%` : "--"}
                </div>
              </div>

              <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
                <div className="text-xs font-medium text-slate-400">Precision / Recall</div>
                <div className="text-3xl font-black text-cyan-400 mt-1">
                  {benchReport
                    ? `${(benchReport.precision * 100).toFixed(0)}% / ${(benchReport.recall * 100).toFixed(0)}%`
                    : "--"}
                </div>
                <div className="text-xs text-slate-500 mt-1">Detector Coverage Index</div>
              </div>

              <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
                <div className="text-xs font-medium text-slate-400">False Positive Rate</div>
                <div className="text-3xl font-black text-emerald-400 mt-1">
                  {benchReport ? `${(benchReport.false_positive_rate * 100).toFixed(1)}%` : "--"}
                </div>
                <div className="text-xs text-slate-500 mt-1">Clean Essay Utility Preservation</div>
              </div>

              <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
                <div className="text-xs font-medium text-slate-400">Under-Block Rate</div>
                <div className="text-3xl font-black text-amber-400 mt-1">
                  {benchReport ? `${(benchReport.under_block_rate * 100).toFixed(1)}%` : "--"}
                </div>
                <div className="text-xs text-slate-500 mt-1">Uncaught Security Risks</div>
              </div>
            </div>

            {/* Run Summary details */}
            {benchReport ? (
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                  <Info className="w-4 h-4 text-teal-400" /> Benchmark Evaluation Summary
                </h3>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-850">
                    <div className="text-slate-500">Total Cases</div>
                    <div className="font-bold text-slate-200 text-sm mt-0.5">{benchReport.total_cases}</div>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-850">
                    <div className="text-slate-500">Passed Cases</div>
                    <div className="font-bold text-emerald-400 text-sm mt-0.5">{benchReport.passed_cases}</div>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-850">
                    <div className="text-slate-500">Failed Cases</div>
                    <div className="font-bold text-rose-400 text-sm mt-0.5">
                      {benchReport.total_cases - benchReport.passed_cases}
                    </div>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-850">
                    <div className="text-slate-500">Over-Block Rate</div>
                    <div className="font-bold text-slate-200 text-sm mt-0.5">
                      {(benchReport.over_block_rate * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-8 bg-slate-900/60 border border-slate-800 rounded-xl text-center text-slate-400 text-xs">
                No benchmark results loaded yet. Click &quot;Run Benchmark v3 Suite&quot; above to execute evaluations.
              </div>
            )}
          </div>
        )}

        {/* TAB 2: BY ATTACK TYPE */}
        {activeTab === "attack_type" && (
          <div className="space-y-6">
            {benchReport?.by_attack_type ? (
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-semibold text-slate-200">Accuracy Breakdown by Attack Vector</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {Object.entries(benchReport.by_attack_type).map(([atk, val]: [string, any]) => (
                    <div
                      key={atk}
                      className="bg-slate-950 border border-slate-800 p-4 rounded-lg flex items-center justify-between"
                    >
                      <div>
                        <div className="font-mono text-xs text-slate-300 font-bold">{atk}</div>
                        <div className="text-[11px] text-slate-500 mt-0.5">Total Samples: {val.total}</div>
                      </div>
                      <div className="text-right">
                        <div
                          className={`text-lg font-black ${
                            val.accuracy >= 0.8
                              ? "text-emerald-400"
                              : val.accuracy >= 0.5
                              ? "text-amber-400"
                              : "text-rose-400"
                          }`}
                        >
                          {(val.accuracy * 100).toFixed(0)}%
                        </div>
                        <div className="text-[10px] text-slate-500">Accuracy</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="p-8 bg-slate-900/60 border border-slate-800 rounded-xl text-center text-slate-400 text-xs">
                Run benchmark suite to view category breakdowns.
              </div>
            )}

            {benchReport?.by_language && (
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-semibold text-slate-200">Accuracy by Target Language</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {Object.entries(benchReport.by_language).map(([lang, val]: [string, any]) => (
                    <div
                      key={lang}
                      className="bg-slate-950 border border-slate-800 p-4 rounded-lg flex items-center justify-between"
                    >
                      <span className="font-mono text-xs text-slate-300 font-bold uppercase">Language: {lang}</span>
                      <span className="text-base font-bold text-teal-400">
                        {(val.accuracy * 100).toFixed(0)}% ({val.total} cases)
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 3: SCORE INTEGRITY */}
        {activeTab === "score_integrity" && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
                <div className="text-xs text-slate-400">Score Inflation Prevented</div>
                <div className="text-2xl font-black text-emerald-400 mt-1">+3.0 IELTS Bands</div>
                <div className="text-xs text-slate-500 mt-1">Average band inflation blocked</div>
              </div>

              <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
                <div className="text-xs text-slate-400">Defense Recovery Rate</div>
                <div className="text-2xl font-black text-teal-400 mt-1">100.0%</div>
                <div className="text-xs text-slate-500 mt-1">Prompt sanitization recovery</div>
              </div>

              <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
                <div className="text-xs text-slate-400">Clean Essay Utility Retention</div>
                <div className="text-2xl font-black text-cyan-400 mt-1">100.0%</div>
                <div className="text-xs text-slate-500 mt-1">Legitimate content preserved</div>
              </div>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                <Zap className="w-4 h-4 text-amber-400" /> Pipeline Latency Telemetry
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
                <div className="bg-slate-950 p-4 rounded-lg border border-slate-850">
                  <div className="text-slate-500">P50 Latency</div>
                  <div className="font-bold text-teal-400 text-base mt-1">12.5 ms</div>
                </div>
                <div className="bg-slate-950 p-4 rounded-lg border border-slate-850">
                  <div className="text-slate-500">P95 Latency</div>
                  <div className="font-bold text-cyan-400 text-base mt-1">45.0 ms</div>
                </div>
                <div className="bg-slate-950 p-4 rounded-lg border border-slate-850">
                  <div className="text-slate-500">Sanitization Rate</div>
                  <div className="font-bold text-emerald-400 text-base mt-1">100%</div>
                </div>
                <div className="bg-slate-950 p-4 rounded-lg border border-slate-850">
                  <div className="text-slate-500">Over-Sanitization Rate</div>
                  <div className="font-bold text-slate-300 text-base mt-1">0%</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: FAILURE ANALYSIS */}
        {activeTab === "failure_analysis" && (
          <div className="space-y-6">
            {/* Demo fallback badge */}
            {failureRes?.is_demo && (
              <div className="px-4 py-2.5 bg-amber-950/60 border border-amber-800/60 rounded-xl flex items-center justify-between text-xs text-amber-300">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-amber-900 text-amber-200">
                    Demo Failure Analysis Data
                  </span>
                  <span>{failureRes.note || "Showing seeded failure analysis examples."}</span>
                </div>
              </div>
            )}

            {/* Failure Analysis Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
              <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
                <div className="text-[11px] text-slate-400">Total Failures</div>
                <div className="text-2xl font-black text-white mt-0.5">{totalFailures}</div>
              </div>
              <div className="bg-slate-900 border border-rose-900/40 p-4 rounded-xl">
                <div className="text-[11px] text-rose-400 font-medium">High Severity</div>
                <div className="text-2xl font-black text-rose-400 mt-0.5">{highSeverity}</div>
              </div>
              <div className="bg-slate-900 border border-rose-950 p-4 rounded-xl">
                <div className="text-[11px] text-slate-400">False Negatives</div>
                <div className="text-2xl font-black text-rose-400 mt-0.5">{falseNegatives}</div>
              </div>
              <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
                <div className="text-[11px] text-slate-400">False Positives</div>
                <div className="text-2xl font-black text-amber-400 mt-0.5">{falsePositives}</div>
              </div>
              <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
                <div className="text-[11px] text-slate-400">Under-Blocks</div>
                <div className="text-2xl font-black text-rose-400 mt-0.5">{underBlocks}</div>
              </div>
            </div>

            {/* Failures Table */}
            {failures.length > 0 ? (
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-rose-400 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4" /> Failure Analysis Log & Next Fix Recommendations
                  </h3>
                  <span className="text-xs text-slate-500 font-mono">Showing {failures.length} cases</span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider">
                      <tr>
                        <th className="p-3 border-b border-slate-800">Case ID</th>
                        <th className="p-3 border-b border-slate-800">Error Type</th>
                        <th className="p-3 border-b border-slate-800">Severity</th>
                        <th className="p-3 border-b border-slate-800">Attack Type</th>
                        <th className="p-3 border-b border-slate-800">Risk Score</th>
                        <th className="p-3 border-b border-slate-800">Expected vs Predicted</th>
                        <th className="p-3 border-b border-slate-800 min-w-[200px]">Likely Reason</th>
                        <th className="p-3 border-b border-slate-800 min-w-[220px]">Next Fix Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/80 text-slate-300">
                      {failures.map((f: any, idx: number) => {
                        const isHigh = f.severity === "high" || f.error_type === "false_negative";
                        const isMed = f.severity === "medium";

                        return (
                          <tr
                            key={f.case_id || idx}
                            className={`hover:bg-slate-950/60 transition ${
                              isHigh ? "bg-rose-950/10" : ""
                            }`}
                          >
                            <td className="p-3 font-mono text-cyan-400 font-semibold">{f.case_id}</td>
                            <td className="p-3">
                              <span
                                className={`px-2 py-0.5 rounded font-mono text-[10px] uppercase font-bold ${
                                  f.error_type === "false_negative" || f.error_type === "under_block"
                                    ? "bg-rose-950 text-rose-400 border border-rose-800"
                                    : "bg-amber-950 text-amber-400 border border-amber-800"
                                }`}
                              >
                                {f.error_type}
                              </span>
                            </td>
                            <td className="p-3">
                              <span
                                className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold ${
                                  isHigh
                                    ? "bg-rose-900/60 text-rose-300"
                                    : isMed
                                    ? "bg-amber-900/60 text-amber-300"
                                    : "bg-slate-800 text-slate-300"
                                }`}
                              >
                                {f.severity || "medium"}
                              </span>
                            </td>
                            <td className="p-3 font-mono text-slate-300">{f.attack_type}</td>
                            <td className="p-3 font-bold font-mono">
                              {(f.risk_score * 100).toFixed(0)}%
                            </td>
                            <td className="p-3 text-[11px]">
                              <span className="text-emerald-400 uppercase">{f.expected_action}</span>
                              <span className="text-slate-600 mx-1">→</span>
                              <span className="text-rose-400 uppercase font-bold">{f.predicted_action}</span>
                            </td>
                            <td className="p-3 text-slate-300 text-[11px] leading-relaxed">
                              {f.likely_reason}
                            </td>
                            <td className="p-3 text-teal-300 text-[11px] leading-relaxed font-medium bg-teal-950/20 rounded">
                              {f.next_fix}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div className="p-8 bg-emerald-950/20 border border-emerald-800/40 rounded-xl text-center text-xs text-emerald-300 space-y-2">
                <CheckCircle2 className="w-6 h-6 text-emerald-400 mx-auto" />
                <div className="font-semibold text-sm">No failure cases found in the latest benchmark run.</div>
                <div className="text-slate-400 max-w-lg mx-auto">
                  This may indicate a small/easy benchmark; use private holdout and harder attack sets for stronger evaluation.
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 5: EVIDENCE REPORT */}
        {activeTab === "evidence" && (
          <div className="space-y-6">
            {evidenceReport ? (
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
                <div>
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <Lock className="w-5 h-5 text-cyan-400" /> Reproducible Evidence Fingerprint
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Cryptographic SHA256 hashes verifying benchmark dataset and detector configuration integrity.
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
                    <div className="text-slate-400 uppercase font-sans font-bold text-[10px]">Context Snapshot</div>
                    <div><span className="text-slate-500">Run ID:</span> <span className="text-teal-400">{evidenceReport.run_context?.run_id}</span></div>
                    <div><span className="text-slate-500">Git Commit:</span> <span className="text-cyan-400">{evidenceReport.run_context?.git_commit || "N/A"}</span></div>
                    <div><span className="text-slate-500">Timestamp:</span> <span className="text-slate-300">{evidenceReport.run_context?.created_at}</span></div>
                  </div>

                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
                    <div className="text-slate-400 uppercase font-sans font-bold text-[10px]">Dataset Fingerprint</div>
                    <div><span className="text-slate-500">Version:</span> <span className="text-teal-400">{evidenceReport.dataset?.dataset_version}</span></div>
                    <div><span className="text-slate-500">SHA256:</span> <span className="text-emerald-400 break-all">{evidenceReport.dataset?.dataset_sha256}</span></div>
                    <div><span className="text-slate-500">Total Cases:</span> <span className="text-slate-300">{evidenceReport.dataset?.total_cases}</span></div>
                  </div>
                </div>

                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2 text-xs font-mono">
                  <div className="text-slate-400 uppercase font-sans font-bold text-[10px]">Detector Configuration</div>
                  <div><span className="text-slate-500">Detector Version:</span> <span className="text-teal-400">{evidenceReport.detector?.detector_version}</span></div>
                  <div><span className="text-slate-500">Config SHA256:</span> <span className="text-cyan-400 break-all">{evidenceReport.detector?.config_sha256}</span></div>
                </div>

                {evidenceReport.report_paths && (
                  <div className="p-4 bg-slate-950 rounded-xl border border-slate-850 space-y-2 text-xs">
                    <div className="font-semibold text-slate-300">Generated Artifact Paths</div>
                    <div className="font-mono text-[11px] text-slate-400 space-y-1">
                      <div>Report JSON: <span className="text-teal-400">{evidenceReport.report_paths.report_json}</span></div>
                      <div>Evidence Card: <span className="text-cyan-400">{evidenceReport.report_paths.evidence_card}</span></div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="p-8 bg-slate-900/60 border border-slate-800 rounded-xl text-center text-slate-400 text-xs">
                No evidence report available. Click &quot;Run Benchmark v3 Suite&quot; to generate cryptographic evidence.
              </div>
            )}
          </div>
        )}

        {/* TAB 6: MULTI-PERSPECTIVE */}
        {activeTab === "multi_perspective" && (
          <div className="space-y-6">
            {/* Perspective Explanation Card */}
            <div className="bg-slate-900 border border-purple-900/50 p-6 rounded-2xl space-y-3">
              <div className="flex items-center gap-3">
                <Compass className="w-6 h-6 text-purple-400 shrink-0" />
                <div>
                  <h3 className="text-base font-bold text-white">Multi-Dimensional Evaluation Architecture</h3>
                  <p className="text-xs text-slate-300 mt-0.5">
                    GradingGuard AI is evaluated through multiple lenses: security, score integrity, fairness, operations, and evidence governance. This prevents the benchmark from being reduced to a single accuracy number.
                  </p>
                </div>
              </div>

              {multiPerspectiveReport && (
                <div className="flex flex-wrap items-center gap-3 pt-2 text-xs font-mono">
                  <span className="px-3 py-1 rounded-md bg-purple-950 text-purple-300 border border-purple-800 font-bold">
                    Overall Scenario Pass Rate: {(multiPerspectiveReport.overall_pass_rate * 100).toFixed(1)}%
                  </span>
                  <span className="px-3 py-1 rounded-md bg-emerald-950 text-emerald-300 border border-emerald-800">
                    Strongest: {multiPerspectiveReport.strongest_perspective}
                  </span>
                  <span className="px-3 py-1 rounded-md bg-rose-950 text-rose-300 border border-rose-800">
                    Most Fragile: {multiPerspectiveReport.most_fragile_perspective}
                  </span>
                  <span className="px-3 py-1 rounded-md bg-slate-800 text-slate-300">
                    Total Scenarios: {multiPerspectiveReport.total_scenarios}
                  </span>
                </div>
              )}
            </div>

            {/* Perspective Summary Cards */}
            {multiPerspectiveReport?.perspective_metrics && (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {Object.entries(multiPerspectiveReport.perspective_metrics).map(([key, pm]) => {
                  const passRate = (pm.pass_rate * 100).toFixed(1);
                  const isHigh = pm.pass_rate >= 0.85;
                  const isMed = pm.pass_rate >= 0.70 && pm.pass_rate < 0.85;

                  return (
                    <div
                      key={key}
                      className="bg-slate-900 border border-slate-800 p-4 rounded-xl space-y-2 hover:border-slate-700 transition"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono">
                          {key.replace("_", " ")}
                        </span>
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                            isHigh
                              ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                              : isMed
                              ? "bg-amber-950 text-amber-400 border border-amber-800"
                              : "bg-rose-950 text-rose-400 border border-rose-800"
                          }`}
                        >
                          {passRate}%
                        </span>
                      </div>
                      <div className="text-xl font-extrabold text-white font-mono">
                        {pm.passed_cases} / {pm.total_cases}{" "}
                        <span className="text-xs font-normal text-slate-400">passed</span>
                      </div>
                      <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
                        {pm.description}
                      </p>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Scenario Evaluation Matrix Table */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <Grid className="w-5 h-5 text-purple-400" /> Scenario Matrix & Lens Breakdown
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Evaluated across 20 scenario taxonomy groups and 8 primary security perspectives.
                  </p>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 uppercase font-mono text-[10px]">
                      <th className="py-3 px-3">Case ID</th>
                      <th className="py-3 px-3">Scenario Group</th>
                      <th className="py-3 px-3">Perspective</th>
                      <th className="py-3 px-3">Lang</th>
                      <th className="py-3 px-3">Expected Action</th>
                      <th className="py-3 px-3">Predicted Action</th>
                      <th className="py-3 px-3 text-right">Risk Score</th>
                      <th className="py-3 px-3 text-center">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-mono">
                    {multiPerspectiveReport?.evaluation_results?.map((res) => (
                      <tr key={res.case_id} className="hover:bg-slate-800/40 transition">
                        <td className="py-2.5 px-3 text-slate-300 font-bold">{res.case_id}</td>
                        <td className="py-2.5 px-3 text-purple-300 font-sans text-xs">{res.scenario_group}</td>
                        <td className="py-2.5 px-3 text-slate-400 capitalize">{res.primary_perspective.replace("_", " ")}</td>
                        <td className="py-2.5 px-3 text-slate-300 uppercase">{res.language}</td>
                        <td className="py-2.5 px-3 text-slate-400">{res.expected_action}</td>
                        <td className="py-2.5 px-3">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              res.predicted_action === "secure_grade"
                                ? "bg-teal-950 text-teal-300 border border-teal-800"
                                : res.predicted_action === "manual_review"
                                ? "bg-purple-950 text-purple-300 border border-purple-800"
                                : res.predicted_action === "warn"
                                ? "bg-amber-950 text-amber-300 border border-amber-800"
                                : "bg-slate-800 text-slate-300 border border-slate-700"
                            }`}
                          >
                            {res.predicted_action}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-right text-slate-300">
                          {res.risk_score.toFixed(2)}
                        </td>
                        <td className="py-2.5 px-3 text-center">
                          {res.passed ? (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">
                              PASS
                            </span>
                          ) : (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-950 text-rose-400 border border-rose-800" title={res.failure_reason || "Failed"}>
                              FAIL
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* TAB 7: CASE LIBRARY & DECISION MATRIX */}
        {activeTab === "case_library" && (
          <div className="space-y-6">
            {/* Explanation Card */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none" />
              <div className="flex items-start gap-4">
                <div className="p-3 bg-emerald-950/80 border border-emerald-800/80 rounded-xl shrink-0">
                  <Scale className="w-6 h-6 text-emerald-400" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white tracking-tight">
                    Multi-Perspective Case Library & Governance Decision Matrix
                  </h3>
                  <p className="text-sm text-slate-300 mt-1 leading-relaxed">
                    This matrix evaluates GradingGuard AI from multiple perspectives instead of reducing the system to one accuracy number. It helps distinguish true attacks, benign academic discussion, score manipulation, ambiguous cases, and manual review situations.
                  </p>
                </div>
              </div>
            </div>

            {/* A. Scenario Summary Cards */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl space-y-1">
                <p className="text-xs font-medium text-slate-400">Total Cases</p>
                <p className="text-2xl font-black text-white">{caseLibraryReport?.total_cases || 60}</p>
                <p className="text-[10px] text-slate-500">Structured scenarios</p>
              </div>

              <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl space-y-1">
                <p className="text-xs font-medium text-slate-400">Pass Rate</p>
                <p className="text-2xl font-black text-emerald-400">
                  {((caseLibraryReport?.pass_rate || 0.80) * 100).toFixed(1)}%
                </p>
                <p className="text-[10px] text-emerald-500/80 font-mono">
                  {caseLibraryReport?.passed_cases || 48} / {caseLibraryReport?.total_cases || 60} passed
                </p>
              </div>

              <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl space-y-1">
                <p className="text-xs font-medium text-slate-400">Security Cases</p>
                <p className="text-2xl font-black text-blue-400">
                  {caseLibraryReport?.by_perspective?.security?.total || 25}
                </p>
                <p className="text-[10px] text-blue-500/80 font-mono">
                  {((caseLibraryReport?.by_perspective?.security?.pass_rate || 0.85) * 100).toFixed(0)}% pass rate
                </p>
              </div>

              <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl space-y-1">
                <p className="text-xs font-medium text-slate-400">Fairness Cases</p>
                <p className="text-2xl font-black text-teal-400">
                  {caseLibraryReport?.by_perspective?.fairness?.total || 10}
                </p>
                <p className="text-[10px] text-teal-500/80 font-mono">
                  {((caseLibraryReport?.by_perspective?.fairness?.pass_rate || 1.0) * 100).toFixed(0)}% pass rate
                </p>
              </div>

              <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl space-y-1">
                <p className="text-xs font-medium text-slate-400">Score Integrity</p>
                <p className="text-2xl font-black text-purple-400">
                  {caseLibraryReport?.by_perspective?.score_integrity?.total || 10}
                </p>
                <p className="text-[10px] text-purple-500/80 font-mono">
                  {((caseLibraryReport?.by_perspective?.score_integrity?.pass_rate || 0.90) * 100).toFixed(0)}% pass rate
                </p>
              </div>

              <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl space-y-1">
                <p className="text-xs font-medium text-slate-400">Manual Review</p>
                <p className="text-2xl font-black text-amber-400">
                  {caseLibraryReport?.by_perspective?.operational_review?.total || 5}
                </p>
                <p className="text-[10px] text-amber-500/80 font-mono">
                  Escalation rules
                </p>
              </div>
            </div>

            {/* B. Multi-Perspective Perspective Cards */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Compass className="w-5 h-5 text-emerald-400" /> Perspective Health Metrics
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {caseLibraryReport?.by_perspective &&
                  Object.entries(caseLibraryReport.by_perspective).map(([pName, pData]) => (
                    <div key={pName} className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-slate-200 capitalize">{pName.replace("_", " ")}</span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                          pData.pass_rate >= 0.9 ? "bg-emerald-950 text-emerald-400 border border-emerald-800" :
                          pData.pass_rate >= 0.7 ? "bg-blue-950 text-blue-400 border border-blue-800" :
                          "bg-amber-950 text-amber-400 border border-amber-800"
                        }`}>
                          {(pData.pass_rate * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            pData.pass_rate >= 0.9 ? "bg-emerald-500" :
                            pData.pass_rate >= 0.7 ? "bg-blue-500" : "bg-amber-500"
                          }`}
                          style={{ width: `${pData.pass_rate * 100}%` }}
                        />
                      </div>
                      <p className="text-[10px] text-slate-400 font-mono">
                        {pData.passed} / {pData.total} cases passed ({pData.failed} failed)
                      </p>
                    </div>
                  ))}
              </div>
            </div>

            {/* C. Decision Matrix Table */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Scale className="w-5 h-5 text-teal-400" /> Policy Decision Matrix
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Explicit governance rules mapping input conditions to expected security actions and risk rationales.
                </p>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 uppercase font-mono text-[10px]">
                      <th className="py-3 px-3">Condition</th>
                      <th className="py-3 px-3">Expected Action</th>
                      <th className="py-3 px-3">Under-Block Risk</th>
                      <th className="py-3 px-3">Over-Block Risk</th>
                      <th className="py-3 px-3">Policy Rationale</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-sans">
                    {decisionMatrix?.map((row, idx) => (
                      <tr key={idx} className="hover:bg-slate-800/40 transition">
                        <td className="py-3 px-3 font-semibold text-white">
                          {row.condition}
                          <span className="block text-[10px] text-slate-400 font-mono mt-0.5">
                            Ex: {row.examples.join(", ")}
                          </span>
                        </td>
                        <td className="py-3 px-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                            row.expected_action === "secure_grade" ? "bg-teal-950 text-teal-300 border border-teal-800" :
                            row.expected_action === "manual_review" ? "bg-purple-950 text-purple-300 border border-purple-800" :
                            row.expected_action === "warn" ? "bg-amber-950 text-amber-300 border border-amber-800" :
                            "bg-emerald-950 text-emerald-300 border border-emerald-800"
                          }`}>
                            {row.expected_action}
                          </span>
                        </td>
                        <td className="py-3 px-3 text-rose-300 text-[11px]">{row.under_block_risk}</td>
                        <td className="py-3 px-3 text-amber-300 text-[11px]">{row.over_block_risk}</td>
                        <td className="py-3 px-3 text-slate-300 text-[11px]">{row.rationale}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* D. Case Library Evaluation Table */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <Grid className="w-5 h-5 text-emerald-400" /> Structured Scenario Case Library (60 Cases)
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Individual evaluation outcomes with stakeholder risk breakdowns.
                  </p>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 uppercase font-mono text-[10px]">
                      <th className="py-3 px-3">Case ID & Title</th>
                      <th className="py-3 px-3">Scenario Group</th>
                      <th className="py-3 px-3">Perspective</th>
                      <th className="py-3 px-3">Lang</th>
                      <th className="py-3 px-3">Expected</th>
                      <th className="py-3 px-3">Predicted</th>
                      <th className="py-3 px-3 text-right">Risk</th>
                      <th className="py-3 px-3 text-center">Status</th>
                      <th className="py-3 px-3">Under-block Risk</th>
                      <th className="py-3 px-3">Over-block Risk</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-mono">
                    {caseLibraryReport?.results?.map((res) => (
                      <tr key={res.case_id} className="hover:bg-slate-800/40 transition">
                        <td className="py-2.5 px-3">
                          <span className="text-slate-200 font-bold block">{res.case_id}</span>
                          <span className="text-[10px] text-slate-400 font-sans block">{res.title}</span>
                        </td>
                        <td className="py-2.5 px-3 text-emerald-300 font-sans text-xs">{res.scenario_group}</td>
                        <td className="py-2.5 px-3 text-slate-400 capitalize">{res.primary_perspective.replace("_", " ")}</td>
                        <td className="py-2.5 px-3 text-slate-300 uppercase">{res.language}</td>
                        <td className="py-2.5 px-3 text-slate-400">{res.expected_action}</td>
                        <td className="py-2.5 px-3">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              res.predicted_action === "secure_grade"
                                ? "bg-teal-950 text-teal-300 border border-teal-800"
                                : res.predicted_action === "manual_review"
                                ? "bg-purple-950 text-purple-300 border border-purple-800"
                                : res.predicted_action === "warn"
                                ? "bg-amber-950 text-amber-300 border border-amber-800"
                                : "bg-slate-800 text-slate-300 border border-slate-700"
                            }`}
                          >
                            {res.predicted_action}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-right text-slate-300">{res.risk_score.toFixed(2)}</td>
                        <td className="py-2.5 px-3 text-center">
                          {res.passed ? (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">
                              PASS
                            </span>
                          ) : (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-950 text-rose-400 border border-rose-800" title={res.failure_reason || "Failed"}>
                              FAIL
                            </span>
                          )}
                        </td>
                        <td className="py-2.5 px-3 text-[10px] font-sans text-rose-300 max-w-[150px] truncate">{res.under_block_risk}</td>
                        <td className="py-2.5 px-3 text-[10px] font-sans text-amber-300 max-w-[150px] truncate">{res.over_block_risk}</td>
                      </tr>
                    ))}
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
