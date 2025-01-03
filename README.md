# A RAG App

This is my holiday project: to create a small bot that answers questions based on my past writing. I used a locally running OpenSearch to create a RAG index and Bedrock to answer questions. I used GitHub Copilot to help me write code.

## Getting Started

Start with the usual Python plumbing.

```zsh
sudo pip3 install virtualenv
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Install and start OpenSearch. I am using the local version as the AWS hosted OpenSearch is pricey.

```zsh
brew install opensearch
opensearch-plugin install https://repo1.maven.org/maven2/org/opensearch/plugin/opensearch-knn/2.18.0.0/opensearch-knn-2.18.0.0.zip
/opt/homebrew/opt/opensearch/bin/opensearch
```

Ensure you have access keys to make AWS API calls from your environment. Also, [get a LangChain API_KEY](https://docs.smith.langchain.com/administration/how_to_guides/organization_management/create_account_api_key) and set it as an environment variable in your working environment.

## Build the RAG

These will take several minutes to complete.

```zsh
python3 index-the-blog.py
python3 index-tweets.py
```

### Try the bot

```zsh
python3 say-it-like-subbu.py
```

Here is a sample output:

```
Enter your question (or 'exit' to quit): What did the author say about authenticity?
According to the context, the author emphasizes that authenticity is not something we're born with or fixed, but rather something we shape through experience. The author suggests that people often mistakenly use authenticity as an excuse to stay in their comfort zone, avoiding challenges to their beliefs and values. The author also argues that you can be authentic while still evolving as a leader by being willing to challenge your existing beliefs and broaden your experiences.
Enter your question (or 'exit' to quit):
```
