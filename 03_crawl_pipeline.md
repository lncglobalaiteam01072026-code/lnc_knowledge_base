# LNC Knowledge Base — Crawl Pipeline

> Tài liệu này dành cho Claude Code thực thi crawl pipeline.
> Đọc toàn bộ trước khi bắt đầu. Làm theo từng bước, không bỏ qua.

---

## Tổng quan

Pipeline này crawl dữ liệu từ các official government sources, xử lý và lưu vào
thư mục `lnc-knowledge-base/` theo cấu trúc đã định nghĩa trong `01_directory_tree.md`.

**Tech stack:**
- Python 3.11+
- `crawl4ai` — crawl và extract markdown từ HTML
- `pypdf` — extract text từ PDF
- `httpx` — HTTP client cho các request đơn giản
- `pydantic` — validate schema đầu ra
- `python-frontmatter` — ghi YAML frontmatter vào file .md

**Không cần:** Selenium, Playwright, browser automation.
Tất cả target sites đều render server-side, không cần JS execution.

---

## Cấu trúc repo

```
lnc-kb-crawler/
├── .github/
│   └── workflows/
│       ├── crawl_monthly.yml          # Monthly: draw history
│       ├── crawl_quarterly.yml        # Quarterly: program core
│       └── crawl_annual.yml           # Annual: language tests, ECA
├── crawlers/
│   ├── __init__.py
│   ├── base_crawler.py                # Base class
│   ├── aaip_crawler.py                # AAIP sources
│   ├── bcpnp_crawler.py               # BC PNP sources
│   ├── ircc_crawler.py                # IRCC sources
│   └── pdf_crawler.py                 # PDF sources
├── processors/
│   ├── __init__.py
│   ├── section_splitter.py            # Tách section từ một URL → nhiều files
│   ├── table_converter.py             # Markdown table → narrative text
│   └── frontmatter_writer.py          # Gắn YAML metadata vào .md
├── validators/
│   ├── __init__.py
│   └── schema_validator.py            # Validate output trước khi commit
├── config/
│   └── sources.json                   # Crawl sources config (copy từ crawl_config.json)
├── output/
│   └── lnc-knowledge-base/            # Output folder — commit vào KB repo
├── requirements.txt
├── crawl.py                           # Entry point
└── README.md
```

---

## File config: `config/sources.json`

Claude Code tạo file này với nội dung sau:

