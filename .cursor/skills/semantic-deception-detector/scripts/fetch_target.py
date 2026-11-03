"""Materialize scan targets from URLs into a local temp directory.

Stdlib only. Fetched trees are never executed — read-only scan downstream.
"""
from __future__ import annotations

import io
import json
import re
import shutil
import tempfile
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from contextlib import contextmanager
from typing import Iterator
from urllib.parse import urlparse

MAX_ARCHIVE_BYTES = 50 * 1024 * 1024
MAX_RAW_BYTES = 2 * 1024 * 1024
USER_AGENT = "semantic-deception-detector/1.0.2 (+local CLI; read-only fetch)"

GITHUB_REPO_RE = re.compile(
    r"^https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$"
)
GITHUB_TREE_RE = re.compile(
    r"^https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/tree/(?P<ref>[^/]+)(?:/(?P<subpath>.+))?/?$"
)
GITHUB_BLOB_RE = re.compile(
    r"^https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/blob/(?P<ref>[^/]+)/(?P<subpath>.+?)/?$"
)
GIST_RE = re.compile(r"^https?://gist\.github\.com/(?:[^/]+/)?(?P<id>[a-f0-9]+)/?$")
PASTEBIN_PAGE_RE = re.compile(r"^https?://pastebin\.com/(?!raw/)(?P<id>\w+)/?$")
PASTEBIN_RAW_RE = re.compile(r"^https?://pastebin\.com/raw/(?P<id>\w+)/?$")


@dataclass(frozen=True)
class FetchSpec:
    kind: str
    url: str
    owner: str | None = None
    repo: str | None = None
    ref: str | None = None
    subpath: str | None = None
    gist_id: str | None = None


@dataclass
class MaterializedTarget:
    root: Path
    source_url: str
    source_kind: str
    _tmpdir: tempfile.TemporaryDirectory[str] | None = None

    def cleanup(self) -> None:
        if self._tmpdir is not None:
            self._tmpdir.cleanup()
            self._tmpdir = None


def _request(url: str, *, accept: str | None = None) -> bytes:
    headers = {"User-Agent": USER_AGENT}
    if accept:
        headers["Accept"] = accept
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read(MAX_ARCHIVE_BYTES + 1)
    if len(data) > MAX_ARCHIVE_BYTES:
        raise ValueError(f"Download too large (> {MAX_ARCHIVE_BYTES} bytes): {url}")
    return data


