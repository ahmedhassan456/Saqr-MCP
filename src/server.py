from mcp.server.fastmcp import FastMCP
import asyncio
from logger import logger
from tavily import TavilyClient
import os
from dotenv import load_dotenv

_ = load_dotenv()

mcp = FastMCP("Saqr Server")
search_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@mcp.tool()
def web_search(query: str):
    """Use this to find current information about any query related pages using a search engine.
    
    Args:
        query (str): The search query.
    """

    try:
        results = search_client.search(query)
        if results:
            return results
        else:
            return "No results found."
    except Exception as e:
        logger.error(f"Error during web search: {e}")
        return "An error occurred while performing the search."


def main():
    try:
        asyncio.run(mcp.run(transport="stdio"))
    except KeyboardInterrupt:
        logger.error("Server stopped")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()