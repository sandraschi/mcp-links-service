# mcp-links-service (MCPB Bundle)

Centralized Webapp and Container Links Service

## Usage

Add to \claude_desktop_config.json\:
\\\json
{
  "mcpServers": {
    "mcp-links-service": {
      "command": "uv",
      "args": ["run", "--directory", "\D:\Dev\repos", "python", "-m", "mcp_links_service"],
      "env": { "PYTHONPATH": "\D:\Dev\repos/src" }
    }
  }
}
\\\

## Tools

- **mcp-links-service**: Centralized Webapp and Container Links Service

## Requirements

- Python 3.12+
- uv
