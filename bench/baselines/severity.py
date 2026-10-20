from __future__ import annotations

import re
from collections.abc import Sequence

_SEVERE_LEVELS = {"FATAL", "SEVERE", "ERROR", "FAILURE", "KILL", "CRITICAL", "ALERT", "EMERG", "PANIC"}
_KW = re.compile(
    r"\b(fatal|panic|segfault|oom|kill(ed)?|corrupt\w*|exception|error|fail(ed|ure)?|"
    r"refused|timed?\s?out|unreachable|unavailable)\b",
    re.IGNORECASE,
)


def flag_by_severity(levels: Sequence[str], messages: Sequence[str]) -> list[bool]:
    out = []
    for lvl, msg in zip(levels, messages, strict=True):
        hit = (lvl or "").upper() in _SEVERE_LEVELS or bool(_KW.search(msg or ""))
        out.append(hit)
    return out