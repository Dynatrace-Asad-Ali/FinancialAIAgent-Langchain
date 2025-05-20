# FinancialAIAgent-Langchain
This sample application does stock analysis by conducting news search, fundamental review and technical analysis.
This app is built on Single Supervisor with multiple agents architecture as described [here](https://github.com/langchain-ai/langgraph/blob/main/docs/docs/tutorials/multi_agent/agent_supervisor.ipynb). 
The multiple agents used in this app uses OpenAI LLM Model and uses TavilySearch tool to search for news. Additionally it uses Yahoo Finance for fundamental and technical analysis.

### API Keys
The following API keys are required for this app
* OPENAI_API_KEY

### Requirements
* Python 3.8 or higher

### Usage
The app uses gradio to create a web page so that users can interact with the app using browser. Once the app is launched, it spits out the url to access the app. Open a browser window and put the url to access the UI of this app.

### Instrumentation
The app uses traceloop to send telemetry data. If you want to capture those telemetry data please add the endpoints in .env file.

### How to run
```commandline
python -m venv financialagent
financialagent/bin/activate
pip install -r requirements.txt

python main.py
```
### Suggested Chat Commands
* Analyze APPL stock
* Give me latest news on Nvidia
* Conduct fundamental analysis on DIS
