# Saqr-MCP ![image](https://github.com/user-attachments/assets/2ee374a5-8b63-4f5a-b7fd-5bdae3a05e37)

Saqr-MCP is a Python application that implements the Model Context Protocol (MCP) to enable AI assistant capabilities with both local models through Ollama and cloud models through Groq. It provides a client-server architecture where the client can communicate with either local or cloud models, while the server provides tools for the LLM including web search capabilities.

## Features

- Interactive chat interface for querying models
- Support for both local models (Ollama) and cloud models (Groq)
- Robust web search tool integration using Tavily API
- Async architecture for efficient processing
- Visual loading animations for better user experience

## Prerequisites

- Python 3.11 or higher
- [Ollama](https://ollama.ai/) installed with local models (for local model usage)
- [UV](https://github.com/astral-sh/uv) package manager (recommended)
- Groq API key (for cloud model usage)

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/ahmedhassan456/Saqr-MCP.git
   cd saqr-mcp
   ```

2. Create and activate a virtual environment (optional but recommended):

   ```bash
   uv venv
   # On Windows
   .venv\Scripts\activate
   # On Unix or MacOS
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   uv add -r requirements.txt
   ```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Configure the following variables:
     - `MODEL_NAME`: Your preferred Ollama model (e.g., `qwen3:1.7b`)
     - `TAVILY_API_KEY`: Your Tavily API key from [Tavily website](https://app.tavily.com/home)
     - `GROQ_MODEL_NAME`: Your preferred Groq model name
     - `GROQ_API_KEY`: Your Groq API key

## Usage

1. For local model usage, ensure Ollama is running with your chosen model available

2. Configure the client:
   - By default, the application uses Ollama client (`from src.ollama_client import SaqrMCPClient`)
   - To use Groq instead, modify `main.py` to use `from src.groq_client import SaqrMCPClient`

3. Run the client:

   ```bash
   python main.py
   ```

4. Type your queries in the interactive console:

   ```
   MCP Client Started!
   Type your queries or 'quit' to exit.

   Query:
   ```

5. Type `quit` to exit the application

## Project Structure

- `main.py` - Entry point that starts the MCP client
- `src/`
  - `ollama_client.py` - MCP client implementation for Ollama models
  - `groq_client.py` - MCP client implementation for Groq models
  - `server.py` - MCP server implementation with web search tool
  - `logger.py` - Custom logging utilities with visual animations

## Available Tools

Currently, the server implements the following tools:

- **web_search**: Searches the web using Tavily API

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MODEL_NAME` | The name of the Ollama model to use (e.g., `qwen3:1.7b`) | None |
| `TAVILY_API_KEY` | Tavily API Key | None |
| `GROQ_MODEL_NAME` | The name of the Groq model to use | None |
| `GROQ_API_KEY` | Groq API Key | None |

## Dependencies

- `mcp[cli]` - Model Context Protocol implementation
- `httpx` - HTTP client for Python
- `loguru` - Python logging made simple
- `groq` - Groq API client
- `ollama` - Interface to Ollama for local models
- `tavily-python` - Search Engine tailored for AI agents
- `fastapi` - Web framework for building APIs
- `uvicorn` - ASGI server implementation
- `htmldocx` - HTML to DOCX converter
- `playwright` - Browser automation
- `duckduckgo-search` - Search engine integration
- `python-docx` - DOCX file handling
- `markdown` - Markdown processing

## License

[MIT](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
