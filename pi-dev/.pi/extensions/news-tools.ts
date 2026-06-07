import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import TurndownService from "turndown";
import { writeFileSync, mkdirSync } from "node:fs";
import { join, dirname } from "node:path";

const ALLOWED_DOMAINS = ["news.ycombinator.com", "lobste.rs"];
const DATA_DIR = join(process.cwd(), "data");
const turndown = new TurndownService();

export default function (pi: ExtensionAPI) {
  pi.registerTool({
    name: "web_fetch",
    label: "Fetch URL",
    description: `Fetch a web page and return its content as markdown. Allowed domains: ${ALLOWED_DOMAINS.join(", ")}`,
    parameters: Type.Object({
      url: Type.String({ description: "URL to fetch" }),
    }),
    async execute(_id, params) {
      const hostname = new URL(params.url).hostname;
      if (!ALLOWED_DOMAINS.includes(hostname)) {
        throw new Error(`Domain not allowed: ${hostname}. Allowed: ${ALLOWED_DOMAINS.join(", ")}`);
      }
      const resp = await fetch(params.url);
      const html = await resp.text();
      return { content: [{ type: "text", text: turndown.turndown(html) }], details: {} };
    },
  });

  pi.registerTool({
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
}
