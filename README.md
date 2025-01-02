# Say it Like Subbu

This is my holiday prokect to create a small bot that answers questions based on the things I wrote in the past. I use a locally running OpenSearch (the AWS Serverless version is pricey) to create a RAG index, and use Bedrock to answer questions. I used GitHub Copilot to help me write code.

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
