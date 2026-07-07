#!/usr/bin/env python3
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

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
import time
from datetime import datetime, timezone
from pathlib import Path

from crawlers.aaip_crawler import AAIPCrawler
from crawlers.bcpnp_crawler import BCPNPCrawler
from crawlers.csv_crawler import CSVCrawler
from crawlers.ircc_crawler import IRCCCrawler
from crawlers.news_crawler import NewsCrawler
from crawlers.nz_crawler import NZCrawler
from crawlers.pdf_crawler import PDFCrawler
from crawlers.raw_crawler import RawFileCrawler
from crawlers.reddit_crawler import RedditCrawler
from validators.schema_validator import validate_output

CONFIG_PATH = Path("config/sources.json")
OUTPUT_ROOT = Path("output/lnc-knowledge-base")


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text())


def filter_sources(sources: list, frequency: str = None, source_id: str = None, layer: str = None) -> list:
    if source_id:
        return [s for s in sources if s["id"] == source_id]
    result = sources
    if layer:
        result = [s for s in result if s.get("layer") == layer]
    if frequency:
        result = [s for s in result if s["frequency"] == frequency]
    return result


def get_crawler(source: dict):
    program = source["program"]
    if source.get("raw_download"):
        return RawFileCrawler(source, OUTPUT_ROOT)
    if source.get("is_pdf"):
        return PDFCrawler(source, OUTPUT_ROOT)
    if source.get("is_csv"):
        return CSVCrawler(source, OUTPUT_ROOT)
    if program == "REDDIT":
        return RedditCrawler(source, OUTPUT_ROOT)
    if program in ("CICNEWS", "JOBBANK", "NEWS"):
        return NewsCrawler(source, OUTPUT_ROOT)
    if program == "AAIP":
        return AAIPCrawler(source, OUTPUT_ROOT)
    if program == "BCPNP":
        return BCPNPCrawler(source, OUTPUT_ROOT)
    if program == "IRCC":
        return IRCCCrawler(source, OUTPUT_ROOT)
    if program == "NZAEWV":
        return NZCrawler(source, OUTPUT_ROOT)
    raise ValueError(f"Unknown program: {program}")


async def _crawl_one(source: dict, sem: asyncio.Semaphore) -> dict:
    """Crawl một source, dùng semaphore để giới hạn concurrency."""
    async with sem:
        sid = source["id"]
        print(f"\n>> Crawling: {sid} ({source['url'][:60]}...)")
        t0 = time.monotonic()
        record = {
            "id": sid,
            "url": source["url"],
            "program": source.get("program", ""),
            "topic": source.get("metadata", {}).get("topic", ""),
            "status": "ok",
            "changed": False,
            "files": [],
            "errors": [],
            "duration_s": 0,
        }
        try:
            crawler = get_crawler(source)
            output_files = await crawler.run()
            record["duration_s"] = round(time.monotonic() - t0, 1)
            record["changed"] = len(crawler._changed_files) > 0

            for f in output_files:
                rel = str(Path(f).relative_to(OUTPUT_ROOT)) if Path(f).is_relative_to(OUTPUT_ROOT) else str(f)
                validation_errors = validate_output(f, source)
                if validation_errors:
                    print(f"  [WARN] {sid}: {validation_errors}")
                    record["status"] = "failed"
                    record["errors"].extend(validation_errors)
                else:
                    changed_mark = " [changed]" if Path(f) in crawler._changed_files else ""
                    print(f"  [OK] {sid}: {f}{changed_mark}")
                    record["files"].append(rel)

        except Exception as e:
            record["duration_s"] = round(time.monotonic() - t0, 1)
            print(f"  [FAIL] {sid}: {e}")
            record["status"] = "failed"
            record["errors"].append(str(e))

        return record


async def run(sources: list, concurrency: int = 3) -> list:
    """Run sources concurrently (default 3 at a time) and return result records."""
    sem = asyncio.Semaphore(concurrency)
    tasks = [_crawl_one(s, sem) for s in sources]
    records = await asyncio.gather(*tasks)
    records = list(records)

    success = [r for r in records if r["status"] == "ok"]
    failed = [r for r in records if r["status"] == "failed"]
    print(f"\n{'='*50}")
    print(f"[OK] Success: {len(success)}")
    print(f"[FAIL] Failed:  {len(failed)}")
    if failed:
        print(f"  Failed IDs: {', '.join(r['id'] for r in failed)}")
    if failed and not success:
        sys.exit(1)

    return records


