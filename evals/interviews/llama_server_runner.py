"""Read a prompt from stdin and send it to a local llama-server Unix socket."""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("socket", type=Path)
    parser.add_argument("--temperature", type=float, default=0.0)
    args = parser.parse_args()
    socket = args.socket.expanduser()
    if not socket.is_socket():
        parser.error("socket must be a local Unix socket")

    request = {
        "messages": [{"role": "user", "content": sys.stdin.read()}],
        "temperature": args.temperature,
        "max_tokens": 256,
    }
    result = subprocess.run(
        ["curl", "--disable", "--fail", "--silent", "--show-error", "--noproxy", "*",
         "--max-time", "240", "--unix-socket", str(socket), "--header",
         "Content-Type: application/json", "--data-binary", "@-",
         "http://localhost/v1/chat/completions"],
        input=json.dumps(request, ensure_ascii=False), capture_output=True,
        text=True, encoding="utf-8", check=True,
    )
    choice = json.loads(result.stdout)["choices"][0]
    answer = (choice["message"].get("content") or "").strip()
    if choice["finish_reason"] != "stop" or not answer:
        sys.exit(f"Incomplete local model response (finish_reason={choice['finish_reason']})")
    print(answer)


if __name__ == "__main__":
    main()
