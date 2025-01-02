import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

def crawl(url, domain, visited_links):
    """
    Recursively crawls a website starting from the given URL.

    Args:
        url (str): The URL to start crawling from.
        domain (str): The domain to restrict the crawling to.
        visited_links (set): A set of already visited URLs to avoid revisiting.

    Returns:
        None
    """
    if url in visited_links:
        return
    visited_links.add(url)
    print(f"Visited: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to retrieve {url}: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(url, href)
        if urlparse(full_url).netloc == domain:
            crawl(full_url, domain, visited_links)
        time.sleep(0.5)  # Be polite and avoid overwhelming the server

def crawl_the_blog(start_url):
    """
    Initiates crawling of a blog starting from the given URL.

    Args:
        start_url (str): The URL to start crawling from.

    Returns:
        set: A set of all visited URLs.
    """
    domain = urlparse(start_url).netloc
    visited_links = set()
    crawl(start_url, domain, visited_links)
    return visited_links
