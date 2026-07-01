from pathlib import Path
import httpx
from .base_crawler import BaseCrawler
from processors.table_converter import tables_to_narrative

_PNP_LABELS = {
    "pnp-base": "Provincial nominees (base stream)",
    "pnp-ee": "Provincial nominees via Express Entry",
}


class IRCCCrawler(BaseCrawler):

    async def run(self) -> list[Path]:
        if self.source.get("is_json_api"):
            return await self._run_json_api()
        return await self._run_html()

    async def _run_json_api(self) -> list[Path]:
        resp = httpx.get(self.source["url"], timeout=20, follow_redirects=True)
        resp.raise_for_status()
        data = resp.json()

        last_updated = data.get("default-update", {}).get("flpt_lastupdated", "unknown")
        keys = self.source.get("json_keys", [])

        lines = [
            "# IRCC PNP Processing Times",
            "",
            f"**Last updated:** {last_updated}",
            "",
        ]
        for key in keys:
            label = _PNP_LABELS.get(key, key)
            flpt = data.get("current-flpt", {}).get(key, "N/A")
            waiting = data.get("total-people", {}).get(key, "N/A")
            lines += [
                f"## {label}",
                "",
                f"Estimated processing time: {flpt}",
                "",
                f"Total people waiting: {waiting}",
                "",
            ]

        content = "\n".join(lines).strip()
        output_cfg = self.source["output_files"][0]
        path = self.build_output_path(output_cfg["file"])
        self.write_markdown(path, content, {"file_role": path.stem})
        return [path]

    async def _run_html(self) -> list[Path]:
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
                print(f"  ⚠ Empty content — skipping {path.name}")
                continue

            if self.source.get("has_tables"):
                content = tables_to_narrative(content)

            self.write_markdown(path, content, {"file_role": path.stem})
            written.append(path)

        return written
