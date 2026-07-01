import re
from pathlib import Path
from .base_crawler import BaseCrawler, _clean_url_artifacts
from processors.table_converter import tables_to_narrative


class BCPNPCrawler(BaseCrawler):

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
                print(f"  [WARN] Empty content for '{selector}' — skipping {path.name}")
                continue

            fmt = output_cfg.get("output_format", "markdown")

            if self.source.get("has_tables") and fmt != "json":
                content = tables_to_narrative(content)
            if fmt == "json":
                data = self._parse_invitation_table(content)
                self.write_json(path, data)
            else:
                self.write_markdown(path, content, {"file_role": path.stem})

            written.append(path)

        return written

    def _parse_invitation_table(self, content: str) -> list[dict]:
        """Parse BC PNP invitation table — pipe format or narrative fallback."""
        rows = []
        pipe_lines = [l for l in content.split("\n") if "|" in l]

        if len(pipe_lines) >= 2:
            # Standard pipe table
            headers = [re.sub(r'[*,;]+', '', h).strip().lower().replace(" ", "_")
                       for h in pipe_lines[0].split("|") if h.strip()]
            for line in pipe_lines[2:]:
                cells = [_clean_url_artifacts(c.strip()) for c in line.split("|") if c.strip()]
                if len(cells) == len(headers):
                    rows.append(dict(zip(headers, cells)))
        else:
            # Narrative format: "Date: X. Stream: Y. Minimum Score: Z. Number of Invitations: N."
            date_re = re.compile(
                r"Date:\s*(.+?)\.\s*Stream:\s*(.+?)\.\s*Minimum Score:\s*(.+?)\.\s*Number of Invitations:\s*(\d+)",
                re.IGNORECASE,
            )
            for line in content.split("\n"):
                m = date_re.search(line)
                if m:
                    rows.append({
                        "date": m.group(1).strip(),
                        "stream": m.group(2).strip(),
                        "minimum_score": m.group(3).strip(),
                        "number_of_invitations": m.group(4).strip(),
                    })

        return rows
