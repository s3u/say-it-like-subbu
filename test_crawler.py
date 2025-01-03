import unittest
from unittest.mock import patch, Mock

import requests
from crawler import crawl, crawl_the_site

class TestCrawler(unittest.TestCase):

    @patch('crawler.requests.get')
    def test_crawl_single_page(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.text = '<html><body><a href="http://example.com/page1">Page 1</a></body></html>'
        mock_get.return_value = mock_response

        visited_links = set()
        crawl('http://example.com', 'example.com', visited_links)
        
        self.assertIn('http://example.com', visited_links)
        self.assertIn('http://example.com/page1', visited_links)

    @patch('crawler.requests.get')
    def test_crawl_avoid_non_http_links(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.text = '<html><body><a href="ftp://example.com/file">File</a></body></html>'
        mock_get.return_value = mock_response

        visited_links = set()
        crawl('http://example.com', 'example.com', visited_links)
        self.assertIn('http://example.com', visited_links)
        self.assertNotIn('ftp://example.com/file', visited_links)

    @patch('crawler.requests.get')
    def test_crawl_handles_request_exception(self, mock_get):
        mock_get.side_effect = requests.RequestException

        visited_links = set()
        crawl('http://example.com', 'example.com', visited_links)
        
        self.assertIn('http://example.com', visited_links)

    @patch('crawler.requests.get')
    def test_crawl_the_site(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.text = '<html><body><a href="http://example.com/page1">Page 1</a></body></html>'
        mock_get.return_value = mock_response

        visited_links = crawl_the_site('http://example.com')
        
        self.assertIn('http://example.com', visited_links)
        self.assertIn('http://example.com/page1', visited_links)

if __name__ == '__main__':
    unittest.main()
