import asyncio
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent
from urllib.parse import urlparse

import httpx
from markdownify import MarkdownConverter
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

# ------------------------------------
# Configuration
# ------------------------------------

ALLOWED_DOMAINS = ["news.ycombinator.com", "lobste.rs"]
DATA_DIR = Path(__file__).parent / "data"
MODEL = "anthropic:claude-haiku-4-5"

http_client = httpx.AsyncClient(
    timeout=30.0,
    headers={"User-Agent": "news-reader-bot/1.0"},
)


# ------------------------------------
# Data model
# ------------------------------------


class NewsItem(BaseModel):
    title: str = Field(description="Article headline")
    url: str = Field(description="Link to the article")
    source: str = Field(description="Site name, e.g. 'Hacker News' or 'Lobsters'")
    tags: list[str] = Field(description="Topic tags, e.g. ['python', 'ai', 'devtools']")
    summary: str = Field(description="One-sentence summary")
    discussion_url: str | None = Field(
        default=None, description="URL to the discussion page"
    )


class ScraperResult(BaseModel):
    items: list[NewsItem] = Field(description="All scraped news items")
    report: str = Field(description="Brief bullet-list report of what was scraped")


# ------------------------------------
# Sub-agent: scrapes one site
# ------------------------------------

site_scraper = Agent(
    MODEL,
    output_type=list[NewsItem],
    instructions=dedent("""\
        You scrape a single news site. Fetch the front page, identify items
        relevant to Python, developer tools, AI/ML, and software architecture.
        Return a list of NewsItem objects. Skip items about business/funding,
        social media drama, or unrelated topics. For each item include the title,
        URL, source site name, relevant tags, a one-sentence summary, and the
        discussion URL.
    """),
)


@site_scraper.tool_plain
async def web_fetch(url: str) -> str:
    """Fetch a web page and return its content as markdown.

    Args:
        url: URL to fetch. Must be from an allowed domain.
    """
    hostname = urlparse(url).hostname
    if hostname not in ALLOWED_DOMAINS:
        raise ValueError(f"Domain not allowed: {hostname}. Allowed: {ALLOWED_DOMAINS}")
    resp = await http_client.get(url, follow_redirects=True)
    resp.raise_for_status()
    md = MarkdownConverter(strip=["img", "script", "style"]).convert(resp.text)
    return md[:50000]


# ------------------------------------
# Coordinator agent
# ------------------------------------

coordinator = Agent(
    MODEL,
    output_type=ScraperResult,
    retries=3,
    instructions=dedent("""\
        You coordinate news scraping. For each site the user asks about, call
        scrape_site with the URL. Deduplicate results across sites if needed,
        then return a ScraperResult with the combined items and a brief report.

        Available sites: Hacker News (https://news.ycombinator.com),
        Lobsters (https://lobste.rs).
    """),
)


@coordinator.tool
async def scrape_site(ctx: RunContext[None], url: str) -> list[NewsItem]:
    """Scrape a news site and return relevant items.

    Args:
        url: Front page URL of the news site to scrape.
    """
    result = await site_scraper.run(f"Fetch and process: {url}", usage=ctx.usage)
    return result.output


# ------------------------------------
# Main
# ------------------------------------


async def main():
    DATA_DIR.mkdir(exist_ok=True)

    try:
        result = await coordinator.run(
            "Scrape Hacker News and Lobsters for relevant tech news.",
        )

        for item in result.output.items:
            slug = "".join(c if c.isalnum() else "-" for c in item.title.lower())[:60]
            path = DATA_DIR / f"{int(time.time())}_{slug}.json"
            data = item.model_dump()
            data["saved_at"] = datetime.now(timezone.utc).isoformat()
            path.write_text(json.dumps(data, indent=2))

        print(result.output.report)
        print(f"\nSaved {len(result.output.items)} items to {DATA_DIR}")
    finally:
        await http_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
