import os
import json
from typing import Optional
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from groq import Groq
from dotenv import load_dotenv
from src.core.logger import logger, loading_animation

_ = load_dotenv()

class SaqrMCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.model = os.getenv("GROQ_MODEL_NAME")
        self.groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
        logger.info(f"Using model: {self.model}")
        self.history = []

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

        self.history.append({
            "role": "user",
            "content": query
        })
        
        messages = self.history

        tools = await self.session.list_tools()

        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        } for tool in tools.tools]

        stop = False
        while not stop:
            try:
                with loading_animation("Processing query"):
                    response = self.groq.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        tools=available_tools,
                        max_tokens=1000,
                        tool_choice="auto",
                    )

                    # logger.info(f"Response: {response}")

                tool_calls = response.choices[0].message.tool_calls
                if tool_calls is None:
                    messages.append({
                        "role": "assistant",
                        "content": response.choices[0].message.content,
                    })
                    stop = True
                else:
                    tool_name = response.choices[0].message.tool_calls[0].function.name
                    tool_args = json.loads(response.choices[0].message.tool_calls[0].function.arguments)

                    logger.info(f"Calling {tool_name}")

                    with loading_animation(f"Calling {tool_name}"):
                        result = await self.session.call_tool(tool_name, tool_args)

                    messages.append({
                        "role": "user",
                        "content": f"""
                            - type: tool_result.
                            - tool_use_name: {tool_name}.
                            - content": {result}.

                            use this results to answer the user questions.
                        """,
                    })

            except Exception as e:
                logger.error(f"Error processing query: {str(e)}")
                stop = True
            
        return messages[-1]["content"]
    
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

                self.history.append({ 
                    "role": "assistant",
                    "content": response
                })

            except Exception as e:
                logger.error(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

