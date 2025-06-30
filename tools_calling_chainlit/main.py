import os
import requests
import random
import chainlit as cl
from dotenv import load_dotenv
from agents import (
    Agent, Runner, OpenAIChatCompletionsModel,
    AsyncOpenAI, set_tracing_disabled, function_tool
)

# Load .env variables
load_dotenv()
set_tracing_disabled(disabled=True)

# API keys
api_key = os.getenv("API_KEY")
weather_api_key = os.getenv("WEATHER_API_KEY")

# Set up provider and model
provider = AsyncOpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"  # NOTE: Ensure this supports your model
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",  # Ensure compatibility
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
        response = requests.get(
             f"http://api.weatherapi.com/v1/current.json?key=8e3aca2b91dc4342a1162608252604&q={city}"
        )
        data = response.json()
        return f"The current weather in {city} is {data['current']['condition']['text']} with a temperature of {data['current']['temp_c']}°C."
    except Exception as e:
        return f"Error fetching weather data: {str(e)}"

# Agent definition
agent = Agent(
    name="Assistant",
    instructions="""
    If the user asks for jokes, first call 'how_many_jokes' function, then tell that many jokes with numbers.
    If the user asks for weather, call the 'get_weather' function with the city name.
    """,
    model=model,
    tools=[how_many_jokes, get_weather],
)

# Chainlit app entry
@cl.on_message
async def main(message: cl.Message):
    result = await Runner.run(agent, input=message.content)
    await cl.Message(content=result.final_output).send()
