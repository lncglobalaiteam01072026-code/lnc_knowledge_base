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
            content = self.extract_section(
                markdown,
                selector,
                stop_before=output_cfg.get("stop_before"),
                start_after=output_cfg.get("start_after"),
            )

            if not content.strip():
                print(f"  [WARN] Empty content for selector '{selector}' — skipping {path.name}")
                continue

            fmt = output_cfg.get("output_format", "markdown")

            if self.source.get("has_tables") and fmt != "json":
                content = tables_to_narrative(content)
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

        headers = [re.sub(r'[*,;]+', '', h).strip().lower().replace(" ", "_") for h in lines[0].split("|") if h.strip()]

        for line in lines[2:]:  # Skip header + separator
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if len(cells) == len(headers):
                rows.append(dict(zip(headers, cells)))

        return rows