```json
{
  "version": "1.0.0",
  "astradb": {
    "collection_text": "lnc_kb_chunks",
    "collection_json": "lnc_kb_structured"
  },
  "sources": [
    {
      "id": "aaip_eligibility",
      "program": "AAIP",
      "layer": "01_program_core",
      "url": "https://www.alberta.ca/aaip-rural-entrepreneur-stream-eligibility",
      "output_files": [
        {
          "file": "01_program_core/aaip/eligibility.md",
          "section_selector": "overview_to_points_grid",
          "stop_before": "## Factors that increase"
        },
        {
          "file": "01_program_core/aaip/points_grid.md",
          "section_selector": "h2:contains('Points Grid')",
          "start_after": "## Selection from EOI pool"
        },
        {
          "file": "01_program_core/aaip/ineligible_businesses.md",
          "section_selector": "h3:contains('Ineligible businesses')"
        }
      ],
      "frequency": "quarterly",
      "chunk_strategy": "standard",
      "has_tables": true,
      "priority_weight": 1,
      "metadata": {
        "program": "AAIP",
        "province": "AB",
        "topic": "eligibility",
        "lang": "en",
        "access_level": "chatbot"
      }
    },
    {
      "id": "aaip_how_to_apply",
      "program": "AAIP",
      "layer": "01_program_core",
      "url": "https://www.alberta.ca/aaip-rural-entrepreneur-stream-how-to-apply",
      "output_files": [
        {
          "file": "01_program_core/aaip/how_to_apply.md",
          "section_selector": "full_page"
        }
      ],
      "frequency": "quarterly",
      "chunk_strategy": "standard",
      "has_tables": false,
      "priority_weight": 1,
      "metadata": {
        "program": "AAIP",
        "province": "AB",
        "topic": "process",
        "lang": "en",
        "access_level": "chatbot"
      }
    },
    {
      "id": "aaip_after_nominated",
      "program": "AAIP",
      "layer": "01_program_core",
      "url": "https://www.alberta.ca/aaip-rural-entrepreneur-stream-after-you-are-nominated",
      "output_files": [
        {
          "file": "01_program_core/aaip/nominee_obligations.md",
          "section_selector": "start_to_h2_permanent_residence"
        },
        {
          "file": "01_program_core/aaip/pr_application_guide.md",
          "section_selector": "h2:contains('permanent residence')"
        }
      ],
      "frequency": "quarterly",
      "chunk_strategy": "standard",
      "has_tables": false,
      "priority_weight": 1,
      "metadata": {
        "program": "AAIP",
        "province": "AB",
        "topic": "post_nomination",
        "lang": "en",
        "access_level": "chatbot"
      }
    },
    {
      "id": "aaip_communities",
      "program": "AAIP",
      "layer": "03_province_community",
      "url": "https://www.alberta.ca/aaip-rural-entrepreneur-stream-participating-communities",
      "output_files": [
        {
          "file": "03_province_community/alberta/communities/_index.md",
          "section_selector": "full_page"
        }
      ],
      "frequency": "quarterly",
      "chunk_strategy": "standard",
      "has_tables": true,
      "priority_weight": 1,
      "metadata": {
        "program": "AAIP",
        "province": "AB",
        "topic": "communities",
        "lang": "en",
        "access_level": "chatbot"
      }
    },
    {
      "id": "aaip_processing_info",
      "program": "AAIP",
      "layer": "06_statistics",
      "url": "https://www.alberta.ca/aaip-processing-information",
      "output_files": [
        {
          "file": "06_statistics/aaip/entrepreneur_pipeline.md",
          "section_selector": "h2:contains('Entrepreneur')"
        },
        {
          "file": "06_statistics/aaip/draw_history_{year}.json",
          "section_selector": "table:contains('Draw information')",
          "output_format": "json"
        }
      ],
      "frequency": "monthly",
      "chunk_strategy": "structured",
      "has_tables": true,
      "priority_weight": 1,
      "metadata": {
        "program": "AAIP",
        "province": "AB",
        "topic": "statistics",
        "lang": "en",
        "access_level": "chatbot"
      }
    },
    {
      "id": "aaip_draw_summary_pdf",
      "program": "AAIP",
      "layer": "06_statistics",
      "url": "https://www.alberta.ca/system/files/im-aaip-draw-history-summary.pdf",
      "output_files": [
        {
          "file": "06_statistics/aaip/draw_history_{year}.json",
          "output_format": "json",
          "merge_with": "aaip_processing_info"
        }
      ],
      "frequency": "monthly",
      "chunk_strategy": "pdf_page",
      "is_pdf": true,
      "priority_weight": 1,
      "metadata": {
        "program": "AAIP",
        "province": "AB",
        "topic": "draw_history",
        "lang": "en",
        "access_level": "chatbot"
      }
    },
    {
      "id": "bcpnp_entrepreneur",
      "program": "BCPNP",
      "layer": "01_program_core",
      "url": "https://www.welcomebc.ca/immigrate-to-b-c/for-entrepreneurs-and-businesses",
      "output_files": [
        {
          "file": "01_program_core/bcpnp/base_stream.md",
          "section_selector": "h2:contains('Base Stream')"
        },
        {
          "file": "01_program_core/bcpnp/regional_stream.md",
          "section_selector": "h2:contains('Regional Stream')"
        },
        {
          "file": "01_program_core/bcpnp/strategic_projects.md",
          "section_selector": "h2:contains('Strategic Projects')"
        },
        {
          "file": "01_program_core/bcpnp/ineligible_businesses.md",
          "section_selector": "h3:contains('Ineligible businesses')"
        },
        {
          "file": "01_program_core/bcpnp/performance_agreement.md",
          "section_selector": "h3:contains('Performance Agreement')"
        },
        {
          "file": "01_program_core/bcpnp/fees.md",
          "section_selector": "h2:contains('Fees')"
        }
      ],
      "frequency": "quarterly",
      "chunk_strategy": "standard",
      "has_tables": true,
      "priority_weight": 1,
      "metadata": {
        "program": "BCPNP",
        "province": "BC",
        "topic": "program_core",
        "lang": "en",
        "access_level": "chatbot"
      }
    },
    {
      "id": "bcpnp_documents",
      "program": "BCPNP",
      "layer": "02_documents_compliance",
      "url": "https://www.welcomebc.ca/immigrate-to-b-c/about-the-bc-provincial-nominee-program/documents",
      "output_files": [
        {
          "file": "02_documents_compliance/checklists/bcpnp_document_checklist.md",
          "section_selector": "full_page"
        }
      ],
      "frequency": "quarterly",
      "chunk_strategy": "standard",
      "has_tables": false,
      "priority_weight": 1,
      "metadata": {
        "program": "BCPNP",
        "province": "BC",
        "topic": "documents",
        "lang": "en",
        "access_level": "chatbot"
      }
    },
    {
      "id": "bcpnp_regional_communities",
      "program": "BCPNP",
      "layer": "03_province_community",
      "url": "https://www.welcomebc.ca/immigrate-to-b-c/about-the-bc-provincial-nominee-program/regional-immigration",
      "output_files": [
        {
          "file": "03_province_community/bc/economic_regions/_index.md",
          "section_selector": "full_page"
        }
      ],
      "frequency": "quarterly",
      "chunk_strategy": "standard",
      "has_tables": true,
      "priority_weight": 1,
      "metadata": {
        "program": "BCPNP",
        "province": "BC",
        "topic": "communities",
        "lang": "en",
        "access_level": "chatbot"
      }
    },
    {
      "id": "bcpnp_invitations",
      "program": "BCPNP",
      "layer": "06_statistics",
      "url": "https://www.welcomebc.ca/immigrate-to-b-c/about-the-bc-provincial-nominee-program/invitations-to-apply",
      "output_files": [
        {
          "file": "06_statistics/bcpnp/ei_draw_history_{year}.json",
          "section_selector": "table:contains('invitation')",
          "output_format": "json"
        },
        {
          "file": "06_statistics/bcpnp/ei_pool_snapshot.md",
          "section_selector": "pool statistics section"
        }
      ],
      "frequency": "monthly",
      "chunk_strategy": "structured",
      "has_tables": true,
      "priority_weight": 1,
      "metadata": {
        "program": "BCPNP",
        "province": "BC",
        "topic": "draw_history",
        "lang": "en",
        "access_level": "chatbot"
      }
    },
    {
      "id": "ircc_language_tests",
      "program": "IRCC",
      "layer": "02_documents_compliance",
      "url": "https://www.canada.ca/en/immigration-refugees-citizenship/corporate/publications-manuals/operational-bulletins-manuals/standard-requirements/language-requirements/test-equivalency-charts.html",
      "output_files": [
        {
          "file": "02_documents_compliance/language_tests.md",
          "section_selector": "full_page"
        }
      ],
      "frequency": "annual",
      "chunk_strategy": "standard",
      "has_tables": true,
      "priority_weight": 1,
      "metadata": {
        "program": "BOTH",
        "topic": "language_requirements",
        "lang": "en",
        "access_level": "chatbot"
      }
    },
    {
      "id": "ircc_eca",
      "program": "IRCC",
      "layer": "02_documents_compliance",
      "url": "https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/documents/education-assessed/how.html",
      "output_files": [
        {
          "file": "02_documents_compliance/eca_guide.md",
          "section_selector": "full_page"
        }
      ],
      "frequency": "annual",
      "chunk_strategy": "standard",
      "has_tables": false,
      "priority_weight": 1,
      "metadata": {
        "program": "BOTH",
        "topic": "education_credential",
        "lang": "en",
        "access_level": "chatbot"
      }
    },
    {
      "id": "ircc_processing_times",
      "program": "IRCC",
      "layer": "06_statistics",
      "url": "https://www.canada.ca/en/immigration-refugees-citizenship/services/application/check-processing-times.html",
      "output_files": [
        {
          "file": "06_statistics/ircc/pnp_processing_times.md",
          "section_selector": "provincial nominee section"
        }
      ],
      "frequency": "quarterly",
      "chunk_strategy": "standard",
      "has_tables": true,
      "priority_weight": 1,
      "metadata": {
        "program": "IRCC",
        "topic": "processing_times",
        "lang": "en",
        "access_level": "chatbot"
      }
    }
  ]
}
```

