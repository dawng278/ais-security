# GradingGuard AI — Competition Topic Alignment

> **Purpose**: State explicitly, for judges and for the team, which competition
> topic this project targets and why — so the pitch does not have to be
> re-derived live in front of a panel. Read this alongside
> `docs/final_one_pager.md` (executive summary) and
> `docs/demo_script_student_account_security.md` (secondary-feature demo).

---

## 1. Declared Topic: "AI Security & Robustness"

Of the 9 competition topics, GradingGuard AI targets **topic 4: Bảo mật mô
hình AI và dữ liệu huấn luyện (AI Security & Robustness)** — specifically the
**robustness** half of that topic: defending an LLM-based automated grading
pipeline against prompt injection and score-manipulation attacks embedded in
untrusted user-submitted text.

**Why this topic and not the other 8**: the other 8 topics (deepfake/phishing
detection, network threat detection, vulnerability scanning, malware/forensics,
network traffic anomaly detection, misconfiguration detection, predictive
network maintenance, RL-based routing) all target infrastructure- or
network-layer security. GradingGuard AI's core technical contribution is
application-layer: an AI system's own input channel is the attack surface,
not a network or a binary. That is squarely an "AI Security & Robustness"
problem, not any of the other 8.

**What "robustness" means concretely here**: the grading LLM would otherwise
treat a student's submission as trusted prompt context. An attacker
(the test-taker themselves) can embed instructions inside their own essay to
manipulate the model into returning an inflated score or leaking the grading
rubric. This is a real, published class of LLM vulnerability (prompt
injection / indirect prompt injection), applied to a concrete, measurable
domain: IELTS band scores.

---

## 2. What Satisfies the Topic (Primary Submission Content)

This is the part of the project that should anchor the pitch, the demo, and
any Q&A — it is where the technical judging criteria (dataset, ML/AI use,
robustness evaluation) are actually met:

| Requirement implied by "AI Security & Robustness" | What the project has |
| :--- | :--- |
| A real AI system with a real attack surface | LLM-based IELTS Writing/Speaking grader; submission text is untrusted prompt context |
| A concrete, measurable attack class | Prompt injection / score manipulation — measured in **IELTS band-score inflation** (5.5 → 8.5 without defense), not abstract classification accuracy |
| A defense pipeline, not just detection | 6-stage pipeline: Input Normalizer → Risk Scoring Engine → AI Sanitizer → Secure Grader (XML context isolation) → Score Integrity Verifier → Evidence Generator |
| Adversarial evaluation, not just clean-data accuracy | Attack Arena: 4 attacker profiles (Novice, Multilingual, Obfuscator, Adaptive) red-teaming the defense |
| A real, self-built dataset | Benchmark v3: 662 scenario cases; 7 registered data sources through an 8-stage lineage pipeline (satisfies §4.1 "tự xây dựng tập dữ liệu") |
| Honest, falsifiable evaluation | 0.0% critical failure on the core IELTS score-integrity track; general-robustness under-block cases are surfaced, not hidden, in Failure Analysis |
| Reproducibility / auditability | Evidence Generator emits `dataset_sha256` / `config_sha256` — any judge can independently re-run and verify |

**Bottom line**: the `firewall/`, `benchmark/`, and `grader/` backend modules,
plus the `/playground`, `/attack-arena`, `/benchmark`, `/data-lineage`, and
`/evidence` frontend pages, are the actual competition entry. The demo script
for this content is `docs/demo_script_5min.md`.

---

## 3. What Does NOT Satisfy the Topic (Secondary Feature)

**Student Account Security** — the 2-concurrent-device limit, bcrypt password
hashing, session management, CSRF/rate-limit hardening, and immediate
revocation shipped and audited across 7 release-acceptance gates
(`STUDENT_ACCOUNT_SECURITY_PRODUCTION_READY: PASS`, `origin/main` @
`bf36728`) — is **standard web application security (AppSec), not AI
Security**. No AI/ML model is attacked, defended, or evaluated by that
feature. bcrypt hashing, Origin-header CSRF validation, and a SQLite
fixed-window rate limiter are decades-old, non-AI techniques.

**Do not lead a topic-4 pitch with this feature.** If asked "how does this
relate to AI Security?", the honest answer is: it doesn't, directly — it
demonstrates the product is a complete, credibly-deployable system around the
AI security core, not a bare research prototype. Frame it as **supporting
evidence of engineering maturity**, in one sentence, near the end of a pitch —
not as a second pillar of the submission. Over-explaining it risks the panel
concluding the team misunderstood the topic.

**Suggested one-line mention, if it comes up**: *"Beyond the core AI security
pipeline, we also hardened the platform's own account layer — device limits,
proper password hashing, session revocation — so the security story doesn't
stop at the model boundary. That work is fully tested and documented but is
not itself an AI/ML component."*

---

## 4. Pitch Structure Recommendation

1. **Open** on the AI Security problem (prompt injection into LLM grading) —
   this is topic 4, stated explicitly by name in the first 30 seconds.
2. **Demo** `docs/demo_script_5min.md` in full: Playground → Attack Arena →
   Benchmark → Data Lineage → Evidence.
3. **Close** with the honest limitations already in `README.md` §15
   (heuristic fallback, novel mutation vectors, manual review dependency) —
   judges reward transparency over inflated claims.
4. **Only if asked**, or in a closing "what else did you build" beat,
   mention Student Account Security as engineering-maturity evidence per §3
   above. Do not give it its own dedicated demo slot in a topic-4 pitch.

---

## 5. Honest Assessment: Competitive Position

- **Topic fit**: partial but real. The prompt-injection/robustness core is a
  legitimate, well-evidenced instance of topic 4. It is not, however, a
  central "AI Security & Robustness" case in the way e.g. adversarial-example
  detection or training-data poisoning defense would be — it is closer to
  "AI application security" (protecting a downstream LLM consumer) than
  "AI model security" (protecting the model/training pipeline itself).
  Judges scoring strictly against "bảo mật mô hình AI và dữ liệu huấn luyện"
  may read this as adjacent to, rather than squarely inside, the topic.
- **Strongest asset**: the self-built 662-case benchmark with transparent
  failure reporting (not hiding under-block cases) is a genuine
  differentiator most hackathon entries in this space won't have.
- **Weakest point relative to competition norms**: no training-data
  poisoning, adversarial-example, or model-extraction angle — the topic name
  explicitly says "mô hình AI và dữ liệu huấn luyện" (the model and its
  training data), and this project defends a model's *runtime input*, not
  its *training data or weights*. A strict reading of the topic could
  exclude this project; a broad reading (LLM security generally) includes it
  comfortably.
- **Top-1 likelihood**: realistic framing is "competitive, not favored."
  Winning depends heavily on how strictly the panel interprets topic 4's
  scope. If interpreted broadly (any AI system under adversarial input), this
  entry's depth of evaluation (662 cases, red-team arena, reproducible
  evidence) is genuinely strong. If interpreted narrowly (training-data /
  model-weight security specifically), this entry is off-topic regardless of
  execution quality, and no amount of additional polish fixes that — only a
  scope change would.
