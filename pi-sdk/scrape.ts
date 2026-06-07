import {
  createAgentSession,
  DefaultResourceLoader,
  defineTool,
  getAgentDir,
  SessionManager,
} from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import TurndownService from "turndown";
import { writeFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const ALLOWED_DOMAINS = ["news.ycombinator.com", "lobste.rs"];
const DATA_DIR = join(process.cwd(), "data");
const turndown = new TurndownService();

const SYSTEM_PROMPT = `You are a news scraper agent. Your job is to fetch tech news and save relevant items.

Fetch the front page of Hacker News (news.ycombinator.com) and Lobsters (lobste.rs). Identify items relevant to: Python, developer tools, AI/ML, and software architecture.

For each relevant item, call save_news_item with:
- title: the item title
- url: the link URL
- source: "Hacker News" or "Lobsters"
- tags: relevant topic tags
- summary: a one-sentence summary of what the item is about
- discussion_url: the comments/discussion page URL

Skip items about business/funding, social media drama, or topics unrelated to the interests listed above.

After saving all items, output a brief bullet-list report of what was scraped.`;

const webFetchTool = defineTool({
  name: "web_fetch",
  label: "Fetch URL",
  description: `Fetch a web page and return its content as markdown. Allowed domains: ${ALLOWED_DOMAINS.join(", ")}`,
  parameters: Type.Object({
    url: Type.String({ description: "URL to fetch" }),
  }),
  async execute(_id, params) {
    const hostname = new URL(params.url).hostname;
    if (!ALLOWED_DOMAINS.includes(hostname)) {
      throw new Error(`Domain not allowed: ${hostname}`);
    }
    const resp = await fetch(params.url);
    const html = await resp.text();
    return { content: [{ type: "text", text: turndown.turndown(html) }], details: {} };
  },
});

const saveNewsItemTool = defineTool({
  name: "save_news_item",
  label: "Save News Item",
  description: "Save a news item as a JSON file in the data directory.",
  parameters: Type.Object({
    title: Type.String({ description: "Article headline" }),
    url: Type.String({ description: "Link to the article" }),
    source: Type.String({ description: "Site name, e.g. 'Hacker News' or 'Lobsters'" }),
    tags: Type.Array(Type.String(), { description: "Topic tags, e.g. ['python', 'ai', 'devtools']" }),
    summary: Type.String({ description: "One-sentence summary" }),
    discussion_url: Type.Optional(Type.String({ description: "URL to the discussion page" })),
  }),
  async execute(_id, params) {
    mkdirSync(DATA_DIR, { recursive: true });
    const slug = params.title.toLowerCase().replace(/[^a-z0-9]+/g, "-").slice(0, 60);
    const path = join(DATA_DIR, `${Date.now()}_${slug}.json`);
    const data = { ...params, saved_at: new Date().toISOString() };
    writeFileSync(path, JSON.stringify(data, null, 2));
    return { content: [{ type: "text", text: `Saved: ${params.title}` }], details: {} };
  },
});

async function main() {
  const resourceLoader = new DefaultResourceLoader({
    cwd: process.cwd(),
    agentDir: getAgentDir(),
    systemPromptOverride: () => SYSTEM_PROMPT,
    appendSystemPromptOverride: () => [],
    skillsOverride: () => ({ skills: [], diagnostics: [] }),
  });
  await resourceLoader.reload();

  const { session } = await createAgentSession({
    resourceLoader,
    customTools: [webFetchTool, saveNewsItemTool],
    tools: ["web_fetch", "save_news_item"],
    sessionManager: SessionManager.inMemory(),
  });

  try {
    session.subscribe((event) => {
      if (event.type === "message_update" && event.assistantMessageEvent.type === "text_delta") {
        process.stdout.write(event.assistantMessageEvent.delta);
      }
    });

    await session.prompt("Go");
    console.log();
  } finally {
    session.dispose();
  }
}

main();
