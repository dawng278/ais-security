# Authentication and RBAC

Phase 4 implements a real signed-token boundary for local/test/pilot usage.

- Token type: HS256 signed local/test token.
- Required claims: subject, actor type, roles, client ID, tenant, issued-at and expiry.
- Invalid, unsigned, expired, issuer/audience-mismatched tokens are rejected.
- Tokens are never logged.

Roles:

- `viewer`
- `analyst`
- `policy_manager`
- `security_admin`
- `integration_service`

Authorization is enforced server-side. UI hiding is not considered authorization.

Production external IdP/SSO remains pending. Production mode must not use a development bypass.

