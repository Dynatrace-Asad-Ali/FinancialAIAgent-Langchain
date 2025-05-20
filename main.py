import getpass
import os
import gradio as gr
from gradio import ChatMessage

from utils.pretty_print import pretty_print_messages
from utils.get_pretty import get_pretty_messages
# from flask import Flask, request, jsonify
from dotenv import load_dotenv
from agents.news_agent import news_agent
from agents.fundamental_agent import fundamental_agent
from agents.supervisor_agent import supervisor_agent
from agents.technical_agent import technical_agent
from agents.humorous_news_agent import humorous_news_agent
from traceloop.sdk import Traceloop

Traceloop.init()
Traceloop.init(disable_batch=True)

headers = { "Authorization": os.environ.get("DYNATRACE_EXPORTER_OTLP_HEADERS") }
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


# Initialize checkpointer
# checkpointer = InMemorySaver()
# supervisor_app = supervisor.compile(checkpointer=checkpointer)
# config = {"configurable": {"thread_id": "1"}}

def process_message(user_input: str, chat_history):
  """Process user message and update chat history"""
  try:
    # First, add user message to history for display
    chat_history.append({"role": "user", "content": user_input})
    yield chat_history
    # result = supervisor_app.invoke({
    #   "messages": [{
    #     "role": "user",
    #     "content": user_input
    #   }]
    # }, config=config)

    for chunk in supervisor.stream(
      {
        "messages": [
          {
            "role": "user",
            "content": user_input
          }
        ]
      },
    ):
      chat_history.append({"role": "assistant", "content": get_pretty_messages(chunk, last_message=True)})
      pretty_print_messages(chunk, last_message=False)
      yield chat_history
  except Exception as e:
    print(str(e))
    error_msg = f"An error occurred: {str(e)}"
    chat_history.append({"role": "assistant", "content": error_msg})
    yield chat_history

css = """
p {
    text-align: center;
}
"""

# Create Gradio Interface
with gr.Blocks(css="footer {visibility: hidden}") as demo:
  gr.Markdown("""
    # <p align='center'>✨ Stock Analysis Demo</p>


    """)

  chatbot = gr.Chatbot(
    height=500,
    show_label=False,
    avatar_images=(None, "https://api.dicebear.com/7.x/bottts/svg?seed=gemma"),
    type="messages"
  )

  with gr.Row():
    msg = gr.Textbox(
      scale=5,
      show_label=False,
      placeholder="Ask me news/fundamentals/technical analysis of any stock...",
      container=False
    )
    submit_btn = gr.Button("Send", scale=1)

  with gr.Row():
    clear_btn = gr.Button("Clear Chat")

  # Set up event handlers
  msg.submit(
    process_message,
    [msg, chatbot],
    [chatbot],
  )

  submit_btn.click(
    process_message,
    [msg, chatbot],
    [chatbot],
  )

  clear_btn.click(
    lambda: [],
    None,
    chatbot,
    queue=False
  )

  # Clear textbox after sending message
  msg.submit(lambda: "", None, msg)
  submit_btn.click(lambda: "", None, msg)

if __name__ == "__main__":
  demo.launch(inbrowser=False, share=False, queue=False)


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
