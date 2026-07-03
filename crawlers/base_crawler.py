import hashlib
import re
import shutil
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

import frontmatter
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

_ABBREV_RE = re.compile(r'^\s*\*\[.*?\]:.*$', re.MULTILINE)
_BACK_NEXT_RE = re.compile(r'^(Back to |Next |Previous )\[.*', re.MULTILINE)

# crawl4ai renders JS-resolved links as https://host/base/<https:/ext/> or https://host/base/</path>
# Generic patterns (work for any domain)
_URL_ART_EXT_RE = re.compile(r'https://[^\s<"(]+<https?:/{1,2}([^>]+)>')
_URL_ART_ANC_RE = re.compile(r'https://[^\s<"(]+<(#[^>]+)>')
_URL_ART_TEL_RE = re.compile(r'https://[^\s<"(]+<(tel:[^>]+)>')
# Domain-specific internal paths (replacement must prepend correct host)
_URL_INT_ALBERTA_RE = re.compile(
    r'https://www\.alberta\.ca/[^\s<"(]*</?([a-zA-Z0-9][^>"\)\s]*?)>'
)
_URL_INT_WELCOMEBC_RE = re.compile(
    r'https://www\.welcomebc\.ca/[^\s<"(]*</?([a-zA-Z][^>"\)\s]*?)>'
)
_URL_INT_CANADA_RE = re.compile(
    r'https://www\.canada\.ca/[^\s<"(]*</?([a-zA-Z][^>"\)\s]*?)>'
)
_URL_INT_INZ_RE = re.compile(
    r'https://www\.immigration\.govt\.nz/[^\s<"(]*</?([a-zA-Z][^>"\)\s]*?)>'
)
_IMG_HEADING_RE = re.compile(r'^#{1,6}\s+!\[[^\]]*\]\([^)]+\)\s*$', re.MULTILINE)
# Empty markdown links with javascript: void URLs e.g. [](https://host/path/<javascript%3Avoid.../>)
_EMPTY_JS_LINK_RE = re.compile(r'\[\]\(https://[^\s"()]+<javascript[^>]*>\)')


def _clean_url_artifacts(content: str) -> str:
    """Fix crawl4ai URL artifacts where crawled site links wrap external/internal URLs."""
    content = _EMPTY_JS_LINK_RE.sub('', content)                                     # [](javascript:void)
    content = _URL_ART_TEL_RE.sub(r'\1', content)                                    # tel:
    content = _URL_ART_ANC_RE.sub(r'\1', content)                                    # #anchor
    content = _URL_ART_EXT_RE.sub(r'https://\1', content)                           # external embed
    content = _URL_INT_ALBERTA_RE.sub(r'https://www.alberta.ca/\1', content)        # alberta internal
    content = _URL_INT_WELCOMEBC_RE.sub(r'https://www.welcomebc.ca/\1', content)    # bc internal
    content = _URL_INT_CANADA_RE.sub(r'https://www.canada.ca/\1', content)          # canada.ca internal
    content = _URL_INT_INZ_RE.sub(r'https://www.immigration.govt.nz/\1', content)  # INZ internal
    content = _IMG_HEADING_RE.sub('', content)                                       # heading=image artifact
    return content