def _github_default_branch(owner: str, repo: str) -> str:
    url = f"https://api.github.com/repos/{owner}/{repo}"
    try:
        payload = json.loads(_request(url, accept="application/vnd.github+json").decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise ValueError(f"GitHub repo not found or unreachable: {owner}/{repo} ({exc.code})") from exc
    return payload.get("default_branch") or "main"


def parse_target(raw: str) -> FetchSpec | None:
    text = raw.strip().strip('"').strip("'")
    if not text.startswith(("http://", "https://")):
        return None

    m = GIST_RE.match(text)
    if m:
        return FetchSpec(kind="gist", url=text, gist_id=m.group("id"))

    m = PASTEBIN_PAGE_RE.match(text)
    if m:
        return FetchSpec(kind="pastebin_raw", url=f"https://pastebin.com/raw/{m.group('id')}")

    m = PASTEBIN_RAW_RE.match(text)
    if m:
        return FetchSpec(kind="pastebin_raw", url=text)

    m = GITHUB_TREE_RE.match(text)
    if m:
        return FetchSpec(
            kind="github_repo",
            url=text,
            owner=m.group("owner"),
            repo=m.group("repo"),
            ref=m.group("ref"),
            subpath=m.group("subpath"),
        )

    m = GITHUB_BLOB_RE.match(text)
    if m:
        return FetchSpec(
            kind="github_file",
            url=text,
            owner=m.group("owner"),
            repo=m.group("repo"),
            ref=m.group("ref"),
            subpath=m.group("subpath"),
        )

    m = GITHUB_REPO_RE.match(text)
    if m:
        return FetchSpec(
            kind="github_repo",
            url=text,
            owner=m.group("owner"),
            repo=m.group("repo"),
        )

    parsed = urlparse(text)
    if parsed.scheme in {"http", "https"}:
        return FetchSpec(kind="raw_url", url=text)
    return None


def _extract_github_zip(data: bytes, dest: Path) -> Path:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        names = [n for n in zf.namelist() if n and not n.endswith("/")]
        if not names:
            raise ValueError("GitHub archive zip was empty")
        top = names[0].split("/")[0]
        zf.extractall(dest)
        return dest / top


def _materialize_github_repo(spec: FetchSpec, dest: Path) -> Path:
    owner = spec.owner or ""
    repo = spec.repo or ""
    ref = spec.ref or _github_default_branch(owner, repo)
    archive_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{ref}.zip"
    try:
        data = _request(archive_url)
    except urllib.error.HTTPError:
        archive_url = f"https://github.com/{owner}/{repo}/archive/{ref}.zip"
        data = _request(archive_url)
    root = _extract_github_zip(data, dest)
    if spec.subpath:
        sub = root / Path(spec.subpath.replace("\\", "/"))
        if not sub.exists():
            raise ValueError(f"Subpath not found in archive: {spec.subpath}")
        return sub
    return root


def _materialize_github_file(spec: FetchSpec, dest: Path) -> Path:
    owner = spec.owner or ""
    repo = spec.repo or ""
    ref = spec.ref or "main"
    subpath = spec.subpath or ""
    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{subpath}"
    data = _request(raw_url)
    if len(data) > MAX_RAW_BYTES:
        raise ValueError(f"Single-file download too large: {raw_url}")
    name = Path(subpath).name or "download.txt"
    out = dest / name
    out.write_bytes(data)
    return dest


def _materialize_gist(spec: FetchSpec, dest: Path) -> Path:
    gist_id = spec.gist_id or ""
    api_url = f"https://api.github.com/gists/{gist_id}"
    payload = json.loads(_request(api_url, accept="application/vnd.github+json").decode("utf-8"))
    files = payload.get("files") or {}
    if not files:
        raise ValueError(f"Gist has no files: {gist_id}")
    for info in files.values():
        content = info.get("content")
        filename = info.get("filename") or "gist.txt"
        if content is None:
            raw_url = info.get("raw_url")
            if not raw_url:
                continue
            content = _request(raw_url).decode("utf-8", errors="replace")
        (dest / filename).write_text(content, encoding="utf-8", errors="replace")
    return dest


def _materialize_raw_url(spec: FetchSpec, dest: Path) -> Path:
    data = _request(spec.url)
    if len(data) > MAX_RAW_BYTES:
        raise ValueError(f"Raw URL too large: {spec.url}")
    name = Path(urlparse(spec.url).path).name or "download.txt"
    (dest / name).write_text(data.decode("utf-8", errors="replace"), encoding="utf-8", errors="replace")
    return dest


def materialize(spec: FetchSpec) -> MaterializedTarget:
    tmp = tempfile.TemporaryDirectory(prefix="semantic-scan-")
    dest = Path(tmp.name)
    kind = spec.kind
    if kind == "github_repo":
        root = _materialize_github_repo(spec, dest)
    elif kind == "github_file":
        root = _materialize_github_file(spec, dest)
    elif kind == "gist":
        root = _materialize_gist(spec, dest)
    elif kind in {"pastebin_raw", "raw_url"}:
        root = _materialize_raw_url(spec, dest)
    else:
        tmp.cleanup()
        raise ValueError(f"Unsupported fetch kind: {kind}")
    return MaterializedTarget(root=root.resolve(), source_url=spec.url, source_kind=kind, _tmpdir=tmp)


@contextmanager
def resolve_scan_root(target: str) -> Iterator[MaterializedTarget]:
    """Provide a scan root. Cleans up temp materialization on context exit."""
    text = target.strip().strip('"').strip("'")
    path = Path(text).expanduser()
    if path.exists():
        yield MaterializedTarget(root=path.resolve(), source_url=str(path.resolve()), source_kind="local")
        return

    spec = parse_target(text)
    if spec is None:
        raise ValueError(f"Not a local path or supported URL: {target}")

    mat = materialize(spec)
    try:
        yield mat
    finally:
        mat.cleanup()
