"""
MCP wrapper around the verification HTTP service.

Exposes the verification layer as an MCP tool that any MCP client
(Claude Desktop, Cursor, Cline, OpenAI agents, custom agents) can call.

Architecture:
    LLM client (Claude Desktop, etc.)
        ↓ stdio (MCP protocol)
    THIS PROCESS — verification_mcp.py
        ↓ HTTP POST
    Verification service (localhost:5000)
        ↓ kubectl
    kind cluster
"""

import os
import requests

from mcp.server.fastmcp import FastMCP

# Where the verification HTTP service is reachable.
# Configurable via env var so this MCP wrapper can talk to a remote
# verification service if needed.
VERIFICATION_URL = os.getenv("VERIFICATION_URL", "http://localhost:5000/verify")

mcp = FastMCP("verification-layer", host="0.0.0.0", port=8080)


@mcp.tool()
def kubectl_action(
    verb: str,
    resource: str,
    namespace: str = "agent-sandbox",
    replicas: int | None = None,
) -> dict:
    """
    Submit a kubectl action through the verification layer.

    The verification layer applies safety policies and either executes
    the action against the kind cluster (if allowed) or refuses it.
    Every action is logged to the audit log.

    Args:
        verb: The kubectl verb. One of: get, create, apply, scale, delete.
        resource: Resource specification, e.g., "deployment/test-app" or "deployments".
        namespace: Kubernetes namespace. Default: agent-sandbox.
        replicas: For 'scale' verb only. Number of replicas to scale to.

    Returns:
        A dict with action_id, decision (status, reason, policy),
        and real_outcome (if the action was allowed and executed).
    """
    payload = {
        "tool": "kubectl",
        "verb": verb,
        "resource": resource,
        "namespace": namespace,
    }

    if verb == "scale" and replicas is not None:
        payload["params"] = {"replicas": replicas}

    try:
        response = requests.post(VERIFICATION_URL, json=payload, timeout=20)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {
            "error": "verification_layer_unreachable",
            "message": f"Cannot reach verification layer at {VERIFICATION_URL}. Is the service running?",
        }
    except requests.exceptions.HTTPError as e:
        return {
            "error": "verification_layer_http_error",
            "status_code": e.response.status_code,
            "message": str(e),
        }
    except Exception as e:
        return {"error": "unexpected", "message": str(e)}


@mcp.tool()
def get_action_log(limit: int = 10) -> list[dict]:
    """
    Read the most recent N entries from the action audit log.

    Useful for the LLM to inspect what actions have been attempted
    and their outcomes.

    Args:
        limit: Maximum number of recent entries to return. Default: 10.

    Returns:
        A list of action records, each containing action_id, timestamp,
        action, decision, and real_outcome.
    """
    import json

    LOG_FILE = os.path.expanduser("~/testbed/logs/action_log.jsonl")

    try:
        with open(LOG_FILE) as f:
            lines = f.readlines()
    except FileNotFoundError:
        return [{"error": "no_log_yet", "message": "No actions recorded yet."}]

    recent = lines[-limit:] if limit > 0 else lines
    return [json.loads(line) for line in recent]


@mcp.tool()
def health_check() -> dict:
    """
    Check that the verification layer is alive and responding.

    Returns:
        Status info about the verification service.
    """
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        return response.json()
    except Exception as e:
        return {"status": "unreachable", "error": str(e)}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
