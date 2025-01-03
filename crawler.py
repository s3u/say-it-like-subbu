import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

max_depth = 10  # Limit the depth of recursion
max_size = 10 * 1024 * 1024  # 10 MB limit for page size

def crawl(url, domain, visited_links, depth=0):
    """
    Recursively crawls a given URL and collects all unique links within the same domain.

    Args:
        url (str): The URL to start crawling from.
        domain (str): The domain to limit the crawl to.
        visited_links (set): A set of URLs that have already been visited.
        depth (int): The current depth of recursion.

    The function checks if the URL has already been visited. If not, it adds the URL to
    the visited set and attempts to retrieve the page content. If successful, it parses 
    the page for links and recursively crawls each link that belongs to the same domain.
    The function includes a delay between requests to avoid overwhelming the server.
    """
    if url in visited_links or depth > max_depth:
        return
    visited_links.add(url)
    print(".", end='', flush=True)

    headers = {'User-Agent': 'Mozilla/5.0 (compatible; MyCrawler/1.0)'}
 
    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()

        # Check for non-HTML content
        if 'text/html' not in response.headers.get('Content-Type', ''):
            print(f"Skipping non-HTML content at {url}")
            return

        # Check for large pages
        if int(response.headers.get('Content-Length', 0)) > max_size:
            print(f"Skipping large page at {url}")
            return
    except requests.RequestException as e:
        print(f"Failed to retrieve {url}: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(url, href)

        parsed_url = urlparse(full_url)
        if parsed_url.scheme in ['http', 'https'] and parsed_url.netloc == domain:
            crawl(full_url, domain, visited_links, depth + 1)
        time.sleep(0.1)  # Be polite and avoid overwhelming the server

def crawl_the_site(start_url):
    """
    Crawls the entire site starting from the given URL.

    Args:
        start_url (str): The URL to start crawling from.

    Returns:
        set: A set of all unique URLs found within the same domain.
    """
    domain = urlparse(start_url).netloc
    visited_links = set()
    crawl(start_url, domain, visited_links)
    return visited_links

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python crawler.py <start_url>")
        sys.exit(1)
    
    start_url = sys.argv[1]
    visited_links = crawl_the_site(start_url)
    print(f"Total visited links: {len(visited_links)}")
