# Operating Modes

Supported modes: `shadow`, `warn`, `enforce`, `degraded`.

## SHADOW

- Detectors run.
- Decision is calculated.
- Audit must be written when persistent audit exists.
- Original grading path remains authoritative.
- No block.
- No automatic score modification.
- Use for pilot observation and detector calibration.

## WARN

- Grading continues.
- Warning/evidence is attached to the decision.
- Optional analyst queue may be created.
- No hard block unless explicitly configured by a published policy.
- Use when visibility is needed but score availability remains preferred.

## ENFORCE

- Selected policy action is applied.
- Requires published policy.
- Requires rollback.
- Requires acceptable detector health.
- Requires readiness gate.
- Must not silently fall back to unsafe grading when audit/policy dependencies fail.

## DEGRADED

- One or more critical dependencies are unavailable.
- Mode may be entered automatically.
- Reason codes are required.
- Runtime and frontend must expose degraded state.
- Degraded mode is a state of reduced assurance, not a blanket fail-open policy.

## Transition rules

| transition | who can change | required permission | audit | confirmation | rollback | invalid transition |
|---|---|---|---|---|---|---|
| shadow -> warn | security admin | mode:write | `mode_changed` | yes | shadow | reject with `FORBIDDEN`/`CONFLICT` |
| warn -> enforce | security admin | mode:write + policy:publish | `mode_changed` | yes, two-step | warn | reject unless readiness gate passes |
| enforce -> warn | security admin | mode:write | `mode_changed` | yes | enforce with previous policy | allowed as rollback |
| any -> degraded | system/admin | system health or mode:write | `mode_changed` | no for automatic, yes for manual | previous mode after health recovers | require reason code |
| degraded -> previous | system/admin | health restored or mode:write | `mode_changed` | yes for manual | degraded | reject if dependency still critical |

## Failure-mode decision matrix

Allowed behaviors: `fail-open`, `fail-closed`, `continue-with-warning`, `manual-review`, `retry`, `reject`.

| failure | shadow | warn | enforce | rationale | residual risk |
|---|---|---|---|---|---|
| rule detector unavailable | continue-with-warning | continue-with-warning | manual-review | Heuristic detector is core to current coverage. | review backlog. |
| embedding detector unavailable | continue-with-warning | continue-with-warning | continue-with-warning if rules healthy | Embedding is optional and currently unavailable in runtime evidence. | lower semantic recall. |
| all detectors unavailable | fail-open only with critical warning | manual-review | fail-closed or manual-review | No detector signal means no safe enforcement. | availability pressure. |
| policy store unavailable | continue-with-warning using default shadow | continue-with-warning using cached published policy | fail-closed or manual-review | Enforce requires known policy. | stale policy. |
| audit store unavailable | continue-with-warning | manual-review | fail-closed or manual-review | Enforce decisions require audit. | temporary audit gap. |
| grader unavailable | retry then continue original path | retry then manual-review | retry then manual-review/reject | Score availability vs integrity differs by mode. | delayed grading. |
| grader timeout | retry | retry then manual-review | retry then reject/manual-review | Timeout budget is explicit. | repeated provider outage. |
| invalid grader output | continue original path with warning | manual-review | reject/manual-review | Invalid structured output cannot be trusted. | false invalids. |
| manual-review queue unavailable | continue-with-warning | continue-with-warning | reject unless policy permits retry | Queue must exist before enforce review actions. | blocked grading. |
| malformed request | reject | reject | reject | Contract violation. | client integration bug. |
| oversized request | reject | reject | reject | Prevent resource exhaustion. | legitimate long essays need limits. |
| rate limit exceeded | reject | reject | reject | Availability protection. | user friction. |

