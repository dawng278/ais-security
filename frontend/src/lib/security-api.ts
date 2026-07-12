"use client";

export type Role = "viewer" | "analyst" | "policy_manager" | "security_admin" | "integration_service";
export type OperatingMode = "shadow" | "warn" | "enforce" | "degraded";
export type SecurityAction = "allow" | "warn" | "sanitize" | "secure_grade" | "manual_review" | "block";

export interface SecuritySession {
  accessToken: string;
  subject: string;
  clientId: string;
  roles: Role[];
  truthLabel: "DEVELOPMENT_ONLY_SIGNED_TOKEN" | "USER_SUPPLIED_TOKEN";
}

export interface ApiError {
  code: string;
  message: string;
  retryable: boolean;
  correlationId?: string | null;
  status: number;
}

export interface RequestState<T> {
  status: "idle" | "loading" | "success" | "empty" | "error" | "unauthorized" | "forbidden" | "rate_limited" | "conflict" | "degraded" | "offline";
  data?: T;
  error?: ApiError;
}

export interface GatewayDecision {
  schema_version: "grading_decision.v1";
  decision_id: string;
  request_id: string;
  correlation_id: string;
  operating_mode: OperatingMode;
  applied_action: SecurityAction;
  counterfactual_action?: SecurityAction | null;
  risk_score: number;
  severity: "low" | "medium" | "high" | "critical" | string;
  detected_techniques: string[];
  policy_id: string;
  policy_version: string;
  detector_health: Record<string, string>;
  review_state?: string | null;
  incident_id?: string | null;
  review_id?: string | null;
  final_outcome: string;
  grader_result_metadata: Record<string, unknown>;
  safe_preview: string;
  redaction_state: string;
  retryable: boolean;
  created_at: string;
  completed_at: string;
}

export interface Incident {
  incident_id: string;
  decision_id: string;
  correlation_id: string;
  severity: string;
  status: string;
  techniques_json: string;
  selected_action: SecurityAction;
  assignee?: string | null;
  opened_at: string;
  updated_at: string;
  resolved_at?: string | null;
  resolution?: string | null;
  safe_summary: string;
  restricted_evidence_ref: string;
  version: number;
}

export interface ManualReview {
  review_id: string;
  decision_id: string;
  incident_id?: string | null;
  correlation_id: string;
  state: string;
  priority: string;
  sla_deadline: string;
  assignee?: string | null;
  safe_content_preview: string;
  resolution?: string | null;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface PolicyVersion {
  version_id: string;
  policy_id: string;
  version: string;
  status: string;
  policy_json: string;
  checksum: string;
  created_by: string;
  approved_by?: string | null;
  created_at: string;
  updated_at: string;
  published_at?: string | null;
  name?: string;
}

export interface AuditEvent {
  event_id: string;
  correlation_id: string;
  actor_subject: string;
  actor_type: string;
  action: string;
  target_type: string;
  target_id: string;
  environment: string;
  policy_version?: string | null;
  safe_metadata_json: string;
  redaction_state: string;
  outcome: string;
  reason_code: string;
  created_at: string;
}

export interface RuntimeStatus {
  mode: {
    mode: OperatingMode;
    version: number;
    reason_code: string;
    active_policy_version_id?: string | null;
    updated_at: string;
  };
  metrics: {
    status: string;
    high_cardinality_guard: string;
    metrics: Array<{ name: string; count: number }>;
  };
  embedding: string;
}

export interface ReadinessStatus {
  status: string;
  database: string;
  schema_version: number;
  mode: OperatingMode;
  audit_persistence: string;
  embedding: string;
}

export interface GatewayRequest {
  schema_version: "grading_request.v1";
  request_id: string;
  correlation_id?: string;
  submission_id: string;
  pseudonymous_user_id?: string;
  task_type: "writing" | "speaking";
  candidate_content: string;
  language: string;
  metadata?: Record<string, string>;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function normalizeError(status: number, payload: unknown): ApiError {
  const maybe = payload as { error?: { code?: string; message?: string; retryable?: boolean; correlation_id?: string | null } };
  return {
    status,
    code: maybe.error?.code || (status === 401 ? "UNAUTHORIZED" : status === 403 ? "FORBIDDEN" : "REQUEST_FAILED"),
    message: maybe.error?.message || `Request failed with status ${status}`,
    retryable: Boolean(maybe.error?.retryable),
    correlationId: maybe.error?.correlation_id,
  };
}

export function stateForError(error: ApiError): RequestState<never>["status"] {
  if (error.status === 401) return "unauthorized";
  if (error.status === 403) return "forbidden";
  if (error.status === 409) return "conflict";
  if (error.status === 429) return "rate_limited";
  if (error.status >= 500) return "degraded";
  return "error";
}

export async function securityRequest<T>(
  path: string,
  options: RequestInit & { token?: string; idempotencyKey?: string; timeoutMs?: number } = {},
): Promise<T> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), options.timeoutMs ?? 8000);
  try {
    const headers = new Headers(options.headers);
    headers.set("Content-Type", "application/json");
    if (options.token) headers.set("Authorization", `Bearer ${options.token}`);
    if (options.idempotencyKey) headers.set("Idempotency-Key", options.idempotencyKey);
    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
      signal: controller.signal,
    });
    const text = await response.text();
    const payload = text ? JSON.parse(text) : {};
    if (!response.ok) throw normalizeError(response.status, payload);
    return payload as T;
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw {
        status: 408,
        code: "TIMEOUT",
        message: "Request timed out.",
        retryable: true,
      } satisfies ApiError;
    }
    if (typeof navigator !== "undefined" && !navigator.onLine) {
      throw {
        status: 0,
        code: "OFFLINE",
        message: "Browser appears offline.",
        retryable: true,
      } satisfies ApiError;
    }
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}

