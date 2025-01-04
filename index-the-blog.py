import asyncio
import logging
from dataclasses import dataclass
from typing import Set, List

import bs4
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_core.documents import Document
from crawler import WebCrawler

@dataclass
class IndexerConfig:
    start_url: str = "https://www.subbu.org"
    index_name: str = "subbu_stuff"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    opensearch_url: str = "http://localhost:9200"
    model_id: str = "amazon.titan-embed-text-v2:0"

class BlogIndexer:
    def __init__(self, config: IndexerConfig):
        self.config = config
        self.crawler = WebCrawler()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    async def crawl_site(self) -> Set[str]:
        self.logger.info(f"Starting crawl of {self.config.start_url}")
        visited_links = await self.crawler.crawl_site(self.config.start_url)
        self.logger.info(f"Found {len(visited_links)} links")
        return visited_links

    def load_documents(self, urls: Set[str]) -> List[Document]:
        self.logger.info("Loading documents")
        loader = WebBaseLoader(
            web_paths=urls,
            bs_kwargs=dict(parse_only=bs4.SoupStrainer(class_=("post")))
        )
        return loader.load()

    def split_documents(self, docs: List[Document]) -> List[Document]:
        self.logger.info("Splitting documents")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap
        )
        return splitter.split_documents(docs)

    def index_documents(self, docs: List[Document]):
        self.logger.info("Initializing embeddings")
        embeddings = BedrockEmbeddings(model_id=self.config.model_id)

        self.logger.info("Creating vector store")
        vector_store = OpenSearchVectorSearch.from_documents(
            docs,
            embeddings,
            bulk_size=1000,
            opensearch_url=self.config.opensearch_url,
            index_name=self.config.index_name
        )
        self.logger.info("Indexing complete")
        return vector_store

    async def run(self):
        try:
            urls = await self.crawl_site()
            docs = self.load_documents(urls)
            chunks = self.split_documents(docs)
            self.index_documents(chunks)
        except Exception as e:
            self.logger.error(f"Indexing failed: {str(e)}")
            raise

async def main():
    config = IndexerConfig()
    indexer = BlogIndexer(config)
    await indexer.run()

if __name__ == "__main__":
    asyncio.run(main())