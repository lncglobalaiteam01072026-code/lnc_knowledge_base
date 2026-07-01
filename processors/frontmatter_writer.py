from pathlib import Path

import frontmatter


def write_with_frontmatter(path: Path, content: str, meta: dict):
    """Ghi file markdown với YAML frontmatter."""
    post = frontmatter.Post(content, **meta)
    path.write_text(frontmatter.dumps(post), encoding="utf-8")
