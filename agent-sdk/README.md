# News Reader: Agent SDK

The Agent SDK implementation from the [Agent SDK version](https://roman.pt/posts/agent-sdk-rewrite/) blog post. Everything lives in a single Python file: data models, sub-agent definitions, an in-process MCP tool, and the orchestration loop.

## Prerequisites

Python 3.12+, [uv](https://docs.astral.sh/uv/). Set `ANTHROPIC_API_KEY` in your environment.

## Usage

```bash
export ANTHROPIC_API_KEY=sk-ant-...
uv run python scrape_sdk.py

# Browse results:
uv run python web.py      # http://localhost:5001
```

## How it works

`scrape_sdk.py` uses `claude_agent_sdk.query()` with an in-process MCP tool for saving articles. The orchestrator (Haiku) spawns two `news-fetcher` sub-agents in parallel (one for Hacker News, one for Lobsters). Each sub-agent fetches the front page with `WebFetch` and saves relevant items by calling `save_news_item` through the MCP server.

`permission_mode="dontAsk"` auto-denies any tool not in the explicit `allowed_tools` list, so the script runs non-interactively. Domain-scoped rules like `WebFetch(domain:news.ycombinator.com)` restrict which sites the agents can fetch.
