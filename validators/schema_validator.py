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

    for field in REQUIRED_FIELDS:
        if field not in post.metadata:
            errors.append(f"Missing frontmatter field: {field}")

    if len(post.content.strip()) < 100:
        errors.append(f"Content too short ({len(post.content)} chars) — possible crawl failure")

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
