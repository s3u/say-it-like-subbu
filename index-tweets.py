import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

from langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_core.documents import Document

@dataclass
class IndexerConfig:
    js_file_path: Path = Path('data/tweets.js')
    json_file_path: Path = Path('data/tweets.json')
    index_name: str = "subbu_stuff"
    opensearch_url: str = "http://localhost:9200"
    model_id: str = "amazon.titan-embed-text-v2:0"
    batch_size: int = 100

class TweetIndexer:
    def __init__(self, config: IndexerConfig):
        self.config = config
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def validate_files(self):
        if not self.config.js_file_path.exists():
            raise FileNotFoundError(f"Tweet file not found: {self.config.js_file_path}")
        if not self.config.js_file_path.stat().st_size > 0:
            raise ValueError(f"Tweet file is empty: {self.config.js_file_path}")

    def convert_js_to_json(self) -> None:
        self.logger.info("Converting JS to JSON")
        with open(self.config.js_file_path, 'r') as js_file:
            js_content = js_file.read()
        
        json_content = re.sub(r'^.*?=\s*', '', js_content)
        
        with open(self.config.json_file_path, 'w') as json_file:
            json_file.write(json_content)

    def parse_tweets(self) -> List[Document]:
        self.logger.info("Parsing tweets")
        with open(self.config.json_file_path, 'r') as file:
            data = json.load(file)
        
        tweets = []
        for tweet in data:
            obj = tweet.get("tweet")
            if not obj:
                continue
            
            tweet_info = Document(
                id=obj.get("id"),
                page_content=obj.get("full_text"),
                metadata={
                    "created_at": obj.get("created_at"),
                    "type": "tweet"
                }
            )
            tweets.append(tweet_info)
        
        self.logger.info(f"Parsed {len(tweets)} tweets")
        return tweets

    def index_tweets(self, documents: List[Document]) -> None:
        self.logger.info("Initializing embeddings")
        embeddings = BedrockEmbeddings(model_id=self.config.model_id)

        self.logger.info("Creating vector store")
        vector_store = OpenSearchVectorSearch(
            opensearch_url=self.config.opensearch_url,
            index_name=self.config.index_name,
            embedding_function=embeddings
        )

        total_docs = len(documents)
        for i in range(0, total_docs, self.config.batch_size):
            batch = documents[i:i + self.config.batch_size]
            self.logger.info(f"Indexing batch {i//self.config.batch_size + 1}")
            vector_store.add_documents(documents=batch)

    def run(self):
        try:
            self.validate_files()
            self.convert_js_to_json()
            documents = self.parse_tweets()
            self.index_tweets(documents)
            self.logger.info("Indexing complete")
        except Exception as e:
            self.logger.error(f"Indexing failed: {str(e)}")
            raise

def main():
    config = IndexerConfig()
    indexer = TweetIndexer(config)
    indexer.run()

if __name__ == "__main__":
    main()
