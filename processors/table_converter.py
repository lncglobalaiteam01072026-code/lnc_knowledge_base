import re

# Matches both `| --- |` and `---|---` separator rows (any combo of |, -, :, spaces)
_SEP_RE = re.compile(r"^[\s|:\-]+$")


def tables_to_narrative(markdown: str) -> str:
    """
    Convert Markdown tables sang narrative text.
    Bắt buộc trước khi embed các file có bảng để tránh chunk bị cắt gãy giữa cột.

    Input:
        | Criteria | Max Points | Mandatory |
        |---|---|---|
        | Business Location | 25 | Yes |

    Output:
        Criteria: Business Location. Max Points: 25. Mandatory: Yes.
    """
    lines = markdown.split("\n")
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        next_line = lines[i + 1].rstrip() if i + 1 < len(lines) else ""
        is_sep = bool(next_line and _SEP_RE.match(next_line) and "|" in next_line and "-" in next_line)
        if "|" in line and is_sep:
            headers = [h.strip() for h in line.split("|") if h.strip()]
            i += 2  # Skip separator row

            while i < len(lines) and "|" in lines[i]:
                cells = [c.strip() for c in lines[i].split("|") if c.strip()]
                if len(cells) == len(headers):
                    narrative = _row_to_narrative(headers, cells)
                    result.append(narrative)
                i += 1
        else:
            result.append(line)
            i += 1

    # Strip standalone HR artifacts (--- separator rows emitted by Alberta.ca tables)
    result = [ln for ln in result if ln.strip() not in ("---", "* * *", "***")]
    return "\n".join(result)


def _row_to_narrative(headers: list[str], cells: list[str]) -> str:
    """Convert một row thành câu narrative."""
    if not cells or not any(cells):
        return ""

    h_lower = [h.lower() for h in headers]

    if "criteria" in h_lower[0] or "tiêu chí" in h_lower[0]:
        parts = []
        for h, c in zip(headers, cells):
            if c and c != "—":
                parts.append(f"{h}: {c}")
        return ". ".join(parts) + "."

    parts = []
    for h, c in zip(headers, cells):
        if c and c not in ("—", "-", "N/A", ""):
            parts.append(f"{h}: {c}")

    if not parts:
        return ""

    return ". ".join(parts) + "."
