import { AppShell } from "@/components/AppShell";
import {
  AlertTriangle,
  CheckCircle2,
  Clock3,
  Database,
  FileCode2,
  Fingerprint,
  Gauge,
  GitCommit,
  ShieldCheck,
} from "lucide-react";

export const dynamic = "force-dynamic";

type MetricMap = Record<string, number>;

interface EvidenceReport {
  run_context?: {
    run_id?: string;
    created_at?: string;
    git_commit?: string | null;
    random_seed?: number;
    environment?: string;
  };
  dataset?: {
    dataset_path?: string;
    dataset_version?: string;
    dataset_sha256?: string;
    total_cases?: number;
    label_distribution?: Record<string, number>;
    split_distribution?: Record<string, number>;
    attack_type_distribution?: Record<string, number>;
    language_distribution?: Record<string, number>;
  };
  detector?: {
    detector_version?: string;
    threshold_version?: string;
    enable_embedding_detector?: boolean;
    enable_classifier_detector?: boolean;
    embedding_configured_state?: string;
    embedding_dependency_state?: string;
    embedding_model_load_state?: string;
    embedding_runtime_state?: string;
    embedding_model_name?: string | null;
    embedding_fallback_reason?: string | null;
    config_sha256?: string | null;
  };
  metrics?: {
    overall_metrics?: MetricMap;
    score_integrity_metrics?: MetricMap;
    sanitizer_metrics?: MetricMap;
    latency_metrics?: MetricMap;
  };
  failure_case_count?: number;
  report_paths?: Record<string, string>;
  notes?: string[];
}

interface EvidenceLoadResult {
  report: EvidenceReport | null;
  error: string | null;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function loadEvidence(): Promise<EvidenceLoadResult> {
  try {
    const response = await fetch(`${API_BASE}/api/evidence/latest`, {
      cache: "no-store",
      next: { revalidate: 0 },
    });

    if (!response.ok) {
      return { report: null, error: `Backend returned ${response.status}` };
    }

    const report = (await response.json()) as EvidenceReport;
    return { report, error: null };
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown evidence fetch error";
    return { report: null, error: message };
  }
}

function formatPercent(value: number | undefined): string {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return "Unavailable";
  }
  return `${(value * 100).toFixed(1)}%`;
}

function formatNumber(value: number | undefined): string {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return "Unavailable";
  }
  return value.toLocaleString();
}

function metricValue(metrics: MetricMap | undefined, key: string): number | undefined {
  return typeof metrics?.[key] === "number" ? metrics[key] : undefined;
}

function shortHash(value: string | null | undefined): string {
  if (!value) {
    return "Unavailable";
  }
  return value.length > 18 ? `${value.slice(0, 10)}...${value.slice(-8)}` : value;
}

function StateBadge({ tone, children }: { tone: "measured" | "degraded" | "stale"; children: React.ReactNode }) {
  const toneClass = {
    measured: "border-emerald-800 bg-emerald-950 text-emerald-300",
    degraded: "border-amber-800 bg-amber-950 text-amber-300",
    stale: "border-slate-700 bg-slate-900 text-slate-300",
  }[tone];

  return (
    <span className={`inline-flex items-center rounded-md border px-2 py-1 text-xs font-semibold ${toneClass}`}>
      {children}
    </span>
  );
}

function MetricCard({ label, value, note }: { label: string; value: string; note: string }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
      <div className="text-xs font-medium text-slate-400">{label}</div>
      <div className="mt-2 text-2xl font-black text-white">{value}</div>
      <div className="mt-1 text-xs text-slate-500">{note}</div>
    </div>
  );
}