---

## Entry point: `crawl.py`

Claude Code viết file này:

```python
#!/usr/bin/env python3
"""
LNC Knowledge Base Crawler
Entry point cho GitHub Actions và local run.

Usage:
  python crawl.py --frequency quarterly
  python crawl.py --frequency monthly
  python crawl.py --frequency annual
  python crawl.py --id aaip_eligibility          # chạy một source cụ thể
  python crawl.py --all                           # chạy tất cả
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

from crawlers.aaip_crawler import AAIPCrawler
from crawlers.bcpnp_crawler import BCPNPCrawler
from crawlers.ircc_crawler import IRCCCrawler
from crawlers.pdf_crawler import PDFCrawler
from validators.schema_validator import validate_output

CONFIG_PATH = Path("config/sources.json")
OUTPUT_ROOT = Path("output/lnc-knowledge-base")


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text())


def filter_sources(sources: list, frequency: str = None, source_id: str = None) -> list:
    if source_id:
        return [s for s in sources if s["id"] == source_id]
    if frequency:
        return [s for s in sources if s["frequency"] == frequency]
    return sources


def get_crawler(source: dict):
    program = source["program"]
    if source.get("is_pdf"):
        return PDFCrawler(source, OUTPUT_ROOT)
    if program == "AAIP":
        return AAIPCrawler(source, OUTPUT_ROOT)
    if program == "BCPNP":
        return BCPNPCrawler(source, OUTPUT_ROOT)
    if program == "IRCC":
        return IRCCCrawler(source, OUTPUT_ROOT)
    raise ValueError(f"Unknown program: {program}")


async def run(sources: list):
    results = {"success": [], "failed": [], "skipped": []}
    
    for source in sources:
        print(f"\n→ Crawling: {source['id']} ({source['url'][:60]}...)")
        try:
            crawler = get_crawler(source)
            output_files = await crawler.run()
            
            for f in output_files:
                errors = validate_output(f, source)
                if errors:
                    print(f"  ⚠ Validation errors in {f}: {errors}")
                    results["failed"].append(source["id"])
                else:
                    print(f"  ✓ Written: {f}")
                    results["success"].append(source["id"])
                    
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            results["failed"].append(source["id"])

    # Summary
    print(f"\n{'='*50}")
    print(f"✓ Success: {len(results['success'])}")
    print(f"✗ Failed:  {len(results['failed'])}")
    if results["failed"]:
        print(f"  Failed IDs: {', '.join(results['failed'])}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--frequency", choices=["monthly", "quarterly", "annual"])
    parser.add_argument("--id", help="Run single source by ID")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    config = load_config()
    sources = config["sources"]

    if args.id:
        sources = filter_sources(sources, source_id=args.id)
    elif args.frequency:
        sources = filter_sources(sources, frequency=args.frequency)
    elif not args.all:
        parser.print_help()
        sys.exit(1)

    if not sources:
        print("No sources matched.")
        sys.exit(1)

    print(f"Running {len(sources)} source(s) at {datetime.now().isoformat()}")
    asyncio.run(run(sources))


if __name__ == "__main__":
    main()
```

