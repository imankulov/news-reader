# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "flask",
# ]
# ///

import json
import os
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

from flask import Flask, render_template_string

DATA_DIR = Path(__file__).parent / "data"

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>News Reader</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; color: #333; line-height: 1.6; }
        .container { max-width: 800px; margin: 0 auto; padding: 2rem 1rem; }
        h1 { margin-bottom: 0.5rem; font-size: 1.8rem; }
        .subtitle { color: #666; margin-bottom: 2rem; font-size: 0.9rem; }
        .item { background: #fff; border-radius: 8px; padding: 1.25rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
        .item h2 { font-size: 1.1rem; margin-bottom: 0.4rem; }
        .item h2 a { color: #1a1a1a; text-decoration: none; }
        .item h2 a:hover { color: #0066cc; }
        .meta { font-size: 0.8rem; color: #888; margin-bottom: 0.5rem; }
        .meta a { color: #888; text-decoration: none; }
        .meta a:hover { text-decoration: underline; }
        .summary { font-size: 0.95rem; color: #444; }
        .tags { margin-top: 0.5rem; }
        .tag { display: inline-block; background: #e8f0fe; color: #1a73e8; font-size: 0.75rem; padding: 2px 8px; border-radius: 12px; margin-right: 4px; }
        .empty { text-align: center; padding: 3rem; color: #999; }
    </style>
</head>
<body>
    <div class="container">
        <h1>News Reader</h1>
        <p class="subtitle">{{ items | length }} items from {{ sources | join(', ') }}</p>
        {% if items %}
            {% for item in items %}
            <div class="item">
                <h2><a href="{{ item.url }}" target="_blank">{{ item.title }}</a></h2>
                <div class="meta">
                    {{ item.source }}
                    &middot; {{ item.saved_at_fmt }}
                    {% if item.discussion_url %}
                        &middot; <a href="{{ item.discussion_url }}" target="_blank">discussion</a>
                    {% endif %}
                </div>
                <div class="summary">{{ item.summary }}</div>
                <div class="tags">
                    {% for tag in item.tags %}
                    <span class="tag">{{ tag }}</span>
                    {% endfor %}
                </div>
            </div>
            {% endfor %}
        {% else %}
            <div class="empty">No news items yet. Run the /scraper skill to fetch some.</div>
        {% endif %}
    </div>
</body>
</html>
"""


def _safe_url(url: str | None) -> str:
    if not url:
        return ""
    scheme = urlparse(url).scheme
    if scheme in ("http", "https"):
        return url
    return ""


def _load_items():
    items = []
    for filepath in DATA_DIR.glob("*.json"):
        try:
            item = json.loads(filepath.read_text(encoding="utf-8"))
            saved_at = datetime.fromisoformat(item["saved_at"])
            item["saved_at_fmt"] = saved_at.strftime("%b %d, %H:%M")
            item["url"] = _safe_url(item.get("url"))
            item["discussion_url"] = _safe_url(item.get("discussion_url"))
            items.append(item)
        except (json.JSONDecodeError, KeyError, OSError, ValueError):
            continue
    items.sort(key=lambda x: x.get("saved_at", ""), reverse=True)
    return items


@app.route("/")
def index():
    items = _load_items()
    sources = sorted({item["source"] for item in items}) if items else []
    return render_template_string(TEMPLATE, items=items, sources=sources)


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1", port=5001)
