# News Reader (Pi version)

A tech news scraper built as a [Pi](https://pi.dev) extension. Fetches the front pages of Hacker News and Lobsters, filters for relevant items, and saves them as JSON files.

## Prerequisites

- [Pi](https://pi.dev) installed globally: `npm install -g @earendil-works/pi-coding-agent`
- An API key for a supported provider (e.g. `ANTHROPIC_API_KEY`)

## Setup

```bash
npm install
```

This installs `turndown` (HTML-to-markdown converter), the only project dependency. Pi's own packages resolve from the global install.

## Usage

```bash
npm run scrape
```

This runs:

```bash
pi -p --no-builtin-tools --no-context-files --no-session "Go"
```

Pi loads the extension from `.pi/extensions/news-tools.ts` (registers `web_fetch` and `save_news_item` tools) and reads `.pi/SYSTEM.md` as the system prompt. The agent fetches both sites and saves relevant items to `data/`.

To use a different model:

```bash
pi -p --no-builtin-tools --no-context-files --no-session --model openai/gpt-4o-mini "Go"
```

## Project structure

```
.pi/
├── extensions/
│   └── news-tools.ts     # web_fetch and save_news_item tools
└── SYSTEM.md              # system prompt (replaces Pi's default)
data/                      # output: one JSON file per news item
package.json               # only dependency: turndown
```
