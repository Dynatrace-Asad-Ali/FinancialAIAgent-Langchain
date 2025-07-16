sed -i "s,DYNATRACE_EXPORTER_OTLP_ENDPOINT_TOREPLACE,$DYNATRACE_EXPORTER_OTLP_ENDPOINT," /workspaces/$RepositoryName/setEnv.sh
sed -i "s,DYNATRACE_API_TOKEN_TOREPLACE,$DYNATRACE_API_TOKEN," /workspaces/$RepositoryName/setEnv.sh
sed -i "s,OPENAI_API_KEY_TOREPLACE,$OPENAI_API_KEY," /workspaces/$RepositoryName/setEnv.sh
sed -i "s,TAVILY_API_KEY_TOREPLACE,$TAVILY_API_KEY," /workspaces/$RepositoryName/setEnv.sh


source /workspaces/$RepositoryName/setEnv.sh
chmod +x /workspaces/$RepositoryName/run.sh
chmod +x /workspaces/$RepositoryName/mcp/run-mcp.sh
