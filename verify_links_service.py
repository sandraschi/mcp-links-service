import sys
import os

# Add src to path
sys.path.append(os.path.abspath("src"))

from mcp_links_service.server import (
    _list_webapps_logic,
    _list_containers_logic,
    _get_webapp_status_logic,
)


def verify():
    print("--- Webapps Status ---")
    webapps = _list_webapps_logic()
    for app in webapps:
        print(f"[{app['status']}] {app['label']} (Port: {app['port']})")

    print("\n--- Container Links ---")
    containers = _list_containers_logic()
    for container in containers:
        print(f"{container['label']}: {container['url']}")

    print("\n--- Detailed Status (Robotics MCP) ---")
    status = _get_webapp_status_logic("robotics-mcp")
    # Clean up large dicts for printing
    if "memory_info" in status:
        status["memory_info"] = "..."
    print(status)


if __name__ == "__main__":
    verify()
