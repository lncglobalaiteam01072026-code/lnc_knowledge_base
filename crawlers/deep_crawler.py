"""DeepCrawler — BFS recursive crawler for arbitrary-depth site sections.

Config keys (in sources.json):
  crawl_depth    int   > 1 to trigger this crawler (e.g. 2 or 3)
  link_filter    str   only follow URLs containing this string (e.g. "sobirovs.com")
  max_articles   int   max total pages to write (default 30)
  output_dir     str   directory for {slug}.md output files
  crawl_delay    float seconds between requests (default 1.5)
  verify_links   bool  HEAD-check each discovered URL before enqueuing (default false)
"""
import asyncio
import re
from pathlib import Path

import httpx

from .base_crawler import BaseCrawler

_SKIP = [
    "/wp-content/", "/wp-json/", "/category/", "/tag/",
    "/author/", "/page/", "/feed/", "#",
    ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".pdf",
    ".ico", ".woff", ".woff2", ".css", ".js",
    "/contact", "/terms", "/privacy", "/disclaimer",
    "/sitemap", "/login", "/logout", "/register",
    "/testimonials", "/video-library", "/careers",
    "/free-consultation", "/lia-disclaimer",
    "calendly.com", "tiktok.com", "instagram.com",
    "youtube.com", "linkedin.com", "facebook.com",
    "maps.app.goo", "maps.google",
    "mailto:", "tel:", "javascript:",
]


class DeepCrawler(BaseCrawler):
    """BFS crawler: starts at source URL, discovers links up to crawl_depth levels deep."""

    async def _url_exists(self, client: httpx.AsyncClient, url: str) -> bool:
        """HEAD-check a URL; returns True if status < 400."""
        try:
            r = await client.head(url, follow_redirects=True, timeout=8)
            return r.status_code < 400
        except Exception:
            return False

    async def run(self) -> list[Path]:
        startup_delay = self.source.get("startup_delay", 0)
        if startup_delay:
            print(f"  [WAIT] DeepCrawler startup_delay={startup_delay}s for {self.source['id']}")
            await asyncio.sleep(startup_delay)

        link_filter = self.source.get("link_filter", "")
        max_pages = self.source.get("max_articles", 30)
        max_depth = self.source.get("crawl_depth", 2)
        delay = self.source.get("crawl_delay", 1.5)
        verify_links = self.source.get("verify_links", False)
        output_dir = self.source.get("output_dir", "08_news_updates/")
        output_base = self.output_root / output_dir
        output_base.mkdir(parents=True, exist_ok=True)

        visited: set[str] = set()
        queue: list[tuple[str, int]] = [(self.source["url"], 1)]
        written: list[Path] = []

        headers = {"User-Agent": "Mozilla/5.0 (compatible; LNCBot/1.0)"}
        async with httpx.AsyncClient(headers=headers) as client:
            while queue and len(written) < max_pages:
                url, depth = queue.pop(0)
                url = url.rstrip(".,)>;\"'")

                if url in visited:
                    continue
                if any(p in url for p in _SKIP):
                    visited.add(url)
                    continue
                if link_filter and link_filter not in url:
                    visited.add(url)
                    continue

                # Skip homepage — empty meaningful path after domain
                if link_filter:
                    path_part = url.split(link_filter, 1)[-1].strip("/")
                else:
                    path_part = url.split("//", 1)[-1].split("/", 1)[-1].strip("/")
                if not path_part and url != self.source["url"]:
                    visited.add(url)
                    continue

                # Skip query-only URLs (e.g. ?s=search) unless they're the root URL
                if "?" in path_part and url != self.source["url"]:
                    visited.add(url)
                    continue

                visited.add(url)

                try:
                    await asyncio.sleep(delay)
                    content = await self.fetch_markdown(url)
                    content = content.strip()
                    if len(content) < 200:
                        print(f"  [SKIP] d={depth} too short ({len(content)} chars): {url[:70]}")
                        continue

                    slug = re.sub(r"[^a-z0-9]+", "-",
                                   url.rstrip("/").split("/")[-1].lower()).strip("-")[:80]
                    if not slug:
                        slug = re.sub(r"\W+", "-", url.split("//")[-1])[:80]

                    path = output_base / f"{slug}.md"
                    self.write_markdown(path, content, {
                        "source_url": url,
                        "file_role": "deep_crawl_page",
                        "crawl_depth_level": depth,
                    })
                    written.append(path)
                    print(f"  [OK] d={depth}/{max_depth} {slug}.md → {output_dir}")

                    # Enqueue child links if not yet at max depth
                    if depth < max_depth:
                        raw_urls = re.findall(r'https?://[^\s\)\]"<>]+', content)
                        candidates = [
                            u.rstrip(".,)>;\"'") for u in raw_urls
                            if u.rstrip(".,)>;\"'") not in visited
                        ]
                        if verify_links:
                            checks = await asyncio.gather(
                                *[self._url_exists(client, u) for u in candidates]
                            )
                            candidates = [u for u, ok in zip(candidates, checks) if ok]

                        added = 0
                        for child_url in candidates:
                            queue.append((child_url, depth + 1))
                            added += 1
                        if added:
                            print(f"  [QUEUE] +{added} child links from d={depth}"
                                  + (" (verified)" if verify_links else ""))

                except Exception as exc:
                    print(f"  [WARN] skip d={depth} {url[:70]}: {exc}")

        print(f"  [DONE] {len(written)}/{min(max_pages,len(visited))} pages written"
              f" · depth={max_depth} · {self.source['url'][:60]}")
        return written
