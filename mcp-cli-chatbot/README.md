# MCP CLI Chatbot

A completely independent, modular CLI chatbot designed to learn and demonstrate the Model Context Protocol (MCP) using Python.

## Project Architecture

This project is separated into clean, modular components:

- **`main.py`**: The main entrypoint containing the interactive CLI loop. It fetches tools from the MCP server, queries Claude, and dynamically routes tool execution.
- **`mcp_client.py`**: The local MCP Client wrapper. It establishes a `stdio` connection to the MCP server using `uv run`, fetches tools, and triggers their execution.
- **`mcp_server.py`**: The FastMCP server. It defines specific, well-typed tools like `read_document` and `edit_document`.
- **`documents.py`**: A simulated in-memory database of document texts representing local files.
- **`config.py`**: Handles initialization of the Anthropic SDK client and validation of environment keys.
- **`docs/`**: Dummy files acting as visual placeholders for the in-memory documents.

## Environment Setup

Ensure you have Python and `uv` installed, then run the following commands to initialize your environment on Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

In the root of the directory, add your Anthropic API Key to the `.env` file:
```
ANTHROPIC_API_KEY=your_key_here
```

## Running the Project

Once the environment is active and variables are set, simply run:

```powershell
python main.py
```

## Example Prompts

Try asking the CLI Chatbot things like:

- *"What tools do you have access to?"*
- *"Read the report.pdf file and summarize the performance."*
- *"Read plan.md and edit it to include Phase 5: Revenue Scaling."*

## Example Output

```
Starting MCP CLI Chatbot. Connecting to FastMCP Server...
Connected! Available tools: ['read_document', 'edit_document']
Type 'exit' to quit.

You: What were the Q1 projections in the financials?

[Tool Use] Calling read_document...
[Tool Result] 2023 FINANCIAL PROJECTIONS

- Q1: $1.2M
- Q2: $1.4M...

Claude: According to the financials.docx document, the Q1 financial projection is $1.2M.
```
