#!/usr/bin/env bash
set -e

echo "========================================================"
echo "GradingGuard AI — Final Verification Check"
echo "========================================================"

echo "Step 1: Running backend tests..."
cd backend
if [ -d "venv" ]; then
    PYTHONPATH=.. ./venv/bin/python -m unittest discover -s tests
else
    PYTHONPATH=.. python3 -m unittest discover -s tests
fi
echo "✓ Backend tests passed."

echo "Step 2: Executing Benchmark v3 suite..."
if [ -d "venv" ]; then
    PYTHONPATH=.. ./venv/bin/python -m app.benchmark.runner_v3
else
    PYTHONPATH=.. python3 -m app.benchmark.runner_v3
fi
echo "✓ Benchmark v3 completed."
cd ..

echo "Step 3: Checking frontend production build..."
cd frontend
npm run build
echo "✓ Frontend build completed cleanly."
cd ..

echo "========================================================"
echo "✓ Final Verification Check Completed Successfully!"
echo "========================================================"
echo ""
echo "Final submission assets created & ready:"
echo "  - Screenshot guide:       docs/screenshots/README.md"
echo "  - Demo recording runbook: docs/demo_recording_runbook.md"
echo "  - Slide deck content:    docs/final_slide_deck_content.md"
echo "  - Final one-pager:       docs/final_one_pager.md"
echo "  - Competition runbook:   docs/competition_day_runbook.md"
echo "  - Judge cheat sheet:     docs/judge_cheat_sheet.md"
echo ""
echo "Remaining manual tasks before submission:"
echo "  1. Record 3-minute video (following docs/demo_recording_runbook.md)"
echo "  2. Capture 9 screenshots (following docs/screenshots/README.md)"
echo "  3. Create slides (using docs/final_slide_deck_content.md)"
echo ""
