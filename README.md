# ⚡️ mcpo

Expose any MCP tool as an OpenAPI-compatible HTTP server—instantly.

mcpo is a dead-simple proxy that takes an MCP server command and makes it accessible via standard RESTful OpenAPI, so your tools "just work" with LLM agents and apps expecting OpenAPI servers.

No custom protocol. No glue code. No hassle.

## 🤔 Why Use mcpo Instead of Native MCP?

MCP servers usually speak over raw stdio, which is:

- 🔓 Inherently insecure
- ❌ Incompatible with most tools
- 🧩 Missing standard features like docs, auth, error handling, etc.

mcpo solves all of that—without extra effort:

- ✅ Works instantly with OpenAPI tools, SDKs, and UIs
- 🛡 Adds security, stability, and scalability using trusted web standards
- 🧠 Auto-generates interactive docs for every tool, no config needed
- 🔌 Uses pure HTTP—no sockets, no glue code, no surprises

What feels like "one more step" is really fewer steps with better outcomes.

mcpo makes your AI tools usable, secure, and interoperable—right now, with zero hassle.

## 🚀 Quick Usage

We recommend using uv for lightning-fast startup and zero config.

```bash
uvx mcpo --port 8000 --api-key "top-secret" -- your_mcp_server_command
```

Or, if you’re using Python:

```bash
pip install mcpo
mcpo --port 8000 --api-key "top-secret" -- your_mcp_server_command
```

To use an SSE-compatible MCP server, simply specify the server type and endpoint:

```bash
mcpo --port 8000 --api-key "top-secret" --server-type "sse" -- http://127.0.0.1:8001/sse
```

You can also provide headers for the SSE connection:

```bash
mcpo --port 8000 --api-key "top-secret" --server-type "sse" --header '{"Authorization": "Bearer token", "X-Custom-Header": "value"}' -- http://127.0.0.1:8001/sse
```

To use a Streamable HTTP-compatible MCP server, specify the server type and endpoint:

```bash
mcpo --port 8000 --api-key "top-secret" --server-type "streamable-http" -- http://127.0.0.1:8002/mcp
```

You can also run mcpo via Docker with no installation:

```bash
docker run -p 8000:8000 ghcr.io/open-webui/mcpo:main --api-key "top-secret" -- your_mcp_server_command
```

## 🐳 Docker Deployment Examples

### Using Docker Run with Config File

Run MCPO with a configuration file and access the WebUI for easy management:

```bash
# Create a config directory
mkdir -p config

# Run with config file and WebUI access
docker run -d --name mcpo-webui \
  -p 8000:8000 \
  -v $(pwd)/config:/app/config \
  --user root \
  ghcr.io/gilberth/mcpo:latest \
  --config /app/config/config.json \
  --host 0.0.0.0 \
  --port 8000 \
  --hot-reload

# Access the WebUI at: http://localhost:8000/webui
# Access the API docs at: http://localhost:8000/docs
```

### Using Docker Compose (Recommended)

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  mcpo-webui:
    image: ghcr.io/gilberth/mcpo:latest
    container_name: mcpo-webui
    ports:
      - "8000:8000"
    volumes:
      - ./config:/app/config
      - ./config.json:/app/config.json
    environment:
      - PYTHONUNBUFFERED=1
    command: >
      --config /app/config.json
      --host 0.0.0.0
      --port 8000
      --hot-reload
    restart: unless-stopped
    user: root
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/webui"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Then run:

```bash
# Start the services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the services
docker-compose down
```

### Available Docker Images

The repository automatically builds multi-platform Docker images:

- **Latest stable**: `ghcr.io/gilberth/mcpo:latest`
- **Development**: `ghcr.io/gilberth/mcpo:main`  
- **Specific version**: `ghcr.io/gilberth/mcpo:v1.0.0`

**Supported architectures**: linux/amd64, linux/arm64

Example:

```bash
uvx mcpo --port 8000 --api-key "top-secret" -- uvx mcp-server-time --local-timezone=America/New_York
```

That's it. Your MCP tool is now available at http://localhost:8000 with a generated OpenAPI schema — test it live at [http://localhost:8000/docs](http://localhost:8000/docs).

