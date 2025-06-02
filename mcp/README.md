# MCP Servers & Client
This sample application setups 2 mcp servers that run locally and one streamlit based mcp client. It uses langgraph framework for the client app and creates one node create react agent. The react native agent connects to 3 MCP servers:
* Math MCP Server
* Weather MCP Server
* Dynatrace MCP Server (Running on a separate server)


### API Keys
The following API keys are required for this app
* OPENAI_API_KEY

### Requirements
* Python 3.8 or higher

### Usage
The app uses streamlit to create a web page so that users can interact with the app using browser. Once the app is launched, it spits out the url to access the app. Open a browser window and put the url to access the UI of this app.

### Instrumentation
The app uses traceloop to send telemetry data. If you want to capture those telemetry data please add the endpoints in .env file.

To get tracing data in Dynatrace, provide these keys:
* DYNATRACE_EXPORTER_OTLP_ENDPOINT (e.g <tenant>.live.dynatrace.com/api/v2/otlp)
* DYNATRACE_API_TOKEN

### How to run
#### On Desktop
Copy .env.template to .env. 
Update .env file with all the required keys
```commandline
python -m venv financialagent
financialagent/bin/activate
pip install -r requirements.txt
python math_mcp_server.py &
python weather_mcp_server.py &
streamlit run app.py
```
pyt
#### Codespaces
```commandline
./run-mcp.sh
```
### Suggested Chat Commands
* How many tools do you have
* Name the tools that you have
* What is 2 + 4   /* Look at the answer. Is it correct? */
* What is the weather in Orlando
* List Dynatrace capabilities provided by the Dynatrace tool
* List all the vulnerabilities in my Dynatrace tenant
* List top 5  problems in the Dynatrace tenant
