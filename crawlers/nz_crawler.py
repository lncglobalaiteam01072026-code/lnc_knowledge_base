from pathlib import Path

from .base_crawler import BaseCrawler
from processors.table_converter import tables_to_narrative


class NZCrawler(BaseCrawler):
    """Crawler cho các chương trình di trú New Zealand (INZ — immigration.govt.nz)."""

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

            if self.source.get("has_tables"):
                content = tables_to_narrative(content)

            self.write_markdown(path, content, {"file_role": path.stem})
            written.append(path)

        return written