class BaseCrawler(ABC):
    def __init__(self, source: dict, output_root: Path):
        self.source = source
        self.output_root = output_root
        self.year = str(datetime.now().year)
        self._changed_files: set[Path] = set()

    def _maybe_archive(self, path: Path, new_content: str) -> bool:
        """Lưu file cũ vào _archive/ nếu content thay đổi. Trả về True nếu changed."""
        new_hash = hashlib.sha256(new_content.encode()).hexdigest()
        if not path.exists():
            return True
        old_content = path.read_text(encoding="utf-8")
        if hashlib.sha256(old_content.encode()).hexdigest() == new_hash:
            return False
        date_str = datetime.now().strftime("%Y-%m-%d")
        archive_dir = self.output_root / "_archive" / self.source["id"]
        archive_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, archive_dir / f"{date_str}_{path.name}")
        return True

    async def fetch_markdown(self, url: str) -> str:
        """Crawl URL và trả về markdown content.

        canada.ca blocks HTTP/2 from CI environments — use httpx (HTTP/1.1)
        + markdownify for those URLs instead of Playwright.
        """
        if self.source.get("use_httpx") or "canada.ca" in url:
            return await self._fetch_markdown_httpx(url)

        browser_config = BrowserConfig(headless=True, verbose=False)
        run_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            css_selector=self.source.get("content_selector"),
            delay_before_return_html=self.source.get("crawl_delay", 0),
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=url, config=run_config)
            if not result.success:
                raise RuntimeError(f"Crawl failed for {url}: {result.error_message}")
            return result.markdown

    async def _fetch_markdown_httpx(self, url: str) -> str:
        """Fetch page with httpx (HTTP/1.1) and convert HTML to markdown.
        Used for canada.ca which blocks HTTP/2 from CI environments.
        """
        import httpx
        from bs4 import BeautifulSoup
        from markdownify import markdownify as md

        headers = {"User-Agent": "Mozilla/5.0 (compatible; LNCBot/1.0)"}
        async with httpx.AsyncClient(
            timeout=60, follow_redirects=True, http2=False
        ) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        selector = self.source.get("content_selector")
        if selector:
            node = soup.find(selector)
            html = str(node) if node else resp.text
        else:
            html = resp.text

        return md(html, heading_style="ATX", bullets="-")

    def extract_section(
        self,
        markdown: str,
        selector: str,
        stop_before: str = None,
        start_after: str = None,
    ) -> str:
        """Tách section từ markdown dựa trên selector và optional modifiers."""
        if selector in ("full_page", "overview_to_points_grid"):
            content = self._strip_leading_navblock(markdown)
        elif selector.startswith("h1:contains("):
            keyword = re.search(r"contains\('(.+?)'\)", selector).group(1)
            content = self._extract_by_heading(markdown, keyword, level=1)
        elif selector.startswith("h2:contains("):
            keyword = re.search(r"contains\('(.+?)'\)", selector).group(1)
            content = self._extract_by_heading(markdown, keyword, level=2)
        elif selector.startswith("h3:contains("):
            keyword = re.search(r"contains\('(.+?)'\)", selector).group(1)
            content = self._extract_by_heading(markdown, keyword, level=3)
        elif selector.startswith("table:contains("):
            keyword = re.search(r"contains\('(.+?)'\)", selector).group(1)
            content = self._extract_table_section(markdown, keyword)
        else:
            content = markdown

        if start_after:
            content = self._apply_start_after(content, start_after)
        if stop_before:
            content = self._apply_stop_before(content, stop_before)

        return content

    def _apply_stop_before(self, markdown: str, marker: str) -> str:
        """Cắt content trước line chứa marker text.

        - Marker có '#' prefix (ví dụ '## Contact'): chỉ match heading lines (startswith).
        - Marker không có '#' (ví dụ 'Be fraud aware'): match heading (in) VÀ non-heading (in).
        """
        is_heading_marker = marker.lstrip().startswith("#")
        marker_text = marker.lstrip("#").strip().lower()
        lines = markdown.split("\n")
        for i, line in enumerate(lines):
            line_text = line.lstrip("#").strip().lower()
            is_heading = line.startswith("#")

            if is_heading:
                if is_heading_marker:
                    if line_text.startswith(marker_text):
                        return "\n".join(lines[:i]).strip()
                else:
                    if marker_text in line_text:
                        return "\n".join(lines[:i]).strip()
            else:
                if not is_heading_marker and marker_text in line_text:
                    return "\n".join(lines[:i]).strip()
        return markdown

    def _strip_leading_navblock(self, markdown: str) -> str:
        """Strip nav/breadcrumb blocks at top of content before first real heading.

        Handles:
        - Alberta.ca: 'Explore pages in:' + 'On this page:' in-page nav
        - WelcomeBC: '* [Home](...) > ...' breadcrumb trail inside <main>
        """
        stripped = markdown.lstrip()
        is_alberta_nav = stripped.startswith("Explore pages in:")
        is_breadcrumb = stripped.startswith("* [Home]") or stripped.startswith("* [home]")
        if not (is_alberta_nav or is_breadcrumb):
            return markdown
        lines = markdown.split("\n")
        for i, line in enumerate(lines):
            if re.match(r'^#{1,3} ', line):
                return "\n".join(lines[i:]).strip()
        return markdown

    def _apply_start_after(self, markdown: str, marker: str) -> str:
        """Trả về content từ sau heading chứa marker text (bỏ qua heading level)."""
        marker_text = marker.lstrip("#").strip().lower()
        lines = markdown.split("\n")
        for i, line in enumerate(lines):
            if line.lstrip("#").strip().lower().startswith(marker_text):
                return "\n".join(lines[i + 1:]).strip()
        return markdown

    def _extract_by_heading(self, markdown: str, keyword: str, level: int) -> str:
        """Trích đoạn từ heading chứa keyword đến heading cùng cấp hoặc cao hơn tiếp theo."""
        prefix = "#" * level + " "
        lines = markdown.split("\n")
        start_idx = None

        for i, line in enumerate(lines):
            if line.startswith(prefix) and keyword.lower() in line.lower():
                start_idx = i
                break

        if start_idx is None:
            for i, line in enumerate(lines):
                if line.startswith(prefix) and any(
                    w in line.lower() for w in keyword.lower().split()
                ):
                    start_idx = i
                    break

        if start_idx is None:
            return markdown

        end_idx = len(lines)
        for i in range(start_idx + 1, len(lines)):
            # Stop at same-level heading
            if lines[i].startswith(prefix) and not lines[i].startswith(prefix + "#"):
                end_idx = i
                break
            # Stop at any higher-level heading (h1 for h2+, h1/h2 for h3+, etc.)
            for stop_level in range(1, level):
                if lines[i].startswith("#" * stop_level + " "):
                    end_idx = i
                    break
            else:
                continue
            break

        return "\n".join(lines[start_idx:end_idx]).strip()

    def _extract_table_section(self, markdown: str, keyword: str) -> str:
        """Trích đoạn chứa table với keyword."""
        lines = markdown.split("\n")
        table_start = None

        for i, line in enumerate(lines):
            if "|" in line and keyword.lower() in "\n".join(lines[max(0,i-5):i+5]).lower():
                table_start = i
                while table_start > 0 and "|" in lines[table_start - 1]:
                    table_start -= 1
                break

        if table_start is None:
            return ""

        table_end = table_start
        while table_end < len(lines) and ("|" in lines[table_end] or lines[table_end].strip() == ""):
            table_end += 1

        return "\n".join(lines[table_start:table_end]).strip()

    def build_output_path(self, file_pattern: str) -> Path:
        """Thay thế {year} placeholder và trả về Path đầy đủ."""
        filename = file_pattern.replace("{year}", self.year)
        path = self.output_root / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def write_markdown(self, path: Path, content: str, extra_meta: dict = None):
        """Ghi file .md với YAML frontmatter. Archive bản cũ nếu content thay đổi."""
        content = _ABBREV_RE.sub('', content)
        content = _BACK_NEXT_RE.sub('', content)
        content = _clean_url_artifacts(content)
        content = content.strip()

        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        meta = {
            **self.source["metadata"],
            "source_id": self.source["id"],
            "source_url": self.source["url"],
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "version": "1.0",
            "chunk_strategy": self.source.get("chunk_strategy", "standard"),
            "priority_weight": self.source.get("priority_weight", 1),
            "retrieval_strategy": "parent_child" if "communities" in str(path) else "direct",
            "content_hash": content_hash,
        }
        if extra_meta:
            meta.update(extra_meta)

        new_text = frontmatter.dumps(frontmatter.Post(content, **meta))
        if self._maybe_archive(path, new_text):
            self._changed_files.add(path)
        path.write_text(new_text, encoding="utf-8")

    def write_json(self, path: Path, data: dict | list):
        """Ghi file .json với metadata wrapper. Archive bản cũ nếu content thay đổi."""
        import json
        wrapper = {
            "metadata": {
                "source_id": self.source["id"],
                "source_url": self.source["url"],
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "program": self.source["metadata"]["program"],
            },
            "data": data,
        }
        new_text = json.dumps(wrapper, ensure_ascii=False, indent=2)
        if self._maybe_archive(path, new_text):
            self._changed_files.add(path)
        path.write_text(new_text, encoding="utf-8")

    @abstractmethod
    async def run(self) -> list[Path]:
        """Chạy crawler và trả về danh sách files đã ghi."""
        pass
