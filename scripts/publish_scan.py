"""Publish preflight scanner — port of the main repo's
`frontend/src/persistence/{secretScanner,publishScan}.ts` into plain stdlib
Python for hub CI (see `schema_check.py` for why this can't just import the
TS module across repos).

Only `secret`-rule findings are `block`; everything else (`private_host`,
`local_path`, `email`, ...) is `warn`/`info` — a human PR reviewer judges
those (R9: "PR review is the moderation"), CI only hard-fails on leaked keys.
Manually re-sync with the upstream module if it changes.

No third-party dependencies — see `build_index.py` for why.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

# ── secret patterns (mirrors secretScanner.ts::SECRET_PATTERNS) ──
SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("OpenAI", re.compile(r"sk-[a-zA-Z0-9_-]{20,}")),
    ("Anthropic", re.compile(r"sk-ant-[a-zA-Z0-9_-]{20,}")),
    ("Google", re.compile(r"AIza[0-9A-Za-z\-_]{35}")),
    ("Groq", re.compile(r"gsk_[a-zA-Z0-9]{20,}")),
    ("GitHub", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("Bearer", re.compile(r"Bearer\s+[A-Za-z0-9\-._~+/]{20,}")),
]

PUBLIC_ENDPOINT_HOSTS = frozenset({
    "api.openai.com", "api.anthropic.com", "api.groq.com", "api.mistral.ai",
    "api.deepseek.com", "api.together.xyz", "api.fireworks.ai",
    "api.perplexity.ai", "api.cohere.com", "api.x.ai", "openrouter.ai",
    "generativelanguage.googleapis.com", "integrate.api.nvidia.com",
})
INTERNAL_TLDS = frozenset({"local", "internal", "intranet", "corp", "lan", "home", "private"})
EXAMPLE_DOMAINS = frozenset({"example.com", "example.net", "example.org", "example.edu"})
PATH_FIELDS = frozenset({"output_file", "storage_path", "file_ref"})
ENDPOINT_FIELDS = frozenset({"base_url"})
INLINE_BODY_MIN = 120

URL_RE = re.compile(r"https?://[^\s\"'`<>)\]}]+", re.IGNORECASE)
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)+")
PHONE_RE = re.compile(r"(?:\+\d{1,3}[ -])?(?:0\d{1,2}|\(0?\d{1,3}\))[ -]\d{3,4}[ -]\d{4}")
HOME_PATH_RES = [
    re.compile(r"/Users/[^/\s\"'`,;]+(?:/[^\s\"'`,;]*)*"),
    re.compile(r"/home/[^/\s\"'`,;]+(?:/[^\s\"'`,;]*)*"),
    re.compile(r"/Volumes/[^\s\"'`,;]+"),
    re.compile(r"[A-Za-z]:\\\\(?:Users|Documents and Settings)\\\\[^\s\"'`,;]*"),
]


@dataclass
class Finding:
    rule: str
    risk: str  # block | warn | info
    path: str
    match: str


def _host_of(url: str) -> str | None:
    m = re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://([^/:?#]+)", url)
    if not m:
        return None
    return m.group(1).lower().strip("[]").rstrip(".")


def _host_kind(host: str) -> str:
    if host == "localhost" or host == "::1" or host == "0.0.0.0" or re.match(r"^127\.", host):
        return "loopback"
    if host.endswith(".localhost"):
        return "loopback"
    v4 = re.match(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$", host)
    if v4:
        a, b = int(v4.group(1)), int(v4.group(2))
        if a in (10, 127):
            return "private"
        if a == 192 and b == 168:
            return "private"
        if a == 172 and 16 <= b <= 31:
            return "private"
        if a == 169 and b == 254:
            return "private"
        return "public"
    if re.match(r"^f[cd][0-9a-f]{2}:", host) or re.match(r"^fe[89ab][0-9a-f]:", host):
        return "private"
    labels = host.split(".")
    if labels[-1] in INTERNAL_TLDS:
        return "private"
    if len(labels) == 1:
        return "private"
    return "public"


@dataclass
class _Site:
    path: str
    value: str
    field: str | None = None
    node_type: str | None = None


def _walk_doc(doc: dict[str, Any]) -> list[_Site]:
    sites: list[_Site] = []
    for k in ("name", "description", "author"):
        v = doc.get(k)
        if isinstance(v, str) and v:
            sites.append(_Site(f"$.{k}", v))
    for i, tag in enumerate(doc.get("tags") or []):
        if isinstance(tag, str) and tag:
            sites.append(_Site(f"$.tags[{i}]", tag))
    fork = doc.get("forked_from") or {}
    for k in ("source", "name"):
        v = fork.get(k)
        if isinstance(v, str) and v:
            sites.append(_Site(f"$.forked_from.{k}", v))
    for i, node in enumerate(doc.get("nodes") or []):
        data = node.get("data")
        if not isinstance(data, dict):
            continue
        node_type = node.get("type")
        for key, v in data.items():
            if isinstance(v, str) and v:
                sites.append(_Site(f"$.nodes[{i}].data.{key}", v, field=key, node_type=node_type))
    return sites


def _detect_inline_body(site: _Site) -> list[Finding]:
    if site.node_type != "knowledge" or site.field != "content":
        return []
    if len(site.value) < INLINE_BODY_MIN:
        return []
    return [Finding("inline_body", "info", site.path, f"<{len(site.value)} chars>")]


def _detect_secrets(value: str) -> list[Finding]:
    hits = []
    for name, pat in SECRET_PATTERNS:
        for m in pat.finditer(value):
            hits.append(Finding("secret", "block", "", m.group(0)))
    return hits


def _detect_urls(site: _Site) -> list[Finding]:
    hits: list[Finding] = []
    is_endpoint = site.field is not None and site.field in ENDPOINT_FIELDS

    def classify(host: str, match: str) -> None:
        kind = _host_kind(host)
        if kind == "loopback":
            hits.append(Finding("loopback_url", "info", site.path, match))
        elif kind == "private":
            hits.append(Finding("private_host", "warn", site.path, match))
        elif is_endpoint and host not in PUBLIC_ENDPOINT_HOSTS:
            hits.append(Finding("custom_endpoint", "info", site.path, match))

    for m in URL_RE.finditer(site.value):
        raw = re.sub(r"[.,;:!?'\"]+$", "", m.group(0))
        host = _host_of(raw)
        if host:
            classify(host, raw)

    if is_endpoint and not re.match(r"^https?://", site.value, re.IGNORECASE):
        trimmed = site.value.strip()
        if re.match(r"^[A-Za-z0-9._-]+(?::\d{2,5})?(?:/\S*)?$", trimmed):
            host = _host_of(f"http://{trimmed}")
            if host and ("." in host or host == "localhost" or re.search(r":\d", trimmed)):
                classify(host, trimmed)
    return hits


def _detect_paths(site: _Site) -> list[Finding]:
    hits: list[Finding] = []
    for pat in HOME_PATH_RES:
        for m in pat.finditer(site.value):
            hits.append(Finding("local_path", "warn", site.path, m.group(0)))
    if site.field and site.field in PATH_FIELDS and not hits:
        v = site.value.strip()
        if re.match(r"^(/[^/]|[A-Za-z]:[\\/])", v):
            hits.append(Finding("abs_path", "info", site.path, v))
    return hits


def _detect_emails(value: str) -> list[Finding]:
    hits = []
    for m in EMAIL_RE.finditer(value):
        domain = m.group(0).split("@")[1].lower()
        if domain in EXAMPLE_DOMAINS or re.search(r"\.(example|invalid|test)$", domain):
            continue
        hits.append(Finding("email", "warn", "", m.group(0)))
    return hits


def _detect_phones(value: str) -> list[Finding]:
    hits = []
    for m in PHONE_RE.finditer(value):
        before = value[m.start() - 1] if m.start() > 0 else ""
        after = value[m.end()] if m.end() < len(value) else ""
        if re.match(r"[\d-]", before) or re.match(r"[\d-]", after):
            continue
        hits.append(Finding("phone", "warn", "", m.group(0)))
    return hits


def scan_for_publish(doc: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    for site in _walk_doc(doc):
        for hit in _detect_secrets(site.value):
            findings.append(Finding(hit.rule, hit.risk, site.path, hit.match))
        for hit in _detect_urls(site):
            findings.append(Finding(hit.rule, hit.risk, site.path, hit.match))
        for hit in _detect_paths(site):
            findings.append(Finding(hit.rule, hit.risk, site.path, hit.match))
        for hit in _detect_emails(site.value):
            findings.append(Finding(hit.rule, hit.risk, site.path, hit.match))
        for hit in _detect_phones(site.value):
            findings.append(Finding(hit.rule, hit.risk, site.path, hit.match))
        for hit in _detect_inline_body(site):
            findings.append(Finding(hit.rule, hit.risk, site.path, hit.match))
    return findings


__all__ = ["Finding", "scan_for_publish", "SECRET_PATTERNS"]