_TOPIC_LABELS = {
    "eligibility": "Điều kiện đủ điều kiện",
    "process": "Quy trình nộp hồ sơ",
    "post_nomination": "Sau khi được đề cử",
    "draw_history": "Lịch sử draws / mời ứng viên",
    "statistics": "Thống kê & pipeline",
    "processing_times": "Thời gian xử lý hồ sơ",
    "faq": "Câu hỏi thường gặp (FAQ)",
    "language_requirements": "Yêu cầu ngôn ngữ",
    "education_credential": "Chứng chỉ học vấn (ECA)",
    "communities": "Danh sách cộng đồng",
    "forms": "Biểu mẫu",
    "guide": "Hướng dẫn",
    "legal": "Văn bản pháp lý",
    "pr_approvals": "Số lượng phê duyệt thường trú nhân (PR)",
    "authorization": "Biểu mẫu ủy quyền",
    "representative": "Biểu mẫu đại diện",
    "invitations": "Lịch sử mời ứng viên",
}

_NEXT_UPDATE = {
    "weekly": "tuần tới (thứ Hai)",
    "biweekly": "2 tuần tới (ngày 1 hoặc 15)",
    "monthly": "tháng tới (ngày 1)",
    "quarterly": "quý tới",
    "annual": "năm tới (tháng 1)",
}

_PROGRAM_NAMES = {
    "AAIP": "AAIP — Alberta Advantage Immigration Program",
    "BCPNP": "BCPNP — BC Provincial Nominee Program",
    "IRCC": "IRCC — Immigration, Refugees and Citizenship Canada",
    "REDDIT": "Reddit — Cộng đồng di trú",
    "CICNEWS": "CIC News — Tin tức di trú",
    "JOBBANK": "Job Bank — Thị trường việc làm Canada",
    "NZAEWV": "NZAEWV — New Zealand Accredited Employer Work Visa",
    "NEWS": "Immigration.ca — Tin tức nhập cư Canada",
}


def _topic_label(record: dict) -> str:
    topic = record.get("topic") or ""
    return _TOPIC_LABELS.get(topic, topic or record["id"])


def _build_content(records: list, run_label: str, started_at: datetime) -> str:
    # Vietnam time = UTC+7
    vn_hour = (started_at.hour + 7) % 24
    vn_period = "sáng" if vn_hour < 12 else ("chiều" if vn_hour < 18 else "tối")
    ts_vn = f"{started_at.strftime('%d/%m/%Y')} lúc {vn_hour:02d}:{started_at.strftime('%M')} {vn_period} (giờ VN)"

    success = [r for r in records if r["status"] == "ok"]
    failed = [r for r in records if r["status"] == "failed"]

    lines = [
        "# Tóm tắt dữ liệu crawl mới nhất",
        "",
        f"**Cập nhật lúc:** {ts_vn}  ",
        f"**Loại cập nhật:** {run_label.capitalize()}  ",
        f"**Kết quả:** {len(records)} nguồn | ✅ {len(success)} thành công | ❌ {len(failed)} thất bại",
        "",
        "---",
        "",
        "## Dữ liệu đã cập nhật",
    ]

    # Group by program
    programs = {}
    for r in records:
        prog = r["program"] or "Khác"
        programs.setdefault(prog, []).append(r)

    for prog, recs in programs.items():
        prog_name = _PROGRAM_NAMES.get(prog, prog)
        lines += ["", f"### {prog_name}"]
        for r in recs:
            icon = "✅" if r["status"] == "ok" else "❌"
            label = _topic_label(r)
            if r["status"] == "ok":
                lines.append(f"- {icon} {label}")
            else:
                err_summary = r["errors"][0][:120] if r["errors"] else "Lỗi không xác định"
                lines.append(f"- {icon} **{label}** — _{err_summary}_")

    if failed:
        lines += [
            "",
            "---",
            "",
            "## ⚠️ Nguồn bị lỗi",
            "",
            "Các nguồn dưới đây chưa được cập nhật lần này, hệ thống sẽ thử lại vào lần chạy tiếp theo:",
            "",
        ]
        for r in failed:
            lines.append(f"- **{_topic_label(r)}** ({r['program']}): {r['url']}")

    next_update = _NEXT_UPDATE.get(run_label, "lần chạy tiếp theo")
    lines += [
        "",
        "---",
        "",
        f"_Cập nhật tiếp theo: {next_update}._",
    ]

    return "\n".join(lines) + "\n"


