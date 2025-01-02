import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import bs4
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import OpenSearchVectorSearch

start_url = "https://www.subbu.org"
index_name = "subbu_stuff"
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

    The function checks if the URL has already been visited. If not, it adds the URL to the visited set and attempts to retrieve the page content. If successful, it parses the page for links and recursively crawls each link that belongs to the same domain. The function includes a delay between requests to avoid overwhelming the server.
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

        response_content = response.content
    except requests.RequestException as e:
        print(f"Failed to retrieve {url}: {e}")
        return

    soup = BeautifulSoup(response_content, 'html.parser')
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(url, href)
        if urlparse(full_url).netloc == domain:
            crawl(full_url, domain, visited_links, depth + 1)
        time.sleep(0.1)  # Be polite and avoid overwhelming the server

def crawl_the_site(start_url):
    """
    Recursively crawls a blog starting from the given URL and collects all unique links within the same domain.

    Args:
        start_url (str): The starting URL of the blog to crawl.

    Returns:
        set: A set of all unique URLs visited during the crawl.

    The function initializes the domain and a set to keep track of visited links. It then calls the `crawl` function to start the recursive crawling process. The crawl is limited to links within the same domain as the starting URL.
    """
    domain = urlparse(start_url).netloc
    visited_links = set()
    crawl(start_url, domain, visited_links)
    return visited_links 

# Crawl the blog and collect links
web_links = crawl_the_site(start_url)
print()
print(f"Found links: {len(web_links)}")

# Initialize embeddings
embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0")

# Load and chunk contents of the blog
loader = WebBaseLoader(
    web_paths=set(web_links),
    bs_kwargs=dict(
        parse_only=bs4.SoupStrainer(
            class_=("post")
        )
    ),
)
docs = loader.load()

# Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
all_splits = text_splitter.split_documents(docs)

# Initialize vector store and index documents
vector_store = OpenSearchVectorSearch.from_documents(
    all_splits,
    embeddings, 
    bulk_size=1000,
    opensearch_url="http://localhost:9200",
    index_name=index_name
)

print(f"Split blog post into {len(all_splits)} sub-documents.")
print("Now indexing blog content...")

# Index chunks
response = vector_store.add_documents(documents=all_splits, bulk_size=1000)
print("Done indexing blog content.")

