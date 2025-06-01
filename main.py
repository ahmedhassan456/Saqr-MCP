from src.ollama_client import SaqrMCPClient
import asyncio

async def main():
    client = SaqrMCPClient()
    try:
        await client.connect_to_server(
            args=[
                "run",
                "--with",
                "mcp",
                "mcp",
                "run",
                "src\\server.py"
            ]
        )
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())