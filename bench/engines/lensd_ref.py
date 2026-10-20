from __future__ import annotations

import re
from collections.abc import Sequence

_SEPS = set(" \t\r\n,;()[]{}\"'")

_UUID = re.compile(r"\A[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\Z")


def _all_digits(s: str) -> bool:
    return len(s) > 0 and s.isdigit()


def _is_time(s: str) -> bool:
    n = len(s)
    if n >= 10 and _all_digits(s[0:4]):
        sep = s[4]
        if sep in "-/." and _all_digits(s[5:7]) and s[7] == sep and _all_digits(s[8:10]):
            return True
    if n >= 8 and _all_digits(s[0:2]) and s[2] == ":" and _all_digits(s[3:5]) and s[5] == ":" and _all_digits(s[6:8]):
        if n == 8:
            return True
        return s[8] in ".," and _all_digits(s[9:])
    return False


def _is_ipv4(s: str) -> bool:
    if len(s) < 7:
        return False
    host = s
    port = None
    if ":" in s:
        host, _, port = s.partition(":")
    parts = host.split(".")
    if len(parts) != 4:
        return False
    for p in parts:
        if not (1 <= len(p) <= 3) or not p.isdigit() or int(p) > 255:
            return False
    if port is not None:
        if not (1 <= len(port) <= 5) or not port.isdigit():
            return False
    return True


def _is_ipv6(s: str) -> bool:
    colons = s.count(":")
    if colons < 2:
        return False
    has_hex_letter = False
    for ch in s:
        if ch == ":":
            continue
        if ch in "0123456789abcdefABCDEF":
            if ch not in "0123456789":
                has_hex_letter = True
        else:
            return False
    return has_hex_letter or "::" in s


def _is_ip(s: str) -> bool:
    if s.startswith("/"):
        s = s[1:]
    return _is_ipv4(s) or _is_ipv6(s)


def _is_blk(s: str) -> bool:
    i = 0
    while i < len(s) and s[i].isalpha():
        i += 1
    if i == 0 or i >= len(s):
        return False
    if s[i] not in "_-":
        return False
    digits = 0
    for ch in s[i:]:
        if ch.isdigit():
            digits += 1
        elif ch not in "-_":
            return False
    return digits >= 4


_HEXCHARS = set("0123456789abcdefABCDEF")


def _is_hex(s: str) -> bool:
    n = len(s)
    if n >= 3 and s[0] == "0" and s[1] in "xX":
        return all(c in _HEXCHARS for c in s[2:])
    if n < 6:
        return False
    has_digit = has_letter = False
    for c in s:
        if c not in _HEXCHARS:
            return False
        if c.isdigit():
            has_digit = True
        else:
            has_letter = True
    return has_digit and has_letter  


def _is_num(s: str) -> bool:
    i, n = 0, len(s)
    if n == 0:
        return False
    if s[i] in "+-":
        i += 1
    digits = dots = exp = 0
    while i < n:
        c = s[i]
        if c.isdigit():
            digits += 1
        elif c == ".":
            dots += 1
            if dots > 1 or exp > 0:
                return False
        elif c in "eE":
            exp += 1
            if exp > 1 or digits == 0:
                return False
            if i + 1 < n and s[i + 1] in "+-":
                i += 1
        else:
            return False
        i += 1
    return digits > 0


def _is_path(s: str) -> bool:
    if len(s) >= 3 and s[0].isalpha() and s[1] == ":" and s[2] in "\\/":
        return True
    return s.count("/") >= 2


def _classify(s: str) -> str:
    if not s:
        return "WORD"
    if _UUID.match(s):
        return "<UUID>"
    if _is_time(s):
        return "<TIME>"
    if _is_ip(s):
        return "<IP>"
    if _is_blk(s):
        return "<BLK>"
    if _is_hex(s):
        return "<HEX>"
    if _is_num(s):
        return "<NUM>"
    if _is_path(s):
        return "<PATH>"
    return "WORD"


_KEY_START = re.compile(r"[A-Za-z_]")
_KEY_CHAR = re.compile(r"[A-Za-z0-9_.\-]")


def _kv_split(tok: str) -> int:
    if len(tok) < 3 or not _KEY_START.match(tok[0]):
        return -1
    for i in range(1, len(tok) - 1):
        if tok[i] == "=":
            if all(_KEY_CHAR.match(c) for c in tok[:i]):
                return i
            return -1
    return -1


def _tokens(line: str) -> list[str]:
    out, cur = [], []
    for ch in line:
        if ch in _SEPS:
            if cur:
                out.append("".join(cur))
                cur = []
        else:
            cur.append(ch)
    if cur:
        out.append("".join(cur))
    return out


def mask_line(line: str) -> str:
    parts = []
    for tok in _tokens(line):
        eq = _kv_split(tok)
        if eq > 0:
            key, val = tok[:eq], tok[eq + 1 :]
            cls = _classify(val)
            parts.append(f"{key}=" + (val if cls == "WORD" else cls))
        else:
            cls = _classify(tok)
            parts.append(tok if cls == "WORD" else cls)
    return " ".join(parts)


def group_lensd_ref(messages: Sequence[str]) -> list[str]:
    return [mask_line(m) for m in messages]