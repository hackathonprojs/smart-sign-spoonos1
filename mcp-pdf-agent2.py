import asyncio
import os
from spoon_ai.agents.toolcall import ToolCallAgent
from spoon_ai.chat import ChatBot
from spoon_ai.tools import ToolManager
from spoon_ai.tools.base import BaseTool
from spoon_ai.tools.mcp_tool import MCPTool

# Define a custom tool
class TextInputTool(BaseTool):
    name: str = "text_input"
    description: str = "Provide text to convert to PDF"
    parameters: dict = {
        "type": "object",
        "properties": {
            "text": {"type": "string"},
            "file_name": {"type": "string"}
        },
        "required": ["text"]
    }

    async def execute(self, text: str, file_name: str = "output.pdf") -> str:
        return text

# Create your agent
class Text2PDFAgent(ToolCallAgent):
    name: str = "text2pdf_agent"
    description: str = "Generate a PDF from provided text"

    system_prompt: str = """
    Convert provided text into a PDF file using the available tool.
    """

    available_tools: ToolManager = ToolManager([
        TextInputTool(),
        MCPTool(
            name="text2pdf",
            description="Convert text to PDF via Composio MCP",
            mcp_config={
                "url": "https://backend.composio.dev/v3/mcp/25fbb523-9300-47ee-9256-392e6aa9bfe5/mcp?user_id=pg-test-51cd384e-26ab-4272-8b15-c59b4028bfbb",
                "transport": "http",
                "headers": {"x-api-key": os.getenv("COMPOSIO_X_API_KEY", "")},
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

async def generate_pdf(text: str, file_name: str = "output.pdf"):
    agent = Text2PDFAgent(
        llm=ChatBot(
            llm_provider="openai",
            model_name="gpt-4o"
        )
    )
    mcp_tool = None
    for t in agent.available_tools.tools:
        if isinstance(t, MCPTool):
            mcp_tool = t
            break
    if mcp_tool is None:
        return ""
    await mcp_tool.ensure_parameters_loaded()
    res = await mcp_tool.execute(text=text, file_name=file_name, file_type="txt")
    return res

if __name__ == "__main__":
    result = asyncio.run(generate_pdf("Hello PDF", "hello.pdf"))
    print(result)