def write_meta_layer(records: list, run_label: str, started_at: datetime, all_sources: list) -> None:
    """Ghi 00_meta/: sources.yaml, crawl_log.jsonl, last_updated.json."""
    import json as _json
    import yaml

    meta_dir = OUTPUT_ROOT / "00_meta"
    meta_dir.mkdir(parents=True, exist_ok=True)

    # sources.yaml — map toàn bộ sources từ config
    sources_data = [
        {
            "id": s["id"],
            "program": s.get("program", ""),
            "frequency": s.get("frequency", ""),
            "url": s.get("url", ""),
            "outputs": [f["file"] for f in s.get("output_files", [])],
        }
        for s in all_sources
    ]
    (meta_dir / "sources.yaml").write_text(
        yaml.dump(sources_data, allow_unicode=True, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )

    # crawl_log.jsonl — append 1 dòng/source/run
    run_id = f"{started_at.strftime('%Y-%m-%dT%H:%MZ')}_{run_label}"
    log_path = meta_dir / "crawl_log.jsonl"
    with log_path.open("a", encoding="utf-8") as f:
        for r in records:
            entry = {
                "run_id": run_id,
                "source_id": r["id"],
                "status": r["status"],
                "changed": r.get("changed", False),
                "duration_s": r["duration_s"],
                "timestamp": started_at.isoformat(),
            }
            f.write(_json.dumps(entry, ensure_ascii=False) + "\n")

    # last_updated.json — update chỉ các source thành công
    lu_path = meta_dir / "last_updated.json"
    last_updated = _json.loads(lu_path.read_text(encoding="utf-8")) if lu_path.exists() else {}
    for r in records:
        if r["status"] == "ok":
            last_updated[r["id"]] = started_at.isoformat()
    lu_path.write_text(_json.dumps(last_updated, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[META] Updated: {meta_dir}/")


def write_crawl_log(records: list, run_label: str, started_at: datetime) -> None:
    content = _build_content(records, run_label, started_at)
    summary_file = OUTPUT_ROOT / "CRAWL_SUMMARY.md"
    summary_file.write_text(content, encoding="utf-8")
    print(f"\n[LOG] Updated: {summary_file}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--frequency", choices=["daily", "weekly", "biweekly", "monthly", "quarterly", "annual"])
    parser.add_argument("--id", help="Run single source by ID")
    parser.add_argument("--ids", nargs="+", help="Run multiple sources by ID (parallel)")
    parser.add_argument("--layer", help="Filter by layer (e.g. 07_unofficial, 08_news_updates)")
    parser.add_argument("--concurrency", type=int, default=3, help="Max concurrent crawls (default 3)")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    config = load_config()
    all_sources = config["sources"]
    sources = all_sources

    if args.ids:
        sources = [s for s in all_sources if s["id"] in args.ids]
    elif args.id:
        sources = filter_sources(sources, source_id=args.id)
    elif args.frequency or args.layer:
        sources = filter_sources(sources, frequency=args.frequency, layer=args.layer)
    elif not args.all:
        parser.print_help()
        sys.exit(1)

    if not sources:
        print("No sources matched.")
        sys.exit(1)

    started_at = datetime.now(timezone.utc)
    run_label = args.id or args.frequency or "all"
    print(f"Running {len(sources)} source(s) at {started_at.isoformat()} [concurrency={args.concurrency}]")

    records = asyncio.run(run(sources, concurrency=args.concurrency))
    if OUTPUT_ROOT.exists():
        write_meta_layer(records, run_label, started_at, all_sources)
        write_crawl_log(records, run_label, started_at)


if __name__ == "__main__":
    main()
