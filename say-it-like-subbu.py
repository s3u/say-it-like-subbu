import os
import bs4
from typing_extensions import List, TypedDict
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langgraph.graph import START, StateGraph
from langchain_aws import ChatBedrock, BedrockEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.vectorstores import OpenSearchVectorSearch

index_name = "subbu_stuff"
model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
opensearch_url = "http://localhost:9200"

os.environ["LANGCHAIN_TRACING_V2"] = "True"
os.environ["LANGCHAIN_API_KEY"] = "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"
os.environ["USER_AGENT"] = "Mozilla/5.0 (compatible; MyCrawler/1.0)"

llm = ChatBedrock(model=model_id, beta_use_converse_api=True)
embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0")

vector_store = OpenSearchVectorSearch(
    opensearch_url=opensearch_url,
    index_name=index_name,
    embedding_function=embeddings
)

# Define prompt for question-answering
prompt = hub.pull("rlm/rag-prompt")

# Define state for application
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

# Define application steps
def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}

def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}

# Compile application and test
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

def main():
    while True:
        question = input("Enter your question (or 'exit' to quit): ")
        if question.lower() == 'exit':
            break
        response = graph.invoke({"question": question})
        print(response["answer"])

if __name__ == "__main__":
    main()