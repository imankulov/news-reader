# News Reader — smolagents

Same news scraper, built with [smolagents](https://huggingface.co/docs/smolagents/) CodeAgent.

Instead of calling predefined tools, the agent writes and executes Python code in a
sandboxed Blaxel VM. The generated code fetches pages with httpx, parses HTML with
BeautifulSoup, and validates output with Pydantic.

## Setup

Python 3.12+, [uv](https://docs.astral.sh/uv/). Set `ANTHROPIC_API_KEY` in your
environment. Authenticate with Blaxel (`bl login <workspace>`).

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

A single `CodeAgent` with no tools receives the task as a prompt. It generates Python
code across multiple steps, executing each in a Blaxel sandbox (a Jupyter kernel in a
remote VM). The sandbox has full network access and can install packages with pip.
