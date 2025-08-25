# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

mcpo is a Python-based proxy that exposes MCP (Model Context Protocol) servers as OpenAPI-compatible HTTP servers. It enables seamless integration of MCP tools with standard REST APIs and web applications.

## Commands

### Development Setup
```bash
# Install dependencies (including dev dependencies)
uv sync --dev

# Run locally with active changes
uv run mcpo --port 8000 -- your_mcp_server_command
```

### Testing
```bash
# Run all tests
uv run pytest
```

### Build and Package
```bash
# Install from source
pip install -e .

# Or use uv for development
uv sync
```

## Architecture

### Core Components

- **Entry Point**: `src/mcpo/__init__.py` - CLI interface using Typer
- **Main Server**: `src/mcpo/main.py` - FastAPI application with lifecycle management
- **Authentication**: `src/mcpo/utils/auth.py` - API key middleware and verification
- **Config Management**: `src/mcpo/utils/config_watcher.py` - Hot-reload functionality for config files
- **Tool Handling**: `src/mcpo/utils/main.py` - MCP tool to OpenAPI endpoint conversion

### Server Types Supported

1. **stdio**: Standard MCP servers communicating via stdin/stdout
2. **sse**: Server-Sent Events based MCP servers  
3. **streamable-http**: HTTP-based streaming MCP servers

### Application Structure

The application uses a hierarchical FastAPI structure:
- Main app serves as the root with global middleware and documentation
- Sub-applications are mounted for each MCP server when using config files
- Each sub-app has its own OpenAPI schema and lifespan management
- Dynamic endpoint creation based on MCP tool schemas

### Key Features

- **Hot Reload**: Automatic config file watching and server reload without downtime
- **Graceful Shutdown**: Proper cleanup of MCP connections and background tasks  
- **Multi-server Support**: Single proxy can handle multiple MCP servers via config
- **Security**: API key authentication with optional strict mode
- **CORS**: Configurable cross-origin resource sharing

### Configuration

Supports both single-server mode (command line) and multi-server mode (JSON config file) following Claude Desktop format.

### Error Handling

Comprehensive error handling for MCP server connections, config validation, and graceful degradation when servers fail to connect.
- este equipo no tiene docker instalados, para ello usa ssh root@10.10.10.202 "COMANDOS" para ejeuctar comandos no solo docker en el servidor