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
from langchain_core.messages import HumanMessage
from langchain_core.messages.ai import AIMessageChunk
from utils import astream_graph, random_uuid
from langchain_core.runnables import RunnableConfig
from langchain_core.messages.tool import ToolMessage
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
import json
import os
from traceloop.sdk import Traceloop

load_dotenv()

headers = { "Authorization": "Api-Token " + os.environ.get("DYNATRACE_API_TOKEN") }
Traceloop.init(
    app_name="MCPAgent",
    api_endpoint=os.environ.get("DYNATRACE_EXPORTER_OTLP_ENDPOINT"),
    headers=headers,
    disable_batch=True
)
# Create and reuse global event loop (create once and continue using)
if "event_loop" not in st.session_state:
    loop = asyncio.new_event_loop()
    st.session_state.event_loop = loop
    asyncio.set_event_loop(loop)

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

# Initialize session state
if "session_initialized" not in st.session_state:
    st.session_state.session_initialized = False  # Session initialization flag
    st.session_state.agent = None  # Storage for ReAct agent object
    st.session_state.history = []  # List for storing conversation history
    st.session_state.mcp_client = None  # Storage for MCP client object
    st.session_state.timeout_seconds = (
        120  # Response generation time limit (seconds), default 120 seconds
    )
    st.session_state.selected_model = (
        "gpt-4o-mini"  # Default model selection
    )
    st.session_state.recursion_limit = 100  # Recursion call limit, default 100

if "thread_id" not in st.session_state:
    st.session_state.thread_id = random_uuid()

SYSTEM_PROMPT = """<ROLE>
You are a smart agent with an ability to use tools.
You will be given a question and you will use the tools to answer the question.
Pick the most relevant tool to answer the question.
Your answer should be very polite and professional.
Only use tools provided. Do not use your own tools
</ROLE>

----

<INSTRUCTIONS>
Step 1: Analyze the question
- Analyze user's question and final goal.
- If the user's question is consist of multiple sub-questions, split them into smaller sub-questions.

Step 2: Pick the most relevant tool
- Pick the most relevant tool to answer the question.
- If you are failed to answer the question, do not try different tools to get context.

Step 3: Answer the question
- Answer the question in the same language as the question.
- Your answer should be very polite and professional.

Step 4: Provide the source of the answer(if applicable)
- If you've used the tool, provide the source of the answer.
- Valid sources are either a website(URL) or a document(PDF, etc).

Guidelines:
- If you've used the tool, your answer should be based on the tool's output(tool's output is more important than your own knowledge).
- If you've used the tool, and the source is valid URL, provide the source(URL) of the answer.
- Skip providing the source if the source is not URL.
- Answer in the same language as the question.
- Answer should be concise and to the point.
- Avoid response your output with any other information than the answer and the source.
</INSTRUCTIONS>

----

<OUTPUT_FORMAT>
(concise answer to the question)

**Source**(if applicable)
- (source1: valid URL)
- (source2: valid URL)
- ...
</OUTPUT_FORMAT>
"""

