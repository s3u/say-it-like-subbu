# LangChain Blog Indexer

This project is designed to crawl a blog, extract its content, split the content into manageable chunks, and index these chunks into an OpenSearch vector store. This allows for efficient searching and retrieval of blog content using vector embeddings.

## Getting Started

Start with the usual python plubming. 

```zsh
sudo pip3 install virtualenv
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Install and start OpenSearch.

```zsh
brew install opensearch
opensearch-plugin install https://repo1.maven.org/maven2/org/opensearch/plugin/opensearch-knn/2.18.0.0/opensearch-knn-2.18.0.0.zip
/opt/homebrew/opt/opensearch/bin/opensearch
```

## Build the RAG

```zsh
python3 blog_indexer.py
```

### Try the bot

```zsh
python3 say-it-like-subbu.py
```