---

## Base crawler: `crawlers/base_crawler.py`

```python
import re
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

import frontmatter
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode


class BaseCrawler(ABC):
    def __init__(self, source: dict, output_root: Path):
        self.source = source
        self.output_root = output_root
        self.year = str(datetime.now().year)

    async def fetch_markdown(self, url: str) -> str:
        """Crawl URL và trả về markdown content."""
        config = BrowserConfig(headless=True, verbose=False)
        run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
        
        async with AsyncWebCrawler(config=config) as crawler:
            result = await crawler.arun(url=url, config=run_config)
            if not result.success:
                raise RuntimeError(f"Crawl failed for {url}: {result.error_message}")
            return result.markdown

    def extract_section(self, markdown: str, selector: str) -> str:
        """Tách section từ markdown dựa trên selector."""
        if selector == "full_page":
            return markdown

        # Tách theo heading
        if selector.startswith("h2:contains("):
            keyword = re.search(r"contains\('(.+?)'\)", selector).group(1)
            return self._extract_by_heading(markdown, keyword, level=2)

        if selector.startswith("h3:contains("):
            keyword = re.search(r"contains\('(.+?)'\)", selector).group(1)
            return self._extract_by_heading(markdown, keyword, level=3)

        # Tách theo table keyword
        if selector.startswith("table:contains("):
            keyword = re.search(r"contains\('(.+?)'\)", selector).group(1)
            return self._extract_table_section(markdown, keyword)

        return markdown

    def _extract_by_heading(self, markdown: str, keyword: str, level: int) -> str:
        """Trích đoạn từ heading chứa keyword đến heading cùng cấp tiếp theo."""
        prefix = "#" * level + " "
        lines = markdown.split("\n")
        start_idx = None
        
        for i, line in enumerate(lines):
            if line.startswith(prefix) and keyword.lower() in line.lower():
                start_idx = i
                break

        if start_idx is None:
            # Thử case-insensitive partial match
            for i, line in enumerate(lines):
                if line.startswith(prefix) and any(
                    w in line.lower() for w in keyword.lower().split()
                ):
                    start_idx = i
                    break

        if start_idx is None:
            return markdown  # fallback: trả về toàn bộ

        # Tìm end: heading cùng cấp tiếp theo
        end_idx = len(lines)
        for i in range(start_idx + 1, len(lines)):
            if lines[i].startswith(prefix) and not lines[i].startswith(prefix + "#"):
                end_idx = i
                break

        return "\n".join(lines[start_idx:end_idx]).strip()

    def _extract_table_section(self, markdown: str, keyword: str) -> str:
        """Trích đoạn chứa table với keyword."""
        lines = markdown.split("\n")
        table_start = None
        
        for i, line in enumerate(lines):
            if "|" in line and keyword.lower() in "\n".join(lines[max(0,i-5):i+5]).lower():
                # Tìm đầu table
                table_start = i
                while table_start > 0 and "|" in lines[table_start - 1]:
                    table_start -= 1
                break

        if table_start is None:
            return ""

        # Tìm cuối table
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
        """Ghi file .md với YAML frontmatter."""
        meta = {
            **self.source["metadata"],
            "source_id": self.source["id"],
            "source_url": self.source["url"],
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "version": "1.0",
            "chunk_strategy": self.source.get("chunk_strategy", "standard"),
            "priority_weight": self.source.get("priority_weight", 1),
            "retrieval_strategy": "parent_child" if "communities" in str(path) else "direct",
        }
        if extra_meta:
            meta.update(extra_meta)

        post = frontmatter.Post(content, **meta)
        path.write_text(frontmatter.dumps(post), encoding="utf-8")

    def write_json(self, path: Path, data: dict | list):
        """Ghi file .json với metadata wrapper."""
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
        path.write_text(json.dumps(wrapper, ensure_ascii=False, indent=2), encoding="utf-8")

    @abstractmethod
    async def run(self) -> list[Path]:
        """Chạy crawler và trả về danh sách files đã ghi."""
        pass
```

