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

export interface BenchmarkCaseResult {
  id: string;
  label: string;
  expected_action: string;
  actual_action: string;
  risk_score: number;
  passed: boolean;
}

export interface BenchmarkSummary {
  total_cases: number;
  passed_cases: number;
  accuracy: number;
  precision: number;
  recall: number;
  false_positive_rate: number;
  case_results: BenchmarkCaseResult[];
}

export interface BenchmarkCaseEvaluationResultV2 {
  sample_id: string;
  group_id: string;
  label: string;
  attack_type: string;
  expected_action: string;
  predicted_action: string;
  risk_score: number;
  passed: boolean;
  error_type?: string | null;
}

export interface BenchmarkReportV2 {
  benchmark_id: string;
  total_cases: number;
  passed_cases: number;
  accuracy: number;
  precision: number;
  recall: number;
  macro_f1: number;
  false_positive_rate: number;
  under_block_rate: number;
  over_block_rate: number;
  by_attack_type: Record<string, { accuracy: number; total: number }>;
  by_language: Record<string, { accuracy: number; total: number }>;
  failure_cases: BenchmarkCaseEvaluationResultV2[];
}

export interface AttackerProfile {
  profile_id: string;
  name: string;
  description: string;
  skill_level: string;
  attack_types: string[];
}

export interface DefenseStep {
  name: string;
  status: string;
  details: string;
}

export interface ArenaAttempt {
  attempt_id: number;
  attack_type: string;
  injected_span: string;
  baseline_score: number;
  secure_score: number;
  risk_score: number;
  action: FirewallAction | string;
  result_status: string;
  removed_spans: string[];
  defense_steps: DefenseStep[];
}

export interface ArenaRunRequest {
  original_text: string;
  profile_id: string;
  task_type?: TaskType | string;
}

export interface ArenaRunResponse {
  scenario_id: string;
  profile: AttackerProfile;
  attempts: ArenaAttempt[];
  total_attempts: number;
  secured_attempts: number;
  manual_review_attempts: number;
  benign_allowed: number;
  total_score_inflation_prevented: number;
  clean_utility_loss: number;
}

export interface FailureAnalysisItem {
  case_id: string;
  error_type: string;
  attack_type: string;
  language: string;
  risk_score: number;
  expected_action: string;
  predicted_action: string;
  likely_reason: string;
  next_fix: string;
  severity: 'high' | 'medium' | 'low' | string;
  text_preview: string;
}

export interface FailureAnalysisResponse {
  is_demo: boolean;
  count: number;
  note?: string;
  failures: FailureAnalysisItem[];
}

export interface DataSourceLineage {
  source_id: string;
  platform: string;
  purpose: string;
  license_status: string;
  raw_rows: number;
  accepted_rows: number;
  rejected_rows: number;
  notes: string;
}

export interface TransformStage {
  stage: string;
  input_rows: number;
  output_rows: number;
  rejected_rows: number;
  reason: string;
}

export interface DatasetLineageReport {
  dataset_version: string;
  dataset_sha256?: string | null;
  sources: DataSourceLineage[];
  stages: TransformStage[];
  split_distribution: Record<string, number>;
  label_distribution: Record<string, number>;
  attack_type_distribution: Record<string, number>;
  language_distribution: Record<string, number>;
  notes: string[];
}

export interface PerspectiveMetric {
  perspective_name: string;
  total_cases: number;
  passed_cases: number;
  pass_rate: number;
  description: string;
}

export interface ScenarioEvaluationResult {
  case_id: string;
  scenario_group: string;
  language: string;
  task_type: string;
  is_attack: boolean;
  primary_perspective: string;
  risk_dimension: string;
  expected_action: string;
  predicted_action: string;
  risk_score: number;
  passed: boolean;
  failure_reason?: string | null;
  text_preview: string;
  notes?: string | null;
}

export interface MultiPerspectiveReport {
  report_id: string;
  total_scenarios: number;
  overall_pass_rate: number;
  perspective_metrics: Record<string, PerspectiveMetric>;
  scenario_group_pass_rates: Record<string, number>;
  language_pass_rates: Record<string, number>;
  most_fragile_perspective: string;
  strongest_perspective: string;
  is_demo?: boolean;
  evaluation_results: ScenarioEvaluationResult[];
}

export interface DecisionMatrixItem {
  condition: string;
  examples: string[];
  expected_action: string;
  under_block_risk: string;
  over_block_risk: string;
  rationale: string;
}

export interface CaseLibraryEvaluationResult {
  case_id: string;
  title: string;
  scenario_group: string;
  language: string;
  task_type: string;
  primary_perspective: string;
  expected_action: string;
  predicted_action: string;
  risk_score: number;
  passed: boolean;
  failure_reason?: string | null;
  under_block_risk: string;
  over_block_risk: string;
  stakeholder_lenses?: string[];
  evidence_observed?: Record<string, any>;
  text_preview: string;
}

export interface CaseLibraryEvaluationReport {
  total_cases: number;
  passed_cases: number;
  failed_cases: number;
  pass_rate: number;
  by_perspective: Record<string, { total: number; passed: number; failed: number; pass_rate: number }>;
  by_scenario_group: Record<string, { total: number; passed: number; failed: number; pass_rate: number }>;
  by_language: Record<string, { total: number; passed: number; failed: number; pass_rate: number }>;
  by_expected_action: Record<string, { total: number; passed: number; failed: number; pass_rate: number }>;
  most_fragile_perspective: string;
  strongest_perspective: string;
  is_demo?: boolean;
  results: CaseLibraryEvaluationResult[];
}

export interface StakeholderLens {
  stakeholder_id: string;
  name: string;
  main_concern: string;
  what_good_looks_like: string;
  risk_if_underblocked: string;
  risk_if_overblocked: string;
  evidence_needed: string[];
}





