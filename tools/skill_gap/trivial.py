"""Shared trivial-ack detector for endgates + rank_skills (one pattern, two callers)."""

from __future__ import annotations

import re

_MAX_PROMPT_LEN = 40
_ACK_WORDS = frozenset(
    {
        "thanks", "thank", "you", "ok", "okay", "cool", "got", "it", "yes", "no",
        "yep", "nope", "done", "great", "sure", "and", "ty", "thx", "👍",
    }
)
_TOKEN_RE = re.compile(r"[^\W_]+|👍", re.UNICODE)


def is_trivial_ack(prompt: str) -> bool:
    """True when the whole prompt is a short run of ack words ("okay, got it").

    A prompt with any non-ack word ("okay, run the deploy") is substantive.
    """
    p = (prompt or "").strip()
    if not p or len(p) > _MAX_PROMPT_LEN:
        return False
    tokens = [t.lower() for t in _TOKEN_RE.findall(p)]
    return bool(tokens) and all(t in _ACK_WORDS for t in tokens)