---

## AAIP Crawler: `crawlers/aaip_crawler.py`

```python
import json
import re
from pathlib import Path

from .base_crawler import BaseCrawler
from processors.table_converter import tables_to_narrative
from processors.section_splitter import split_sections


class AAIPCrawler(BaseCrawler):

    async def run(self) -> list[Path]:
        markdown = await self.fetch_markdown(self.source["url"])
        written = []

        for output_cfg in self.source["output_files"]:
            path = self.build_output_path(output_cfg["file"])
            selector = output_cfg.get("section_selector", "full_page")
            content = self.extract_section(markdown, selector)

            if not content.strip():
                print(f"  ⚠ Empty content for selector '{selector}' — skipping {path.name}")
                continue

            # Convert tables nếu file có bảng
            if self.source.get("has_tables"):
                content = tables_to_narrative(content)

            fmt = output_cfg.get("output_format", "markdown")
            if fmt == "json":
                data = self._parse_draw_table(content)
                self.write_json(path, data)
            else:
                self.write_markdown(path, content, {"file_role": path.stem})

            written.append(path)

        return written

    def _parse_draw_table(self, content: str) -> list[dict]:
        """Parse bảng draw history thành list of dicts."""
        rows = []
        lines = [l for l in content.split("\n") if "|" in l]
        
        if len(lines) < 2:
            return rows

        # Header row
        headers = [h.strip().lower().replace(" ", "_") for h in lines[0].split("|") if h.strip()]
        
        for line in lines[2:]:  # Skip header + separator
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if len(cells) == len(headers):
                rows.append(dict(zip(headers, cells)))

        return rows
```

---

## BC PNP Crawler: `crawlers/bcpnp_crawler.py`

```python
from pathlib import Path
from .base_crawler import BaseCrawler
from processors.table_converter import tables_to_narrative


class BCPNPCrawler(BaseCrawler):

    async def run(self) -> list[Path]:
        markdown = await self.fetch_markdown(self.source["url"])
        written = []

        for output_cfg in self.source["output_files"]:
            path = self.build_output_path(output_cfg["file"])
            selector = output_cfg.get("section_selector", "full_page")
            content = self.extract_section(markdown, selector)

            if not content.strip():
                print(f"  ⚠ Empty content for '{selector}' — skipping {path.name}")
                continue

            if self.source.get("has_tables"):
                content = tables_to_narrative(content)

            fmt = output_cfg.get("output_format", "markdown")
            if fmt == "json":
                data = self._parse_invitation_table(content)
                self.write_json(path, data)
            else:
                self.write_markdown(path, content, {"file_role": path.stem})

            written.append(path)

        return written

    def _parse_invitation_table(self, content: str) -> list[dict]:
        """Parse BC PNP invitation table."""
        rows = []
        lines = [l for l in content.split("\n") if "|" in l]
        
        if len(lines) < 2:
            return rows

        headers = [h.strip().lower().replace(" ", "_") for h in lines[0].split("|") if h.strip()]
        for line in lines[2:]:
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if len(cells) == len(headers):
                rows.append(dict(zip(headers, cells)))

        return rows
```

