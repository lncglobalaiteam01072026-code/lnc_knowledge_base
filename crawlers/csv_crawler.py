import csv
import io
from pathlib import Path

import httpx

from .base_crawler import BaseCrawler


class CSVCrawler(BaseCrawler):
    """Download a CSV from IRCC open data and write filtered JSON."""

    async def run(self) -> list[Path]:
        written = []

        print(f"  Downloading CSV: {self.source['url']}")
        async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
            resp = await client.get(self.source["url"])
            resp.raise_for_status()

        text = resp.content.decode("utf-8-sig")  # strip BOM if present
        # Auto-detect delimiter: tab if first line has more tabs than commas
        first_line = text.split("\n")[0]
        delimiter = "\t" if first_line.count("\t") > first_line.count(",") else ","
        rows = list(csv.DictReader(io.StringIO(text), delimiter=delimiter))

        for output_cfg in self.source["output_files"]:
            path = self.build_output_path(output_cfg["file"])
            filters = output_cfg.get("filters", {})
            filtered = self._apply_filters(rows, filters)

            self.write_json(path, filtered)
            written.append(path)

        return written

    def _apply_filters(self, rows: list[dict], filters: dict) -> list[dict]:
        """Filter CSV rows by column value matchers defined in sources.json."""
        result = rows
        for col, matcher in filters.items():
            if isinstance(matcher, list):
                result = [r for r in result if r.get(col, "").strip() in matcher]
            else:
                result = [r for r in result if r.get(col, "").strip() == str(matcher)]
        return result
