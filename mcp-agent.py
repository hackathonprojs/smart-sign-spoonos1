import asyncio
import os
from spoon_ai.agents.toolcall import ToolCallAgent
from spoon_ai.chat import ChatBot
from spoon_ai.tools import ToolManager
from spoon_ai.tools.base import BaseTool
from spoon_ai.tools.mcp_tool import MCPTool

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

    available_tools: ToolManager = ToolManager([
        GreetingTool(),
        MCPTool(
            name="tavily",
            description="Tavily MCP web search",
            mcp_config={
                "command": "npx",
                "args": ["tavily-mcp"],
                "env": {"TAVILY_API_KEY": os.getenv("TAVILY_API_KEY", "")},
            },
        ),
    ])

    async def list_mcp_tools(self):
        from mcp.types import Tool as MCPToolDef
        async def load_tool_params(tool):
            if hasattr(tool, 'ensure_parameters_loaded'):
                try:
                    base_timeout = float(getattr(tool, '_connection_timeout', 30))
                    preload_timeout = max(15.0, min(base_timeout + 10.0, 60.0))
                    await asyncio.wait_for(tool.ensure_parameters_loaded(), timeout=preload_timeout)
                except Exception:
                    pass
            return tool
        mcp_tool_instances = [tool for tool in self.available_tools.tool_map.values() if hasattr(tool, 'mcp_config')]
        loaded_tools = await asyncio.gather(*[load_tool_params(tool) for tool in mcp_tool_instances])
        try:
            if hasattr(self, 'available_tools') and hasattr(self.available_tools, 'reindex'):
                self.available_tools.reindex()
        except Exception:
            pass
        tools = []
        for tool in loaded_tools:
            tools.append(
                MCPToolDef(
                    name=tool.name,
                    description=tool.description,
                    inputSchema=tool.parameters if tool.parameters else {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                )
            )
        return tools

async def main():
    # Initialize agent with LLM
    agent = MyFirstAgent(
        llm=ChatBot(
            llm_provider="openai",         # or "anthropic", "gemini", "deepseek", "openrouter"
            model_name="gpt-4o"   # Framework default for OpenAI
        )
    )

    # Run the agent - framework handles all error cases automatically
    response = await agent.run("Please greet me, my name is Alice")
    return response

if __name__ == "__main__":
    result = asyncio.run(main())
    print(result)