---

## IRCC Crawler: `crawlers/ircc_crawler.py`

```python
from pathlib import Path
from .base_crawler import BaseCrawler
from processors.table_converter import tables_to_narrative


class IRCCCrawler(BaseCrawler):

    async def run(self) -> list[Path]:
        markdown = await self.fetch_markdown(self.source["url"])
        written = []

        for output_cfg in self.source["output_files"]:
            path = self.build_output_path(output_cfg["file"])
            selector = output_cfg.get("section_selector", "full_page")
            content = self.extract_section(markdown, selector)

            if not content.strip():
                print(f"  ⚠ Empty content — skipping {path.name}")
                continue

            if self.source.get("has_tables"):
                content = tables_to_narrative(content)

            self.write_markdown(path, content, {"file_role": path.stem})
            written.append(path)

        return written
```

---

## PDF Crawler: `crawlers/pdf_crawler.py`

```python
import io
import json
from pathlib import Path

import httpx
import pypdf

from .base_crawler import BaseCrawler


class PDFCrawler(BaseCrawler):

    async def run(self) -> list[Path]:
        written = []
        
        print(f"  Downloading PDF: {self.source['url']}")
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.get(self.source["url"])
            resp.raise_for_status()

        pdf_bytes = io.BytesIO(resp.content)
        reader = pypdf.PdfReader(pdf_bytes)
        
        pages_text = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                pages_text.append({"page": i + 1, "text": text.strip()})

        for output_cfg in self.source["output_files"]:
            path = self.build_output_path(output_cfg["file"])
            fmt = output_cfg.get("output_format", "json")

            if fmt == "json":
                # Parse draw table từ PDF text
                rows = self._parse_pdf_draw_table(pages_text)
                self.write_json(path, rows)
            else:
                # Ghi raw text
                combined = "\n\n".join(p["text"] for p in pages_text)
                self.write_markdown(path, combined)

            written.append(path)

        return written

    def _parse_pdf_draw_table(self, pages: list[dict]) -> list[dict]:
        """Extract draw data từ PDF pages."""
        import re
        rows = []
        
        date_pattern = re.compile(
            r"(\w+ \d+, \d{4})\s*[–-]\s*(.+?)\s+(\d+)\s+(\d+)"
        )
        
        for page in pages:
            for match in date_pattern.finditer(page["text"]):
                rows.append({
                    "date": match.group(1),
                    "stream": match.group(2).strip(),
                    "cutoff_score": match.group(3),
                    "invitations": match.group(4),
                    "source_page": page["page"],
                })

        return rows
```

---

## Table converter: `processors/table_converter.py`

```python
import re


def tables_to_narrative(markdown: str) -> str:
    """
    Convert Markdown tables sang narrative text.
    Đây là bước bắt buộc trước khi embed các file có bảng biểu
    để tránh chunk bị cắt gãy giữa chừng cột.

    Input:
        | Criteria | Max Points | Mandatory |
        |---|---|---|
        | Business Location | 25 | Yes |

    Output:
        Tiêu chí Business Location có điểm tối đa là 25 điểm. Bắt buộc: Yes.
    """
    lines = markdown.split("\n")
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Phát hiện bắt đầu của table
        if "|" in line and i + 1 < len(lines) and re.match(r"\|[\s\-:]+\|", lines[i + 1]):
            # Parse header
            headers = [h.strip() for h in line.split("|") if h.strip()]
            i += 2  # Skip separator row

            # Parse rows
            while i < len(lines) and "|" in lines[i]:
                cells = [c.strip() for c in lines[i].split("|") if c.strip()]
                if len(cells) == len(headers):
                    narrative = _row_to_narrative(headers, cells)
                    result.append(narrative)
                i += 1
        else:
            result.append(line)
            i += 1

    return "\n".join(result)


def _row_to_narrative(headers: list[str], cells: list[str]) -> str:
    """Convert một row thành câu narrative."""
    if not cells or not any(cells):
        return ""

    # Pattern đặc biệt cho points grid
    h_lower = [h.lower() for h in headers]
    
    if "criteria" in h_lower[0] or "tiêu chí" in h_lower[0]:
        parts = []
        for h, c in zip(headers, cells):
            if c and c != "—":
                parts.append(f"{h}: {c}")
        return ". ".join(parts) + "."

    # Pattern chung
    parts = []
    for h, c in zip(headers, cells):
        if c and c not in ("—", "-", "N/A", ""):
            parts.append(f"{h} là {c}")

    if not parts:
        return ""

    return ". ".join(parts) + "."
```

