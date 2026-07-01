from pathlib import Path

import httpx

from .base_crawler import BaseCrawler


class RawFileCrawler(BaseCrawler):
    """Download file(s) as-is without processing.

    Supports two modes:
    - Single URL: source["url"] used for all output_files (same binary written N times)
    - Per-file URL: each output_files entry has its own "url" field
    """

    async def run(self) -> list[Path]:
        written = []
        async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
            for output_cfg in self.source["output_files"]:
                url = output_cfg.get("url") or self.source["url"]
                path = self.build_output_path(output_cfg["file"])
                path.parent.mkdir(parents=True, exist_ok=True)

                print(f"  Downloading: {url.split('/')[-1]}")
                resp = await client.get(url)
                resp.raise_for_status()

                path.write_bytes(resp.content)
                size_kb = len(resp.content) // 1024
                print(f"    Saved {size_kb} KB -> {path.name}")
                written.append(path)

        return written
