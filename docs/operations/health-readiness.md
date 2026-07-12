# Health and Readiness

Endpoints:

- `/api/v1/security/health/live`
- `/api/v1/security/health/ready`
- authenticated `/api/v1/security/runtime`

Readiness reports database reachability, schema version, current mode, audit persistence and truthful embedding status.

No sensitive configuration is exposed publicly.

