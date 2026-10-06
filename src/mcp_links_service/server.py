import json
import os
import socket
import subprocess

import psutil
from fastmcp import FastMCP

# Define paths
REPOS_ROOT = "D:/Dev/repos"
CENTRAL_DOCS = os.path.join(REPOS_ROOT, "mcp-central-docs")
WEBAPP_REGISTRY = os.path.join(CENTRAL_DOCS, "docs/operations/webapp-registry.json")
CONTAINER_REGISTRY = os.path.join(CENTRAL_DOCS, "docs/operations/container-registry.json")

# Create MCP server
mcp = FastMCP("Links Service")


def get_port_status(port: int) -> str:
    """Checks if a port is open and listening."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.2)
        try:
            s.connect(("127.0.0.1", port))
            return "Running"
        except (TimeoutError, ConnectionRefusedError):
            return "Disconnected"


def find_process_by_port(port: int) -> psutil.Process | None:
    """Finds the process ID listening on a specific port."""
    try:
        for conn in psutil.net_connections(kind="inet"):
            if conn.laddr.port == port and conn.status == "LISTEN":
                try:
                    return psutil.Process(conn.pid)
                except psutil.NoSuchProcess:
                    return None
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        return None
    return None


def _list_webapps_logic() -> list[dict]:
    if not os.path.exists(WEBAPP_REGISTRY):
        return []
    with open(WEBAPP_REGISTRY) as f:
        data = json.load(f)
    apps = data.get("webapps", [])
    for app in apps:
        app["status"] = get_port_status(app["port"])
    return apps


def _list_containers_logic() -> list[dict]:
    if not os.path.exists(CONTAINER_REGISTRY):
        return []
    with open(CONTAINER_REGISTRY) as f:
        data = json.load(f)
    return data.get("containers", [])


def _get_webapp_status_logic(app_id: str) -> dict:
    if not os.path.exists(WEBAPP_REGISTRY):
        return {"error": "Registry not found"}
    with open(WEBAPP_REGISTRY) as f:
        data = json.load(f)
    app = next((a for a in data["webapps"] if a["id"] == app_id), None)
    if not app:
        return {"error": f"Webapp '{app_id}' not found."}
    app["status"] = get_port_status(app["port"])
    proc = find_process_by_port(app["port"])
    if proc:
        try:
            app["pid"] = proc.pid
            app["cpu_percent"] = proc.cpu_percent(interval=0.1)
            app["memory_info"] = proc.memory_info()._asdict()
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
    return app


# --- MCP Tools ---


@mcp.tool()
def list_webapps() -> list[dict]:
    """Lists all registered webapps and their current status."""
    return _list_webapps_logic()


@mcp.tool()
def list_containers() -> list[dict]:
    """Lists all registered container links."""
    return _list_containers_logic()


@mcp.tool()
def launch_webapp(app_id: str) -> str:
    """Launches a webapp by its ID using its registered start command."""
    if not os.path.exists(WEBAPP_REGISTRY):
        return "Error: Registry not found."
    with open(WEBAPP_REGISTRY) as f:
        data = json.load(f)
    app = next((a for a in data["webapps"] if a["id"] == app_id), None)
    if not app:
        return f"Error: Webapp '{app_id}' not found in registry."
    if get_port_status(app["port"]) == "Running":
        return f"Webapp '{app_id}' is already running on port {app['port']}."
    try:
        subprocess.Popen(
            app["start_command"],
            cwd=app["repo_path"],
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
        )
        return f"Launch command issued for '{app_id}'."
    except Exception as e:
        return f"Failed to launch '{app_id}': {e!s}"


@mcp.tool()
def stop_webapp(app_id: str) -> str:
    """Stops a webapp by killing the process on its registered port."""
    app_info = _get_webapp_status_logic(app_id)
    if "error" in app_info:
        return app_info["error"]
    proc = find_process_by_port(app_info["port"])
    if not proc:
        return "No running process found."
    try:
        proc.terminate()
        return f"Stop signal sent to '{app_id}' (PID {proc.pid})."
    except Exception as e:
        return f"Failed to stop: {e!s}"


@mcp.tool()
def get_webapp_status(app_id: str) -> dict:
    """Gets the detailed status of a specific webapp."""
    return _get_webapp_status_logic(app_id)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
