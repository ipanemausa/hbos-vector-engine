import subprocess
import json
import sys

proc = subprocess.Popen(
    ['node', r'C:\Users\ipane\.gemini\config\hbos-freellmapi\index.js'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    encoding='utf-8'
)

# Enviar initialize
init_req = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test-client", "version": "1.0.0"}
    }
}

proc.stdin.write(json.dumps(init_req) + "\n")
proc.stdin.flush()

line = proc.stdout.readline()
err = proc.stderr.read() if not line else ""
print(f"Stdout raw: {repr(line)}")
if err:
    print(f"Stderr raw: {repr(err)}")

if line:
    data = json.loads(line)
    print("Init response:", data)

    # Notificar initialized
    notif = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    proc.stdin.write(json.dumps(notif) + "\n")
    proc.stdin.flush()

    # Tools list
    proc.stdin.write(json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}) + "\n")
    proc.stdin.flush()
    tools_line = proc.stdout.readline()
    print("Tools response:", json.loads(tools_line))

    # Call list_models tool
    call_req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "list_models",
            "arguments": {}
        }
    }
    proc.stdin.write(json.dumps(call_req) + "\n")
    proc.stdin.flush()
    call_line = proc.stdout.readline()
    print("\nCall list_models response:", json.loads(call_line))

proc.kill()
