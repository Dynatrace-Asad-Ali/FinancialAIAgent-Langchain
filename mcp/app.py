from typing import List
from typing_extensions import TypedDict
from typing import Annotated
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.checkpoint.memory import MemorySaver

from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.prompts import load_mcp_prompt
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
import streamlit as st


load_dotenv()

client = MultiServerMCPClient(
    {
        "math": {
            "url": "http://localhost:8000/mcp",
            "transport": "streamable_http",
        },
        "weather": {
            "url": "http://localhost:8080/mcp",
            "transport": "streamable_http",
        },
      "dynatrace": {
        "url": "http://52.186.168.229:3000/mcp",
        "transport": "streamable_http",
      }
    }
)

async def create_graph(math_session, weather_session, dynatrace_session):
  llm = init_chat_model(model="gpt-4o-mini", temperature=0)

  math_tools = await load_mcp_tools(math_session)
  weather_tools = await load_mcp_tools(weather_session)
  dynatrace_tools = await load_mcp_tools(dynatrace_session)
  tools = math_tools + weather_tools + dynatrace_tools
  llm_with_tool = llm.bind_tools(tools)

  system_prompt = await load_mcp_prompt(math_session, "system_prompt")
  prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_prompt[0].content),
    MessagesPlaceholder("messages")
  ])

  # State Management
  class State(TypedDict):
    messages: Annotated[List, add_messages]

  # Nodes
  def chat_node(state: State) -> State:
    return {"messages": [llm_with_tool.invoke(state["messages"])]}

  # Building the graph
  graph_builder = StateGraph(State)
  graph_builder.add_node("chat_node", chat_node)
  graph_builder.add_node("tool_node", ToolNode(tools=tools))
  graph_builder.add_edge(START, "chat_node")
  graph_builder.add_conditional_edges("chat_node", tools_condition, {"tools": "tool_node", "__end__": END})
  graph_builder.add_edge("tool_node", "chat_node")
  graph = graph_builder.compile(checkpointer=MemorySaver())
  return graph

if "messages" not in st.session_state:
  st.session_state["messages"] = [
    {"role": "assistant", "content": "Ask me about basic math operations, weather report and Dynatrace specific questions"}]

for msg in st.session_state.messages:
  st.chat_message(msg["role"]).write(msg["content"])

async def main():
  config = {"configurable": {"thread_id": 1234}}
  try:
    async with client.session("math") as math_session, client.session("weather") as weather_session, client.session("dynatrace") as dynatrace_session:
       # Use the MCP Server in the graph
        agent = await create_graph(math_session, weather_session, dynatrace_session)
        if prompt := st.chat_input():
          try:
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            response = await agent.ainvoke({"messages": prompt}, config=config)
            # for chunk in supervisor.stream(
            #   {
            #     "messages": [
            #       {
            #         "role": "user",
            #         "content": prompt
            #       }
            #     ]
            #   },
            # ):
            pretty_chunk = response["messages"][-1].content
            st.session_state.messages.append({"role": "assistant", "content": pretty_chunk})
            st.chat_message("assistant").write(pretty_chunk)
          except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
  except Exception as e:
    print(f"connection error: {e}")
    # while True:
    #     message = input("User: ")
    #     response = await agent.ainvoke({"messages": message}, config=config)
    #     print("AI: " + response["messages"][-1].content)


if __name__ == "__main__":
  asyncio.run(main())
