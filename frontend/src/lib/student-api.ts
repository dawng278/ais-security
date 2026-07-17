// frontend/src/lib/student-api.ts
import type { GatewayDecision } from "./security-api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface StudentApiError {
  code: string;
  message: string;
  retryable: boolean;
}

export class StudentRequestError extends Error {
  code: string;
  status: number;
  retryable: boolean;

  constructor(status: number, error: StudentApiError) {
    super(error.message);
    this.code = error.code;
    this.status = status;
    this.retryable = error.retryable;
  }
}

async function studentRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
  });
  const text = await response.text();
  const payload = text ? JSON.parse(text) : {};
  if (!response.ok) {
    const error: StudentApiError = payload?.error ?? {
      code: "UNKNOWN_ERROR",
      message: "Something went wrong.",
      retryable: false,
    };
    throw new StudentRequestError(response.status, error);
  }
  return payload as T;
}

export interface StudentProfile {
  id: string;
  email: string;
  full_name?: string | null;
}

export interface StudentDevice {
  id: string;
  user_agent: string | null;
  ip_address: string | null;
  created_at: string;
  last_seen_at: string;
  expires_at: string;
}

export interface StudentSubmission {
  decision_id: string;
  request_id: string;
  applied_action: string;
  risk_score: number;
  severity: string;
  created_at: string;
}

export const studentApi = {
  register: (input: { email: string; password: string; full_name?: string; phone?: string }) =>
    studentRequest<StudentProfile>("/api/v1/students/register", {
      method: "POST",
      body: JSON.stringify(input),
    }),

  login: (input: { email: string; password: string }) =>
    studentRequest<StudentProfile>("/api/v1/students/login", {
      method: "POST",
      body: JSON.stringify(input),
    }),

  logout: () => studentRequest<{ ok: boolean }>("/api/v1/students/logout", { method: "POST" }),

  me: () => studentRequest<StudentProfile>("/api/v1/students/me"),

  devices: () => studentRequest<{ devices: StudentDevice[] }>("/api/v1/students/devices"),

  revokeDevice: (sessionId: string) =>
    studentRequest<{ ok: boolean }>(`/api/v1/students/devices/${sessionId}/revoke`, { method: "POST" }),

  submissions: () => studentRequest<{ submissions: StudentSubmission[] }>("/api/v1/students/submissions"),

  // Note: no student_id/pseudonymous_user_id field exists here by design --
  // the backend binds the submission to the authenticated student from the
  // session cookie, never from client input. See backend/app/api/student_auth_v1.py.
  analyze: (input: { submission_id: string; task_type: "writing" | "speaking"; candidate_content: string; language?: string }) =>
    studentRequest<GatewayDecision>("/api/v1/students/analyze", {
      method: "POST",
      body: JSON.stringify(input),
    }),
};
