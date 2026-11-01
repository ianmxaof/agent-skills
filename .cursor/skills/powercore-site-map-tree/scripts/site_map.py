#!/usr/bin/env python3
"""Site / repo map tree for Hub Vincent (/run site-map).

v1.1 — origin-rooted full map: robots/sitemap + BFS, Mermaid, evidence-tagged
flow/nav read, sibling compose hints. Inventory + IA speculation only —
not trust, docs-vs-code, or aesthetics. Stdlib only. Never executes fetched code.
"""
from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from collections import deque
from dataclasses import asdict, dataclass, field
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse

VERSION = "1.1.0"
UA = "PowerCore-SiteMap/1.1 (+local; read-only map)"

# Lite = v1.0 Hub-scannable defaults; full = whole-site spine
MAX_NODES_LITE = 80
MAX_DEPTH_LITE = 3
MAX_NODES_FULL = 250
MAX_DEPTH_FULL = 4
MAX_HTML_FETCHES = 36  # Hub must stay snappy; sitemap fills the rest
MAX_SITEMAP_BYTES = 4_000_000
MAX_SITEMAP_FILES = 8
MAX_HTML = 1_500_000
MAX_TREE_JSON = 8_000_000
MAX_MERMAID_NODES = 60
MAX_FLOW_BULLETS = 8
MAX_COMPOSE = 5
SKIP_PATH_EXT = re.compile(
    r"\.(?:png|jpe?g|gif|webp|svg|ico|css|js|mjs|map|woff2?|ttf|eot|pdf|zip|gz|mp4|webm|mp3|xml)$",
    re.I,
)

GITHUB_REPO_RE = re.compile(
    r"^https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$"
)
GITHUB_TREE_RE = re.compile(
    r"^https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/tree/(?P<ref>[^/]+)(?:/(?P<subpath>.+))?/?$"
)
HREF_RE = re.compile(r"""<a\b([^>]*)\bhref\s*=\s*["']([^"']+)["']""", re.I)
NAVISH_ATTR_RE = re.compile(
    r"""(?:id|class|role|aria-label)\s*=\s*["'][^"']*\b(?:nav|menu|header|footer|sidebar|breadcrumb)\b""",
    re.I,
)
NAV_REGION_RE = re.compile(
    r"""<(?:nav|header|footer)\b[^>]*>(.*?)</(?:nav|header|footer)>""",
    re.I | re.S,
)
SKIP_SCHEME = re.compile(r"^(javascript:|mailto:|tel:|data:|#)", re.I)
SKIP_REPO_PARTS = frozenset(
    {
        "node_modules",
        ".git",
        "dist",
        "build",
        "vendor",
        "__pycache__",
        ".venv",
        "venv",
        "third_party",
        "third-party",
    }
)

# Path segment → product-intent hint (only cited when path exists)
INTENT_HINTS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^/(pricing|plans|buy|checkout|cart)(/|$)", re.I), "monetization / paywall surface"),
    (re.compile(r"^/(docs|documentation|api|reference|developers?)(/|$)", re.I), "docs / developer funnel"),
    (re.compile(r"^/(blog|news|articles?|changelog)(/|$)", re.I), "content / SEO flywheel"),
    (re.compile(r"^/(login|signin|signup|register|auth)(/|$)", re.I), "auth gate"),
    (re.compile(r"^/(app|dashboard|console|overview|account|settings)(/|$)", re.I), "product / logged-in app"),
    (re.compile(r"^/(about|company|team|careers)(/|$)", re.I), "trust / company story"),
    (re.compile(r"^/(contact|support|help|faq)(/|$)", re.I), "support / recovery"),
    (re.compile(r"^/(privacy|terms|legal|cookies?)(/|$)", re.I), "legal / compliance footer lane"),
]


@dataclass
class Report:
    ok: bool
    version: str
    mode: str
    root: str
    tree_lines: list[str] = field(default_factory=list)
    node_count: int = 0
    capped: bool = False
    max_nodes: int = MAX_NODES_LITE
    max_depth: int = MAX_DEPTH_LITE
    notes: list[str] = field(default_factory=list)
    error: str | None = None
    # v1.1 spine
    origin: str = ""
    profile: str = "lite"  # lite | full
    sources: list[str] = field(default_factory=list)
    mermaid: str = ""
    flow_lines: list[str] = field(default_factory=list)
    compose: list[str] = field(default_factory=list)
    nav_paths: list[str] = field(default_factory=list)
    sitemap_count: int = 0
    path_order: list[str] = field(default_factory=list)