export async function createDevelopmentSession(): Promise<SecuritySession> {
  const response = await securityRequest<{
    access_token: string;
    subject: string;
    client_id: string;
    roles: Role[];
    truth_label: "DEVELOPMENT_ONLY_SIGNED_TOKEN";
  }>("/api/v1/security/session/dev-token", {
    method: "POST",
    body: JSON.stringify({
      subject: "phase5-console-operator",
      client_id: "phase5-console",
      roles: ["viewer", "analyst", "policy_manager", "security_admin", "integration_service"],
    }),
  });
  return {
    accessToken: response.access_token,
    subject: response.subject,
    clientId: response.client_id,
    roles: response.roles,
    truthLabel: response.truth_label,
  };
}

export const securityApi = {
  runtime: (session: SecuritySession) => securityRequest<RuntimeStatus>("/api/v1/security/runtime", { token: session.accessToken }),
  readiness: () => securityRequest<ReadinessStatus>("/api/v1/security/health/ready"),
  decisions: (session: SecuritySession) => securityRequest<{ items: GatewayDecision[] }>("/api/v1/security/decisions", { token: session.accessToken }),
  decision: (session: SecuritySession, id: string) => securityRequest<GatewayDecision>(`/api/v1/security/decisions/${encodeURIComponent(id)}`, { token: session.accessToken }),
  restrictedEvidence: (session: SecuritySession, id: string, purpose: string) =>
    securityRequest<{ decision_id: string; content_hash: string; restricted_evidence: Record<string, unknown> }>(
      `/api/v1/security/decisions/${encodeURIComponent(id)}/restricted-evidence?purpose=${encodeURIComponent(purpose)}`,
      { token: session.accessToken },
    ),
  incidents: (session: SecuritySession) => securityRequest<{ items: Incident[] }>("/api/v1/security/incidents", { token: session.accessToken }),
  incident: (session: SecuritySession, id: string) => securityRequest<Incident>(`/api/v1/security/incidents/${encodeURIComponent(id)}`, { token: session.accessToken }),
  reviews: (session: SecuritySession) => securityRequest<{ items: ManualReview[] }>("/api/v1/security/reviews", { token: session.accessToken }),
  assignReview: (session: SecuritySession, review: ManualReview, assignee: string, note: string) =>
    securityRequest<ManualReview>(`/api/v1/security/reviews/${encodeURIComponent(review.review_id)}/assign`, {
      method: "POST",
      token: session.accessToken,
      idempotencyKey: `assign-${review.review_id}-${review.version}`,
      body: JSON.stringify({ assignee, expected_version: review.version, note }),
    }),
  startReview: (session: SecuritySession, review: ManualReview, note: string) =>
    securityRequest<ManualReview>(`/api/v1/security/reviews/${encodeURIComponent(review.review_id)}/start`, {
      method: "POST",
      token: session.accessToken,
      idempotencyKey: `start-${review.review_id}-${review.version}`,
      body: JSON.stringify({ expected_version: review.version, note }),
    }),
  resolveReview: (session: SecuritySession, review: ManualReview, resolution: "resolved_allow" | "resolved_block" | "escalated", note: string) =>
    securityRequest<ManualReview>(`/api/v1/security/reviews/${encodeURIComponent(review.review_id)}/resolve`, {
      method: "POST",
      token: session.accessToken,
      idempotencyKey: `resolve-${review.review_id}-${review.version}-${resolution}`,
      body: JSON.stringify({ resolution, expected_version: review.version, note, confirm: true }),
    }),
  policies: (session: SecuritySession) => securityRequest<{ items: PolicyVersion[] }>("/api/v1/security/policies", { token: session.accessToken }),
  createPolicy: (session: SecuritySession, policyId: string, name: string, version: string, action: SecurityAction) =>
    securityRequest<{ version_id: string; status: string; checksum: string }>(`/api/v1/security/policies`, {
      method: "POST",
      token: session.accessToken,
      idempotencyKey: `policy-${policyId}-${version}`,
      body: JSON.stringify({
        policy_id: policyId,
        name,
        version,
        policy: { operating_modes: ["shadow", "warn", "enforce"], action, priority: 100, fallback: "warn" },
      }),
    }),
  publishPolicy: (session: SecuritySession, policy: PolicyVersion) =>
    securityRequest<Record<string, string>>(`/api/v1/security/policies/${encodeURIComponent(policy.policy_id)}/publish`, {
      method: "POST",
      token: session.accessToken,
      idempotencyKey: `publish-${policy.version_id}`,
      body: JSON.stringify({ version_id: policy.version_id, confirm: true }),
    }),
  rollbackPolicy: (session: SecuritySession, policy: PolicyVersion) =>
    securityRequest<Record<string, string>>(`/api/v1/security/policies/${encodeURIComponent(policy.policy_id)}/rollback`, {
      method: "POST",
      token: session.accessToken,
      idempotencyKey: `rollback-${policy.version_id}`,
      body: JSON.stringify({ target_version_id: policy.version_id, confirm: true }),
    }),
  changeMode: (session: SecuritySession, runtime: RuntimeStatus, mode: OperatingMode) =>
    securityRequest<RuntimeStatus["mode"]>("/api/v1/security/runtime/mode", {
      method: "POST",
      token: session.accessToken,
      idempotencyKey: `mode-${mode}-${runtime.mode.version}`,
      body: JSON.stringify({ mode, expected_version: runtime.mode.version, justification: `Phase 5 console transition to ${mode}`, confirm: true }),
    }),
  audit: (session: SecuritySession, targetType?: string, targetId?: string, correlationId?: string) => {
    const params = new URLSearchParams();
    if (targetType) params.set("target_type", targetType);
    if (targetId) params.set("target_id", targetId);
    if (correlationId) params.set("correlation_id", correlationId);
    return securityRequest<{ items: AuditEvent[] }>(`/api/v1/security/audit?${params.toString()}`, { token: session.accessToken });
  },
  analyze: (session: SecuritySession, request: GatewayRequest) =>
    securityRequest<GatewayDecision>("/api/v1/security/analyze", {
      method: "POST",
      token: session.accessToken,
      idempotencyKey: `analyze-${request.request_id}`,
      body: JSON.stringify(request),
    }),
  grade: (session: SecuritySession, request: GatewayRequest) =>
    securityRequest<GatewayDecision>("/api/v1/security/grade", {
      method: "POST",
      token: session.accessToken,
      idempotencyKey: `grade-${request.request_id}`,
      body: JSON.stringify(request),
    }),
};

export function parseJsonArray(value: string | undefined | null): string[] {
  if (!value) return [];
  try {
    const parsed = JSON.parse(value);
    return Array.isArray(parsed) ? parsed.map(String) : [];
  } catch {
    return [];
  }
}

export function formatPercent(value: number | undefined | null, digits = 1): string {
  return typeof value === "number" && Number.isFinite(value) ? `${(value * 100).toFixed(digits)}%` : "Unavailable";
}

export function createRequestId(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
}

