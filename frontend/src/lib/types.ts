export type TaskType = "writing" | "speaking";

export type AttackType =
  | "direct_english"
  | "direct_vietnamese"
  | "direct_chinese"
  | "unicode_obfuscation"
  | "base64_instruction"
  | "markdown_role_spoofing"
  | "indirect_injection"
  | "speaking_transcript_injection";

export type FirewallAction =
  | "allow"
  | "warn"
  | "secure_grade"
  | "manual_review";

export interface FirewallResult {
  risk_score: number;
  risk_level: "low" | "medium" | "high" | "critical";
  action: FirewallAction;
  attack_type: string;
  detected_patterns: string[];
  normalization_flags: string[];
  explanation: string;
}

export interface RedteamResult {
  attack_type: string;
  original_text: string;
  injected_text: string;
  injected_span: string;
  explanation: string;
}

export interface GradingResult {
  mode: "baseline" | "secure" | "clean";
  overall_band: number;
  criteria: {
    task_response: number;
    coherence_cohesion: number;
    lexical_resource: number;
    grammar: number;
  };
  feedback: string;
  security_notes?: string | null;
}

export interface SecureGradeResponse {
  firewall: FirewallResult;
  sanitizer: {
    cleaned_text: string;
    removed_spans: string[];
  };
  grading: GradingResult;
  verifier: {
    integrity_status: string;
    attack_inflation: number;
    defense_recovery: number;
    score_stability: number;
    issues: string[];
    recommendation: string;
  };
}

export interface CompareResponse {
  clean_result: GradingResult;
  baseline_injected_result: GradingResult;
  secure_injected_result: GradingResult;
  score_delta: {
    attack_inflation: number;
    defense_recovery: number;
    score_stability: number;
  };
  firewall: FirewallResult;
  verifier: {
    integrity_status: string;
    recommendation: string;
  };
}

export interface DashboardStats {
  total_submissions: number;
  attacks_detected: number;
  high_risk_count: number;
  average_risk_score: number;
  score_manipulations_prevented: number;
  attack_type_breakdown: Record<string, number>;
  action_breakdown: Record<string, number>;
}

export interface SecurityEvent {
  id: string;
  submission_id: string;
  risk_score: number;
  risk_level: "low" | "medium" | "high" | "critical";
  action: FirewallAction;
  attack_type: string;
  detected_patterns: string[];
  removed_spans: string[];
  explanation: string;
  created_at: string;
}
