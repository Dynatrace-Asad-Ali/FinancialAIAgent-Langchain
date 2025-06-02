python -m venv mcp && source mcp/bin/activate && pip install -r requirements.txt
source /workspaces/$RepositoryName/setEnv.sh
python math_mcp_server.py &
python weather_mcp_server.py &
/workspaces/$RepositoryName/mcp/mcp/bin/streamlit run app.py
