import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
# from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool, AgentType
from langgraph.prebuilt import create_react_agent
from langchain_openai import OpenAIEmbeddings
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

vector_store: FAISS


def humorous_news_agent() -> create_react_agent:
  dirname = os.getcwd()
  filename = os.path.join(dirname, 'fake_news.txt')
  # Load data from a text file
  loader = TextLoader(filename)  # Replace with your knowledge base
  documents = loader.load()
  # Split data into manageable chunks
  text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
  docs = text_splitter.split_documents(documents)
  # Create a vector store with embeddings
  embeddings = OpenAIEmbeddings()
  global vector_store
  vector_store = FAISS.from_documents(docs, embeddings)
  # print("Vector store created")
  # tools = Tool(
  #         name="Document Retrieval",
  #         func=lambda q: retrieval_qa_chain({"query": q})["result"],
  # func=process_retrieval,
  # description="Retrieve knowledge from the document database."
  # )

  agent = create_react_agent(
    model="gpt-4o-mini",
    tools=[retrieve_rag_data],
    prompt=(
      # "You are a news agent that provides fake news only.\n\n"
      "You are an automated AI humorous or funny mews assistant for a company that provides a software platform. You are responsible to providing humorous news about this company"
      "You have access  to the news. You can use this information from this sources to help answer any fake news related questions"
      "Unless you are sure you have an accurate answer to the user's question, send the response to the user Do not make up an answer if you are unsure."
      "INSTRUCTIONS:\n"
      # "- Assist ONLY with humorous news related tasks, DO NOT provide real news\n"
      "- Get the data from the tool and pass it on to the supervisor"
    ),
    name="humorous_news_agent"
  )
  return agent


# def retrieve_data(q: str):
#   """Retrieve knowledge from the document database."""
#   print("retrieval called")
#   print(q)
#   Initialize a retriever for querying the vector store
# global vector_store
# retriever = vector_store.as_retriever(search_type="similarity", search_k=3)
#
# Initialize the LLM
# llm = ChatOpenAI(model="gpt-4")
# Create the Retrieval QA chain
# retrieval_qa_chain = RetrievalQA.from_chain_type(
#     llm=llm,
#     retriever=retriever,
#     return_source_documents=True
# )
#
# retrieved_doc = retrieval_qa_chain({"query": q})["result"]
# retrieved_doc = retrieval_qa_chain()["result"]
# print ("*********************************")
# print(retrieved_doc)
# print ("*********************************")
# return retrieved_doc

def retrieve_rag_data(q: str) -> str:
  # """Your job is to return fake news data about Dynatrace from the vector store. Do not send anything else. """
  """Return the content from the vector store. """
  # print(q)
  prompt = hub.pull("rlm/rag-prompt")

  def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

  global vector_store
  llm = ChatOpenAI(model="gpt-4")
  qa_chain = (
    {
      "context": vector_store.as_retriever() | format_docs,
      "question": RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
  )
  output = qa_chain.invoke(q)
  # print("*********************************")
  # print(output)
  # print("*********************************")
  return output
