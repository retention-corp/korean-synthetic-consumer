"""Run a local ChatML/Qwen GGUF with llama-completion, using CPU inference."""
import argparse
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("model", type=Path)
args = parser.parse_args()
prompt = sys.stdin.read()
formatted = ("<|im_start|>system\nYou follow instructions exactly. /no_think<|im_end|>\n"
             f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n")
if prompt.startswith("Independently judge"):
    grammar = r'root ::= ("A" | "B" | "TIE") "\n" [A-Z가-힣] [^\n]*'
elif prompt.startswith("You edit reusable"):
    grammar = 'root ::= [A-Z] [A-Za-z ,]+ "."'
else:
    grammar = r'root ::= [가-힣] [^\n?]+ "?"'

command = ["llama-completion", "-m", str(args.model.expanduser()), "--no-conversation",
           "--no-display-prompt", "--device", "none", "--fit", "off", "--no-op-offload",
           "--no-kv-offload", "-ngl", "0", "-t", "6", "-c", "3072", "-n", "150",
           "--grammar", grammar, "--temp", "0.45", "-p", formatted]
result = subprocess.run(command, stdin=subprocess.DEVNULL, capture_output=True, text=True)
if result.returncode:
    sys.exit(result.stderr[-1500:])
print(result.stdout.strip().removesuffix("[end of text]").strip())
