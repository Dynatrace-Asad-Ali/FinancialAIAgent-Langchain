from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from tools.fundamental_tool import fundamental_tool
load_dotenv()
my_fundamental_tool = fundamental_tool()

def fundamental_agent() -> create_react_agent:
  my_fundamental_agent = create_react_agent(
      model="openai:gpt-4.1",
      tools=[my_fundamental_tool],
      prompt=(
          "You are a fundamental analysis agent that helps users analyze the financial health of companies.\n\n"
          "INSTRUCTIONS:\n"
          # "- Assist ONLY with research-related tasks, DO NOT do any math\n"
          # "- After you're done with your tasks, respond to the supervisor directly\n"
          # "- Respond ONLY with the results of your work, do NOT include ANY other text."
            "Conduct fundamental analysis of the stock. Include:\n"
            "Financial Statements (3 Years): Review key highlights.\n"
            "Key Ratios: P/E, P/B, P/S, PEG, Debt-to-Equity, etc.\n"
            "Competitive Position: Strengths and market advantages.\n"
            "Management Effectiveness: Assess ROE and capital allocation.\n"
            "Growth Trends: Revenue and earnings trajectory.\n"
            "Growth Catalysts & Risks (2-3 Years): Identify key drivers and challenges.\n"
            "DCF Valuation: Include assumptions and insights.\n"
            "Competitor & Industry Comparison: Analyze against peers and averages."
      ),
      name="fundamental_agent",
  )
  return my_fundamental_agent
