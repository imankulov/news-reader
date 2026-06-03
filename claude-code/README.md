# News Reader: Claude Code

The Claude Code implementation from [Claude Code as Your Execution Environment](https://roman.pt/posts/claude-code-as-your-execution-environment/). The agent drives the flow; Python only handles storage and display.

## Prerequisites

Python 3.12+, [uv](https://docs.astral.sh/uv/), [Claude Code](https://code.claude.com/).

## Usage

```bash
# In an interactive Claude Code session:
/scraper

# Or non-interactively:
claude -p /scraper

# Browse results:
uv run web.py             # http://localhost:5001
```

There's also a minimal [Agent SDK wrapper](scrape.py) that runs the same Claude Code project programmatically. This requires `ANTHROPIC_API_KEY` set in your environment:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
uv run scrape.py
```

## Project structure

```
.
├── mcp_server.py                        # MCP server: save_news_item and list_news_items
├── scrape.py                            # Agent SDK wrapper: runs /scraper programmatically
├── web.py                               # Flask app: browse saved items
├── data/                                # JSON files, one per news item
├── .mcp.json                            # registers the MCP server
└── .claude/
    ├── settings.json                    # auto-approved tool permissions
    ├── agents/
    │   └── news-fetcher.md              # sub-agent definition
    └── skills/
        └── scraper/
            └── SKILL.md                 # entry point skill
```

## How it works

The skill (`.claude/skills/scraper/SKILL.md`) spawns two `news-fetcher` sub-agents in parallel. Each sub-agent has restricted tools: `WebFetch` (scoped to HN and Lobsters domains) and `mcp__news__save_news_item` for storage. The skill prompt assigns one site per agent. The MCP server (`mcp_server.py`) validates input with Pydantic before saving JSON files to `data/`.
