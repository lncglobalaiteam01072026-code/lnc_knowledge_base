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
                rows = self._parse_pdf_draw_table(pages_text)
                if not rows:
                    print(f"  [WARN] PDF parse yielded 0 rows — preserving existing {path.name}")
                    written.append(path)
                    continue
                # Merge with existing data when merge_with is set
                if output_cfg.get("merge_with") and path.exists():
                    try:
                        existing = json.loads(path.read_text(encoding="utf-8"))
                        existing_rows = existing.get("data", [])
                        existing_dates = {r.get("date") for r in existing_rows if r.get("date")}
                        new_rows = [r for r in rows if r.get("date") not in existing_dates]
                        rows = existing_rows + new_rows
                        print(f"  Merged {len(new_rows)} new PDF rows into existing {len(existing_rows)} web rows")
                    except Exception:
                        pass
                self.write_json(path, rows)
            else:
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
