# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "claude-agent-sdk",
# ]
# ///

import asyncio
from pathlib import Path

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

PROJECT_DIR = Path(__file__).parent


async def main():
    async for msg in query(
        prompt="/scraper",
        options=ClaudeAgentOptions(
            cwd=str(PROJECT_DIR),
        ),
    ):
        if isinstance(msg, ResultMessage):
            print(msg.result)


if __name__ == "__main__":
    asyncio.run(main())
