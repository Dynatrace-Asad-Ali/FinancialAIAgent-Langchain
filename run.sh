python -m venv financial-agent && source financial-agent/bin/activate && pip install -r requirements.txt
source /workspaces/$RepositoryName/setEnv.sh
/workspaces/$RepositoryName/financial-agent/bin/streamlit run main.py
