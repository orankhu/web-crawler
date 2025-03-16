"""
title: Web Crawl
author: orankhu
git_url: https://github.com/orankhu/web-crawler.git
description: Crawl the web page url using Craw4AI
required_open_webui_version: 0.4.0
requirements: crawl4ai
version: 0.4.0
licence: MIT
"""

from pydantic import BaseModel, Field
from typing import Optional, Callable, Any, Dict
from crawl4ai import *


class Tools:
    class Valves(BaseModel):
        IGNORE_LINKS: bool = Field(
            default=True, description="Ignore links in the web page"
        )
        IGNORE_IMAGES: bool = Field(
            default=True, description="Ignore images in the web page"
        )

    def __init__(self):
        self.valves = self.Valves()

    async def web_crawl(
        self, url: str, __event_emitter__: Optional[Callable[[Dict], Any]] = None
    ) -> str:
        """
        Crawl the web page url using Craw4AI.
        :param url: The web page URL to crawl.
        :return: Crawled web page content in markdown format.
        """

        # Status emitter helper
        async def emit_status(
            description: str, status: str = "in_progress", done: bool = False
        ):
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": description,
                            "status": status,
                            "done": done,
                        },
                    }
                )

        # Initial status
        await emit_status(f"Reading: {url}", "crawling")

        try:
            async with AsyncWebCrawler() as crawler:
                config = CrawlerRunConfig(
                    markdown_generator=DefaultMarkdownGenerator(
                        options={
                            "ignore_links": self.valves.IGNORE_LINKS,
                            "ignore_images": self.valves.IGNORE_IMAGES,
                        }
                    )
                )
                result = await crawler.arun(url=url, config=config)
                response = result.markdown
                await emit_status(f"Read completed", "done", done=True)
                return response

        except Exception as e:
            error_msg = f"Error reading url: {str(e)}"
            await emit_status(error_msg, status="error", done=True)
            return error_msg
