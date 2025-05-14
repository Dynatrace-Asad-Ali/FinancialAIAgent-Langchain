import getpass
import os
# from utils.pretty_print import pretty_print_messages
# from flask import Flask, request, jsonify
from dotenv import load_dotenv
from agents.news_agent import news_agent
from agents.fundamental_agent import fundamental_agent
from agents.supervisor_agent import supervisor_agent
from agents.technical_agent import technical_agent
from langgraph.checkpoint.memory import InMemorySaver

from traceloop.sdk import Traceloop

Traceloop.init()
Traceloop.init(disable_batch=True)

headers = { "Authorization": os.environ.get("OTEL_EXPORTER_OTLP_HEADERS") }
Traceloop.init(
    app_name="FinancialAIAdvisor",
    api_endpoint=os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"),
    headers=headers,
    disable_batch=True
)
load_dotenv()

# app = Flask(__name__)
def _set_if_undefined(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"Please provide your {var}")


_set_if_undefined("OPENAI_API_KEY")
_set_if_undefined("TAVILY_API_KEY")

news_agent = news_agent()
fundamental_agent = fundamental_agent()
technical_agent = technical_agent()
supervisor:supervisor_agent = supervisor_agent(news_agent,fundamental_agent, technical_agent)


# Initialize checkpointer
checkpointer = InMemorySaver()
supervisor_app = supervisor.compile(checkpointer=checkpointer)
config = {"configurable": {"thread_id": "1"}}


# @app.route('/query', methods=['POST'])
# def query():
#     data = request.json
#     result = supervisor_app.invoke({"messages": [{"role": "user", "content": data['query']}]}, config=config)
#     return jsonify(result)
#
# if __name__ == '__main__':
#     app.run(host="0.0.0.0", port=5001, debug=True)
# Main interaction loop
while True:
    user_input = input("\nEnter your query (or 'exit' to quit): ")

    if user_input.lower() == 'exit':
        print("Goodbye!")
        break

    result = supervisor_app.invoke({
        "messages": [{
            "role": "user",
            "content": user_input
        }]
    }, config=config)

    for m in result["messages"]:
        print(m.content)
# display(Image(supervisor.get_graph().draw_mermaid_png()))
# for chunk in supervisor.stream(
#     {
#         "messages": [
#             {
#                 "role": "user",
#                 "content": "Find the latest news on the Dynatrace stock in the last 2 months. Also do fundamental analysis on the stock. Also do technical analysis on this stock",
#             }
#         ]
#     },
# ):
#     pretty_print_messages(chunk, last_message=True)

# final_message_history = chunk["supervisor"]["messages"]
# research_agent = create_react_agent(
#     model="openai:gpt-4.1",
#     tools=[web_search],
#     prompt=(
#         "You are a research agent.\n\n"
#         "INSTRUCTIONS:\n"
#         "- Assist ONLY with research-related tasks, DO NOT do any math\n"
#         "- After you're done with your tasks, respond to the supervisor directly\n"
#         "- Respond ONLY with the results of your work, do NOT include ANY other text."
#     ),
#     name="research_agent",
# )
# research_agent.invoke({"input": "Who is the mayor of NYC"})
# for chunk in research_agent.stream(
#     {"messages": [{"role": "user", "content": "who is the mayor of NYC?"}]}
# ):
#     pretty_print_messages(chunk)
