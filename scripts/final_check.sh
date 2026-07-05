#!/usr/bin/env bash
set -e

echo "========================================================"
echo "GradingGuard AI — Final Verification Check"
echo "========================================================"

echo "Step 1: Running backend tests..."
cd backend
if [ -d "venv" ]; then
    ./venv/bin/python -m unittest discover -s tests
else
    python3 -m unittest discover -s tests
fi
echo "✓ Backend tests passed."

echo "Step 2: Executing Benchmark v3 suite..."
if [ -d "venv" ]; then
    ./venv/bin/python -m app.benchmark.runner_v3
else
    python3 -m app.benchmark.runner_v3
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
