# GradingGuard AI — IELTS AI Grading Security Gateway

GradingGuard AI is a robust AI security gateway designed to protect LLM-based IELTS Writing & Speaking automated grading pipelines against prompt injection attacks and score manipulation exploits.

## Architecture & Workflow

```text
Student Submission
        ↓
[1] Input Normalizer (NFKC, zero-width strip, base64/HTML decode)
        ↓
[2] Prompt Injection Detector (Heuristics + Multilingual Patterns)
        ↓
[3] Risk Scoring Engine (Risk score & Action mapping)
        ↓
[4] AI Grading Sanitizer (Strip malicious instructions)
        ↓
[5] Secure IELTS Grader (Hardened prompt + Untrusted payload containment)
        ↓
[6] Score Integrity Verifier (Inflation delta & Stability check)
```

## Quick Start

### 1. Run Backend (FastAPI)

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Backend API health check: [http://localhost:8001/health](http://localhost:8001/health)  
Interactive API docs: [http://localhost:8001/docs](http://localhost:8001/docs)

### 2. Run Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

Frontend Security Playground: [http://localhost:3000/playground](http://localhost:3000/playground)  
Security Operations Center Dashboard: [http://localhost:3000/dashboard](http://localhost:3000/dashboard)

## Test & Validation

Run unit tests:

```bash
PYTHONPATH=backend python3 -m unittest backend/tests/test_firewall.py
```