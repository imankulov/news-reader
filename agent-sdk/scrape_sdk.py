import asyncio
import json
import logging
import random
import string
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AgentDefinition,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    tool,
    create_sdk_mcp_server,
)

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# --------------------------------------
# Data model
# --------------------------------------

class NewsItem(BaseModel):
    title: str = Field(description="Article headline")
    url: str = Field(description="Link to the article")
    source: str = Field(description="Site name, e.g. 'Hacker News' or 'Lobsters'")
    tags: list[str] = Field(description="Topic tags, e.g. ['python', 'ai', 'devtools']")
    summary: str = Field(description="One-sentence summary")
    discussion_url: str | None = Field(
        default=None, description="URL to the discussion page"
    )


DATA_DIR = Path(__file__).parent / "data"


# --------------------------------------
# In-process MCP tool
# --------------------------------------

@tool(
    "save_news_item",
    "Save a news item as a JSON file in the data directory.",
    NewsItem.model_json_schema(),
)
async def save_news_item(args: dict[str, Any]) -> dict[str, Any]:
    item = NewsItem.model_validate(args)
    DATA_DIR.mkdir(exist_ok=True)
    rnd = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    slug = "".join(c if c.isalnum() else "-" for c in item.title.lower())[:60]
    path = DATA_DIR / f"{int(time.time())}-{rnd}_{slug}.json"
    data = item.model_dump()
    data["saved_at"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(data, indent=2))
    logger.debug("Saved %s", path.name)
    return {"content": [{"type": "text", "text": f"Saved: {item.title}"}]}


news_server = create_sdk_mcp_server(
    name="news",
    version="1.0.0",
    tools=[save_news_item],
)


# --------------------------------------
# Sub-agent definition
# --------------------------------------

NEWS_FETCHER = AgentDefinition(
    description="Fetch and filter news from a specific site",
    prompt="""Fetch the front page of the given news site. Identify items relevant
to these topics: Python, developer tools, AI/ML, and software architecture.

For each relevant item, call save_news_item with the title, url, source, tags,
a one-sentence summary, and the discussion page URL.

Skip items about business/funding, social media drama, or unrelated topics.""",
    tools=["WebFetch", "mcp__news__save_news_item"],
    model="haiku",
)


# --------------------------------------
# Main
# --------------------------------------

PROMPT = """Go to Hacker News (news.ycombinator.com) and Lobsters (lobste.rs).

For each site, spawn a news-fetcher sub-agent to fetch the front page and
save relevant items. Run the two sub-agents in parallel.

After both agents complete, report what was saved."""


async def main():
    logger.info("Starting news scraper")
    async for message in query(
        prompt=PROMPT,
        options=ClaudeAgentOptions(
            model="haiku",
            permission_mode="dontAsk",
            mcp_servers={"news": news_server},
            allowed_tools=[
                "Agent",
                "WebFetch(domain:news.ycombinator.com)",
                "WebFetch(domain:lobste.rs)",
                "mcp__news__save_news_item",
            ],
            agents={"news-fetcher": NEWS_FETCHER},
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    logger.debug("Tool call: %s", block.name)
                elif isinstance(block, TextBlock):
                    logger.debug("Agent: %s", block.text[:200])
        elif isinstance(message, ResultMessage):
            if message.result:
                print(message.result)
            if message.total_cost_usd:
                logger.info("Cost: $%.4f", message.total_cost_usd)


asyncio.run(main())