function DistributionTable({ title, rows }: { title: string; rows: Record<string, number> | undefined }) {
  const entries = Object.entries(rows || {});

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
      <h3 className="text-sm font-bold text-slate-200">{title}</h3>
      {entries.length === 0 ? (
        <p className="mt-3 text-sm text-slate-500">Unavailable</p>
      ) : (
        <div className="mt-3 overflow-x-auto">
          <table className="w-full text-left text-xs">
            <tbody className="divide-y divide-slate-800">
              {entries.map(([key, value]) => (
                <tr key={key}>
                  <td className="py-2 pr-3 font-mono text-slate-300">{key}</td>
                  <td className="py-2 text-right font-mono font-bold text-cyan-300">{value.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default async function EvidencePage() {
  const { report, error } = await loadEvidence();
  const overall = report?.metrics?.overall_metrics;
  const score = report?.metrics?.score_integrity_metrics;
  const detector = report?.detector;
  const embeddingState = detector?.embedding_runtime_state || (detector?.enable_embedding_detector ? "unknown" : "unavailable");
  const isEmbeddingHealthy = embeddingState === "healthy";

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex flex-col gap-4 rounded-lg border border-slate-800 bg-slate-900 p-6 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <h2 className="flex items-center gap-2 text-2xl font-black tracking-tight text-white">
                <FileCode2 className="h-6 w-6 text-cyan-400" />
                Benchmark Evidence
              </h2>
              <StateBadge tone={report ? "measured" : "degraded"}>{report ? "Measured artifact" : "Unavailable"}</StateBadge>
              <StateBadge tone={isEmbeddingHealthy ? "measured" : "degraded"}>
                Embedding {embeddingState}
              </StateBadge>
            </div>
            <p className="mt-2 max-w-3xl text-sm text-slate-400">
              Cryptographic run metadata, dataset fingerprints, detector state, and benchmark metrics loaded from the backend evidence artifact.
            </p>
          </div>

          <div className="rounded-lg border border-slate-800 bg-slate-950 px-4 py-3 text-xs text-slate-400">
            <div className="font-mono text-slate-300">{report?.run_context?.run_id || "No run loaded"}</div>
            <div className="mt-1 flex items-center gap-1">
              <Clock3 className="h-3.5 w-3.5" />
              {report?.run_context?.created_at || "Evidence backend unavailable"}
            </div>
          </div>
        </div>

        {error && (
          <div className="flex items-start gap-3 rounded-lg border border-amber-800 bg-amber-950/60 p-4 text-sm text-amber-200">
            <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />
            <div>
              <div className="font-bold">Evidence backend unavailable</div>
              <div className="mt-1 text-amber-200/80">{error}</div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
          <MetricCard label="Accuracy" value={formatPercent(metricValue(overall, "accuracy"))} note="Measured benchmark artifact" />
          <MetricCard label="Recall" value={formatPercent(metricValue(overall, "recall"))} note="Attack detection sensitivity" />
          <MetricCard label="Macro F1" value={formatPercent(metricValue(overall, "macro_f1"))} note="Balanced class metric" />
          <MetricCard label="Under-block Rate" value={formatPercent(metricValue(overall, "under_block_rate"))} note="Known residual risk" />
        </div>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <div className="rounded-lg border border-slate-800 bg-slate-900 p-5 lg:col-span-2">
            <h3 className="flex items-center gap-2 text-sm font-bold uppercase tracking-wide text-slate-300">
              <Fingerprint className="h-4 w-4 text-cyan-400" />
              Reproducibility Fingerprints
            </h3>
            <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
              <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
                <div className="text-xs text-slate-500">Dataset SHA256</div>
                <div className="mt-2 font-mono text-sm font-bold text-cyan-300">{shortHash(report?.dataset?.dataset_sha256)}</div>
              </div>
              <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
                <div className="text-xs text-slate-500">Config SHA256</div>
                <div className="mt-2 font-mono text-sm font-bold text-cyan-300">{shortHash(detector?.config_sha256)}</div>
              </div>
              <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
                <div className="text-xs text-slate-500">Git Commit</div>
                <div className="mt-2 flex items-center gap-2 font-mono text-sm font-bold text-slate-200">
                  <GitCommit className="h-4 w-4 text-slate-500" />
                  {report?.run_context?.git_commit || "Unavailable"}
                </div>
              </div>
              <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
                <div className="text-xs text-slate-500">Dataset Cases</div>
                <div className="mt-2 flex items-center gap-2 text-sm font-bold text-slate-200">
                  <Database className="h-4 w-4 text-slate-500" />
                  {formatNumber(report?.dataset?.total_cases)}
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-lg border border-slate-800 bg-slate-900 p-5">
            <h3 className="flex items-center gap-2 text-sm font-bold uppercase tracking-wide text-slate-300">
              <ShieldCheck className="h-4 w-4 text-emerald-400" />
              Detector Runtime
            </h3>
            <div className="mt-4 space-y-3 text-sm">
              <div className="flex items-center justify-between gap-3">
                <span className="text-slate-400">Detector</span>
                <span className="font-mono text-slate-200">{detector?.detector_version || "Unavailable"}</span>
              </div>
              <div className="flex items-center justify-between gap-3">
                <span className="text-slate-400">Thresholds</span>
                <span className="font-mono text-slate-200">{detector?.threshold_version || "Unavailable"}</span>
              </div>
              <div className="flex items-center justify-between gap-3">
                <span className="text-slate-400">Embedding</span>
                <StateBadge tone={isEmbeddingHealthy ? "measured" : "degraded"}>{embeddingState}</StateBadge>
              </div>
              <div className="rounded-lg border border-slate-800 bg-slate-950 p-3 text-xs text-slate-400">
                {detector?.embedding_fallback_reason || detector?.embedding_model_name || "No detector detail available"}
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
          <DistributionTable title="Labels" rows={report?.dataset?.label_distribution} />
          <DistributionTable title="Splits" rows={report?.dataset?.split_distribution} />
          <DistributionTable title="Languages" rows={report?.dataset?.language_distribution} />
        </div>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <div className="rounded-lg border border-slate-800 bg-slate-900 p-5">
            <h3 className="flex items-center gap-2 text-sm font-bold uppercase tracking-wide text-slate-300">
              <Gauge className="h-4 w-4 text-teal-400" />
              Score Integrity
            </h3>
            <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
              <MetricCard label="Recovery" value={formatPercent(metricValue(score, "defense_recovery_rate"))} note="Demo/measured per artifact" />
              <MetricCard label="Utility" value={formatPercent(metricValue(score, "utility_retention"))} note="Clean utility retention" />
              <MetricCard label="Failures" value={formatNumber(report?.failure_case_count)} note="Failure cases in run" />
            </div>
          </div>

          <div className="rounded-lg border border-slate-800 bg-slate-900 p-5">
            <h3 className="flex items-center gap-2 text-sm font-bold uppercase tracking-wide text-slate-300">
              <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              Report Paths
            </h3>
            <div className="mt-4 space-y-2">
              {Object.entries(report?.report_paths || {}).length === 0 ? (
                <p className="text-sm text-slate-500">Unavailable</p>
              ) : (
                Object.entries(report?.report_paths || {}).map(([key, value]) => (
                  <div key={key} className="rounded-lg border border-slate-800 bg-slate-950 p-3">
                    <div className="text-xs text-slate-500">{key}</div>
                    <div className="mt-1 break-all font-mono text-xs text-slate-300">{value}</div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
