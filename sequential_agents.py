import asyncio
from typing import List, Dict, Any, Optional
from mcp_pdf_agent import generate_pdf

from spoon_ai.agents.toolcall import ToolCallAgent
from spoon_ai.chat import ChatBot
from spoon_ai.tools import ToolManager
from spoon_ai.tools.base import BaseTool
from spoon_ai.tools.mcp_tools_collection import MCPToolsCollection

# ============================================================
# TOOL: Conversation Collector
# ============================================================

class ConversationCollectorTool(BaseTool):
    name: str = "conversation_collector"
    description: str = "Collects and structures conversation messages"

    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "messages": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["messages"]
    }


    async def execute(self, messages: List[str]) -> Dict[str, Any]:
        return {
            "message_count": len(messages),
            "messages": messages,
            "full_text": "\n".join(messages)
        }

# ============================================================
# AGENT 1: Conversation Collection Agent
# ============================================================

class ConversationCollectionAgent(ToolCallAgent):
    async def collect(self, raw_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        text_messages = [m["content"] for m in raw_messages if "content" in m]
        # ✅ Directly call the ConversationCollectorTool
        tool = self.available_tools.get_tool("conversation_collector")
        collected = await tool.execute(messages=text_messages)
        return collected

# ============================================================
# AGENT 2: Legal Agent
# ============================================================

class LegalAgent(ToolCallAgent):
    async def analyze(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        # Replace with actual MCP tool name for legal analysis
        legal_tool = self.available_tools.get_tool("mcp_legal_analysis")
        prompt = f"""
Analyze this conversation legally:
{collected_data['full_text']}
"""
        result = await legal_tool.execute({"text": prompt})
        return result

# ============================================================
# AGENT 3: Contact Agent (PDF generation + encryption)
# ============================================================


# ============================================================
# SEQUENTIAL FLOW ORCHESTRATOR
# ============================================================

class SequentialFlowAgent:

    def __init__(self):
        llm = ChatBot(
            llm_provider="openai",
            model_name="gpt-4o"
        )

        mcp_collection = MCPToolsCollection()

        # ✅ Use get_tools() if your version requires it
        tools_mgr = ToolManager(
            [ConversationCollectorTool()] + mcp_collection.tool_manager.tools
        )

        self.collect_agent = ConversationCollectionAgent(
            llm=llm,
            available_tools=tools_mgr
        )
        self.legal_agent = LegalAgent(
            llm=llm,
            available_tools=tools_mgr
        )

    async def run(
            self,
            raw_messages: List[Dict[str, Any]],
            encrypt_passphrase: Optional[str] = None
    ):
        collected = await self.collect_agent.collect(raw_messages)
        # legal_out = await self.legal_agent.analyze(collected)

        pdf_payload = {
            "template": "contract_v1",
            "fields": {
                "conversation_summary": collected["full_text"],
                # "legal_summary": str(legal_out)
            },
            "recipients": [
                {"name": "Person A", "email": "a@example.com"},
                {"name": "Person B", "email": "b@example.com"}
            ]
        }

        pdf_text = collected["full_text"]
        pdf_out = await generate_pdf(pdf_text, "conversation.pdf")

        return {
            "conversation": collected,
            # "legal": legal_out,
            "contract_pdf": pdf_out
        }

# ============================================================
# MAIN RUNNER
# ============================================================

async def main():
    flow = SequentialFlowAgent()

    chat_data = [
        {"role": "user", "content": "I agree to sell the car for $8,000."},
        {"role": "assistant", "content": "Please confirm delivery timeline."},
        {"role": "user", "content": "Delivery within 7 days is fine."}
    ]

    result = await flow.run(
        raw_messages=chat_data,
        encrypt_passphrase="UltraSecure123"
    )

    print("\n✅ FINAL WORKFLOW OUTPUT:\n")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
