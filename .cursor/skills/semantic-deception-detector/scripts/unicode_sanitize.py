"""Shared Unicode / control-char sanitizer for PowerCore ingest.

Extracted from semantic-deception-detector TrapDoor tables so Threat Monitor
and skill wrappers import one library — do not fork ZW / bidi tables elsewhere.

Detect + strip + re-check. Homoglyph map is a curated Latin/Cyrillic set for
adversarial fixtures (not a full Unicode confusables database).
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

VERSION = "1.0.0"

# TrapDoor / agent-rule hiding class — owned here after B1 extract.
ZW_CHARS: dict[str, str] = {
    "\u200b": "ZERO WIDTH SPACE",
    "\u200c": "ZERO WIDTH NON-JOINER",
    "\u200d": "ZERO WIDTH JOINER",
    "\u2060": "WORD JOINER",
    "\ufeff": "BOM / ZERO WIDTH NO-BREAK SPACE",
    "\u180e": "MONGOLIAN VOWEL SEPARATOR",
    "\u202a": "LRE",
    "\u202b": "RLE",
    "\u202c": "PDF",
    "\u202d": "LRO",
    "\u202e": "RLO",
}

# CSI / OSC-ish ANSI — strip, never interpret as content.
_ANSI_RE = re.compile(
    r"(?:\x1b\[[0-9;?]*[ -/]*[@-~])|(?:\x1b\][^\x07\x1b]*(?:\x07|\x1b\\))|(?:\x1b[@-Z\\-_])"
)

# Curated lookalikes: Cyrillic → Latin (common bait).
_HOMOGLYPH_MAP: dict[str, str] = {
    "\u0430": "a",  # Cyrillic a
    "\u0435": "e",
    "\u043e": "o",
    "\u0440": "p",
    "\u0441": "c",
    "\u0445": "x",
    "\u0443": "y",
    "\u0456": "i",  # Ukrainian i
    "\u0410": "A",
    "\u0415": "E",
    "\u041e": "O",
    "\u0420": "P",
    "\u0421": "C",
    "\u0425": "X",
}


@dataclass
class HiddenHit:
    index: int
    line: int
    column: int
    codepoint: str
    label: str


@dataclass
class SanitizeResult:
    original: str
    cleaned: str
    stripped_zw: list[dict] = field(default_factory=list)
    stripped_ansi: bool = False
    homoglyph_swaps: list[dict] = field(default_factory=list)
    residual_hits: list[dict] = field(default_factory=list)
    clean: bool = True

    def to_dict(self) -> dict:
        return asdict(self)


def _line_col(text: str, index: int) -> tuple[int, int]:
    line_start = text.rfind("\n", 0, index)
    line = text[:index].count("\n") + 1
    col = index - (line_start + 1 if line_start >= 0 else 0)
    return line, col


def find_hidden_unicode(text: str, *, limit: int = 50) -> list[HiddenHit]:
    hits: list[HiddenHit] = []
    for i, ch in enumerate(text or ""):
        if ch in ZW_CHARS:
            line, col = _line_col(text, i)
            hits.append(
                HiddenHit(
                    index=i,
                    line=line,
                    column=col,
                    codepoint=f"U+{ord(ch):04X}",
                    label=ZW_CHARS[ch],
                )
            )
            if len(hits) >= limit:
                break
    return hits


def strip_hidden_unicode(text: str) -> tuple[str, list[dict]]:
    removed: list[dict] = []
    out: list[str] = []
    for i, ch in enumerate(text or ""):
        if ch in ZW_CHARS:
            line, col = _line_col(text, i)
            removed.append(
                {
                    "index": i,
                    "line": line,
                    "column": col,
                    "codepoint": f"U+{ord(ch):04X}",
                    "label": ZW_CHARS[ch],
                }
            )
        else:
            out.append(ch)
    return "".join(out), removed


def strip_ansi(text: str) -> tuple[str, bool]:
    if not text:
        return "", False
    cleaned, n = _ANSI_RE.subn("", text)
    return cleaned, n > 0


def normalize_homoglyphs(text: str) -> tuple[str, list[dict]]:
    swaps: list[dict] = []
    out: list[str] = []
    for i, ch in enumerate(text or ""):
        repl = _HOMOGLYPH_MAP.get(ch)
        if repl is not None:
            line, col = _line_col(text, i)
            swaps.append(
                {
                    "index": i,
                    "line": line,
                    "column": col,
                    "from": f"U+{ord(ch):04X}",
                    "to": repl,
                }
            )
            out.append(repl)
        else:
            out.append(ch)
    return "".join(out), swaps


def sanitize_external_text(text: str | None) -> SanitizeResult:
    """Strip ZW/bidi, ANSI, curated homoglyphs — then re-check for residual ZW."""
    original = text if isinstance(text, str) else ""
    step1, zw = strip_hidden_unicode(original)
    step2, ansi = strip_ansi(step1)
    step3, glyphs = normalize_homoglyphs(step2)
    residual = find_hidden_unicode(step3)
    residual_dicts = [
        {
            "index": h.index,
            "line": h.line,
            "column": h.column,
            "codepoint": h.codepoint,
            "label": h.label,
        }
        for h in residual
    ]
    return SanitizeResult(
        original=original,
        cleaned=step3,
        stripped_zw=zw,
        stripped_ansi=ansi,
        homoglyph_swaps=glyphs,
        residual_hits=residual_dicts,
        clean=len(residual_dicts) == 0,
    )
