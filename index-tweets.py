import json
import re
from langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

index_name = "subbu_stuff"

def convert_js_to_json(js_file_path, json_file_path):
    with open(js_file_path, 'r') as js_file:
        js_content = js_file.read()
    
    # Remove the JavaScript variable assignment
    json_content = re.sub(r'^.*?=\s*', '', js_content)

    with open(json_file_path, 'w') as json_file:
        json_file.write(json_content)

def parse_tweets(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    tweets = []
    for tweet in data:
        obj = tweet.get("tweet")
        tweet_info = Document(
            id = obj.get("id"),
            page_content = obj.get("full_text"),
            metadata = {
                "created_at": obj.get("created_at"),
            }
        )
        tweets.append(tweet_info)
    
    return tweets

if __name__ == "__main__":
    js_file_path = 'data/tweets.js'
    json_file_path = 'data/tweets.json'
    
    convert_js_to_json(js_file_path, json_file_path)
    parsed_tweets = parse_tweets(json_file_path)
    
    # Initialize embeddings and vector store
    embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0")
    vector_store = OpenSearchVectorSearch(
        opensearch_url="http://localhost:9200",
        index_name=index_name,
        embedding_function=embeddings
    )
    
    # Index parsed tweets
    print(f"Indexing {len(parsed_tweets)} tweets.")
    for tweet in parsed_tweets:
        # document = {"text": tweet.page_content, "metadata": tweet.metadata}
        print(".", end='', flush=True)
        response = vector_store.add_documents(documents=[tweet], bulk_size=1)

    print("Done indexing tweets.")
