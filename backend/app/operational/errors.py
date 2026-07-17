from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GatewayErrorSpec:
    code: str
    status_code: int
    retryable: bool
    public_message: str
    internal_reason_code: str


ERRORS: dict[str, GatewayErrorSpec] = {
    "INVALID_REQUEST": GatewayErrorSpec("INVALID_REQUEST", 400, False, "Request is invalid.", "VALIDATION_FAILED"),
    "UNSUPPORTED_SCHEMA_VERSION": GatewayErrorSpec(
        "UNSUPPORTED_SCHEMA_VERSION",
        400,
        False,
        "Request schema version is not supported.",
        "SCHEMA_VERSION_UNSUPPORTED",
    ),
    "REQUEST_TOO_LARGE": GatewayErrorSpec("REQUEST_TOO_LARGE", 413, False, "Request is too large.", "CONTENT_LIMIT_EXCEEDED"),
    "RATE_LIMITED": GatewayErrorSpec("RATE_LIMITED", 429, True, "Too many requests. Please retry later.", "RATE_LIMIT_EXCEEDED"),
    "UNAUTHORIZED": GatewayErrorSpec("UNAUTHORIZED", 401, False, "Authentication is required.", "AUTH_REQUIRED"),
    "FORBIDDEN": GatewayErrorSpec("FORBIDDEN", 403, False, "You are not allowed to perform this action.", "RBAC_DENIED"),
    "CONFLICT": GatewayErrorSpec("CONFLICT", 409, True, "Resource version conflict. Refresh and retry.", "OPTIMISTIC_LOCK_CONFLICT"),
    "REQUEST_BLOCKED": GatewayErrorSpec("REQUEST_BLOCKED", 403, False, "Request was blocked by security policy.", "POLICY_BLOCKED_REQUEST"),
    "POLICY_UNAVAILABLE": GatewayErrorSpec("POLICY_UNAVAILABLE", 503, True, "Security policy is temporarily unavailable.", "POLICY_STORE_UNAVAILABLE"),
    "AUDIT_UNAVAILABLE": GatewayErrorSpec("AUDIT_UNAVAILABLE", 503, True, "Audit logging is temporarily unavailable.", "AUDIT_STORE_UNAVAILABLE"),
    "GRADER_TIMEOUT": GatewayErrorSpec("GRADER_TIMEOUT", 504, True, "Grading provider timed out.", "GRADER_TIMEOUT_BUDGET_EXCEEDED"),
    "GRADER_INVALID_RESPONSE": GatewayErrorSpec("GRADER_INVALID_RESPONSE", 502, True, "Grading provider returned an invalid response.", "GRADER_SCHEMA_INVALID"),
    "INTERNAL_ERROR": GatewayErrorSpec("INTERNAL_ERROR", 500, True, "Unexpected internal error.", "UNEXPECTED_INTERNAL_ERROR"),
    "DEVICE_LIMIT_EXCEEDED": GatewayErrorSpec(
        "DEVICE_LIMIT_EXCEEDED", 409, False,
        "You are already logged in on 2 devices. Log out from one device to continue.",
        "STUDENT_DEVICE_LIMIT_EXCEEDED",
    ),
    "EMAIL_ALREADY_EXISTS": GatewayErrorSpec(
        "EMAIL_ALREADY_EXISTS", 409, False,
        "An account with this email already exists.",
        "STUDENT_EMAIL_DUPLICATE",
    ),
    "INVALID_CREDENTIALS": GatewayErrorSpec(
        "INVALID_CREDENTIALS", 401, False,
        "Email or password is incorrect.",
        "STUDENT_INVALID_CREDENTIALS",
    ),
    "ORIGIN_NOT_TRUSTED": GatewayErrorSpec(
        "ORIGIN_NOT_TRUSTED", 403, False,
        "This request's origin is not allowed to perform this action.",
        "STUDENT_ORIGIN_UNTRUSTED",
    ),
}


class GatewayException(Exception):
    def __init__(self, code: str, *, detail: str | None = None):
        self.spec = ERRORS[code]
        self.detail = detail or self.spec.internal_reason_code
        super().__init__(self.detail)