def _request(url: str, *, accept: str | None = None, timeout: float = 30, max_bytes: int = MAX_HTML) -> bytes:
    headers = {"User-Agent": UA, "Accept": accept or "*/*"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
        data = resp.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError(f"Response too large (> {max_bytes} bytes)")
    return data


def _normalize_url(base: str, href: str) -> str | None:
    href = (href or "").strip()
    if not href or SKIP_SCHEME.search(href):
        return None
    abs_url = urljoin(base, href)
    try:
        p = urlparse(abs_url)
    except Exception:
        return None
    if p.scheme not in {"http", "https"}:
        return None
    path = p.path or "/"
    # Drop default index noise lightly
    clean = urlunparse((p.scheme, p.netloc.lower(), path, "", "", ""))
    return clean


def _origin_of(url: str) -> str:
    p = urlparse(url)
    return urlunparse((p.scheme, p.netloc.lower(), "", "", "", ""))


def _path_of(url: str) -> str:
    return urlparse(url).path or "/"


def _same_origin(a: str, b: str) -> bool:
    try:
        pa, pb = urlparse(a), urlparse(b)
        return pa.scheme == pb.scheme and pa.netloc.lower() == pb.netloc.lower()
    except Exception:
        return False


def _local(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[-1].lower()
    return tag.lower()


def fetch_robots_sitemaps(origin: str) -> tuple[list[str], dict]:
    """Return sitemap URLs from robots.txt + skim meta."""
    robots_url = origin.rstrip("/") + "/robots.txt"
    meta: dict = {"ok": False, "url": robots_url}
    try:
        text = _request(robots_url, accept="text/plain,*/*", timeout=12, max_bytes=200_000).decode(
            "utf-8", errors="replace"
        )
    except Exception as exc:  # noqa: BLE001
        meta["error"] = f"{type(exc).__name__}: {exc}"
        return [], meta
    sitemaps: list[str] = []
    for ln in text.splitlines():
        s = ln.strip()
        if s.lower().startswith("sitemap:"):
            u = s.split(":", 1)[1].strip()
            if u.startswith("http"):
                sitemaps.append(u)
    meta.update({"ok": True, "sitemap_count": len(sitemaps), "sitemaps": sitemaps[:8]})
    return sitemaps, meta


def _abs_loc(loc: str, *, base: str) -> str | None:
    loc = (loc or "").strip()
    if not loc:
        return None
    if loc.startswith("http"):
        return loc
    return _normalize_url(base, loc)


def parse_sitemap_xml(raw: bytes, *, base: str) -> tuple[list[str], list[str]]:
    """Return (page_urls, child_sitemap_urls) from a sitemap or sitemapindex."""
    pages: list[str] = []
    children: list[str] = []
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return [], []
    kind = _local(root.tag)
    if kind == "sitemapindex":
        for el in root:
            if _local(el.tag) != "sitemap":
                continue
            for c in el:
                if _local(c.tag) == "loc" and c.text:
                    loc = _abs_loc(c.text, base=base)
                    if loc:
                        children.append(loc)
        return pages, children
    # urlset or unknown — treat <url><loc> as pages
    for el in root:
        if _local(el.tag) != "url":
            continue
        for c in el:
            if _local(c.tag) == "loc" and c.text:
                loc = _abs_loc(c.text, base=base)
                if loc:
                    pages.append(loc)
    return pages, children


def collect_sitemap_urls(origin: str, seed_sitemaps: list[str], *, limit: int) -> tuple[list[str], list[str]]:
    """Fetch sitemap(s); return (urls, notes)."""
    candidates: list[str] = []
    for u in seed_sitemaps:
        if u not in candidates:
            candidates.append(u)
    for guess in ("/sitemap.xml", "/sitemap_index.xml", "/sitemap-index.xml"):
        g = origin.rstrip("/") + guess
        if g not in candidates:
            candidates.append(g)

    pages: list[str] = []
    notes: list[str] = []
    fetched = 0
    queue = deque(candidates)
    seen_sm: set[str] = set()

    while queue and fetched < MAX_SITEMAP_FILES and len(pages) < limit:
        sm = queue.popleft()
        if sm in seen_sm:
            continue
        seen_sm.add(sm)
        try:
            raw = _request(
                sm,
                accept="application/xml,text/xml,*/*",
                timeout=20,
                max_bytes=MAX_SITEMAP_BYTES,
            )
            fetched += 1
        except Exception:
            continue
        page_batch, child_sms = parse_sitemap_xml(raw, base=sm)
        if child_sms and not page_batch:
            notes.append(f"Sitemap index: {sm} → {len(child_sms)} child map(s).")
            for c in child_sms:
                if c not in seen_sm and _same_origin(origin, c):
                    queue.append(c)
            continue
        for p in page_batch:
            if not _same_origin(origin, p):
                continue
            if p not in pages:
                pages.append(p)
            if len(pages) >= limit:
                break
        if page_batch:
            notes.append(f"Sitemap {sm}: +{len(page_batch)} URL(s).")

    return pages[:limit], notes


def extract_links(page_url: str, html: str) -> tuple[list[str], list[str]]:
    """All hrefs + chrome links (<nav>/<header>/<footer> regions or navish <a> attrs)."""
    html = html or ""
    all_links: list[str] = []
    nav_links: list[str] = []
    nav_href_blob = " ".join(m.group(1) for m in NAV_REGION_RE.finditer(html))
    region_hrefs: set[str] = set()
    for m in HREF_RE.finditer(nav_href_blob):
        nxt = _normalize_url(page_url, html_lib.unescape(m.group(2) or ""))
        if nxt:
            region_hrefs.add(nxt)
    for m in HREF_RE.finditer(html):
        attrs, href = m.group(1) or "", m.group(2) or ""
        nxt = _normalize_url(page_url, html_lib.unescape(href))
        if not nxt:
            continue
        all_links.append(nxt)
        if nxt in region_hrefs or NAVISH_ATTR_RE.search(attrs):
            nav_links.append(nxt)
    return all_links, nav_links


def _paths_to_tree_lines(paths: list[str], *, line_cap: int) -> list[str]:
    root: dict = {}
    for raw in paths:
        parts = [p for p in (raw or "/").strip("/").split("/") if p]
        if not parts:
            root.setdefault("", {})
            continue
        cur = root
        for part in parts:
            cur = cur.setdefault(part, {})

    lines: list[str] = ["/"]

    def walk(node: dict, indent: int) -> None:
        for name in sorted(node.keys(), key=lambda s: s.lower()):
            if name == "":
                continue
            if len(lines) >= line_cap:
                return
            prefix = "  " * indent
            kids = node[name]
            is_dir = bool(kids)
            lines.append(f"{prefix}- {name}{'/' if is_dir else ''}")
            if kids:
                walk(kids, indent + 1)

    walk(root, 1)
    return lines[:line_cap]


def _mermaid_id(path: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", path.strip("/") or "root")
    if not s or s[0].isdigit():
        s = "n_" + s
    return s[:48]


def paths_to_mermaid(paths: list[str], *, cap: int = MAX_MERMAID_NODES) -> str:
    """Mermaid graph TD from URL paths — visual sitemap."""
    uniq: list[str] = []
    seen: set[str] = set()
    for p in paths:
        path = p if p.startswith("/") else "/" + p
        if path not in seen:
            seen.add(path)
            uniq.append(path)
        if len(uniq) >= cap:
            break

    lines = ["graph TD", '  root["/"]']
    declared = {"/": "root"}

    def ensure(path: str) -> str:
        if path in declared:
            return declared[path]
        nid = _mermaid_id(path)
        # avoid collisions
        base = nid
        i = 2
        while nid in declared.values():
            nid = f"{base}_{i}"
            i += 1
        label = path if len(path) <= 40 else path[:37] + "…"
        label = label.replace('"', "'")
        lines.append(f'  {nid}["{label}"]')
        declared[path] = nid
        return nid

    for path in uniq:
        if path == "/":
            continue
        parts = [p for p in path.strip("/").split("/") if p]
        parent = "/"
        cur = ""
        for part in parts:
            cur = f"{cur}/{part}"
            pid = ensure(parent) if parent == "/" else ensure(parent)
            cid = ensure(cur)
            edge = f"  {pid} --> {cid}"
            if edge not in lines:
                lines.append(edge)
            parent = cur

    if len(uniq) >= cap:
        lines.append(f"  %% capped at {cap} nodes")
    return "\n".join(lines)


def build_flow_lines(
    paths: list[str],
    *,
    nav_paths: list[str],
    sources: list[str],
    tab_path: str,
) -> list[str]:
    """Evidence-tagged IA / nav strategy bullets — no free-floating speculation."""
    bullets: list[str] = []
    path_set = {p if p.startswith("/") else "/" + p for p in paths}
    if "/" not in path_set and paths:
        path_set.add("/")

    top = sorted(
        {
            "/" + p.strip("/").split("/")[0]
            for p in path_set
            if p.strip("/") and "/" not in p.strip("/")
        }
        | {
            "/" + p.strip("/").split("/")[0]
            for p in path_set
            if p.strip("/")
        }
    )
    top = sorted({t for t in top if t != "/"})

    bullets.append(
        f"Inventory size **{len(path_set)}** path(s); sources: {', '.join(sources) or 'none'} "
        f"· ev: path_count={len(path_set)}"
    )
    if tab_path and tab_path not in ("/", ""):
        bullets.append(
            f"Tab was deep at `{tab_path}` — map rooted at origin, not the tab alone "
            f"· ev: tab_path={tab_path}"
        )

    if top:
        show = ", ".join(f"`{t}`" for t in top[:12])
        more = f" (+{len(top) - 12})" if len(top) > 12 else ""
        bullets.append(f"Top-level IA branches: {show}{more} · ev: first path segment")

    nav_set = sorted({_path_of(u) if u.startswith("http") else u for u in nav_paths})
    if nav_set:
        show = ", ".join(f"`{p}`" for p in nav_set[:10])
        bullets.append(
            f"Primary chrome (nav/header/footer-ish `<a>`) surfaces: {show} "
            f"· ev: navish attrs on anchors"
        )
        deep_only = [p for p in sorted(path_set) if p not in nav_set and p != "/"]
        if deep_only and len(deep_only) > len(nav_set):
            bullets.append(
                f"**{len(deep_only)}** path(s) exist outside primary chrome — "
                f"likely footer, sitemap, or app-router only · ev: set(paths)−set(nav)"
            )
    else:
        bullets.append(
            "No nav/header/footer-tagged anchors detected in fetched HTML — "
            "placement read is weak (SPA shell or CSS-only nav) · ev: nav_paths=[]"
        )

    seen_labels: set[str] = set()
    for path in sorted(path_set, key=lambda p: (p.count("/"), len(p), p)):
        for rx, label in INTENT_HINTS:
            if label in seen_labels:
                continue
            if rx.search(path):
                seen_labels.add(label)
                bullets.append(f"Strategy signal: {label} via `{path}` · ev: path pattern")
                break
        if len(seen_labels) >= 5:
            break

    if len(path_set) <= 2 and "sitemap" not in sources:
        bullets.append(
            "Very thin map — likely client-routed SPA or login wall; "
            "enrich with BeatAPI `web_map` or Firecrawl `firecrawl_map` on the origin "
            "· ev: node_count≤2 ∧ no sitemap"
        )

    return bullets[:MAX_FLOW_BULLETS]


def build_compose(mode: str, *, thin: bool) -> list[str]:
    rows = [
        "`/run feature-scan` — features + stack (+ robots skim); shape→stack hop",
        "`/run website-clone` — aesthetics harvest after IA is clear",
    ]
    if mode == "repo":
        rows.insert(0, "`/run repo-trust` — supply-chain / smell on this GitHub tree")
        rows.insert(1, "`/run semantic-scan` — docs↔code when README claims matter")
    else:
        rows.append("`/run repo-trust` — only if a public GitHub mirror is the real product surface")
    if thin:
        rows.append(
            "Thin map: dump BeatAPI/Firecrawl URLs into `--merge-file` "
            "(BeatAPI web_map is paid-tier; Firecrawl map needs auth)"
        )
    rows.append("Inventory ≠ trust — do not treat this card as a security verdict")
    return rows[:MAX_COMPOSE]


def map_web(
    url: str,
    *,
    max_nodes: int = MAX_NODES_FULL,
    max_depth: int = MAX_DEPTH_FULL,
    profile: str = "full",
) -> Report:
    root_in = _normalize_url(url, url) or url
    origin = _origin_of(root_in)
    origin_home = origin.rstrip("/") + "/"
    tab_path = _path_of(root_in)
    notes: list[str] = []
    sources: list[str] = []

    html_fetch_budget = MAX_HTML_FETCHES if profile == "full" else max(12, min(max_nodes, 24))
    if profile == "full":
        notes.append(
            f"Full map: origin-rooted, robots/sitemap + BFS depth≤{max_depth}, "
            f"max {max_nodes} nodes, ≤{html_fetch_budget} HTML fetches."
        )
    else:
        notes.append(
            f"Lite map: same-origin BFS depth≤{max_depth}, max {max_nodes} nodes, "
            f"≤{html_fetch_budget} HTML fetches."
        )

    # --- sitemap spine (inventory without per-URL HTML) ---
    sitemap_pages: list[str] = []
    if profile == "full":
        robots_sms, robots_meta = fetch_robots_sitemaps(origin)
        if robots_meta.get("ok"):
            sources.append("robots")
            notes.append(
                f"robots.txt: {robots_meta.get('sitemap_count', 0)} Sitemap: line(s)."
            )
        else:
            notes.append(f"robots.txt skim failed ({robots_meta.get('error', 'n/a')}).")
        sitemap_pages, sm_notes = collect_sitemap_urls(
            origin, robots_sms, limit=max_nodes
        )
        notes.extend(sm_notes)
        if sitemap_pages:
            sources.append("sitemap")

    def _crawlable(u: str) -> bool:
        if not _same_origin(origin, u):
            return False
        path = _path_of(u)
        if SKIP_PATH_EXT.search(path):
            return False
        return True

    # HTML expansion seeds only (not every sitemap URL)
    expand_seeds: list[str] = []
    seed_raw = (origin_home, root_in) if profile == "full" else (root_in,)
    for u in seed_raw:
        nu = _normalize_url(u, u) or u
        if nu not in expand_seeds and _crawlable(nu):
            expand_seeds.append(nu)

    order_urls: list[str] = []
    seen: set[str] = set()
    nav_urls: list[str] = []
    html_fetches = 0
    q: deque[tuple[str, int]] = deque()

    def remember(u: str) -> bool:
        if u in seen or len(seen) >= max_nodes or not _crawlable(u):
            return False
        seen.add(u)
        order_urls.append(u)
        return True

    def fetch_html(u: str) -> str:
        nonlocal html_fetches
        if html_fetches >= html_fetch_budget:
            return ""
        try:
            html_fetches += 1
            return _request(
                u, accept="text/html,application/xhtml+xml", timeout=12
            ).decode("utf-8", errors="replace")
        except Exception:
            return ""

    for su in expand_seeds:
        if remember(su):
            q.append((su, 0))

    # Sitemap URLs enrich inventory without burning the HTML budget
    for sp in sitemap_pages:
        remember(sp)

    if not seen:
        return Report(
            ok=False,
            version=VERSION,
            mode="web",
            root=root_in,
            origin=origin,
            profile=profile,
            error="fetch failed: no reachable origin/tab HTML and no sitemap URLs",
            notes=notes,
            compose=build_compose("web", thin=True),
        )

    sources.append("bfs")

    while q:
        page, depth = q.popleft()
        html = fetch_html(page)
        if not html:
            continue
        all_links, nav_links = extract_links(page, html)
        for n in nav_links:
            if _crawlable(n) and n not in nav_urls:
                nav_urls.append(n)
        if depth >= max_depth:
            continue
        for nxt in all_links:
            if not remember(nxt):
                continue
            # Only queue for further HTML expansion while budget remains
            if depth + 1 < max_depth and html_fetches < html_fetch_budget:
                q.append((nxt, depth + 1))

    notes.append(f"HTML pages fetched for link expansion: {html_fetches}/{html_fetch_budget}.")

    paths = [_path_of(u) for u in order_urls]
    path_order: list[str] = []
    path_seen: set[str] = set()
    for p in paths:
        if p not in path_seen:
            path_seen.add(p)
            path_order.append(p)

    capped = len(seen) >= max_nodes
    tree = _paths_to_tree_lines(path_order, line_cap=max_nodes + 10)
    mermaid = paths_to_mermaid(path_order, cap=min(MAX_MERMAID_NODES, max_nodes))
    nav_paths = sorted({_path_of(u) for u in nav_urls})
    flow = build_flow_lines(
        path_order,
        nav_paths=nav_paths,
        sources=sources,
        tab_path=tab_path,
    )
    thin = len(path_order) <= 2
    compose = build_compose("web", thin=thin)

    notes.append("Inventory + evidence-tagged IA read — not a trust or docs-vs-code scan.")
    notes.append(
        "Thin-map enrich: pass BeatAPI/Firecrawl URL lists via --merge-urls "
        "(BeatAPI web_map is paid-tier; Firecrawl map needs auth)."
    )

    return Report(
        ok=True,
        version=VERSION,
        mode="web",
        root=origin_home if profile == "full" else root_in,
        origin=origin,
        profile=profile,
        sources=sources,
        tree_lines=tree,
        node_count=len(path_order),
        capped=capped,
        max_nodes=max_nodes,
        max_depth=max_depth,
        mermaid=mermaid,
        flow_lines=flow,
        compose=compose,
        nav_paths=nav_paths,
        sitemap_count=len(sitemap_pages),
        path_order=path_order,
        notes=notes,
    )


def _github_default_branch(owner: str, repo: str) -> str:
    url = f"https://api.github.com/repos/{owner}/{repo}"
    payload = json.loads(
        _request(url, accept="application/vnd.github+json", max_bytes=512_000).decode("utf-8")
    )
    return payload.get("default_branch") or "main"


def map_github(
    owner: str,
    repo: str,
    *,
    ref: str | None = None,
    subpath: str | None = None,
    max_nodes: int = MAX_NODES_LITE,
) -> Report:
    notes = [f"GitHub Trees API — dirs + files, capped at {max_nodes} nodes."]
    try:
        ref = ref or _github_default_branch(owner, repo)
        tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{ref}?recursive=1"
        payload = json.loads(
            _request(
                tree_url, accept="application/vnd.github+json", timeout=45, max_bytes=MAX_TREE_JSON
            ).decode("utf-8")
        )
    except Exception as exc:  # noqa: BLE001
        return Report(
            ok=False,
            version=VERSION,
            mode="repo",
            root=f"https://github.com/{owner}/{repo}",
            error=f"github tree failed: {type(exc).__name__}: {exc}",
            notes=notes,
            compose=build_compose("repo", thin=False),
        )

    prefix = (subpath or "").replace("\\", "/").strip("/")
    entries = payload.get("tree") or []
    paths: list[str] = []
    for ent in entries:
        path = str(ent.get("path") or "").replace("\\", "/")
        if not path:
            continue
        if prefix and not (path == prefix or path.startswith(prefix + "/")):
            continue
        rel = path[len(prefix) + 1 :] if prefix and path.startswith(prefix + "/") else path
        if prefix and path == prefix:
            continue
        parts = rel.lower().split("/")
        if any(p in SKIP_REPO_PARTS for p in parts):
            continue
        if ent.get("type") == "tree":
            paths.append(rel.rstrip("/") + "/")
        else:
            if rel.count("/") > 4:
                continue
            paths.append(rel)
        if len(paths) >= max_nodes:
            break

    paths.sort(key=lambda p: (p.count("/"), p.lower()))
    capped = len(paths) >= max_nodes
    norm = []
    for p in paths:
        if p.endswith("/"):
            norm.append("/" + p.rstrip("/"))
        else:
            norm.append("/" + p)
    lines = _paths_to_tree_lines(norm, line_cap=max_nodes + 10)
    root = f"https://github.com/{owner}/{repo}/tree/{ref}" + (f"/{prefix}" if prefix else "")
    mermaid = paths_to_mermaid(norm, cap=min(MAX_MERMAID_NODES, max_nodes))
    flow = [
        f"Repo tree inventory **{len(paths)}** path(s) under `{prefix or '/'}` · ev: GitHub Trees API",
        "Compose with repo-trust / semantic-scan for smell + docs↔code — this card is shape only.",
    ]
    return Report(
        ok=True,
        version=VERSION,
        mode="repo",
        root=root,
        origin=f"https://github.com/{owner}/{repo}",
        profile="repo",
        sources=["github_trees"],
        tree_lines=lines,
        node_count=len(paths),
        capped=capped,
        max_nodes=max_nodes,
        max_depth=MAX_DEPTH_LITE,
        mermaid=mermaid,
        flow_lines=flow,
        compose=build_compose("repo", thin=False),
        notes=notes,
    )


def merge_extra_urls(report: Report, extra: list[str], *, label: str = "merge") -> Report:
    """Union extra same-origin URLs into an existing web report (thin-map enrich)."""
    if not report.ok or report.mode != "web" or not extra:
        return report
    origin = report.origin or _origin_of(report.root)
    paths: list[str] = list(report.path_order or [])
    seen: set[str] = set(paths)
    if not paths:
        paths = ["/"]
        seen.add("/")

    added = 0
    for raw in extra:
        raw = (raw or "").strip()
        if not raw:
            continue
        nu = _normalize_url(origin + "/" if origin else raw, raw) if raw.startswith("/") else (
            _normalize_url(raw, raw) or raw
        )
        if not nu or not str(nu).startswith("http"):
            continue
        if origin and not _same_origin(origin, nu):
            continue
        p = _path_of(nu)
        if p in seen:
            continue
        seen.add(p)
        paths.append(p)
        added += 1

    max_nodes = report.max_nodes or MAX_NODES_FULL
    if len(paths) > max_nodes:
        paths = paths[:max_nodes]
        report.capped = True

    report.path_order = paths
    report.tree_lines = _paths_to_tree_lines(paths, line_cap=max_nodes + 10)
    report.node_count = len(paths)
    report.mermaid = paths_to_mermaid(paths, cap=min(MAX_MERMAID_NODES, max_nodes))
    if label not in report.sources:
        report.sources = list(report.sources) + [label]
    report.flow_lines = build_flow_lines(
        paths,
        nav_paths=report.nav_paths,
        sources=report.sources,
        tab_path=_path_of(report.root) if report.root else "/",
    )
    thin = len(paths) <= 2
    report.compose = build_compose("web", thin=thin)
    report.notes = list(report.notes) + [
        f"Merged +{added} URL(s) via --merge-urls ({label}; {len(extra)} supplied).",
    ]
    if thin:
        report.notes.append(
            "Still thin after merge — BeatAPI web_map needs paid credits; "
            "Firecrawl firecrawl_map needs auth; or pass a fuller --merge-urls list."
        )
    return report


def detect_and_map(
    url: str,
    *,
    max_nodes: int | None = None,
    max_depth: int | None = None,
    profile: str = "full",
) -> Report:
    text = (url or "").strip().strip('"').strip("'")
    if profile == "lite":
        nodes = max_nodes if max_nodes is not None else MAX_NODES_LITE
        depth = max_depth if max_depth is not None else MAX_DEPTH_LITE
    else:
        nodes = max_nodes if max_nodes is not None else MAX_NODES_FULL
        depth = max_depth if max_depth is not None else MAX_DEPTH_FULL

    m = GITHUB_TREE_RE.match(text)
    if m:
        return map_github(
            m.group("owner"),
            m.group("repo"),
            ref=m.group("ref"),
            subpath=m.group("subpath"),
            max_nodes=nodes,
        )
    m = GITHUB_REPO_RE.match(text)
    if m:
        return map_github(m.group("owner"), m.group("repo"), max_nodes=nodes)
    if text.startswith(("http://", "https://")):
        return map_web(text, max_nodes=nodes, max_depth=depth, profile=profile)
    return Report(
        ok=False,
        version=VERSION,
        mode="unknown",
        root=text,
        error="Need an http(s) URL (site or GitHub repo/tree).",
    )


def format_markdown(report: Report) -> str:
    """Hub-parity card (also used for non-JSON CLI)."""
    if not report.ok:
        return f"# Site map\n\n## Couldn’t map\n\n{report.error or 'unknown error'}\n"
    mode = "GitHub repo tree" if report.mode == "repo" else "Site link tree"
    lines = [
        "# Site map",
        "",
        "## Root",
        "",
        report.root or "—",
        "",
    ]
    if report.origin and report.origin.rstrip("/") != (report.root or "").rstrip("/"):
        lines.extend(["## Origin", "", report.origin, ""])
    lines.extend(
        [
            "## Tree",
            "",
            f"_{mode}_ · {report.node_count} nodes"
            + (" (capped)" if report.capped else "")
            + (f" · profile={report.profile}" if report.profile else "")
            + (f" · sources={','.join(report.sources)}" if report.sources else ""),
            "",
        ]
    )
    if report.tree_lines:
        lines.extend(report.tree_lines)
    else:
        lines.append("_Empty tree._")
    if report.mermaid:
        lines.extend(["", "## Visual", "", "```mermaid", report.mermaid, "```"])
    if report.flow_lines:
        lines.extend(["", "## Flow / nav", ""])
        for b in report.flow_lines:
            lines.append(f"- {b}")
    if report.compose:
        lines.extend(["", "## Compose next", ""])
        for c in report.compose:
            lines.append(f"- {c}")
    lines.extend(["", "## Notes", ""])
    for n in report.notes:
        lines.append(f"- {n}")
    if not any("Inventory" in n for n in report.notes):
        lines.append("- Inventory only — not a trust or docs-vs-code scan.")
    return "\n".join(lines) + "\n"


def _self_test() -> int:
    lines = _paths_to_tree_lines(["/", "/docs", "/docs/api", "/about"], line_cap=40)
    assert any("docs" in ln for ln in lines), lines
    assert any("api" in ln for ln in lines), lines

    mm = paths_to_mermaid(["/", "/docs", "/docs/api", "/pricing"], cap=20)
    assert "graph TD" in mm and "pricing" in mm.lower()

    sample = b"""<?xml version="1.0"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
      <url><loc>https://example.com/</loc></url>
      <url><loc>https://example.com/docs</loc></url>
      <url><loc>https://example.com/pricing</loc></url>
    </urlset>"""
    pages, kids = parse_sitemap_xml(sample, base="https://example.com/sitemap.xml")
    assert not kids
    assert len(pages) == 3

    idx = b"""<?xml version="1.0"?>
    <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
      <sitemap><loc>https://example.com/sitemap-pages.xml</loc></sitemap>
    </sitemapindex>"""
    pages2, kids2 = parse_sitemap_xml(idx, base="https://example.com/sitemap_index.xml")
    assert pages2 == [] and len(kids2) == 1

    flow = build_flow_lines(
        ["/", "/overview", "/pricing", "/docs/api"],
        nav_paths=["/overview", "/pricing"],
        sources=["robots", "sitemap", "bfs"],
        tab_path="/overview",
    )
    assert flow and any("Top-level" in f or "monetization" in f for f in flow)
    assert any("ev:" in f for f in flow)

    bad = detect_and_map("not-a-url")
    assert bad.ok is False

    html = '<nav class="main-nav"><a href="/overview">O</a></nav><a href="/hidden">H</a>'
    all_l, nav_l = extract_links("https://example.com/", html)
    assert any(u.endswith("/overview") for u in nav_l)
    assert any(u.endswith("/hidden") for u in all_l)

    thin = Report(
        ok=True,
        version=VERSION,
        mode="web",
        root="https://example.com/",
        origin="https://example.com",
        profile="full",
        sources=["bfs"],
        tree_lines=["/", "  - overview"],
        node_count=2,
        path_order=["/", "/overview"],
        max_nodes=80,
        notes=[],
        compose=[],
        flow_lines=[],
        mermaid="",
        nav_paths=[],
    )
    merged = merge_extra_urls(
        thin,
        ["https://example.com/pricing", "https://example.com/docs"],
        label="merge",
    )
    assert merged.node_count >= 4
    assert "merge" in merged.sources
    assert "/pricing" in merged.path_order

    print(
        "self-test: PASS",
        json.dumps(
            {
                "lines": len(lines),
                "mermaid_chars": len(mm),
                "flow": len(flow),
                "merged": merged.node_count,
            }
        ),
    )
    return 0


def _load_merge_urls(args: argparse.Namespace) -> list[str]:
    out: list[str] = []
    for u in args.merge_urls or []:
        out.append(u)
    if args.merge_file:
        text = Path(args.merge_file).read_text(encoding="utf-8")
        try:
            payload = json.loads(text)
            if isinstance(payload, list):
                out.extend(str(x) for x in payload)
            elif isinstance(payload, dict):
                urls = payload.get("urls") or payload.get("links") or []
                out.extend(str(x) for x in urls)
        except json.JSONDecodeError:
            out.extend(ln.strip() for ln in text.splitlines() if ln.strip() and not ln.startswith("#"))
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Site / repo map tree (inventory + IA spine)")
    p.add_argument("url", nargs="?", help="https site or GitHub repo/tree URL")
    p.add_argument("--json", action="store_true", help="Print JSON report")
    p.add_argument(
        "--lite",
        action="store_true",
        help="v1.0-style shallow BFS from the given URL only (default is full origin map)",
    )
    p.add_argument(
        "--merge-urls",
        action="append",
        default=[],
        metavar="URL",
        help="Extra same-origin URL to union (repeatable). Use for BeatAPI/Firecrawl enrich.",
    )
    p.add_argument(
        "--merge-file",
        metavar="PATH",
        help="JSON list/{urls:[…]} or newline URLs from BeatAPI web_map / Firecrawl map",
    )
    p.add_argument("--max-nodes", type=int, default=None)
    p.add_argument("--max-depth", type=int, default=None)
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args(argv)

    if args.self_test:
        return _self_test()

    if not args.url:
        print(
            "Usage: site_map.py [--json] [--lite] [--merge-urls URL] [--merge-file PATH] <url>",
            file=sys.stderr,
        )
        return 2

    profile = "lite" if args.lite else "full"
    report = detect_and_map(
        args.url,
        max_nodes=args.max_nodes,
        max_depth=args.max_depth,
        profile=profile,
    )
    extra = _load_merge_urls(args)
    if extra and report.ok:
        report = merge_extra_urls(report, extra, label="merge")
    if args.json:
        print(json.dumps(asdict(report), separators=(",", ":")))
    else:
        sys.stdout.write(format_markdown(report))
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