OUTPUT_TOKEN_INFO = {
    "gpt-4o": {"max_tokens": 16000},
    "gpt-4o-mini": {"max_tokens": 16000},
}
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

  # config.json file path setting
  CONFIG_FILE_PATH = "config.json"

  # Function to load settings from JSON file
  def load_config_from_json():
    """
    Loads settings from config.json file.
    Creates a file with default settings if it doesn't exist.

    Returns:
        dict: Loaded settings
    """
    default_config = {
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

    try:
      if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
          return json.load(f)
      else:
        # Create file with default settings if it doesn't exist
        print("Saving default config")
        save_config_to_json(default_config)
        return default_config
    except Exception as e:
      st.error(f"Error loading settings file: {str(e)}")
      return default_config


  # Function to save settings to JSON file
  def save_config_to_json(config):
    """
    Saves settings to config.json file.

    Args:
        config (dict): Settings to save

    Returns:
        bool: Save success status
    """
    try:
      with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
      return True
    except Exception as e:
      st.error(f"Error saving settings file: {str(e)}")
      return False


  async def cleanup_mcp_client():
    """
    Safely terminates the existing MCP client.

    Properly releases resources if an existing client exists.
    """
    if "mcp_client" in st.session_state and st.session_state.mcp_client is not None:
      try:

        await st.session_state.mcp_client.__aexit__(None, None, None)
        st.session_state.mcp_client = None
      except Exception as e:
        import traceback

        # st.warning(f"Error while terminating MCP client: {str(e)}")
        # st.warning(traceback.format_exc())


  async def initialize_session(mcp_config=None):
    """
    Initializes MCP session and agent.

    Args:
        mcp_config: MCP tool configuration information (JSON). Uses default settings if None

    Returns:
        bool: Initialization success status
    """
    with st.spinner("🔄 Connecting to MCP server..."):
      # First safely clean up existing client
      await cleanup_mcp_client()

      if mcp_config is None:
        # Load settings from config.json file
        mcp_config = load_config_from_json()
      client = MultiServerMCPClient(mcp_config)
      # await client.__aenter__()
      tools = await client.get_tools()
      st.session_state.tool_count = len(tools)
      st.session_state.mcp_client = client

      # Initialize appropriate model based on selection
      selected_model = st.session_state.selected_model
      model = ChatOpenAI(
        model=selected_model,
        temperature=0,
        max_tokens=OUTPUT_TOKEN_INFO["gpt-4o-mini"]["max_tokens"],
      )
      agent = create_react_agent(
        model,
        tools,
        checkpointer=MemorySaver(),
        prompt=SYSTEM_PROMPT,
      )
      st.session_state.agent = agent
      st.session_state.session_initialized = True
      return True


  def print_message():
    """
    Displays chat history on the screen.

    Distinguishes between user and assistant messages on the screen,
    and displays tool call information within the assistant message container.
    """
    i = 0
    while i < len(st.session_state.history):
      message = st.session_state.history[i]

      if message["role"] == "user":
        st.chat_message("user", avatar="🧑‍💻").markdown(message["content"])
        i += 1
      elif message["role"] == "assistant":
        # Create assistant message container
        with st.chat_message("assistant", avatar="🤖"):
          # Display assistant message content
          st.markdown(message["content"])

          # Check if the next message is tool call information
          if (
            i + 1 < len(st.session_state.history)
            and st.session_state.history[i + 1]["role"] == "assistant_tool"
          ):
            # Display tool call information in the same container as an expander
            with st.expander("🔧 Tool Call Information", expanded=False):
              st.markdown(st.session_state.history[i + 1]["content"])
            i += 2  # Increment by 2 as we processed two messages together
          else:
            i += 1  # Increment by 1 as we only processed a regular message
      else:
        # Skip assistant_tool messages as they are handled above
        i += 1


def get_streaming_callback(text_placeholder, tool_placeholder):
  """
  Creates a streaming callback function.

  This function creates a callback function to display responses generated from the LLM in real-time.
  It displays text responses and tool call information in separate areas.

  Args:
      text_placeholder: Streamlit component to display text responses
      tool_placeholder: Streamlit component to display tool call information

  Returns:
      callback_func: Streaming callback function
      accumulated_text: List to store accumulated text responses
      accumulated_tool: List to store accumulated tool call information
  """
  accumulated_text = []
  accumulated_tool = []

  def callback_func(message: dict):
    nonlocal accumulated_text, accumulated_tool
    message_content = message.get("content", None)

    if isinstance(message_content, AIMessageChunk):
      content = message_content.content
      # If content is in list form (mainly occurs in Claude models)
      if isinstance(content, list) and len(content) > 0:
        message_chunk = content[0]
        # Process text type
        if message_chunk["type"] == "text":
          accumulated_text.append(message_chunk["text"])
          text_placeholder.markdown("".join(accumulated_text))
        # Process tool use type
        elif message_chunk["type"] == "tool_use":
          if "partial_json" in message_chunk:
            accumulated_tool.append(message_chunk["partial_json"])
          else:
            tool_call_chunks = message_content.tool_call_chunks
            tool_call_chunk = tool_call_chunks[0]
            accumulated_tool.append(
              "\n```json\n" + str(tool_call_chunk) + "\n```\n"
            )
          with tool_placeholder.expander(
            "🔧 Tool Call Information", expanded=True
          ):
            st.markdown("".join(accumulated_tool))
      # Process if tool_calls attribute exists (mainly occurs in OpenAI models)
      elif (
        hasattr(message_content, "tool_calls")
        and message_content.tool_calls
        and len(message_content.tool_calls[0]["name"]) > 0
      ):
        tool_call_info = message_content.tool_calls[0]
        accumulated_tool.append("\n```json\n" + str(tool_call_info) + "\n```\n")
        with tool_placeholder.expander(
          "🔧 Tool Call Information", expanded=True
        ):
          st.markdown("".join(accumulated_tool))
      # Process if content is a simple string
      elif isinstance(content, str):
        accumulated_text.append(content)
        text_placeholder.markdown("".join(accumulated_text))
      # Process if invalid tool call information exists
      elif (
        hasattr(message_content, "invalid_tool_calls")
        and message_content.invalid_tool_calls
      ):
        tool_call_info = message_content.invalid_tool_calls[0]
        accumulated_tool.append("\n```json\n" + str(tool_call_info) + "\n```\n")
        with tool_placeholder.expander(
          "🔧 Tool Call Information (Invalid)", expanded=True
        ):
          st.markdown("".join(accumulated_tool))
      # Process if tool_call_chunks attribute exists
      elif (
        hasattr(message_content, "tool_call_chunks")
        and message_content.tool_call_chunks
      ):
        tool_call_chunk = message_content.tool_call_chunks[0]
        accumulated_tool.append(
          "\n```json\n" + str(tool_call_chunk) + "\n```\n"
        )
        with tool_placeholder.expander(
          "🔧 Tool Call Information", expanded=True
        ):
          st.markdown("".join(accumulated_tool))
      # Process if tool_calls exists in additional_kwargs (supports various model compatibility)
      elif (
        hasattr(message_content, "additional_kwargs")
        and "tool_calls" in message_content.additional_kwargs
      ):
        tool_call_info = message_content.additional_kwargs["tool_calls"][0]
        accumulated_tool.append("\n```json\n" + str(tool_call_info) + "\n```\n")
        with tool_placeholder.expander(
          "🔧 Tool Call Information", expanded=True
        ):
          st.markdown("".join(accumulated_tool))
    # Process if it's a tool message (tool response)
    elif isinstance(message_content, ToolMessage):
      accumulated_tool.append(
        "\n```json\n" + str(message_content.content) + "\n```\n"
      )
      with tool_placeholder.expander("🔧 Tool Call Information", expanded=True):
        st.markdown("".join(accumulated_tool))
    return None

  return callback_func, accumulated_text, accumulated_tool


async def process_query(query, text_placeholder, tool_placeholder, timeout_seconds=60):
  """
  Processes user questions and generates responses.

  This function passes the user's question to the agent and streams the response in real-time.
  Returns a timeout error if the response is not completed within the specified time.

  Args:
      query: Text of the question entered by the user
      text_placeholder: Streamlit component to display text responses
      tool_placeholder: Streamlit component to display tool call information
      timeout_seconds: Response generation time limit (seconds)

  Returns:
      response: Agent's response object
      final_text: Final text response
      final_tool: Final tool call information
  """
  try:
    if st.session_state.agent:
      streaming_callback, accumulated_text_obj, accumulated_tool_obj = (
        get_streaming_callback(text_placeholder, tool_placeholder)
      )
      try:
        response = await asyncio.wait_for(
          astream_graph(
            st.session_state.agent,
            {"messages": [HumanMessage(content=query)]},
            callback=streaming_callback,
            config=RunnableConfig(
              recursion_limit=st.session_state.recursion_limit,
              thread_id=st.session_state.thread_id,
            ),
          ),
          timeout=timeout_seconds,
        )
      except asyncio.TimeoutError:
        error_msg = f"⏱️ Request time exceeded {timeout_seconds} seconds. Please try again later."
        return {"error": error_msg}, error_msg, ""

      final_text = "".join(accumulated_text_obj)
      final_tool = "".join(accumulated_tool_obj)
      return response, final_text, final_tool
    else:
      return (
        {"error": "🚫 Agent has not been initialized."},
        "🚫 Agent has not been initialized.",
        "",
      )
  except Exception as e:
    import traceback

    error_msg = f"❌ Error occurred during query processing: {str(e)}\n{traceback.format_exc()}"
    return {"error": error_msg}, error_msg, ""


loaded_config = load_config_from_json()
# Create pending config based on existing mcp_config_text if not present
if "pending_mcp_config" not in st.session_state:
  try:
    st.session_state.pending_mcp_config = loaded_config
  except Exception as e:
    st.error(f"Failed to set initial pending config: {e}")

  st.session_state.selected_model = (
        "gpt-4o-mini"  # Default model selection
    )
success = st.session_state.event_loop.run_until_complete(
                initialize_session(st.session_state.pending_mcp_config)
            )
# progress_bar = st.progress(0)
# Update progress
# progress_bar.progress(100)
# --- Print conversation history ---
print_message()
user_query = st.chat_input("💬 Enter your question")
if user_query:
    if st.session_state.session_initialized:
        st.chat_message("user", avatar="🧑‍💻").markdown(user_query)
        with st.chat_message("assistant", avatar="🤖"):
            tool_placeholder = st.empty()
            text_placeholder = st.empty()
            resp, final_text, final_tool = (
                st.session_state.event_loop.run_until_complete(
                    process_query(
                        user_query,
                        text_placeholder,
                        tool_placeholder,
                        st.session_state.timeout_seconds,
                    )
                )
            )
        if "error" in resp:
            st.error(resp["error"])
        else:
            st.session_state.history.append({"role": "user", "content": user_query})
            st.session_state.history.append(
                {"role": "assistant", "content": final_text}
            )
            if final_tool.strip():
                st.session_state.history.append(
                    {"role": "assistant_tool", "content": final_tool}
                )
            st.rerun()
    else:
        st.warning(
            "⚠️ MCP server and agent are not initialized. Please click the 'Apply Settings' button in the left sidebar to initialize."
        )
