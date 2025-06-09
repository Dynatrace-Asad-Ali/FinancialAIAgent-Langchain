from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
# from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from tools.technical_tool import technical_tool
load_dotenv()
# my_technical_tool = technical_tool()

from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool

def technical_agent() -> create_react_agent:
  my_technical_agent = create_react_agent(
      model="gpt-4o-mini",
      tools=[YahooFinanceNewsTool()],
      prompt=(
          "You are a technical analysis agent that helps users analyze stock prices and trends for a given stock {stock}.\n\n"
          "INSTRUCTIONS:\n"
          "- Assist ONLY with research-related tasks, DO NOT do any math\n"
          "- After you're done with your tasks, respond to the supervisor directly\n"
          "- Respond ONLY with the results of your work, do NOT include ANY other text."
            "Perform technical analysis on the stock. Include:\n"
                # "Moving Averages (1 Year): 50-day & 200-day, with crossovers.\n"
                # "Support & Resistance: 3 levels each, with significance.\n"
                # "Volume Analysis (3 Months): Trends and anomalies.\n"
                # "RSI & MACD: Compute and interpret signals.\n"
                # "Fibonacci Levels: Calculate and analyze.\n"
                "Chart Patterns (6 Months): Identify 3 key patterns.\n"
                "Sector Comparison: Contrast with sector averages.\n"
        "Get the data from the tool and pass it on to the supervisor"
      ),
      name="technical_agent",
  )
  return my_technical_agent
