# Saqr-MCP ![image](https://github.com/user-attachments/assets/2ee374a5-8b63-4f5a-b7fd-5bdae3a05e37)


Saqr-MCP is a Python application that implements the Model Context Protocol (MCP) to enable AI assistant capabilities with local models. It provides a client-server architecture where the client communicates with local models through Ollama, while the server provides tools for the LLM

## Features

- Interactive chat interface for querying the model
- Web search tool integration using DuckDuckGo and Playwright
- Local model inference through Ollama
- Async architecture for efficient processing
- Visual loading animations for better user experience

## Prerequisites

- Python 3.11 or higher
- [Ollama](https://ollama.ai/) installed with local models
- [UV](https://github.com/astral-sh/uv) package manager (recommended)

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/your-username/saqr-mcp.git
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
   playwright install chromium
   ```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Set `MODEL_NAME` to your preferred Ollama model (e.g., `qwen3:1.7b`)

## Usage

1. Make sure Ollama is running with your chosen model available

2. Run the client:

   ```bash
   python main.py
   ```

3. Type your queries in the interactive console:

   ```
   MCP Client Started!
   Type your queries or 'quit' to exit.

   Query:
   ```

4. Type `quit` to exit the application

## Project Structure

- `main.py` - Entry point that starts the MCP client
- `src/`
  - `client.py` - MCP client implementation connecting to Ollama
  - `server.py` - MCP server implementation with web search tool
  - `logger.py` - Custom logging utilities with visual animations

## Available Tools

Currently, the server implements the following tools:

- **web_search**: Searches the web using DuckDuckGo and extracts relevant content using Playwright.

## Environment Variables

| Variable     | Description                                              | Default |
| ------------ | -------------------------------------------------------- | ------- |
| `MODEL_NAME` | The name of the Ollama model to use (e.g., `qwen3:1.7b`) | None    |

## Dependencies

- `mcp[cli]` - Model Context Protocol implementation
- `httpx` - HTTP client for Python
- `playwright` - Browser automation library
- `duckduckgo-search` - API for DuckDuckGo searches
- `loguru` - Python logging made simple
- `groq` - Groq API client (optional)
- `ollama` - Interface to Ollama for local models

## License

[MIT](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
