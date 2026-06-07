# News Reader — Pydantic AI

Same news scraper, built with [Pydantic AI](https://ai.pydantic.dev/).

## Setup

Python 3.12+, [uv](https://docs.astral.sh/uv/). Set `ANTHROPIC_API_KEY` in your environment.

```bash
export ANTHROPIC_API_KEY=sk-ant-...
uv sync
```

## Run

```bash
uv run python scrape.py
```

Results are saved as JSON files in `data/`.

## How it works

A coordinator agent delegates to a site scraper sub-agent for each requested site. The
sub-agent has a `web_fetch` tool restricted to allowed domains. The coordinator
deduplicates and returns a validated `ScraperResult` Pydantic model.
