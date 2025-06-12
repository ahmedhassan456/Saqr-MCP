from mcp.server.fastmcp import FastMCP
import asyncio
from tavily import TavilyClient
import os
from dotenv import load_dotenv
from docx import Document
import markdown
from htmldocx import HtmlToDocx
from mem0 import MemoryClient
import json
import datetime

_ = load_dotenv()

mcp = FastMCP("Saqr Server")

search_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

mem0_client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))
DEFAULT_USER_ID = "saqr_mcp"
CUSTOM_INSTRUCTIONS = """
Extract the Following Information:

- Memory Type: The category or type of the memory (e.g., "code", "note", "task").
- Content: The main content of the memory.
- Description: A brief description or summary of the memory.
- Related Information: Any additional details, context, or references relevant to the memory.
"""
mem0_client.update_project(custom_instructions=CUSTOM_INSTRUCTIONS)


thoughts_log = []


# web search tool
@mcp.tool()
async def web_search(query: str):
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
        print(f"Error during web search: {e}")
        return "An error occurred while performing the search."


# word files generator tool
@mcp.tool()
async def word_file_generator(filename: str, title: str, content: str) -> str:
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
        print(f"Error creating Word file: {e}")
        return f"An error occurred while creating the Word file: {e}"


# memory tools
@mcp.tool(
    description="""Add a new memory to mem0. This tool stores various types of information for future reference.
    Specify the memory type and the content to store.
    """
)
async def add_memory(memory_type: str, content: str) -> str:
    """Add a new memory to mem0.

    Args:
        memory_type: The type of memory being stored (e.g., "code", "note", "task").
        content: The content of the memory to store.
    """
    try:
        messages = [{"role": "user", "content": content}]
        mem0_client.add(messages, user_id=DEFAULT_USER_ID, output_format="v1.1", metadata={"memory_type": memory_type})
        return f"Successfully added memory of type {memory_type}: {content}"
    except Exception as e:
        print(f"Error adding memory: {str(e)}")
        return f"Error adding memory: {str(e)}"
    

@mcp.tool(
    description="""Retrieve all stored memories for the default user, optionally filtered by memory type.
    This tool is useful when you need complete context of all previously stored memories or specific types of memories.
    """
)
async def get_all_memories(memory_type: str = None) -> str:
    """Get all memories for the default user, optionally filtered by memory type.

    Args:
        memory_type: Optional. If provided, only memories of this type are returned.
    """
    try:
        filter_criteria = {"AND": [{"metadata.memory_type": memory_type}]} if memory_type else None
        memories = mem0_client.get_all(user_id=DEFAULT_USER_ID, page=1, page_size=50, filters=filter_criteria)
        flattened_memories = [memory["memory"] for memory in memories["results"]]
        return json.dumps(flattened_memories, indent=2)
    except Exception as e:
        print(f"Error getting memories: {str(e)}")
        return f"Error getting memories: {str(e)}"
    

@mcp.tool(
    description="""Search through stored memories using semantic search, optionally filtered by memory type.
    This tool should be called for EVERY user query to find relevant information.
    """
)
async def search_memories(query: str, memory_type: str = None) -> str:
    """Search memories using semantic search, optionally filtered by memory type.

    Args:
        query: Search query string describing what you're looking for.
        memory_type: Optional. If provided, only search within memories of this type.
    """
    try:
        filter_criteria = {"AND": [{"metadata.memory_type": memory_type}]} if memory_type else None
        memories = mem0_client.search(query, user_id=DEFAULT_USER_ID, output_format="v1.1", filters=filter_criteria)
        flattened_memories = [memory["memory"] for memory in memories["results"]]
        return json.dumps(flattened_memories, indent=2)
    except Exception as e:
        print(f"Error searching memories: {str(e)}")
        return f"Error searching memories: {str(e)}"
    

# think tools
@mcp.tool()
async def think(thought: str) -> str:
    """Use this tool to think about something. It will not obtain new information or change anything, 
    but just append the thought to the log. Use it when complex reasoning or cache memory is needed.

    Args:
        thought: A thought to think about. This can be structured reasoning, step-by-step analysis,
                policy verification, or any other mental process that helps with problem-solving, with a strict requirement to record the source URL immediately after each piece of evidence that could be used as a reference citation for the final action.
    """
    global thoughts_log
    timestamp = datetime.datetime.now().isoformat()
    thoughts_log.append({
        "timestamp": timestamp,
        "thought": thought
    })
            
    return thought


@mcp.tool()
async def get_thoughts() -> str:
    """Retrieve all thoughts recorded in the current session.
            
    This tool helps review the thinking process that has occurred so far.
    """
    global thoughts_log
    if not thoughts_log:
        return "No thoughts have been recorded yet."
            
    formatted_thoughts = []
    for i, entry in enumerate(thoughts_log, 1):
        formatted_thoughts.append(f"Thought #{i} ({entry['timestamp']}):\n{entry['thought']}\n")
            
    return "\n".join(formatted_thoughts)


@mcp.tool()
async def clear_thoughts() -> str:
    """Clear all recorded thoughts from the current session.
            
    Use this to start fresh if the thinking process needs to be reset.
    """
    global thoughts_log
    count = len(thoughts_log)
    thoughts_log = []
    return f"Cleared {count} recorded thoughts."


@mcp.tool()
async def get_thought_stats() -> str:
    """Get statistics about the thoughts recorded in the current session."""
    global thoughts_log
    if not thoughts_log:
        return "No thoughts have been recorded yet."
            
    total_thoughts = len(thoughts_log)
    avg_length = sum(len(entry["thought"]) for entry in thoughts_log) / total_thoughts if total_thoughts else 0
    longest_thought = max((len(entry["thought"]), i) for i, entry in enumerate(thoughts_log)) if thoughts_log else (0, -1)
            
    stats = {
        "total_thoughts": total_thoughts,
        "average_length": round(avg_length, 2),
        "longest_thought_index": longest_thought[1] + 1 if longest_thought[1] >= 0 else None,
        "longest_thought_length": longest_thought[0] if longest_thought[0] > 0 else None
    }
            
    return json.dumps(stats, indent=2)


def main():
    try:
        asyncio.run(mcp.run(transport="stdio"))
    except KeyboardInterrupt:
        print("Server stopped")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()