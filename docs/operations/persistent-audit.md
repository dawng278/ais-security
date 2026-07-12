# Persistent Audit

Phase 4 stores append-oriented audit events in SQLite pilot storage.

Events include actor, actor type, correlation ID, target, action, environment, policy version, safe metadata, redaction state, outcome and reason code.

Required events covered in the pilot path include request received, detector result, policy evaluated, decision made, incident created, review created/assigned/resolved, policy validated/published/rolled back, mode changed and sensitive-content access.

Audit events are not edited in place. Corrections require a new event.

