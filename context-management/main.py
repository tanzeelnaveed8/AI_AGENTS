from agents import Agent,  Runner, function_tool, RunContextWrapper
import asyncio
from connection import config
from dataclasses import dataclass

@dataclass
class userinfo:
    name: str
    uid: int

@function_tool
async def get_user_info(wrapper: RunContextWrapper[userinfo]) -> str:
   return f"User {wrapper.context.name} is 25 years old"

async def main():
    user_info = userinfo(name="Tanzeel", uid=12345)


    agent = Agent[userinfo](
        name="UserInfoAgent",
        tools=[get_user_info]
    )

    result = await Runner.run(
        starting_agent=agent,
        input="What is the age of the user?",
        context=user_info,
        run_config=config
    )

    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())    
   