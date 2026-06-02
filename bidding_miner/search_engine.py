"""简易搜索引擎 — 纯 DuckDuckGo HTTP，供独立运行时回退使用。"""

from __future__ import annotations

import logging
import urllib.parse
from dataclasses import dataclass, field

import requests
from bs4 import BeautifulSoup

_log = logging.getLogger("bidding_miner.search_engine")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str = ""


@dataclass
class SearchResponse:
    ok: bool
    engine: str
    query: str
    results: list[SearchResult] = field(default_factory=list)
    result_count: int = 0
    error: str = ""


class SimpleSearchEngine:
    """简易搜索引擎 — DuckDuckGo HTTP 直抓。"""

    def route_search(self, query: str, max_results: int = 6) -> SearchResponse:
        return self._search_ddg(query, max_results)

    def _search_ddg(self, query: str, max_results: int = 10) -> SearchResponse:
        try:
            resp = requests.get(
                "https://html.duckduckgo.com/html/",
                params={"q": query},
                headers=HEADERS,
                timeout=15,
            )
            resp.raise_for_status()
        except Exception as e:
            return SearchResponse(
                ok=False, engine="ddg_html", query=query,
                error=f"DuckDuckGo 请求失败: {e}",
            )

        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        for div in soup.select("div.result"):
            a_tag = div.select_one("a.result__a")
            if not a_tag:
                continue
            title = a_tag.get_text(strip=True)
            href = a_tag.get("href", "")
            if "uddg=" in href:
                parsed = urllib.parse.urlparse(href)
                qs = urllib.parse.parse_qs(parsed.query)
                real_url = qs.get("uddg", [href])[0]
            else:
                real_url = href
            snippet_tag = div.select_one("a.result__snippet")
            snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
            if title and real_url:
                results.append(SearchResult(title=title, url=real_url, snippet=snippet))

        results = results[:max_results]
        _log.info("DDG 搜索完成: query=%r → %d 条", query, len(results))
        return SearchResponse(
            ok=len(results) > 0, engine="ddg_html", query=query,
            results=results, result_count=len(results),
        )
