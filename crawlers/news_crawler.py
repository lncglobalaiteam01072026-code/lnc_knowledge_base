"""NewsCrawler — RSS feed parser cho CIC News và plain-HTML cho Job Bank."""
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
        return await self._run_html()

    async def _run_rss(self) -> list[Path]:
        """Fetch RSS feed và ghi các articles thành markdown."""
        resp = httpx.get(self.source["url"], timeout=30, follow_redirects=True,
                         headers={"User-Agent": "Mozilla/5.0 (compatible; LNCBot/1.0)"})
        resp.raise_for_status()

        root = ET.fromstring(resp.content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
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
            # Strip HTML tags from description
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
