"""Improved math MCP server with enhanced functionality."""
from mcp.server.fastmcp import FastMCP
import math
from typing import Union

mcp = FastMCP("Math", description="Advanced mathematical operations server")

# Enhanced prompts
@mcp.prompt()
def math_help_prompt() -> str:
    """Mathematical assistance prompt"""
    return """
You are a mathematical assistant with access to advanced calculation tools.
Available operations:
- Basic arithmetic (add, subtract, multiply, divide)
- Advanced functions (power, square root, logarithms)
- Trigonometric functions (sin, cos, tan)
- Statistical calculations (mean, median, standard deviation)

Provide step-by-step solutions when possible.
"""

@mcp.prompt()
def system_prompt() -> str:
    """System prompt for math operations"""
    return """
You are an AI assistant specialized in mathematical calculations.
Use the available tools for accurate computations and show your work.
"""

# Resources
@mcp.resource("math://constants")
def get_math_constants() -> str:
    """Get common mathematical constants"""
    return f"""
Mathematical Constants:
- π (pi): {math.pi}
- e (Euler's number): {math.e}
- τ (tau): {math.tau}
- Golden ratio: {(1 + math.sqrt(5)) / 2}
"""

@mcp.resource("math://formulas/{category}")
def get_formulas(category: str) -> str:
    """Get mathematical formulas by category"""
    formulas = {
        "geometry": "Area of circle: πr², Volume of sphere: (4/3)πr³",
        "algebra": "Quadratic formula: x = (-b ± √(b²-4ac)) / 2a",
        "trigonometry": "sin²θ + cos²θ = 1, tan θ = sin θ / cos θ"
    }
    return formulas.get(category, "Category not found")

# Enhanced tools
@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers"""
    return a + b

@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract b from a"""
    return a - b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers"""
    return a * b

@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide a by b"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

@mcp.tool()
def power(base: float, exponent: float) -> float:
    """Raise base to the power of exponent"""
    return base ** exponent

@mcp.tool()
def square_root(x: float) -> float:
    """Calculate square root of x"""
    if x < 0:
        raise ValueError("Cannot calculate square root of negative number")
    return math.sqrt(x)

@mcp.tool()
def logarithm(x: float, base: float = math.e) -> float:
    """Calculate logarithm of x with given base (default: natural log)"""
    if x <= 0:
        raise ValueError("Logarithm undefined for non-positive numbers")
    if base <= 0 or base == 1:
        raise ValueError("Invalid logarithm base")
    return math.log(x, base)

@mcp.tool()
def factorial(n: int) -> int:
    """Calculate factorial of n"""
    if n < 0:
        raise ValueError("Factorial undefined for negative numbers")
    return math.factorial(n)

@mcp.tool()
def sin(x: float, degrees: bool = False) -> float:
    """Calculate sine of x (radians by default, set degrees=True for degrees)"""
    if degrees:
        x = math.radians(x)
    return math.sin(x)

@mcp.tool()
def cos(x: float, degrees: bool = False) -> float:
    """Calculate cosine of x (radians by default, set degrees=True for degrees)"""
    if degrees:
        x = math.radians(x)
    return math.cos(x)

@mcp.tool()
def tan(x: float, degrees: bool = False) -> float:
    """Calculate tangent of x (radians by default, set degrees=True for degrees)"""
    if degrees:
        x = math.radians(x)
    return math.tan(x)

@mcp.tool()
def calculate_mean(numbers: list) -> float:
    """Calculate arithmetic mean of a list of numbers"""
    if not numbers:
        raise ValueError("Cannot calculate mean of empty list")
    return sum(numbers) / len(numbers)

@mcp.tool()
def calculate_median(numbers: list) -> float:
    """Calculate median of a list of numbers"""
    if not numbers:
        raise ValueError("Cannot calculate median of empty list")
    sorted_numbers = sorted(numbers)
    n = len(sorted_numbers)
    if n % 2 == 0:
        return (sorted_numbers[n//2 - 1] + sorted_numbers[n//2]) / 2
    else:
        return sorted_numbers[n//2]

@mcp.tool()
def solve_quadratic(a: float, b: float, c: float) -> dict:
    """Solve quadratic equation ax² + bx + c = 0"""
    if a == 0:
        raise ValueError("Coefficient 'a' cannot be zero for quadratic equation")
    
    discriminant = b**2 - 4*a*c
    
    if discriminant > 0:
        x1 = (-b + math.sqrt(discriminant)) / (2*a)
        x2 = (-b - math.sqrt(discriminant)) / (2*a)
        return {"solutions": [x1, x2], "type": "real_distinct"}
    elif discriminant == 0:
        x = -b / (2*a)
        return {"solutions": [x], "type": "real_repeated"}
    else:
        real_part = -b / (2*a)
        imaginary_part = math.sqrt(-discriminant) / (2*a)
        return {
            "solutions": [
                f"{real_part} + {imaginary_part}i",
                f"{real_part} - {imaginary_part}i"
            ],
            "type": "complex"
        }

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)