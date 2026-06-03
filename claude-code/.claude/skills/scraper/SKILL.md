---
name: scraper
description: Crawl tech news sites and save relevant items
allowed-tools: Agent
---

Go to Hacker News and Lobsters. For each site, spawn a sub-agent
using the Agent tool with `subagent_type: "news-fetcher"` to fetch
the front page and save items relevant to my interests: Python,
developer tools, AI/ML, and software architecture.

Run the two sub-agents in parallel and in the background (one for
Hacker News, one for Lobsters) by making both Agent tool calls in a
single message with `run_in_background: true`.

After both agents complete, output a brief bullet-list report of
what was scraped: each bullet should show the item title, source,
and tags.
