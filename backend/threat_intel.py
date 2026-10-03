"""Lure-URL reputation via Google Safe Browsing v4 (threatMatches:find).

Fail-open by design: no key / timeout / API error -> every URL is UNCHECKED,
never blocks an investigation. Results are cached in-memory per normalized URL.
"""
import os
import time

import requests

_API = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
_TIMEOUT = 8
_MAX_URLS = 10
_CACHE_TTL = 6 * 3600  # 6h

_cache: dict[str, tuple[float, dict]] = {}


def _norm(url: str) -> str:
    u = (url or "").strip().lower()
    if not u or "." not in u or len(u) > 200:
        return ""
    if not u.startswith(("http://", "https://")):
        u = "https://" + u
    return u


def check_urls(urls: list[str]) -> list[dict]:
    """Return [{url, status: FLAGGED|CLEAR|UNCHECKED, threats: [...]}, ...]."""
    key = os.getenv("SAFEBROWSING_API_KEY", "")
    targets = []
    for u in urls or []:
        n = _norm(u)
        if n and n not in targets:
            targets.append(n)
    targets = targets[:_MAX_URLS]
    if not targets:
        return []
    if not key:
        return [{"url": u, "status": "UNCHECKED", "threats": []} for u in targets]

    now = time.time()
    fresh = {u: r for u, (ts, r) in _cache.items() if now - ts < _CACHE_TTL}
    _cache.clear()
    _cache.update(fresh)
    pending = [u for u in targets if u not in _cache]
    if pending:
        try:
            resp = requests.post(
                _API,
                params={"key": key},
                json={
                    "client": {"clientId": "swarn-control", "clientVersion": "1.0"},
                    "threatInfo": {
                        "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING",
                                        "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                        "platformTypes": ["ANY_PLATFORM"],
                        "threatEntryTypes": ["URL"],
                        "threatEntries": [{"url": u} for u in pending],
                    },
                },
                timeout=_TIMEOUT,
            )
            matches = (resp.json() or {}).get("matches", []) if resp.ok else []
            flagged: dict[str, list[str]] = {}
            for m in matches:
                u = (m.get("threat") or {}).get("url", "")
                if u:
                    flagged.setdefault(u, []).append(m.get("threatType", "UNKNOWN"))
            for u in pending:
                threats = flagged.get(u, [])
                _cache[u] = (now, {"url": u,
                                   "status": "FLAGGED" if threats else "CLEAR",
                                   "threats": threats})
        except Exception:
            for u in pending:
                _cache[u] = (now, {"url": u, "status": "UNCHECKED", "threats": []})
    return [_cache[u][1] for u in targets]
