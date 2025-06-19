from dotenv import load_dotenv
import os
import asyncio
import warnings
import chainlit as cl
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, Runner
from openai.types.responses import ResponseTextDeltaEvent 

# Suppress Pydantic warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Load environment variables
load_dotenv()
api_key = os.getenv("API_KEY")

if not api_key:
    raise ValueError("API_KEY is not set. Please ensure it is defined in your .env file.")

# Set up Gemini-compatible model (assuming Gemini API supports OpenAI-compatible endpoints)
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

agent = Agent(
    name="Guider Agent",
    instructions="An agent that guides users through a series of steps to achieve a goal.",
)

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("history", [])
    await cl.Message(content="Hello From Tanzeel Khan! How can I help you today?").send()

@cl.on_message
async def handle_message(message: cl.Message):
    history = cl.user_session.get("history", [])
    
 
    history.append({"role": "user", "content": message.content})

    msg = cl.Message(content="")
    await msg.send()

    result = Runner.run_streamed(
        agent,
        input=history,
        run_config=config
    )
    
  
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent ):
            await msg.stream_token(event.data.delta)
       

    history.append({"role": "assistant", "content": result.final_output})
    cl.user_session.set("history", history)
    # await cl.Message(content=result.final_output).send()
