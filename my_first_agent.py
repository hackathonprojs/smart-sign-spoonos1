import asyncio
from spoon_ai.agents.toolcall import ToolCallAgent
from spoon_ai.chat import ChatBot
from spoon_ai.tools import ToolManager
from spoon_ai.tools.base import BaseTool

class GreetingTool(BaseTool):
    name: str = "greeting"
    description: str = "Generate personalized greetings"
    parameters: dict = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Person's name"}
        },
        "required": ["name"],
    }

    async def execute(self, name: str) -> str:
        return f"Hello {name}! Welcome to SpoonOS! 🚀"

class MyFirstAgent(ToolCallAgent):
    name: str = "my_first_agent"
    description: str = "A friendly assistant with greeting capabilities"
    system_prompt: str = (
        "\n    You are a helpful AI assistant built with SpoonOS framework.\n    "
        "You can greet users and help with various tasks.\n    "
    )
    available_tools: ToolManager = ToolManager([GreetingTool()])

async def main():
    agent = MyFirstAgent(
        llm=ChatBot(
            llm_provider="openai",
            model_name="gpt-5.1",
        )
    )
    response = await agent.run("Please greet me, my name is Alice")
    return response

if __name__ == "__main__":
    result = asyncio.run(main())