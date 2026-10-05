# mcp-links-service

![version](https://img.shields.io/badge/version-0.1.0-amber) ![python](https://img.shields.io/badge/python-3.12%2B-blue) ![fastmcp](https://img.shields.io/badge/fastmcp-3.4-purple) ![platform](https://img.shields.io/badge/platform-Windows-lightgrey) ![license](https://img.shields.io/badge/license-MIT-green)

Ask Claude which of your local webapps are up, then start or stop them without leaving the chat.

## What You Can Do

**How it runs**: a stdio MCP server that reads two JSON registries (webapps and containers), probes each webapp's TCP port on `127.0.0.1`, and launches or stops processes on your machine. It does not bundle or host any of the webapps it manages.

- List every registered webapp with a live `Running` / `Disconnected` status
- List registered container links
- Launch a webapp using its registered start command and working directory
- Stop a webapp by terminating the process listening on its registered port
- Inspect one webapp: status, PID, CPU and memory of the listening process

## Quick Install

> **Current limitation**: registry paths are hardcoded to `D:/Dev/repos/mcp-central-docs/docs/operations/` (`webapp-registry.json`, `container-registry.json`). Without those files every tool returns an empty list or a "Registry not found" error. Making the paths configurable is open work.

```powershell
git clone https://github.com/sandraschi/mcp-links-service
cd mcp-links-service
uv sync
```

Then add it to `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-links-service": {
      "command": "uv",
      "args": ["--directory", "C:\\path\\to\\mcp-links-service", "run", "mcp-links-service"]
    }
  }
}
```

Restart Claude Desktop. A `native/` Tauri shell and an `mcpb/` bundle exist in the repo but are not yet documented here.

## Example Prompts

- "Which of my webapps are running right now?"
- "Start the plex webapp and tell me when it's up"
- "Stop whatever is listening for the nekomimi dashboard and show me its memory use first"

## Tools

| Tool | Purpose |
|------|---------|
| `list_webapps` | All registered webapps with live port status |
| `list_containers` | All registered container links |
| `get_webapp_status` | Status, PID, CPU and memory for one webapp |
| `launch_webapp` | Run the registered start command (no-op if the port is already open) |
| `stop_webapp` | Terminate the process on the webapp's port |

`stop_webapp` ends whatever process owns the port, and `launch_webapp` runs a shell command taken from the registry, so keep the registry files trusted.

## Requirements

Windows 10/11, Python 3.12+ via [uv](https://docs.astral.sh/uv/) (`winget install astral-sh.uv`), and the two registry JSON files described above.

## Development

```powershell
uv sync
uv run ruff check .
```

There is no test suite yet.

## License

MIT
