import json
import time
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent

from smolagents import CodeAgent, LiteLLMModel

DATA_DIR = Path(__file__).parent / "data"
MODEL = "anthropic/claude-haiku-4-5"

TASK = dedent("""\
    Scrape the front pages of Hacker News (https://news.ycombinator.com) and
    Lobsters (https://lobste.rs). For each site, find articles relevant to
    Python, developer tools, AI/ML, and software architecture. Skip items about
    business/funding, social media drama, or unrelated topics.

    Return the result by calling final_answer() with a dictionary:
    {
        "items": [
            {
                "title": "Article headline",
                "url": "https://...",
                "source": "Hacker News" or "Lobsters",
                "tags": ["python", "ai", ...],
                "summary": "One-sentence summary",
                "discussion_url": "https://..." or None
            },
            ...
        ],
        "report": "Brief bullet-list summary of what was scraped"
    }

    Validate your result with Pydantic before returning:

    ```
    from pydantic import BaseModel, Field

    class NewsItem(BaseModel):
        title: str
        url: str
        source: str
        tags: list[str]
        summary: str
        discussion_url: str | None = None

    class ScraperResult(BaseModel):
        items: list[NewsItem]
        report: str

    # Validate before returning
    validated = ScraperResult(**your_result)
    final_answer(validated.model_dump())
    ```

    Use httpx to fetch pages and beautifulsoup4 to parse HTML.
    Only fetch from news.ycombinator.com and lobste.rs.
""")


def main():
    DATA_DIR.mkdir(exist_ok=True)

    agent = CodeAgent(
        tools=[],
        model=LiteLLMModel(MODEL),
        executor_type="blaxel",
        executor_kwargs={"sandbox_name": "news-reader"},
        additional_authorized_imports=["httpx", "bs4", "pydantic"],
        max_steps=15,
        verbosity_level=2,
    )

    result = agent.run(TASK)

    if isinstance(result, dict) and "items" in result:
        for item in result["items"]:
            slug = "".join(c if c.isalnum() else "-" for c in item["title"].lower())[:60]
            path = DATA_DIR / f"{int(time.time())}_{slug}.json"
            data = dict(item)
            data["saved_at"] = datetime.now(timezone.utc).isoformat()
            path.write_text(json.dumps(data, indent=2))

        print(result.get("report", ""))
        print(f"\nSaved {len(result['items'])} items to {DATA_DIR}")
    else:
        print("Unexpected result format:")
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
