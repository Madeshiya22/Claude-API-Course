# MCP Course Project

This is a brand new Python project for learning the Model Context Protocol (MCP).

## Project Setup

This project uses [uv](https://github.com/astral-sh/uv) as the package manager. `uv` is extremely fast and manages both Python versions and virtual environments.

### UV Installation

If you haven't installed `uv` yet, you can do so via:

```powershell
# Windows PowerShell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Virtual Environment Activation & Setup

Run these commands in Windows PowerShell to set up the project:

```powershell
# Initialize UV project (if starting from scratch)
# uv init .

# Pin Python version
uv python pin 3.12

# Create virtual environment
uv venv

# Activate venv
.venv\Scripts\activate

# Install dependencies
uv add mcp anthropic python-dotenv

# Generate lock file / sync
uv sync
```

## How to Run

### Run the Server
```powershell
uv run src/server.py
```

### Run the Client
```powershell
uv run src/client.py
```

## Folder Explanation

- `.venv/`: The isolated virtual environment for dependencies.
- `src/`: Contains all source code for the project.
  - `server.py`: The main MCP server entry point.
  - `client.py`: The MCP client to interact with the server.
  - `config.py`: Configuration settings and environment variables.
  - `tools.py`: Definition of MCP tools.
  - `resources.py`: Definition of MCP resources.
  - `prompts.py`: Definition of MCP prompts.
  - `utils.py`: Helper functions and utilities.
- `.env`: Environment variables (API keys, etc.) - Git ignored.
- `.env.example`: Template for environment variables.
- `pyproject.toml`: Project metadata and dependency definitions.
- `uv.lock`: Locked dependency versions for reproducible builds.
