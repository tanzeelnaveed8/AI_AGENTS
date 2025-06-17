from dotenv import load_dotenv
import os
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, Runner
import asyncio
import warnings

# Suppress Pydantic warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Load environment variables
load_dotenv()
api_key = os.getenv("API_KEY")

if not api_key:
    raise ValueError("API_KEY is not set. Please ensure it is defined in your .env file.")

# Set up Gemini-compatible model
external_client = AsyncOpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

async def main():
    agent = Agent(
        name="Guider Agent",
        instructions="An agent that guides users through a series of steps to achieve a goal.",
    )

    response = await Runner.run(
        agent,
        input="ABC ati hai apko roman urdu me ?",
        run_config=config
    )
    print(response.final_output)

# Call main only once, from the global scope
if __name__ == "__main__":
    asyncio.run(main())
