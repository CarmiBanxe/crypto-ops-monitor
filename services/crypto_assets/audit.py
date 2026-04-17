from datetime import datetime, UTC

AUDIT_LOG: list[dict] = []


def record_audit(actor: str, action: str, object_type: str, object_ref: str, before=None, after=None):
    AUDIT_LOG.append(
        {
            "timestamp": datetime.now(UTC).isoformat(),
            "actor": actor,
            "action": action,
            "object_type": object_type,
            "object_ref": object_ref,
            "before": before,
            "after": after,
        }
    )
