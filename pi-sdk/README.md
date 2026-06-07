# News Reader (Pi SDK version)

A tech news scraper using [Pi's SDK](https://pi.dev) programmatically. The entire agent, including custom tools and system prompt, lives in a single TypeScript file.

## Prerequisites

- [Pi](https://pi.dev) installed globally: `npm install -g @earendil-works/pi-coding-agent`
- An API key for a supported provider (e.g. `ANTHROPIC_API_KEY`)

## Setup

```bash
npm install
```

## Usage

```bash
npm run scrape
```

This runs `scrape.ts`, which creates an agent session with inline tool definitions and a custom system prompt. No `.pi/` directory needed. Results are saved to `data/`.

## How it differs from the CLI version

The [CLI version](../pi-dev/) uses Pi's extension system (`.pi/extensions/`) and a system prompt file (`.pi/SYSTEM.md`). This version passes everything programmatically via `createAgentSession()`:

- Tools are `customTools` objects, not an extension file
- System prompt is a `systemPromptOverride` string
- Built-in tools are disabled with `noTools: "builtin"`
- Session is in-memory (no persistence)
