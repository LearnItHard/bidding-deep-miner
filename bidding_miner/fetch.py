"""fetch.py — 智能网页抓取器（Crawl4AI 延迟导入）

策略: Crawl4AI AsyncWebCrawler（PruningContentFilter + 缓存）
      自动降级: fit_markdown → raw_markdown → 失败
用法: fetch(url) → (文本, 策略名)

注意: crawl4ai 在首次调用 fetch() 时按需导入，避免模块级依赖问题。
"""

from __future__ import annotations
import asyncio
import logging

_log = logging.getLogger("bidding_miner.fetch")

# ── 延迟导入（首次调用 fetch 时才加载）────────────────
_CRAWL4AI_AVAILABLE = False
_AsyncWebCrawler = None
_CrawlerRunConfig = None
_CacheMode = None
_BrowserConfig = None
_DefaultMarkdownGenerator = None
_PruningContentFilter = None
_BROWSER_CONFIG = None


def _lazy_init_crawl4ai():
    """按需初始化 Crawl4AI（仅在首次 fetch 调用时执行）。"""
    global _CRAWL4AI_AVAILABLE, _AsyncWebCrawler, _CrawlerRunConfig
    global _CacheMode, _BrowserConfig, _DefaultMarkdownGenerator, _PruningContentFilter
    global _BROWSER_CONFIG

    if _CRAWL4AI_AVAILABLE:
        return True

    try:
        from crawl4ai import (
            AsyncWebCrawler,
            CrawlerRunConfig,
            CacheMode,
            BrowserConfig,
        )
        from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
        from crawl4ai.content_filter_strategy import PruningContentFilter

        _AsyncWebCrawler = AsyncWebCrawler
        _CrawlerRunConfig = CrawlerRunConfig
        _CacheMode = CacheMode
        _BrowserConfig = BrowserConfig
        _DefaultMarkdownGenerator = DefaultMarkdownGenerator
        _PruningContentFilter = PruningContentFilter

        _BROWSER_CONFIG = BrowserConfig(
            headless=True, verbose=False, text_mode=True,
        )
        _CRAWL4AI_AVAILABLE = True
        _log.info("Crawl4AI 已成功加载")
        return True
    except ImportError as e:
        _log.warning("Crawl4AI 加载失败: %s。抓取功能不可用。", e)
        _CRAWL4AI_AVAILABLE = False
        return False


MAX_CHARS = 10000


# ── 核心 API ─────────────────────────────────────────

def fetch(url: str, timeout: int = 30) -> tuple[str, str]:
    """返回 (正文文本, 策略名)。策略名: crawl4ai / fail / no_crawl4ai"""
    if not _lazy_init_crawl4ai():
        err = "⚠️ 获取失败：crawl4ai 未安装。请运行: pip install crawl4ai"
        _log.warning("抓取失败（crawl4ai 不可用）: %s", url[:120])
        return err, "no_crawl4ai"

    _log.debug("抓取开始: %s", url[:120])
    try:
        text = asyncio.run(_crawl(url, timeout))
        if _ok(text):
            _log.debug("抓取成功: 策略=crawl4ai, 大小=%dB, url=%s", len(text), url[:100])
            return text, "crawl4ai"
    except Exception as e:
        _log.warning("Crawl4AI 异常: url=%s, err=%s", url[:120], e)

    _log.info("抓取失败: url=%s", url[:120])
    return f"⚠️ 获取失败: {url}", "fail"


async def _crawl(url: str, timeout: int) -> str:
    """Crawl4AI 异步抓取核心"""
    run_config = _CrawlerRunConfig(
        cache_mode=_CacheMode.ENABLED,
        markdown_generator=_DefaultMarkdownGenerator(
            content_filter=_PruningContentFilter(
                threshold=0.48,
                threshold_type="fixed",
                min_word_threshold=0,
            ),
        ),
        # 等待页面完全加载（含 AJAX 数据）
        wait_until="networkidle",
        # 额外等待确保动态内容渲染完成
        page_timeout=timeout * 1000,
        # 移除广告/跟踪器等干扰元素
        remove_overlay_elements=True,
    )

    async with _AsyncWebCrawler(config=_BROWSER_CONFIG) as crawler:
        result = await crawler.arun(url, config=run_config)

    # 优先使用智能过滤后的 fit_markdown，其次 raw_markdown
    if result.markdown and result.markdown.fit_markdown:
        return _cut(result.markdown.fit_markdown)
    if result.markdown and result.markdown.raw_markdown:
        return _cut(result.markdown.raw_markdown)
    return ""


def _ok(text: str) -> bool:
    return bool(text) and not text.startswith("⚠️") and len(text.strip()) >= 100


def _cut(text: str) -> str:
    return text[:MAX_CHARS] + "\n... [截断]" if len(text) > MAX_CHARS else text