🌐 **Web Configuration Interface**: Access the built-in configuration manager at [http://localhost:8000/webui](http://localhost:8000/webui) to manage your MCP servers through a user-friendly web interface.

🤝 **To integrate with Open WebUI after launching the server, check our [docs](https://docs.openwebui.com/openapi-servers/open-webui/).**

### 🔄 Using a Config File

You can serve multiple MCP tools via a single config file that follows the [Claude Desktop](https://modelcontextprotocol.io/quickstart/user) format.

Enable hot-reload mode with `--hot-reload` to automatically watch your config file for changes and reload servers without downtime:

Start via:

```bash
mcpo --config /path/to/config.json
```

Or with hot-reload enabled:

```bash
mcpo --config /path/to/config.json --hot-reload
```

Example config.json:

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "time": {
      "command": "uvx",
      "args": ["mcp-server-time", "--local-timezone=America/New_York"]
    },
    "mcp_sse": {
      "type": "sse", // Explicitly define type
      "url": "http://127.0.0.1:8001/sse",
      "headers": {
        "Authorization": "Bearer token",
        "X-Custom-Header": "value"
      }
    },
    "mcp_streamable_http": {
      "type": "streamable-http",
      "url": "http://127.0.0.1:8002/mcp"
    } // Streamable HTTP MCP Server
  }
}
```

Each tool will be accessible under its own unique route, e.g.:
- http://localhost:8000/memory
- http://localhost:8000/time

Each with a dedicated OpenAPI schema and proxy handler. Access full schema UI at: `http://localhost:8000/<tool>/docs`  (e.g. /memory/docs, /time/docs)

## 🌐 Web Configuration Interface

MCPO includes a built-in web interface for managing your MCP server configurations. This is particularly useful when running in Docker containers or when you want to modify configurations without editing files manually.

### Accessing the Web Interface

When MCPO is running with a config file, access the web interface at:
- **Local**: http://localhost:8000/webui
- **Docker**: http://localhost:8000/webui (or your configured port)

### Features

- ✅ **Visual Configuration Editor**: Add, edit, and remove MCP servers through a user-friendly interface
- ✅ **Real-time Validation**: Config validation with immediate feedback
- ✅ **JSON Preview**: See the raw configuration before saving
- ✅ **Support for All Server Types**: stdio, SSE, and Streamable HTTP servers
- ✅ **Hot Reload Compatible**: Changes take effect immediately when hot-reload is enabled

### Docker Usage with Web Interface

The web interface is fully integrated and automatically available when running MCPO with Docker. See the [Docker Deployment Examples](#-docker-deployment-examples) section above for complete setup instructions.

The web interface automatically saves configurations to the mounted config directory, making it persistent across container restarts.

## 🔧 Requirements

- Python 3.8+
- uv (optional, but highly recommended for performance + packaging)

## 🛠️ Development & Testing

To contribute or run tests locally:

1.  **Set up the environment:**
    ```bash
    # Clone the repository
    git clone https://github.com/open-webui/mcpo.git
    cd mcpo

    # Install dependencies (including dev dependencies)
    uv sync --dev
    ```

2.  **Run tests:**
    ```bash
    uv run pytest
    ```

3.  **Running Locally with Active Changes:**

    To run `mcpo` with your local modifications from a specific branch (e.g., `my-feature-branch`):

    ```bash
    # Ensure you are on your development branch
    git checkout my-feature-branch

    # Make your code changes in the src/mcpo directory or elsewhere

    # Run mcpo using uv, which will use your local, modified code
    # This command starts mcpo on port 8000 and proxies your_mcp_server_command
    uv run mcpo --port 8000 -- your_mcp_server_command

    # Example with a test MCP server (like mcp-server-time):
    # uv run mcpo --port 8000 -- uvx mcp-server-time --local-timezone=America/New_York
    ```
    This allows you to test your changes interactively before committing or creating a pull request. Access your locally running `mcpo` instance at `http://localhost:8000` and the auto-generated docs at `http://localhost:8000/docs`.


## 🪪 License

MIT

## 🤝 Contributing

We welcome and strongly encourage contributions from the community!

Whether you're fixing a bug, adding features, improving documentation, or just sharing ideas—your input is incredibly valuable and helps make mcpo better for everyone.

Getting started is easy:

- Fork the repo
- Create a new branch
- Make your changes
- Open a pull request

Not sure where to start? Feel free to open an issue or ask a question—we’re happy to help you find a good first task.

## ✨ Star History

<a href="https://star-history.com/#open-webui/mcpo&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=open-webui/mcpo&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=open-webui/mcpo&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=open-webui/mcpo&type=Date" />
  </picture>
</a>

---

✨ Let's build the future of interoperable AI tooling together!
