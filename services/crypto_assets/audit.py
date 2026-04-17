from datetime import datetime, UTC

AUDIT_LOG: list[dict] = []


def log_audit_event(actor: str, action: str, details: dict | None = None) -> dict:
    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "actor": actor,
        "action": action,
        "details": details or {},
    }
    AUDIT_LOG.append(entry)
    return entry
