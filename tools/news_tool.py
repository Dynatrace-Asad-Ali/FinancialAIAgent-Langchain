import os
from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, OpenAI, ChatOpenAI
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.vectorstores import InMemoryVectorStore
from langchain import hub
from langchain_core.tools import tool
import requests
from langchain_tavily import TavilySearch

load_dotenv()


def news_search() -> TavilySearch:
  my_news_search = TavilySearch(max_results=5,topic="news")
  return my_news_search


@tool
def fake_news_search(tool_input: str) -> str:
  """News tools to get fake news data."""
  load_dotenv()
  embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
  llm = ChatOpenAI()
  vectorstore = InMemoryVectorStore(embedding=embeddings)
  retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
  combine_docs_chain = create_stuff_documents_chain(llm, retrieval_qa_chat_prompt)
  retrieval_chain = create_retrieval_chain(retriever=vectorstore.as_retriever(), combine_docs_chain=combine_docs_chain)
  # return retrieval_chain
  result = retrieval_chain.invoke(input={"input": tool_input})
  return "\n\n".join(doc for doc in result)

def weather_lookup(location: str) -> str:
  """Find the weather of a location."""
  r = requests.get(
      'https://api.weatherapi.com/v1/current.json?q=' + location + '&key=redacted')
  return r.json()

  # return result

  # https: // gist.github.com / Dynatrace - Asad - Ali / d8da20a1f402ba0df06a8c5db0d77a2b
