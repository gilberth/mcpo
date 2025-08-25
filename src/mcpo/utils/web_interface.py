import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ValidationError
import logging

logger = logging.getLogger(__name__)

class MCPServerConfig(BaseModel):
    command: Optional[str] = None
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    type: Optional[str] = None
    url: Optional[str] = None
    headers: Optional[Dict[str, str]] = None

class MCPConfig(BaseModel):
    mcpServers: Dict[str, MCPServerConfig]

def create_web_interface_router(config_path: Optional[str] = None) -> APIRouter:
    """Create router for web interface endpoints"""
    router = APIRouter(prefix="/webui", tags=["webui"])
    
    def get_config_path() -> str:
        """Get the config file path"""
        if config_path:
            return config_path
        # Default config path
        return "/app/config.json"
    
    def load_config_file() -> Dict[str, Any]:
        """Load config from file"""
        path = get_config_path()
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return json.load(f)
            return {"mcpServers": {}}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {"mcpServers": {}}
    
    def save_config_file(config_data: Dict[str, Any]) -> None:
        """Save config to file"""
        path = get_config_path()
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Check if file exists and permissions
            if os.path.exists(path):
                # Check if we can write to the file
                if not os.access(path, os.W_OK):
                    logger.error(f"No write permission for {path}")
                    raise PermissionError(f"No write permission for {path}")
            
            with open(path, 'w') as f:
                json.dump(config_data, f, indent=2)
            logger.info(f"Config saved to {path}")
        except PermissionError as e:
            logger.error(f"Permission error saving config: {e}")
            raise HTTPException(status_code=500, detail=f"Permission denied: {str(e)}. Please ensure the config file has write permissions for the mcpo user.")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to save config: {str(e)}")

    @router.get("/", response_class=HTMLResponse)
    async def web_interface():
        """Serve the web interface"""
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCPO Configuration Manager</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .server-config { border: 1px solid #ddd; margin-bottom: 15px; padding: 15px; border-radius: 5px; }
        .server-config.active { border-color: #3498db; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: 500; }
        input, select, textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        textarea { height: 80px; }
        .btn { padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px; }
        .btn-primary { background: #3498db; color: white; }
        .btn-success { background: #27ae60; color: white; }
        .btn-danger { background: #e74c3c; color: white; }
        .btn-secondary { background: #95a5a6; color: white; }
        .btn:hover { opacity: 0.9; }
        .json-preview { background: #f8f9fa; border: 1px solid #ddd; padding: 15px; border-radius: 4px; }
        .status { padding: 10px; border-radius: 4px; margin-bottom: 20px; }
        .status.success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
        .status.error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
        .server-type-fields { margin-top: 10px; }
        .hidden { display: none; }
        .main-layout { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
        .preview-section { }
        .example-box { background: #e8f4f8; border: 1px solid #bee5eb; padding: 15px; border-radius: 4px; margin-bottom: 15px; }
        .example-title { font-weight: bold; color: #0c5460; margin-bottom: 10px; }
        .example-code { background: #f8f9fa; border: 1px solid #ddd; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 12px; white-space: pre-wrap; }
        .form-example { font-size: 12px; color: #666; margin-top: 5px; font-style: italic; }
        @media (max-width: 768px) { .main-layout { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 MCPO Configuration Manager</h1>
            <p>Manage your MCP server configurations</p>
        </div>

        <div id="status" class="status hidden"></div>

        <div class="main-layout">
            <div class="editor-section">
                <div class="card">
                    <h2>MCP Servers Configuration</h2>
                    <div id="servers-container">
                        <!-- Server configs will be loaded here -->
                    </div>
                    <button class="btn btn-primary" onclick="addServer()">+ Add Server</button>
                    <button class="btn btn-success" onclick="saveConfig()">Save Configuration</button>
                    <button class="btn btn-secondary" onclick="loadConfig()">Reload</button>
                </div>
            </div>
            
            <div class="preview-section">
                <div class="card">
                    <h3>📋 Configuration Preview</h3>
                    <pre id="json-preview" class="json-preview"></pre>
                </div>
                
                <div class="card">
                    <h3>💡 Examples</h3>
                    
                    <div class="example-box">
                        <div class="example-title">🔧 Stdio Server (npm package)</div>
                        <div class="example-code">{
  "git-mcp": {
    "command": "npx",
    "args": [
      "mcp-remote", 
      "https://gitmcp.io/{owner}/{repo}"
    ]
  }
}</div>
                        <div class="form-example">Command: npx | Arguments: mcp-remote, https://gitmcp.io/{owner}/{repo}</div>
                    </div>
                    
                    <div class="example-box">
                        <div class="example-title">🌐 HTTP Server (Context7)</div>
                        <div class="example-code">{
  "context7": {
    "type": "streamable-http",
    "url": "https://mcp.context7.com/mcp"
  }
}</div>
                        <div class="form-example">Type: streamable-http | URL: https://mcp.context7.com/mcp</div>
                    </div>
                    
                    <div class="example-box">
                        <div class="example-title">📦 Local Python Server</div>
                        <div class="example-code">{
  "memory": {
    "command": "uvx",
    "args": ["mcp-server-memory"],
    "env": {
      "MEMORY_DIR": "/tmp/memory"
    }
  }
}</div>
                        <div class="form-example">Command: uvx | Arguments: mcp-server-memory | Environment: {"MEMORY_DIR": "/tmp/memory"}</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let config = { mcpServers: {} };

        function autoUpdatePreview() {
            updatePreview();
        }

        function showStatus(message, type = 'success') {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = `status ${type}`;
            status.classList.remove('hidden');
            setTimeout(() => status.classList.add('hidden'), 3000);
        }

        function addServer() {
            const name = prompt('Server name:');
            if (!name || config.mcpServers[name]) {
                showStatus('Invalid or duplicate server name', 'error');
                return;
            }
            
            config.mcpServers[name] = {
                command: '',
                args: []
            };
            renderServers();
            autoUpdatePreview();
        }

        function removeServer(name) {
            if (confirm(`Remove server "${name}"?`)) {
                delete config.mcpServers[name];
                renderServers();
                autoUpdatePreview();
            }
        }

        function updateServerType(name, type) {
            const server = config.mcpServers[name];
            server.type = type;
            
            // Clear incompatible fields
            if (type === 'stdio') {
                delete server.url;
                delete server.headers;
            } else {
                delete server.command;
                delete server.args;
                delete server.env;
            }
            
            renderServers();
            autoUpdatePreview();
        }

        function renderServers() {
            const container = document.getElementById('servers-container');
            container.innerHTML = '';

            Object.entries(config.mcpServers).forEach(([name, server]) => {
                const serverDiv = document.createElement('div');
                serverDiv.className = 'server-config';
                serverDiv.innerHTML = `
                    <h3>${name} <button class="btn btn-danger" onclick="removeServer('${name}')">Remove</button></h3>
                    
                    <div class="form-group">
                        <label>Server Type:</label>
                        <select onchange="updateServerType('${name}', this.value)">
                            <option value="stdio" ${(!server.type || server.type === 'stdio') ? 'selected' : ''}>Stdio</option>
                            <option value="sse" ${server.type === 'sse' ? 'selected' : ''}>SSE</option>
                            <option value="streamable-http" ${server.type === 'streamable-http' ? 'selected' : ''}>Streamable HTTP</option>
                        </select>
                    </div>
                    
                    <div class="stdio-fields ${(!server.type || server.type === 'stdio') ? '' : 'hidden'}">
                        <div class="form-group">
                            <label>Command:</label>
                            <input type="text" value="${server.command || ''}" 
                                placeholder="npx, uvx, python, node..." 
                                onchange="updateServerCommand('${name}', this.value); autoUpdatePreview();" id="command-${name}">
                            <div class="form-example">Example: npx (for npm packages), uvx (for Python tools), python3 (for scripts)</div>
                        </div>
                        <div class="form-group">
                            <label>Arguments (one per line):</label>
                            <textarea placeholder="mcp-server-time&#10;--local-timezone=America/New_York" 
                                onchange="updateServerArgs('${name}', this.value); autoUpdatePreview();" id="args-${name}">${(server.args || []).join('\\\\n')}</textarea>
                            <div class="form-example">Example: Each argument on a new line. For "mcp-remote https://gitmcp.io/{owner}/{repo}", put "mcp-remote" on first line, "https://gitmcp.io/{owner}/{repo}" on second</div>
                        </div>
                        <div class="form-group">
                            <label>Environment (JSON format):</label>
                            <textarea placeholder='{"API_KEY": "your-key", "DEBUG": "true"}' 
                                onchange="try { const val = this.value.trim(); config.mcpServers['${name}'].env = val ? JSON.parse(val) : {}; autoUpdatePreview(); } catch(e) { showStatus('Invalid JSON for env', 'error'); }">${JSON.stringify(server.env || {}, null, 2)}</textarea>
                            <div class="form-example">Optional: JSON object with environment variables. Use {"VARIABLE_NAME": "value"} format</div>
                        </div>
                    </div>
                    
                    <div class="remote-fields ${(server.type === 'sse' || server.type === 'streamable-http') ? '' : 'hidden'}">
                        <div class="form-group">
                            <label>URL:</label>
                            <input type="url" value="${server.url || ''}" 
                                placeholder="https://mcp.context7.com/mcp" 
                                onchange="config.mcpServers['${name}'].url = this.value; autoUpdatePreview();">
                            <div class="form-example">Example: https://mcp.context7.com/mcp (for Context7), http://localhost:3000/sse (local SSE server)</div>
                        </div>
                        <div class="form-group">
                            <label>Headers (JSON format):</label>
                            <textarea placeholder='{"Authorization": "Bearer token", "X-API-Key": "your-key"}' 
                                onchange="try { const val = this.value.trim(); config.mcpServers['${name}'].headers = val ? JSON.parse(val) : {}; autoUpdatePreview(); } catch(e) { showStatus('Invalid JSON for headers', 'error'); }">${JSON.stringify(server.headers || {}, null, 2)}</textarea>
                            <div class="form-example">Optional: JSON object with HTTP headers for authentication or custom headers</div>
                        </div>
                    </div>
                `;
                container.appendChild(serverDiv);
            });
        }

        function updateServerCommand(serverName, command) {
            config.mcpServers[serverName].command = command;
            console.log('Updated command for ' + serverName + ':', command);
        }

        function updateServerArgs(serverName, argsText) {
            const args = argsText.split('\\n').filter(a => a.trim());
            config.mcpServers[serverName].args = args;
            console.log('Updated args for ' + serverName + ':', args);
        }

        function updatePreview() {
            document.getElementById('json-preview').textContent = JSON.stringify(config, null, 2);
        }

        async function loadConfig() {
            try {
                const response = await fetch('/webui/config');
                config = await response.json();
                renderServers();
                autoUpdatePreview();
                showStatus('Configuration loaded');
            } catch (error) {
                showStatus('Failed to load configuration: ' + error.message, 'error');
            }
        }

        async function saveConfig() {
            try {
                console.log('Saving config:', JSON.stringify(config, null, 2));
                
                const response = await fetch('/webui/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(config)
                });
                
                if (response.ok) {
                    showStatus('Configuration saved successfully');
                    // Refresh the preview to show the saved state
                    autoUpdatePreview();
                } else {
                    const error = await response.text();
                    showStatus('Failed to save: ' + error, 'error');
                }
            } catch (error) {
                showStatus('Failed to save configuration: ' + error.message, 'error');
            }
        }

        // Load initial configuration and update preview
        loadConfig();
        
        // Update preview initially even if no config
        setTimeout(() => {
            autoUpdatePreview();
        }, 100);
    </script>
</body>
</html>
        """
        return html_content

    @router.get("/config")
    async def get_config():
        """Get current configuration"""
        return load_config_file()

    @router.post("/config")
    async def save_config(config_data: Dict[str, Any]):
        """Save configuration"""
        try:
            # Clean up None values before saving
            def clean_none_values(obj):
                if isinstance(obj, dict):
                    return {k: clean_none_values(v) for k, v in obj.items() if v is not None}
                elif isinstance(obj, list):
                    return [clean_none_values(item) for item in obj if item is not None]
                else:
                    return obj
            
            cleaned_config = clean_none_values(config_data)
            
            # Validate the config
            validated_config = MCPConfig(**cleaned_config)
            save_config_file(validated_config.dict(exclude_none=True))
            return {"message": "Configuration saved successfully"}
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=f"Invalid configuration: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save configuration: {str(e)}")

    @router.delete("/config/server/{server_name}")
    async def delete_server(server_name: str):
        """Delete a specific server from configuration"""
        config_data = load_config_file()
        if server_name in config_data.get("mcpServers", {}):
            del config_data["mcpServers"][server_name]
            save_config_file(config_data)
            return {"message": f"Server '{server_name}' deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"Server '{server_name}' not found")

    return router