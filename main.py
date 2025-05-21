import getpass
import os

from utils.pretty_print import pretty_print_messages
from utils.get_pretty import get_pretty_messages
from dotenv import load_dotenv
from agents.news_agent import news_agent
from agents.fundamental_agent import fundamental_agent
from agents.supervisor_agent import supervisor_agent
from agents.technical_agent import technical_agent
from agents.humorous_news_agent import humorous_news_agent
from traceloop.sdk import Traceloop
import streamlit as st

Traceloop.init()
Traceloop.init(disable_batch=True)

headers = { "Authorization": "Api-Token " + os.environ.get("DYNATRACE_API_TOKEN") }
Traceloop.init(
    app_name="FinancialAIAdvisor",
    api_endpoint=os.environ.get("DYNATRACE_EXPORTER_OTLP_ENDPOINT"),
    headers=headers,
    disable_batch=True
)
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()


# app = Flask(__name__)
def _set_if_undefined(var: str):
  if not os.environ.get(var):
    os.environ[var] = getpass.getpass(f"Please provide your {var}")


_set_if_undefined("OPENAI_API_KEY")

news_agent = news_agent()
fundamental_agent = fundamental_agent()
technical_agent = technical_agent()
humorous_news_agent = humorous_news_agent()
supervisor: supervisor_agent = supervisor_agent(news_agent, fundamental_agent, technical_agent, humorous_news_agent).compile()

st.title("💬 Stock Analysis Demo")
# st.caption("🚀 A Streamlit chatbot powered by OpenAI")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Ask me news/fundamental/technical analysis of any stock"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():

  try:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    for chunk in supervisor.stream(
      {
        "messages": [
          {
            "role": "user",
            "content": prompt
          }
        ]
      },
    ):
      pretty_chunk = get_pretty_messages(chunk, last_message=True)
      st.session_state.messages.append({"role": "assistant", "content":pretty_chunk})
      st.chat_message("assistant").write(pretty_chunk)
      pretty_print_messages(chunk, last_message=False)
  except Exception as e:
    print(str(e))
    error_msg = f"An error occurred: {str(e)}"
    st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Main interaction loop
# while True:
#     user_input = input("\nEnter your query (or 'exit' to quit): ")
#
#     if user_input.lower() == 'exit':
#         print("Goodbye!")
#         break
#
#     for chunk in supervisor.stream(
#         {
#             "messages": [
#                 {
#                     "role": "user",
#                     "content": user_input
#                 }
#             ]
#         },
#     ):
#         pretty_print_messages(chunk, last_message=True)
# result = supervisor_app.invoke({
#     "messages": [{
#         "role": "user",
#         "content": user_input
#     }]
# }, config=config)
#
# for m in result["messages"]:
#     print("****************************\n")
#     print(type(m.content))
#     print("****************************\n")
#     print(m.content)
