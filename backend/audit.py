import os
import time
from pathlib import Path
from typing import Any

from models import AuditEvent

BACKEND_DIR = Path(__file__).resolve().parent
AUDIT_LOG_PATH = Path(
    os.getenv("AUDIT_LOG_PATH", BACKEND_DIR / ".." / "output" / "audit_trail.json")
).resolve()

_MAX_FIELD_LEN = 200


def _short(value: Any) -> str:
    text = value if isinstance(value, str) else repr(value)
    return text if len(text) <= _MAX_FIELD_LEN else text[:_MAX_FIELD_LEN] + "…"


def _append(event: AuditEvent) -> None:
    # JSON Lines, not a single JSON array: a true append-only log just opens
    # in append mode and writes one line. A single growing array would need
    # a read-modify-rewrite of the whole file on every entry, which is both
    # slower over time and one interrupted write away from corrupting every
    # prior entry — the opposite of "append-only, never wiped."
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(event.model_dump_json(exclude_none=True) + "\n")


def log_tool_call(tool_name: str, args: Any, result: Any) -> None:
    _append(
        AuditEvent(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            type="tool_call",
            tool=tool_name,
            args=_short(args),
            result=_short(result),
        )
    )


def log_run_complete(message: str, stop_reason: str | None, product_count: int, is_guest: bool) -> None:
    _append(
        AuditEvent(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            type="run_complete",
            message_preview=_short(message),
            stop_reason=stop_reason,
            product_count=product_count,
            is_guest=is_guest,
        )
    )
