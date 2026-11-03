#!/usr/bin/env python3
"""Offline password / passphrase forge (PowerCore secret-forge stub).

Uses the stdlib ``secrets`` module only. Prints ``<secret>\\t<bits>`` per line.
Never writes secrets to disk. Never logs secrets.

Wordlist: ``../data/wordlist_eff_stub.txt`` (tiny stub for CI/dev). Replace with
the full EFF long list before calling passphrase entropy "production-honest."
"""
from __future__ import annotations

import argparse
import math
import secrets
import sys
from pathlib import Path

VERSION = "0.1.0-stub"

LOOKALIKE = set("Il1|O0o")
LOWER = "abcdefghijklmnopqrstuvwxyz"
UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITS = "0123456789"
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.?/"

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_WORDLIST = DATA_DIR / "wordlist_eff_stub.txt"


def _alphabet(
    *,
    lower: bool,
    upper: bool,
    number: bool,
    symbol: bool,
    no_lookalike: bool,
) -> str:
    chars = ""
    if lower:
        chars += LOWER
    if upper:
        chars += UPPER
    if number:
        chars += DIGITS
    if symbol:
        chars += SYMBOLS
    if no_lookalike:
        chars = "".join(c for c in chars if c not in LOOKALIKE)
    # de-dupe preserve order
    seen: set[str] = set()
    out: list[str] = []
    for c in chars:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return "".join(out)


def _bits(alphabet_or_list_size: int, length: int) -> float:
    if alphabet_or_list_size < 2:
        raise ValueError("alphabet/wordlist size must be >= 2")
    return length * math.log2(alphabet_or_list_size)


def forge_password(
    *,
    length: int,
    count: int,
    lower: bool,
    upper: bool,
    number: bool,
    symbol: bool,
    no_lookalike: bool,
) -> list[tuple[str, float]]:
    alpha = _alphabet(
        lower=lower,
        upper=upper,
        number=number,
        symbol=symbol,
        no_lookalike=no_lookalike,
    )
    if len(alpha) < 2:
        raise SystemExit("error: alphabet size < 2 after flags / lookalike strip")
    bits = _bits(len(alpha), length)
    rows: list[tuple[str, float]] = []
    for _ in range(count):
        secret = "".join(secrets.choice(alpha) for _ in range(length))
        rows.append((secret, bits))
    return rows


def _load_wordlist(path: Path) -> list[str]:
    if not path.is_file():
        raise SystemExit(f"error: wordlist not found: {path}")
    words = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    if len(words) < 2:
        raise SystemExit("error: wordlist size must be >= 2")
    return words


def forge_passphrase(
    *,
    words: int,
    count: int,
    wordlist_path: Path,
) -> list[tuple[str, float]]:
    wl = _load_wordlist(wordlist_path)
    bits = _bits(len(wl), words)
    rows: list[tuple[str, float]] = []
    for _ in range(count):
        secret = "-".join(secrets.choice(wl) for _ in range(words))
        rows.append((secret, bits))
    return rows


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="secret_forge",
        description="Offline password/passphrase forge — print only, secrets module.",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    p.add_argument(
        "--mode",
        choices=("password", "passphrase"),
        default="password",
        help="generation mode (default: password)",
    )
    p.add_argument("--count", type=int, default=1, help="how many secrets (1-50)")
    p.add_argument(
        "--length",
        type=int,
        default=16,
        help="password length in chars (password mode)",
    )
    p.add_argument(
        "--words",
        type=int,
        default=5,
        help="passphrase word count (passphrase mode)",
    )
    p.add_argument("--no-lower", action="store_true")
    p.add_argument("--no-upper", action="store_true")
    p.add_argument("--no-number", action="store_true")
    p.add_argument("--no-symbol", action="store_true")
    p.add_argument(
        "--no-lookalike",
        action="store_true",
        help=f"strip look-alikes {''.join(sorted(LOOKALIKE))}",
    )
    p.add_argument(
        "--wordlist",
        type=Path,
        default=DEFAULT_WORDLIST,
        help="passphrase wordlist path (default: data/wordlist_eff_stub.txt)",
    )
    p.add_argument(
        "--meta",
        action="store_true",
        help="print footer meta (no secrets) to stderr",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if not 1 <= args.count <= 50:
        print("error: --count must be 1..50", file=sys.stderr)
        return 2

    if args.mode == "password":
        rows = forge_password(
            length=args.length,
            count=args.count,
            lower=not args.no_lower,
            upper=not args.no_upper,
            number=not args.no_number,
            symbol=not args.no_symbol,
            no_lookalike=args.no_lookalike,
        )
        alpha = _alphabet(
            lower=not args.no_lower,
            upper=not args.no_upper,
            number=not args.no_number,
            symbol=not args.no_symbol,
            no_lookalike=args.no_lookalike,
        )
        if args.meta:
            print(
                f"# forge meta mode=password count={args.count} "
                f"length={args.length} alphabet_size={len(alpha)}",
                file=sys.stderr,
            )
    else:
        rows = forge_passphrase(
            words=args.words,
            count=args.count,
            wordlist_path=args.wordlist,
        )
        wl = _load_wordlist(args.wordlist)
        if args.meta:
            print(
                f"# forge meta mode=passphrase count={args.count} "
                f"words={args.words} wordlist_size={len(wl)} "
                f"wordlist={args.wordlist}",
                file=sys.stderr,
            )

    for secret, bits in rows:
        # bits printed with one decimal; no prose between secrets
        print(f"{secret}\t{bits:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
