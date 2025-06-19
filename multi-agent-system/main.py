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

backend_agent = Agent(
    name="Backend Expert",
    instructions="""
You are a backend development expert. You help users with backend topics like APIs, databases, authentication, server frameworks (e.g., Express.js, Django).

Do NOT answer frontend or UI questions.
""",

)


# backend_handoff = handoff(
#     input_filter=backend_agent,
#     on_handoff=backend_agent
    
# )

frontend_agent = Agent(
    name="Frontend Expert",
    instructions="""
You are a frontend expert. You help with UI/UX using HTML, CSS, JavaScript, React, Next.js, and Tailwind CSS.

Do NOT answer backend-related questions.
"""
)

web_dev_agent = Agent(
    name="Web Developer Agent",
    instructions="""
You are a generalist web developer who decides whether a question is about frontend or backend.
Your job is to analyze the user's message and then hand off the task accordingly.
""",
handoffs=[frontend_agent, backend_agent],

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
        web_dev_agent,
        input=history,
        run_config=config
    )
    
  
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent ):
            await msg.stream_token(event.data.delta)
       

    history.append({"role": "assistant", "content": result.final_output})
    cl.user_session.set("history", history)
    # await cl.Message(content=result.final_output).send()
