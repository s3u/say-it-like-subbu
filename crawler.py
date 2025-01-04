import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Set
from urllib.robotparser import RobotFileParser

import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

@dataclass
class CrawlerConfig:
    max_depth: int = 20
    max_size: int = 10 * 1024 * 1024
    timeout: int = 30
    retry_count: int = 3
    rate_limit: float = 0.1
    user_agent: str = 'Mozilla/5.0 (compatible; MyCrawler/1.0)'

class WebCrawler:
    def __init__(self, config: CrawlerConfig = None):
        self.config = config or CrawlerConfig()
        self.visited: Set[str] = set()
        self.session = None
        self.robot_parser = RobotFileParser()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def can_fetch(self, url: str) -> bool:
        robot_url = urljoin(url, '/robots.txt')
        try:
            async with self.session.get(robot_url) as response:
                if response.status == 200:
                    self.robot_parser.parse(await response.text())
                    return self.robot_parser.can_fetch(self.config.user_agent, url)
        except Exception:
            return True
        return True

    async def crawl(self, url: str, domain: str, depth: int = 0) -> Set[str]:
        if depth >= self.config.max_depth or url in self.visited:
            return self.visited

        if not await self.can_fetch(url):
            self.logger.info(f"Skipping {url} as per robots.txt")
            return self.visited

        self.visited.add(url)
        self.logger.info(f"Crawling: {url}")

        try:
            async with self.session.get(
                url, 
                headers={'User-Agent': self.config.user_agent},
                timeout=self.config.timeout
            ) as response:
                if not response.headers.get('content-type', '').startswith('text/html'):
                    return self.visited

                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                
                tasks = []
                for link in soup.find_all('a', href=True):
                    next_url = urljoin(url, link['href'])
                    if urlparse(next_url).netloc == domain:
                        await asyncio.sleep(self.config.rate_limit)
                        tasks.append(self.crawl(next_url, domain, depth + 1))

                await asyncio.gather(*tasks)

        except Exception as e:
            self.logger.error(f"Error crawling {url}: {str(e)}")

        return self.visited

    async def crawl_site(self, start_url: str) -> Set[str]:
        domain = urlparse(start_url).netloc
        async with aiohttp.ClientSession() as session:
            self.session = session
            return await self.crawl(start_url, domain)

def crawl_the_site(start_url: str) -> Set[str]:
    crawler = WebCrawler()
    return asyncio.run(crawler.crawl_site(start_url))

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python crawler.py <start_url>")
        sys.exit(1)
    
    start_url = sys.argv[1]
    visited_links = crawl_the_site(start_url)
    print(f"Total visited links: {len(visited_links)}")
