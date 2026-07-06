# GradingGuard AI — Competition Day Runbook

> **Operational Playbook for Live Judging, Presentations & Emergency Fallbacks**

---

## 1. Pre-Presentation Execution (T-15 Minutes)

Execute the automated system check script to verify all services and reports:

```bash
./scripts/final_check.sh
```

### Start Local Services

1. **Backend API Server**:
   ```bash
   cd backend
   ./venv/bin/python -m uvicorn app.main:app --port 8000
   ```
2. **Frontend UI Server**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Browser Initialization**:
   - Open Google Chrome at `http://localhost:3000/judge-view`.
   - Verify local API health check at `http://localhost:8000/health`.

---

## 2. Recommended Live Presentation Navigation Order

1. **`http://localhost:3000/judge-view`** (0:00 – 0:30): Present the 60-second summary banner & core score story (5.5 → 8.5 → 5.5).
2. **`http://localhost:3000/playground`** (0:30 – 1:40): Demonstrate live attack detection, span sanitization, and score recovery.
3. **`http://localhost:3000/attack-arena`** (1:40 – 2:30): Run adversarial simulation across Novice, Multilingual, Obfuscator, and Adaptive attacker profiles.
4. **`http://localhost:3000/benchmark`** (2:30 – 3:30): Showcase Benchmark v3 score integrity metrics, transparent failure analysis, and scenario decision matrix.
5. **`http://localhost:3000/data-lineage`** (3:30 – 4:15): Display data provenance, source registry, and 8-stage transformation pipeline.
6. **`http://localhost:3000/judge-view` (Evidence Section)** (4:15 – 5:00): Highlight cryptographic SHA256 evidence fingerprints and conclude.

---

## 3. Contingency & Fallback Matrix

| Emergency Scenario | Primary Fallback Action | Secondary Fallback Action |
| :--- | :--- | :--- |
| **Backend Process Crashes / Fails** | Use pre-rendered frontend seeded fallback responses (frontend automatically falls back to seeded benchmark data if backend offline). | Show pre-recorded 3-minute video (`docs/demo_recording_runbook.md`). |
| **Frontend Server / Node Crash** | Present static HTML export or FastAPI interactive docs at `http://localhost:8000/docs`. | Open backup screenshot package (`docs/screenshots/README.md`). |
| **Benchmark API Endpoint Fails** | Load pre-generated benchmark JSON report at `datasets/reports/v3/benchmark_v3_combined.json`. | Present `docs/verification_report.md` & `docs/under_block_audit.md`. |
| **Jury Asks About 69% / 79% Benchmark Accuracy** | Use **Two-Track Evaluation Framing**: *"69% belongs to the broader general robustness track evaluating difficult edge cases. On the core IELTS score manipulation threat, the system achieves 0.0% critical failure and prevents +3.0 bands inflation."* | Show `docs/under_block_audit.md` failure breakdown. |
| **Jury Asks About Production Readiness** | Use **Safe Positioning**: *"GradingGuard AI is a competition-ready prototype with an audit-ready evidence architecture and an explicit production hardening roadmap."* | Show Slide 9 limitation roadmap (`docs/final_slide_deck_content.md`). |
