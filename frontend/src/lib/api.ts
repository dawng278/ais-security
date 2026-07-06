import {
  ArenaRunRequest,
  ArenaRunResponse,
  AttackerProfile,
  BenchmarkReportV2,
  BenchmarkSummary,
  CompareResponse,
  DashboardStats,
  DatasetLineageReport,
  FailureAnalysisResponse,
  FirewallResult,
  GradingResult,
  MultiPerspectiveReport,
  DecisionMatrixItem,
  CaseLibraryEvaluationReport,
  RedteamResult,
  SecureGradeResponse,
  SecurityEvent,
} from "./types";


const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
    ...options,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }

  return res.json();
}

export const api = {
  generateAttack: (body: { text: string; task_type: string; attack_type: string }) =>
    request<RedteamResult>("/api/redteam/generate", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  analyzeFirewall: (body: { text: string; task_type: string }) =>
    request<FirewallResult>("/api/firewall/analyze", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  baselineGrade: (body: { text: string; task_type: string }) =>
    request<GradingResult>("/api/grade/baseline", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  secureGrade: (body: { text: string; task_type: string }) =>
    request<SecureGradeResponse>("/api/grade/secure", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  compare: (body: { original_text: string; injected_text: string; task_type: string }) =>
    request<CompareResponse>("/api/grade/compare", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  dashboardStats: () => request<DashboardStats>("/api/dashboard/stats"),

  dashboardEvents: () => request<SecurityEvent[]>("/api/dashboard/events"),

  runBenchmark: () => request<BenchmarkSummary>("/api/benchmark/run", { method: "POST" }),

  runBenchmarkV2: () => request<BenchmarkReportV2>("/api/benchmark/run_v2", { method: "POST" }),

  runBenchmarkV3: () => request<any>("/api/benchmark/v3/run", { method: "POST" }),

  getBenchmarkV3Report: () => request<any>("/api/benchmark/v3/report"),

  getBenchmarkFailureAnalysis: () => request<FailureAnalysisResponse>("/api/benchmark/v3/failure-analysis"),

  getEvidenceLatest: () => request<any>("/api/evidence/latest"),

  getLineageReport: () => request<DatasetLineageReport>("/api/lineage/report"),

  getArenaProfiles: () => request<AttackerProfile[]>("/api/arena/profiles"),


  runArenaScenario: (body: ArenaRunRequest) =>
    request<ArenaRunResponse>("/api/arena/run", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  getMultiPerspectiveReport: () => request<MultiPerspectiveReport>("/api/benchmark/multi-perspective/report"),

  runMultiPerspective: () => request<MultiPerspectiveReport>("/api/benchmark/multi-perspective/run", { method: "POST" }),

  getDecisionMatrix: () => request<DecisionMatrixItem[]>("/api/benchmark/decision-matrix"),

  getCaseLibraryReport: () => request<CaseLibraryEvaluationReport>("/api/benchmark/case-library"),

  runCaseLibrary: () => request<CaseLibraryEvaluationReport>("/api/benchmark/case-library/run", { method: "POST" }),
};
