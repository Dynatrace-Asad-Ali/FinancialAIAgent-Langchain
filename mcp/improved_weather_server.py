"""Improved weather MCP server with better responses."""
from mcp.server.fastmcp import FastMCP
import json
from typing import Dict, Any

mcp = FastMCP(name="Weather", host="0.0.0.0", port=8080, description="Weather information service")

# Weather data simulation (in real implementation, use actual weather API)
WEATHER_DATA = {
    "new york": {"temp": 22, "condition": "Sunny", "humidity": 65, "wind": "10 mph"},
    "london": {"temp": 15, "condition": "Cloudy", "humidity": 80, "wind": "5 mph"},
    "tokyo": {"temp": 28, "condition": "Partly Cloudy", "humidity": 70, "wind": "8 mph"},
    "paris": {"temp": 18, "condition": "Rainy", "humidity": 85, "wind": "12 mph"},
    "sydney": {"temp": 25, "condition": "Clear", "humidity": 60, "wind": "15 mph"},
}

@mcp.prompt()
def weather_prompt() -> str:
    """Weather assistance prompt"""
    return """
You are a helpful weather assistant. When providing weather information:
1. Give current conditions clearly
2. Include temperature, weather condition, humidity, and wind
3. Add helpful context or recommendations based on conditions
4. Be friendly and conversational
"""

@mcp.resource("weather://cities")
def get_supported_cities() -> str:
    """Get list of supported cities"""
    cities = list(WEATHER_DATA.keys())
    return f"Supported cities: {', '.join(cities).title()}"

@mcp.resource("weather://help")
def get_weather_help() -> str:
    """Get weather service help"""
    return """
Weather Service Help:
- Ask for weather in any supported city
- Get current conditions including temperature, weather, humidity, and wind
- Receive helpful recommendations based on conditions
"""

@mcp.tool()
def get_weather(city: str) -> str:
    """Get comprehensive weather information for a city.
    
    Args:
        city: Name of the city to get weather for
        
    Returns:
        Detailed weather information including temperature, conditions, and recommendations
    """
    city_lower = city.lower().strip()
    
    if city_lower not in WEATHER_DATA:
        available_cities = ", ".join(WEATHER_DATA.keys()).title()
        return f"""
I don't have weather data for "{city}". 

Available cities: {available_cities}

Please try one of these cities, or if you're looking for a specific location, 
try using the nearest major city from the list above.
"""
    
    weather = WEATHER_DATA[city_lower]
    city_name = city.title()
    
    # Generate recommendations based on conditions
    recommendations = _get_weather_recommendations(weather)
    
    return f"""
🌤️ Current Weather for {city_name}:

🌡️ Temperature: {weather['temp']}°C
☁️ Conditions: {weather['condition']}
💧 Humidity: {weather['humidity']}%
💨 Wind: {weather['wind']}

{recommendations}

Have a great day! Stay safe and enjoy the weather! 🌟
"""

@mcp.tool()
def get_weather_summary(cities: list) -> str:
    """Get weather summary for multiple cities.
    
    Args:
        cities: List of city names
        
    Returns:
        Summary of weather conditions across multiple cities
    """
    if not cities:
        return "Please provide a list of cities to get weather summary."
    
    summary = "🌍 Multi-City Weather Summary:\n\n"
    
    for city in cities:
        city_lower = city.lower().strip()
        if city_lower in WEATHER_DATA:
            weather = WEATHER_DATA[city_lower]
            summary += f"📍 {city.title()}: {weather['temp']}°C, {weather['condition']}\n"
        else:
            summary += f"📍 {city.title()}: Weather data not available\n"
    
    return summary

def _get_weather_recommendations(weather: Dict[str, Any]) -> str:
    """Generate weather-based recommendations."""
    temp = weather['temp']
    condition = weather['condition'].lower()
    humidity = weather['humidity']
    
    recommendations = []
    
    # Temperature recommendations
    if temp < 10:
        recommendations.append("🧥 It's quite cold - bundle up with warm clothes!")
    elif temp > 30:
        recommendations.append("🌡️ It's hot out there - stay hydrated and seek shade!")
    elif 20 <= temp <= 25:
        recommendations.append("👕 Perfect temperature for light, comfortable clothing!")
    
    # Condition recommendations
    if "rain" in condition:
        recommendations.append("☔ Don't forget your umbrella!")
    elif "sunny" in condition or "clear" in condition:
        recommendations.append("😎 Great day for outdoor activities - don't forget sunscreen!")
    elif "cloudy" in condition:
        recommendations.append("☁️ Nice overcast day - perfect for a walk!")
    
    # Humidity recommendations
    if humidity > 80:
        recommendations.append("💧 High humidity - you might feel a bit sticky!")
    elif humidity < 40:
        recommendations.append("🏜️ Low humidity - consider using moisturizer!")
    
    return "\n".join(f"💡 {rec}" for rec in recommendations) if recommendations else "💡 Enjoy the weather!"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")