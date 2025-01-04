import unittest
from unittest.mock import patch, Mock, AsyncMock
import aiohttp
from crawler import WebCrawler, CrawlerConfig

class TestWebCrawler(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.config = CrawlerConfig(max_depth=2, rate_limit=0)
        self.crawler = WebCrawler(self.config)
        self.session_mock = AsyncMock(spec=aiohttp.ClientSession)
        self.crawler.session = self.session_mock

    async def test_can_fetch(self):
        response_mock = AsyncMock()
        response_mock.status = 200
        response_mock.text.return_value = "User-agent: *\nAllow: /"
        self.session_mock.get.return_value.__aenter__.return_value = response_mock

        result = await self.crawler.can_fetch("http://example.com")
        self.assertTrue(result)

    async def test_crawl_single_page(self):
        response_mock = AsyncMock()
        response_mock.headers = {'content-type': 'text/html'}
        response_mock.text.return_value = '<html><a href="http://example.com/page1">Link</a></html>'
        self.session_mock.get.return_value.__aenter__.return_value = response_mock

        visited = await self.crawler.crawl("http://example.com", "example.com")
        
        self.assertIn("http://example.com", visited)
        self.assertIn("http://example.com/page1", visited)

    async def test_crawl_respects_depth_limit(self):
        response_mock = AsyncMock()
        response_mock.headers = {'content-type': 'text/html'}
        response_mock.text.return_value = '<html><a href="http://example.com/deep">Deep</a></html>'
        self.session_mock.get.return_value.__aenter__.return_value = response_mock

        self.crawler.config.max_depth = 1
        print(self.crawler.config)
        visited = await self.crawler.crawl("http://example.com", "example.com")
        print(visited)
        self.assertIn("http://example.com", visited)
        self.assertNotIn("http://example.com/deep", visited)

    async def test_crawl_handles_error(self):
        self.session_mock.get.side_effect = aiohttp.ClientError

        visited = await self.crawler.crawl("http://example.com", "example.com")
        
        self.assertIn("http://example.com", visited)

if __name__ == '__main__':
    unittest.main()
