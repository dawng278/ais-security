# Operational Reliability Track

Machine-readable scenarios: `datasets/manifests/operational_reliability_scenarios.json`

## Scope

This is a local benchmark, environment-specific, and not production capacity evidence.

## Scenarios

The track covers:

- normal request latency;
- long request latency;
- rule detector only;
- embedding unavailable;
- partial detector failure simulation;
- detector timeout simulation;
- malformed input;
- oversized input;
- policy error simulation;
- grader timeout simulation;
- audit persistence failure simulation;
- controlled concurrency.

## Metrics

- p50/p95/p99 latency;
- timeout rate;
- error rate;
- throughput;
- detector availability;
- action distribution;
- recovery/failure-state labels.

## Limitation

No production-scale concurrency is fabricated. Missing persistence/policy/grader failures are simulated and labeled as simulated.

