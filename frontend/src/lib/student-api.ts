// frontend/src/lib/student-api.ts
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
};
