# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "fastmcp",
#     "pydantic",
# ]
# ///

import json
import random
import string
from pathlib import Path
from datetime import datetime, timezone

from fastmcp import FastMCP
from pydantic import BaseModel, Field

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

mcp = FastMCP("news")


class NewsItem(BaseModel):
    title: str = Field(description="Article headline")
    url: str = Field(description="Link to the article")
    source: str = Field(description="Site name, e.g. 'Hacker News' or 'Lobsters'")
    tags: list[str] = Field(description="Topic tags, e.g. ['python', 'ai', 'devtools']")
    summary: str = Field(description="One-sentence summary of the article")
    discussion_url: str | None = Field(default=None, description="URL to the comments/discussion page")


@mcp.tool
def save_news_item(item: NewsItem) -> str:
    """Save a news item as a JSON file in the data directory."""
    now = datetime.now(timezone.utc)
    rnd = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    filename = now.strftime("%Y%m%d-%H%M%S") + f"-{rnd}.json"
    filepath = DATA_DIR / filename

    data = item.model_dump()
    data["saved_at"] = now.isoformat()

    filepath.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return f"Saved: {item.title}"


@mcp.tool
def list_news_items() -> list[dict]:
    """Return all saved news items, most recent first."""
    items = []
    for filepath in sorted(DATA_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            items.append(json.loads(filepath.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            continue
    return items


if __name__ == "__main__":
    mcp.run()
