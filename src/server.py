from mcp.server.fastmcp import FastMCP
import asyncio
from logger import logger
from tavily import TavilyClient
import os
from dotenv import load_dotenv
from docx import Document
import markdown
from htmldocx import HtmlToDocx

_ = load_dotenv()

mcp = FastMCP("Saqr Server")
search_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@mcp.tool()
def web_search(query: str):
    """
    This tool performs real-time web searches to retrieve up-to-date information from the internet
    
    Args:
        - query (str): The search query.
    Return:
        - A list of search results
    """

    try:
        results = search_client.search(query)
        if results:
            return results["results"]
        else:
            return "No results found."
    except Exception as e:
        logger.error(f"Error during web search: {e}")
        return "An error occurred while performing the search."

@mcp.tool()
def word_file_generator(filename: str, title: str, content: str):
    """
    This tool generates Microsoft Word (.docx) documents based on structured input

    Args:
        - filename (str): The name of the Word file to be saved (e.g., 'output.docx').
        - title (str): The title to be added as a heading.
        - content (str): The main text content as a Markdown string.
    Return:
        - A .docx file saved locally
    """

    try:
        html = markdown.markdown(content, extensions=['extra', 'tables'])

        doc = Document()
        doc.add_heading(title, level=0)

        new_parser = HtmlToDocx()
        
        new_parser.add_html_to_document(html, doc)
        doc.save(filename)

        return f"The word file created successfully with name: {filename}"
    except Exception as e:
        logger.error(f"Error creating Word file: {e}")
        return f"An error occurred while creating the Word file: {e}"


def main():
    try:
        asyncio.run(mcp.run(transport="stdio"))
    except KeyboardInterrupt:
        logger.error("Server stopped")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()