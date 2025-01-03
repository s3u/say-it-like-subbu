import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import bs4
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import OpenSearchVectorSearch
import os
from crawler import crawl_the_site

start_url = "https://www.subbu.org"
index_name = "subbu_stuff"

# Crawl the site
visited_links = crawl_the_site(start_url)
print()
print(f"Found links: {len(visited_links)}")

# Initialize embeddings
embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0")

# Load and chunk contents of the blog
loader = WebBaseLoader(
    web_paths=set(visited_links),
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