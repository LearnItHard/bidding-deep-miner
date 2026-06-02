"""招投标 URL 资源清单 — 复用 deep-research-agent 的数据源。

如果 deep-research-agent 项目存在，则直接引用其中的数据；
否则提供内置的常用平台列表作为回退。
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from dataclasses import dataclass, field

_log = logging.getLogger("bidding_miner.urls")


@dataclass
class SearchableURL:
    """可搜索 URL 数据源的描述（与 deep-research-agent 兼容）。"""
    name: str
    base_url: str
    query_param: str
    method: str = "GET"
    encoding: str = "utf-8"
    note: str = ""
    extra_params: dict = field(default_factory=dict)


def build_search_url(source: SearchableURL, query: str) -> str:
    """构建搜索 URL。"""
    import urllib.parse
    encoded_keyword = urllib.parse.quote(query, encoding=source.encoding)
    if source.query_param:
        params = {source.query_param: query, **source.extra_params}
        encoded = urllib.parse.urlencode(
            {k: v for k, v in params.items() if k and v},
            encoding=source.encoding,
        )
        sep = "&" if "?" in source.base_url else "?"
        return f"{source.base_url}{sep}{encoded}"
    if source.base_url.endswith("/"):
        return f"{source.base_url}{encoded_keyword}"
    return source.base_url


# ── 尝试复用 deep-research-agent 的 URL 库 ──────────────
_PLATFORMS = None
_GOV_PLATFORMS = None
_PROCUREMENT = None

_parent = Path(__file__).resolve().parent.parent.parent.parent  # e:\Claude_Code-openclaw-agent_etc\
_dr_path = _parent / "deep-research-agent"
if _dr_path.exists():
    sys.path.insert(0, str(_dr_path))
    try:
        from deep_research.urls.bidding import (
            NATIONAL_PLATFORMS as _NP,
            GOV_PLATFORMS as _GP,
            PROCUREMENT_SITES as _PS,
            CUSTOM_SOURCES as _CS,
        )
        from deep_research.urls._base import build_search_url as _build_url
        _PLATFORMS = _NP
        _GOV_PLATFORMS = _GP
        _PROCUREMENT = _PS
        _CUSTOM = _CS
        _log.info("成功复用 deep-research-agent 的招投标 URL 库")
    except ImportError as e:
        _log.warning("导入 deep-research-agent URL 失败: %s", e)

if _PLATFORMS is None:
    # 回退: 内置最常用平台
    _log.info("使用内置的常用招投标平台列表")
    _PLATFORMS = [
        SearchableURL(
            name="全国公共资源交易平台",
            base_url="https://www.ggzy.gov.cn/deal/dealList.html",
            query_param="FINDTXT",
            extra_params={"DEAL_TIME": "05"},
        ),
        SearchableURL(
            name="中国政府采购网",
            base_url="https://search.ccgp.gov.cn/bxsearch",
            query_param="kw",
            extra_params={"searchtype": "1", "page_index": "1", "timeType": "2"},
        ),
    ]
    _GOV_PLATFORMS = []
    _PROCUREMENT = []
    _CUSTOM = []


# ── 聚合 ──────────────────────────────────────────────────
ALL_SOURCES = (_PLATFORMS or []) + (_GOV_PLATFORMS or []) + (_PROCUREMENT or []) + (_CUSTOM or [])

CATEGORIES = {
    "国家级平台": _PLATFORMS or [],
    "省市级交易平台": _GOV_PLATFORMS or [],
    "政府采购网": _PROCUREMENT or [],
    "自定义": _CUSTOM or [],
}
