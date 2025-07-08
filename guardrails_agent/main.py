from agents import (
    Agent,
    GuardrailFunctionOutput,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
    output_guardrail,
    set_tracing_disabled,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    InputGuardrailTripwireTriggered
)
import os
from dotenv import load_dotenv
from pydantic import BaseModel
import chainlit as cl

# 🌍 Load environment
load_dotenv()
set_tracing_disabled(disabled=True)
gemini_api_key = os.getenv("GEMINI_API_KEY")

# ✅ API Client Setup
client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# 🧠 Model
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=client
)

# 🧪 Input Guardrail Output Schema
class PythonRelatedOutput(BaseModel):
    is_python_related: bool
    reasoning: str

# 🔐 Input Guardrail Agent
input_guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user's question is related to Python programming. Only return true if it is about Python.",
    output_type=PythonRelatedOutput,
    model=model
)

# ✅ Input Guardrail Function
@input_guardrail
async def python_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(input_guardrail_agent, input)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=not result.final_output.is_python_related,
    )

# 🧪 Output Guardrail Output Schema
class PythonOutput(BaseModel):
    reasoning: str
    is_python: bool

# 🔐 Output Guardrail Agent
output_guardrail_agent = Agent(
    name="Output Guardrail Check",
    instructions="Check if the output includes any Python-related content. Set `is_python=True` only if it does.",
    output_type=PythonOutput,
    model=model
)

# ✅ Output Guardrail Function
@output_guardrail
async def output_python_guardrail(
    ctx: RunContextWrapper, agent: Agent, output: str
) -> GuardrailFunctionOutput:
    # Use the correct agent for output checking
    result = await Runner.run(output_guardrail_agent, output)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=not result.final_output.is_python,  # ❗ Fix logic
    )
# 🧠 Main Python Expert Agent
one_agent = Agent(
    name="PythonExpert",
    instructions="You are a Python expert. Only respond to Python programming questions.",
    model=model,
    input_guardrails=[python_guardrail],
    output_guardrails=[output_python_guardrail]
)

# 🚀 Chainlit UI: On chat start
@cl.on_chat_start
async def start():
    await cl.Message(content="👋 I’m a Python Expert Assistant. Ask me anything about Python programming!").send()

# 💬 Handle messages
@cl.on_message
async def main(message: cl.Message):
    try:
        result = await Runner.run(
            one_agent,
            input=message.content
        )
        await cl.Message(content=result.final_output).send()

    except InputGuardrailTripwireTriggered:
        await cl.Message(content="⚠️ Sorry, I can only help with Python programming questions.").send()

    except OutputGuardrailTripwireTriggered:
        await cl.Message(content="⚠️ Output blocked: This message was not Python-related.").send()
