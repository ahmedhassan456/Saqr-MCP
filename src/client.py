import os
from typing import Optional
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import ollama
from dotenv import load_dotenv
from src.logger import logger, loading_animation

load_dotenv()

class SaqrMCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.model = os.getenv("MODEL_NAME")
        logger.info(f"Using model: {self.model}")

    async def connect_to_server(self, args: Optional[list[str]] = None) -> None:
        """Connect to an MCP server"""

        server_params = StdioServerParameters(
            command="uv",
            args=args if args is not None else [],
            env=None
        )

        studio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = studio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        with loading_animation("Initializing server"):
            await self.session.initialize()
 
        logger.info("Connected to server")
        response = await self.session.list_tools()
        tools = response.tools
        logger.info(f"Connected to server with tools: {', '.join(tool.name for tool in tools)}")

    async def process_query(self, query: str) -> str:
        """Process a query using ollama and available tools"""
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        tools = await self.session.list_tools()

        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        } for tool in tools.tools]

        with loading_animation("Processing query"):
            response = ollama.chat(
                model=self.model,
                messages=messages,
                tools=available_tools,
            )

        tool_calls = response["message"].get("tool_calls")
        if tool_calls is None:
            return response["message"]["content"]
        else: 
            tool_name = tool_calls[0]["function"]["name"]
            tool_args = tool_calls[0]["function"]["arguments"]

            logger.info(f"Calling {tool_name}")

            with loading_animation(f"Calling {tool_name}"):
                result = await self.session.call_tool(tool_name, tool_args)

            with loading_animation("Processing tool result"):
                response  = ollama.chat(
                    model=self.model,
                    messages=[{
                            "role": "system",
                            "content": f"""You are a helpful assistant. \n answer the user question based on the tool result.
                            
                            Tool result: {result.content}""",
                        },
                        {
                            "role": "user",
                            "content": f"User Question: {query}"
                        }
                    ],
                )

            return response["message"]["content"]
    
    async def chat_loop(self):
        """Run an interactive chat loop"""
        logger.info("MCP Client Started!")
        logger.info("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                logger.error(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

        