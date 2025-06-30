# MCP Multi-Agent System

A sophisticated multi-agent system built with Model Context Protocol (MCP) that provides intelligent assistance through specialized servers for mathematics, weather, and Dynatrace monitoring.

## 🏗️ Architecture

This application implements a clean, modular architecture:

```
mcp/
├── improved_app.py          # Main application with proper structure
├── config_manager.py        # Configuration management
├── session_manager.py       # Session lifecycle management
├── ui_components.py         # Reusable UI components
├── improved_math_server.py  # Enhanced math operations server
├── improved_weather_server.py # Enhanced weather information server
└── utils.py                 # Utility functions
```

## 🚀 Features

### Core Capabilities
- **Multi-Server Architecture**: Connects to multiple MCP servers simultaneously
- **Real-time Streaming**: Live response streaming with tool execution visibility
- **Session Management**: Robust session handling with cleanup and reset
- **Error Handling**: Comprehensive error handling and user feedback
- **Configuration Management**: Flexible server configuration with validation

### Available Services
1. **Math Server**: Advanced mathematical operations including:
   - Basic arithmetic (add, subtract, multiply, divide)
   - Advanced functions (power, square root, logarithms)
   - Trigonometric functions (sin, cos, tan)
   - Statistical calculations (mean, median)
   - Quadratic equation solver

2. **Weather Server**: Weather information service with:
   - Current conditions for major cities
   - Multi-city weather summaries
   - Weather-based recommendations
   - Friendly, conversational responses

3. **Dynatrace Server**: Monitoring and observability queries (external)

## 🛠️ Improvements Made

### Code Quality
- **Modular Architecture**: Separated concerns into dedicated modules
- **Error Handling**: Comprehensive exception handling with user-friendly messages
- **Type Hints**: Added proper type annotations throughout
- **Documentation**: Improved docstrings and comments
- **Configuration**: Centralized configuration management

### User Experience
- **Better UI**: Improved Streamlit interface with clear sections
- **Real-time Feedback**: Enhanced streaming with tool execution visibility
- **Session Management**: Easy session reset and status monitoring
- **Example Queries**: Built-in example queries for quick testing

### Server Enhancements
- **Math Server**: Added advanced mathematical functions and better error handling
- **Weather Server**: More realistic responses with recommendations
- **Resource Management**: Proper cleanup of MCP connections

### Performance & Reliability
- **Async Operations**: Proper async/await patterns
- **Connection Management**: Robust MCP client lifecycle management
- **Timeout Handling**: Configurable timeouts with graceful degradation
- **Memory Management**: Proper cleanup of resources

## 📋 Requirements

- Python 3.8+
- OpenAI API key
- Optional: Dynatrace credentials for observability

## 🚀 Quick Start

1. **Setup Environment**:
   ```bash
   python -m venv mcp-env
   source mcp-env/bin/activate  # On Windows: mcp-env\Scripts\activate
   pip install -r requirements_updated.txt
   ```

2. **Configure Environment**:
   ```bash
   cp ../.env.template .env
   # Edit .env with your API keys
   ```

3. **Start MCP Servers**:
   ```bash
   # Terminal 1: Math Server
   python improved_math_server.py

   # Terminal 2: Weather Server  
   python improved_weather_server.py
   ```

4. **Run Application**:
   ```bash
   streamlit run improved_app.py
   ```

## 💡 Usage Examples

### Math Operations
- "What is 25 * 47?"
- "Calculate the square root of 144"
- "Solve the quadratic equation x² - 5x + 6 = 0"
- "What's the sine of 45 degrees?"

### Weather Queries
- "What's the weather in New York?"
- "Give me weather for London and Paris"
- "How's the weather in Tokyo?"

### Dynatrace Monitoring
- "List Dynatrace capabilities"
- "Show me the top 5 problems in my tenant"
- "List all vulnerabilities"

## 🔧 Configuration

The application uses `config.json` for MCP server configuration:

```json
{
  "math": {
    "url": "http://localhost:8000/mcp",
    "transport": "streamable_http"
  },
  "weather": {
    "url": "http://localhost:8080/mcp", 
    "transport": "streamable_http"
  },
  "dynatrace": {
    "url": "http://52.186.168.229:3000/mcp",
    "transport": "streamable_http"
  }
}
```

## 🔍 Monitoring & Observability

The application supports Dynatrace integration for observability:

```bash
export DYNATRACE_EXPORTER_OTLP_ENDPOINT="https://your-tenant.live.dynatrace.com/api/v2/otlp"
export DYNATRACE_API_TOKEN="your-api-token"
```

## 🧪 Testing

Run the test suite:
```bash
pytest tests/ -v
```

## 🤝 Contributing

1. Follow the modular architecture patterns
2. Add comprehensive error handling
3. Include type hints and documentation
4. Test your changes thoroughly
5. Update README for new features

## 📝 License

This project is part of the FinancialAIAgent system and follows the same licensing terms.