---

## Validator: `validators/schema_validator.py`

```python
from pathlib import Path
import frontmatter


REQUIRED_FIELDS = [
    "source_id", "source_url", "last_updated",
    "program", "topic", "lang", "access_level",
    "chunk_strategy", "priority_weight",
]


def validate_output(path: Path, source: dict) -> list[str]:
    """Validate file output. Trả về list errors (empty = OK)."""
    errors = []

    if not path.exists():
        return [f"File not found: {path}"]

    if path.suffix == ".json":
        return _validate_json(path)

    if path.suffix == ".md":
        return _validate_markdown(path, source)

    return errors


def _validate_markdown(path: Path, source: dict) -> list[str]:
    errors = []

    try:
        post = frontmatter.load(str(path))
    except Exception as e:
        return [f"Cannot parse frontmatter: {e}"]

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in post.metadata:
            errors.append(f"Missing frontmatter field: {field}")

    # Check content not empty
    if len(post.content.strip()) < 100:
        errors.append(f"Content too short ({len(post.content)} chars) — possible crawl failure")

    # Check no raw table if has_tables source
    if source.get("has_tables") and "|---|" in post.content:
        errors.append("Raw markdown table found — table_converter may have failed")

    return errors


def _validate_json(path: Path) -> list[str]:
    import json
    errors = []

    try:
        data = json.loads(path.read_text())
    except Exception as e:
        return [f"Invalid JSON: {e}"]

    if "metadata" not in data:
        errors.append("Missing 'metadata' key in JSON")

    if "data" not in data:
        errors.append("Missing 'data' key in JSON")
    elif not data["data"]:
        errors.append("Empty 'data' array — possible parse failure")

    return errors
```

---

## Requirements: `requirements.txt`

```
crawl4ai==0.4.247
pypdf==4.2.0
httpx==0.27.0
pydantic==2.7.0
python-frontmatter==1.1.0
```

---

## GitHub Actions Workflows

### Monthly: `.github/workflows/crawl_monthly.yml`

```yaml
name: Crawl — Monthly (draw history)

on:
  schedule:
    - cron: "0 2 1 * *"    # 2:00 AM UTC ngày 1 mỗi tháng
  workflow_dispatch:         # Cho phép chạy thủ công

jobs:
  crawl:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - name: Checkout crawler repo
        uses: actions/checkout@v4

      - name: Checkout KB repo
        uses: actions/checkout@v4
        with:
          repository: ${{ secrets.KB_REPO }}
          token: ${{ secrets.KB_REPO_TOKEN }}
          path: output/lnc-knowledge-base

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Install Playwright browsers
        run: python -m playwright install chromium --with-deps

      - name: Run monthly crawl
        run: python crawl.py --frequency monthly

      - name: Commit and push changes
        working-directory: output/lnc-knowledge-base
        run: |
          git config user.name "lnc-crawler-bot"
          git config user.email "crawler@lnc.internal"
          git add -A
          
          if git diff --staged --quiet; then
            echo "No changes to commit"
          else
            MONTH=$(date +"%Y-%m")
            git commit -m "chore: monthly crawl ${MONTH} — draw history update"
            git push
          fi

      - name: Notify on failure
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `Crawl failed: monthly ${new Date().toISOString().slice(0,7)}`,
              body: `Monthly crawl workflow failed. Check: ${context.serverUrl}/${context.repo.owner}/${context.repo.repo}/actions/runs/${context.runId}`,
              labels: ["crawl-failure"]
            })
```

### Quarterly: `.github/workflows/crawl_quarterly.yml`

