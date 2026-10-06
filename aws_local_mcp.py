#!/usr/bin/env python3
"""
Local AWS MCP Server — zero dependencies, Python 3.9+.
Supports --profile for all 108 SSO accounts. No restarts needed.
"""

import json
import sys
import subprocess
import shlex
import os

TOOLS = [
    {
        "name": "call_aws",
        "description": (
            "Execute any AWS CLI command on the LOCAL machine with full --profile support. "
            "Use --profile <name> to target any of the 108 SSO accounts without restarting Cursor. "
            "Command MUST start with 'aws'."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "cli_command": {
                    "type": "string",
                    "description": "Full AWS CLI command starting with 'aws'. Include --profile <name> to target a specific account."
                }
            },
            "required": ["cli_command"],
            "additionalProperties": False
        }
    },
    {
        "name": "list_profiles",
        "description": "List all configured AWS SSO profiles (all 108 accounts).",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
    }
]


def run_command(args, timeout=120):
    try:
        proc = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=os.environ.copy()
        )
        if proc.returncode == 0:
            return proc.stdout or "(no output)"
        else:
            return f"Error (exit {proc.returncode}):\n{proc.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: command timed out after 120s"
    except FileNotFoundError as e:
        return f"Error: {e}"


def handle(request):
    method = request.get("method", "")
    params = request.get("params", {})
    req_id = request.get("id")

    def ok(result):
        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    def err(code, msg):
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": msg}}

    if method == "initialize":
        return ok({
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "aws-local-mcp", "version": "1.0.0"}
        })

    if method == "notifications/initialized":
        return None  # no response needed

    if method == "ping":
        return ok({})

    if method == "tools/list":
        return ok({"tools": TOOLS})

    if method == "tools/call":
        tool_name = params.get("name", "")
        args = params.get("arguments", {})

        if tool_name == "list_profiles":
            output = run_command(["aws", "configure", "list-profiles"], timeout=10)
            profiles = sorted(output.strip().splitlines())
            text = f"{len(profiles)} profiles available:\n\n" + "\n".join(profiles)
            return ok({"content": [{"type": "text", "text": text}]})

        if tool_name == "call_aws":
            cli_command = args.get("cli_command", "").strip()
            if not cli_command.startswith("aws"):
                return ok({"content": [{"type": "text", "text": "Error: command must start with 'aws'"}]})
            try:
                cmd_args = shlex.split(cli_command)
            except ValueError as e:
                return ok({"content": [{"type": "text", "text": f"Parse error: {e}"}]})

            output = run_command(cmd_args)
            return ok({"content": [{"type": "text", "text": output}]})

        return err(-32601, f"Unknown tool: {tool_name}")

    # Unknown method — return empty result (don't crash)
    return ok({})


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            continue

        response = handle(request)
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
