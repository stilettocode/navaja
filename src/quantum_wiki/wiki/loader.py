from pathlib import Path

from .models import WikiPage


def load_markdown_pages(directory: str | Path) -> list[WikiPage]:
    """Load Markdown as data, keeping file identity stable for experiments."""
    root = Path(directory)
    pages = []
    for path in sorted(root.rglob("*.md")):
        content = path.read_text(encoding="utf-8")
        first_line = content.splitlines()[0] if content.splitlines() else path.stem
        title = first_line.removeprefix("# ").strip() or path.stem
        pages.append(WikiPage(path.stem, path, title, content))
    return pages
