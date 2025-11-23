import asyncio
from spoon_ai.agents.toolcall import ToolCallAgent
from spoon_ai.chat import ChatBot
from spoon_ai.tools import ToolManager
from spoon_ai.tools.base import BaseTool
from spoon_ai.tools.crypto_tools import get_crypto_tools

# Define a custom tool
class GreetingTool(BaseTool):
    name: str = "greeting"
    description: str = "Generate personalized greetings"
    parameters: dict = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Person's name"}
        },
        "required": ["name"]
    }

    async def execute(self, name: str) -> str:
        return f"Hello {name}! Welcome to SpoonOS! 🚀"

# Create your agent
class MyFirstAgent(ToolCallAgent):
    name: str = "my_first_agent"
    description: str = "A friendly assistant with greeting capabilities"

    system_prompt: str = """
    You are a helpful AI assistant built with SpoonOS framework.
    You can greet users and help with various tasks.
    """

    available_tools: ToolManager = ToolManager([GreetingTool()])


class Web3Agent(ToolCallAgent):
    name: str = "web3_agent"
    description: str = "AI agent with Web3 and crypto capabilities"

    system_prompt: str = """
    You are a Web3-native AI assistant with access to blockchain data.
    You can help with crypto prices, DeFi operations, and blockchain analysis.
    """

    available_tools: ToolManager = ToolManager([
        GreetingTool(),
        # Loads all crypto/Web3 tools from spoon-toolkits (requires `pip install -e spoon-toolkits`)
        *get_crypto_tools()
    ])

# Usage
async def web3_demo():
    agent = Web3Agent(
        llm=ChatBot(
            llm_provider="openai",
            model_name="gpt-4o"   # Use gpt-4o, gpt-4o-mini, or gpt-4-turbo
        )
    )

    # Framework automatically handles crypto data fetching and error cases
    response = await agent.run("What's the current price of Bitcoin?")
    return response

async def main():
    # Initialize agent with LLM
    agent = MyFirstAgent(
        llm=ChatBot(
            llm_provider="openai",         # or "anthropic", "gemini", "deepseek", "openrouter"
            model_name="gpt-4o"   # Use gpt-4o, gpt-4o-mini, or gpt-4-turbo
        )
    )

    # Run the agent - framework handles all error cases automatically
    response = await agent.run("Please greet me, my name is Alice")
    return response

if __name__ == "__main__":
    result = asyncio.run(main())
    print(result)
    try:
        web3_result = asyncio.run(web3_demo())
        print(web3_result)
    except Exception as e:
        print(f"web3_demo error: {e}")