```yaml
name: Crawl — Quarterly (program core)

on:
  schedule:
    - cron: "0 3 1 1,4,7,10 *"   # 3:00 AM UTC ngày 1 tháng 1/4/7/10
  workflow_dispatch:

jobs:
  crawl:
    runs-on: ubuntu-latest
    timeout-minutes: 60

    steps:
      - uses: actions/checkout@v4

      - name: Checkout KB repo
        uses: actions/checkout@v4
        with:
          repository: ${{ secrets.KB_REPO }}
          token: ${{ secrets.KB_REPO_TOKEN }}
          path: output/lnc-knowledge-base

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - run: pip install -r requirements.txt
      - run: python -m playwright install chromium --with-deps

      - name: Run quarterly crawl
        run: python crawl.py --frequency quarterly

      - name: Validate outputs
        run: python -c "
          from validators.schema_validator import validate_output
          from pathlib import Path
          import json, sys
          cfg = json.loads(Path('config/sources.json').read_text())
          errors = []
          for s in cfg['sources']:
              if s['frequency'] != 'quarterly': continue
              for o in s['output_files']:
                  p = Path('output/lnc-knowledge-base') / o['file'].replace('{year}', '2025')
                  if p.exists():
                      errs = validate_output(p, s)
                      if errs: errors.extend(errs)
          if errors:
              for e in errors: print(f'ERROR: {e}')
              sys.exit(1)
          print(f'All validations passed')
          "

      - name: Commit and push
        working-directory: output/lnc-knowledge-base
        run: |
          git config user.name "lnc-crawler-bot"
          git config user.email "crawler@lnc.internal"
          git add -A
          if git diff --staged --quiet; then
            echo "No changes to commit"
          else
            QUARTER=$(python3 -c "from datetime import date; d=date.today(); print(f'Q{(d.month-1)//3+1}-{d.year}')")
            git commit -m "chore: quarterly crawl ${QUARTER} — program core update"
            git push
          fi

      - name: Notify on failure
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `Crawl failed: quarterly ${new Date().toISOString().slice(0,7)}`,
              body: `Quarterly crawl failed. Run: ${context.serverUrl}/${context.repo.owner}/${context.repo.repo}/actions/runs/${context.runId}`,
              labels: ["crawl-failure"]
            })
```

### Annual: `.github/workflows/crawl_annual.yml`

```yaml
name: Crawl — Annual (language tests, ECA, legal refs)

on:
  schedule:
    - cron: "0 4 15 1 *"    # 4:00 AM UTC ngày 15 tháng 1 hàng năm
  workflow_dispatch:

jobs:
  crawl:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - uses: actions/checkout@v4

      - name: Checkout KB repo
        uses: actions/checkout@v4
        with:
          repository: ${{ secrets.KB_REPO }}
          token: ${{ secrets.KB_REPO_TOKEN }}
          path: output/lnc-knowledge-base

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - run: pip install -r requirements.txt
      - run: python -m playwright install chromium --with-deps

      - name: Run annual crawl
        run: python crawl.py --frequency annual

      - name: Commit and push
        working-directory: output/lnc-knowledge-base
        run: |
          git config user.name "lnc-crawler-bot"
          git config user.email "crawler@lnc.internal"
          git add -A
          if git diff --staged --quiet; then
            echo "No changes"
          else
            YEAR=$(date +"%Y")
            git commit -m "chore: annual crawl ${YEAR} — language tests, ECA update"
            git push
          fi
```

---

## GitHub Secrets cần thiết

Vào **Settings → Secrets and variables → Actions** trong crawler repo, thêm:

| Secret | Giá trị |
|--------|---------|
| `KB_REPO` | `your-org/lnc-knowledge-base` |
| `KB_REPO_TOKEN` | Personal Access Token với quyền `repo` trên KB repo |

---

## Chạy local để test

```bash
# Setup
git clone <crawler-repo>
cd lnc-kb-crawler
pip install -r requirements.txt
python -m playwright install chromium

# Test một source cụ thể
python crawl.py --id aaip_eligibility

# Test toàn bộ quarterly
python crawl.py --frequency quarterly

# Test tất cả (dry-run check)
python crawl.py --all
```

---

## Checklist trước khi deploy

- [ ] `requirements.txt` đầy đủ, version pinned
- [ ] `config/sources.json` đúng format, tất cả URLs hợp lệ
- [ ] `output/lnc-knowledge-base/` gitignored trong crawler repo
- [ ] Secrets `KB_REPO` và `KB_REPO_TOKEN` đã set
- [ ] Test local ít nhất 2–3 sources trước khi enable schedule
- [ ] Tạo issue label `crawl-failure` trong repo để nhận notifications
- [ ] Verify KB repo có branch `main` và crawler bot có write access

---

## Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân | Giải pháp |
|-----|-------------|-----------|
| `Crawl failed: 403` | Government site block bot | Thêm `user_agent` vào `BrowserConfig` |
| `Empty content for selector` | Heading thay đổi sau update site | Kiểm tra lại selector trong `sources.json` |
| `Raw markdown table found` | `table_converter` miss case | Debug `tables_to_narrative()` với content thực tế |
| `Missing frontmatter field` | `write_markdown()` thiếu field | Thêm field vào `metadata` trong `sources.json` |
| `Invalid JSON` | PDF parse fail | Kiểm tra lại regex trong `_parse_pdf_draw_table()` |
| `timeout-minutes exceeded` | Site chậm hoặc quá nhiều sources | Tăng timeout hoặc chia nhỏ workflow |
