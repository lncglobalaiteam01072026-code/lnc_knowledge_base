# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies (requires Python 3.11+)
pip install -r requirements.txt
python -m playwright install chromium --with-deps

# Run crawls by frequency
python crawl.py --frequency quarterly   # AAIP + BCPNP program core, communities, IRCC processing times
python crawl.py --frequency monthly     # Draw history (AAIP, BCPNP)
python crawl.py --frequency annual      # Language tests, ECA guide

# Run a single source by ID
python crawl.py --id aaip_eligibility

# Run all sources
python crawl.py --all

# Validate quarterly outputs
python scripts/validate_quarterly.py
```

## Architecture

This is a **knowledge base crawler** for Canadian immigration programs (AAIP, BCPNP, IRCC). It fetches government webpages and PDFs, then writes structured Markdown and JSON files to a separate KB repository checked out at `output/lnc-knowledge-base/`.

### Data flow

```
config/sources.json  →  crawl.py  →  get_crawler()  →  BaseCrawler subclass
                                                              ↓
                                                    fetch_markdown() via crawl4ai
                                                              ↓
                                                    extract_section() (selector-based)
                                                              ↓
                                                    processors/ (table conversion)
                                                              ↓
                                                    write_markdown() / write_json()
                                                              ↓
                                                    validators/schema_validator.py
```

### Source configuration (`config/sources.json`)

Each source entry controls everything:
- `frequency`: `monthly` | `quarterly` | `annual` — determines which GitHub Actions workflow runs it
- `output_files[].section_selector`: CSS-like selectors for content extraction — `full_page`, `h2:contains('...')`, `h3:contains('...')`, `table:contains('...')`
- `output_files[].output_format`: `markdown` (default) or `json`
- `has_tables`: triggers `tables_to_narrative()` conversion before writing
- `is_pdf`: routes to `PDFCrawler` instead of a web crawler

### Crawler classes

- `BaseCrawler` — fetch, section extraction, and file writing logic shared by all crawlers
- `AAIPCrawler` / `BCPNPCrawler` / `IRCCCrawler` — thin subclasses; primarily differ in `_parse_*_table()` methods for JSON draw history output
- `PDFCrawler` — downloads PDF via `httpx`, extracts text with `pypdf`, parses draw records with regex

### Processors

- `table_converter.tables_to_narrative()` — converts Markdown tables to prose sentences to prevent vector DB chunks from being split across table columns
- `section_splitter.split_sections()` — alternative heading-based splitter (used less frequently; `BaseCrawler.extract_section()` is the primary path)
- `processors/frontmatter_writer.py` — thin wrapper around `python-frontmatter`; actual writing goes through `BaseCrawler.write_markdown()`

### Output structure

Files are written under `output/lnc-knowledge-base/` (gitignored here; it's a separate repo). Layers in the path reflect knowledge hierarchy:
- `01_program_core/` — eligibility, how-to-apply, post-nomination
- `02_documents_compliance/` — language tests, ECA, document checklists
- `03_province_community/` — community/regional lists
- `06_statistics/` — draw history (JSON) and processing times

All `.md` outputs include YAML frontmatter with `source_id`, `source_url`, `last_updated`, `program`, `topic`, `lang`, `access_level`, `chunk_strategy`, and `priority_weight`. All `.json` outputs are wrapped as `{"metadata": {...}, "data": [...]}`.

### GitHub Actions workflows

Three workflows in `.github/workflows/` check out the KB repo as a subpath, run the crawl, then commit changes back to the KB repo using secrets `KB_REPO` (repo name) and `KB_REPO_TOKEN` (PAT with write access). The quarterly workflow also runs `scripts/validate_quarterly.py` as a gate before committing.

### Validation

`validators/schema_validator.validate_output()` checks:
- Markdown: all required frontmatter fields present, content ≥ 100 chars, no raw `|---|` tables (indicates `table_converter` failure)
- JSON: has `metadata` and `data` keys, `data` is non-empty
