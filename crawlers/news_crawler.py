"""NewsCrawler — RSS feed parser cho CIC News, plain-HTML cho Job Bank, deep crawl cho news sites."""
import asyncio
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

import httpx

from .base_crawler import BaseCrawler


class NewsCrawler(BaseCrawler):

    async def run(self) -> list[Path]:
        if self.source.get("is_rss"):
            return await self._run_rss()
        if self.source.get("crawl_depth", 1) > 1:
            return await self._run_deep_crawl()
        return await self._run_html()

    async def _run_rss(self) -> list[Path]:
        """Fetch RSS feed và ghi các articles thành markdown."""
        resp = httpx.get(self.source["url"], timeout=30, follow_redirects=True,
                         headers={"User-Agent": "Mozilla/5.0 (compatible; LNCBot/1.0)"})
        resp.raise_for_status()

        root = ET.fromstring(resp.content)
        channel = root.find("channel")
        if channel is None:
            channel = root

        items = channel.findall("item")
        max_items = self.source.get("max_items", 20)
        articles = []

        for item in items[:max_items]:
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            pub_date = (item.findtext("pubDate") or "").strip()
            description = (item.findtext("description") or "").strip()
            description = re.sub(r"<[^>]+>", "", description).strip()

            if title:
                articles.append({"title": title, "link": link,
                                  "date": pub_date, "summary": description})

        lines = [f"# {self.source.get('feed_title', 'News Feed')}", "",
                 f"**Crawled:** {datetime.now().strftime('%Y-%m-%d')}  ",
                 f"**Source:** {self.source['url']}", "", "---", ""]

        for a in articles:
            lines += [f"## {a['title']}", "",
                      f"**Date:** {a['date']}  ",
                      f"**Link:** {a['link']}", ""]
            if a["summary"]:
                lines += [a["summary"], ""]
            lines += ["---", ""]

        content = "\n".join(lines)
        written = []
        for output_cfg in self.source["output_files"]:
            path = self.build_output_path(output_cfg["file"])
            self.write_markdown(path, content, {"file_role": path.stem,
                                                "article_count": len(articles)})
            written.append(path)

        # Optionally fetch full article content for each link
        if self.source.get("fetch_full_content") and articles:
            output_dir = self.source.get("output_dir", "08_news_updates/cicnews/")
            output_base = self.output_root / output_dir
            output_base.mkdir(parents=True, exist_ok=True)
            for article in articles:
                url = article["link"]
                if not url:
                    continue
                try:
                    await asyncio.sleep(1)
                    full_content = await self.fetch_markdown(url)
                    full_content = full_content.strip()
                    if len(full_content) < 100:
                        continue
                    slug = re.sub(r"[^a-z0-9]+", "-",
                                   url.rstrip("/").split("/")[-1].lower()).strip("-")[:80]
                    if not slug:
                        slug = re.sub(r"\W+", "-", url.split("//")[-1])[:80]
                    path = output_base / f"{slug}.md"
                    self.write_markdown(path, full_content, {
                        "source_url": url,
                        "file_role": "news_article",
                        "article_title": article["title"],
                        "pub_date": article["date"],
                    })
                    written.append(path)
                    print(f"  [OK] {slug} → {output_dir}")
                except Exception as exc:
                    print(f"  [WARN] RSS full-content skip {url[:60]}: {exc}")

        return written

    async def _run_deep_crawl(self) -> list[Path]:
        """Crawl index page (depth 1) → extract article links → crawl each article (depth 2).

        Config keys:
          crawl_depth    int   - phải > 1 để trigger (default 1)
          max_articles   int   - giới hạn số bài crawl (default 10)
          link_filter    str   - chỉ giữ URLs chứa chuỗi này (vd: "immigration.ca/")
          output_dir     str   - thư mục output tương đối, mỗi bài 1 file {slug}.md
          content_selector     - áp dụng cho từng bài (full page nếu None)
        """
        _SKIP = [
            "?", "/wp-content/", "/category/", "/tag/",
            "/author/", "/page/", "/feed/", "#",
            ".jpg", ".png", ".gif", ".svg", ".pdf", ".ico",
            "/about", "/our-team", "/contact", "/terms", "/privacy",
            "/editorial", "/sitemap", "/login", "/register",
        ]

        # --- Bước 1: Lấy index page dùng content_selector (chỉ article excerpts) ---
        index_md = await self.fetch_markdown(self.source["url"])

        # --- Bước 2: Trích xuất article links ---
        link_filter = self.source.get("link_filter", "")
        raw_urls = re.findall(r'https?://[^\s\)\]"<>]+', index_md)

        article_urls: list[str] = []
        seen: set[str] = set()
        for url in raw_urls:
            url = url.rstrip(".,)>;")
            if link_filter and link_filter not in url:
                continue
            if any(p in url for p in _SKIP):
                continue
            # Bỏ homepage (path rỗng sau domain)
            path_part = url.split(link_filter, 1)[-1] if link_filter in url else url.split("//", 1)[-1]
            if not path_part.strip("/"):
                continue
            if url not in seen:
                seen.add(url)
                article_urls.append(url)

        max_articles = self.source.get("max_articles", 10)
        article_urls = article_urls[:max_articles]

        if not article_urls:
            print(f"  [WARN] deep crawl: no article links found at {self.source['url']}")
            return []

        # --- Bước 3: Crawl từng bài và ghi file ---
        output_dir = self.source.get("output_dir", "08_news_updates/")
        output_base = self.output_root / output_dir
        output_base.mkdir(parents=True, exist_ok=True)

        written: list[Path] = []
        for article_url in article_urls:
            try:
                await asyncio.sleep(1)
                content = await self.fetch_markdown(article_url)
                content = content.strip()
                if len(content) < 100:
                    continue
                slug = re.sub(r"[^a-z0-9]+", "-",
                               article_url.rstrip("/").split("/")[-1].lower()).strip("-")[:80]
                if not slug:
                    slug = re.sub(r"\W+", "-", article_url.split("//")[-1])[:80]
                path = output_base / f"{slug}.md"
                self.write_markdown(path, content, {
                    "source_url": article_url,
                    "file_role": "news_article",
                })
                written.append(path)
            except Exception as exc:
                print(f"  [WARN] deep crawl skip {article_url[:60]}: {exc}")

        return written

    async def _run_html(self) -> list[Path]:
        """Crawl HTML page thông thường (dùng cho Job Bank)."""
        markdown = await self.fetch_markdown(self.source["url"])
        written = []

        for output_cfg in self.source["output_files"]:
            path = self.build_output_path(output_cfg["file"])
            selector = output_cfg.get("section_selector", "full_page")
            content = self.extract_section(
                markdown, selector,
                stop_before=output_cfg.get("stop_before"),
                start_after=output_cfg.get("start_after"),
            )

            if not content.strip():
                print(f"  [WARN] Empty content for '{selector}' — skipping {path.name}")
                continue

            self.write_markdown(path, content, {"file_role": path.stem})
            written.append(path)

        return written
