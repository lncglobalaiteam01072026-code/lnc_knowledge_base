from pathlib import Path


def split_sections(markdown: str, selectors: list[dict]) -> dict[str, str]:
    """
    Tách markdown thành nhiều sections dựa trên danh sách selectors.
    Trả về dict mapping file_key -> content.
    """
    sections = {}
    for sel in selectors:
        key = sel.get("file", "")
        heading = sel.get("heading", "")
        if heading:
            sections[key] = _extract_heading_block(markdown, heading)
        else:
            sections[key] = markdown
    return sections


def _extract_heading_block(markdown: str, heading: str) -> str:
    lines = markdown.split("\n")
    start = None
    level = None

    for i, line in enumerate(lines):
        stripped = line.lstrip("#")
        depth = len(line) - len(stripped)
        if depth > 0 and heading.lower() in line.lower():
            start = i
            level = depth
            break

    if start is None:
        return ""

    prefix = "#" * level + " "
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith(prefix) and not lines[i].startswith(prefix + "#"):
            end = i
            break

    return "\n".join(lines[start:end]).strip()
