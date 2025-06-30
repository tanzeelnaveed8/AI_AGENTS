from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, set_tracing_disabled, function_tool
import os
from dotenv import load_dotenv
import requests
import random

# Load .env variables
load_dotenv()
set_tracing_disabled(disabled=True)

# Get API key
api_key = os.getenv("API_KEY")

# Setup OpenAI provider (you are using Gemini endpoint — ensure this is valid or update)
provider = AsyncOpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/" 
)

# Set up model
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",  # Make sure this model is supported by the endpoint you're using
    openai_client=provider
)

# Tool 1: Joke counter
@function_tool
def how_many_jokes() -> str:
    """Get random number for jokes."""
    return random.randint(1, 10)

# Tool 2: Weather
@function_tool
def get_weather(city: str) -> str:
    """Get the current weather for a given city."""
    try:
        result = requests.get(
            f"http://api.weatherapi.com/v1/current.json?key=8e3aca2b91dc4342a1162608252604&q={city}"
        )
        data = result.json()
        return f"The current weather in {city} is {data['current']['condition']['text']} with a temperature of {data['current']['temp_c']}°C."
    except Exception as e:
        return f"Error fetching weather data: {str(e)}"

# Define the agent
agent = Agent(
    name="Asistant",
    instructions="""
    If the user asks for jokes, first call 'how_many_jokes' function, then tell that many jokes with numbers.
    If the user asks for weather, call the 'get_weather' function with the city name.
    """,
    model=model,
    tools=[how_many_jokes, get_weather],
)

# Run the agent
result = Runner.run_sync(
    agent,
    input="tell me karachi weather and tell me jokes"
)

print(result.final_output)
