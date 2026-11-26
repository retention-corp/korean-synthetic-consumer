# Interview follow-up evaluation

## Calibrate with the public cases

Use one model to generate questions and a different model to judge them. To use
two local GGUF models, run the following from the repository root. The server
uses each model's embedded chat template and listens on a private Unix socket.

```sh
socket_dir=$(mktemp -d /tmp/interview-eval.XXXXXX)
llama-server --offline --host "$socket_dir/generator.sock" --no-webui --log-disable \
  --parallel 1 --ctx-size 4096 --load-mode none -m /path/to/generator.gguf &
generator_pid=$!
llama-server --offline --host "$socket_dir/judge.sock" --no-webui --log-disable \
  --parallel 1 --ctx-size 4096 --load-mode none -m /path/to/judge.gguf &
judge_pid=$!

runner="python3 evals/interviews/llama_server_runner.py $socket_dir/generator.sock --temperature 0.2"
judge="python3 evals/interviews/llama_server_runner.py $socket_dir/judge.sock"
# Wait until both models return HTTP 200.
curl --unix-socket "$socket_dir/generator.sock" --fail http://localhost/health
curl --unix-socket "$socket_dir/judge.sock" --fail http://localhost/health
python3 evals/interviews/calibrate.py --runner "$runner" --judge "$judge" \
  --out /tmp/interview-calibration.json
# After the evaluations, stop both servers.
kill "$generator_pid" "$judge_pid"
```

For each public dialogue, the calibration samples three questions from the original
guide. Read all nine and confirm that each is one natural Korean question grounded
in the respondent's correction. Record how many ask what the respondent did in a
specific past situation.

The judge sees each fixed pair twice, with A and B reversed. It should prefer
the grounded past-action question over the rejected premise and the hypothetical
pitch. It should tie equivalent phrasings and identical questions. The command
returns a nonzero exit code for any format or control mismatch and writes the
observations to the report. Inspect the generated questions and judge evidence
before deciding whether to evaluate any private case.

### Public run on 2026-11-26

The generator was Qwen3-4B-Instruct-2507 Q8_0 at temperature 0.2. Gemma 3
12B IT Q4_K_M judged at temperature 0. Both ran locally with llama.cpp build
11669 and their embedded chat templates.
[Qwen GGUF](https://huggingface.co/bartowski/Qwen_Qwen3-4B-Instruct-2507-GGUF/blob/ae44f08e1392f39c0e474af10c3ff8355c8b6688/Qwen_Qwen3-4B-Instruct-2507-Q8_0.gguf)
[Gemma GGUF](https://huggingface.co/bartowski/google_gemma-3-12b-it-GGUF/blob/648e3a36a77c8a9f12d86e741f9dcb9089c769c4/google_gemma-3-12b-it-Q4_K_M.gguf)

- All 9 generations used a single Korean question and addressed the issue in
  the respondent's correction. In manual review, 0 of 9 asked what the
  respondent did in a specific past incident. One question also assumed the
  stated issue was the respondent's biggest inconvenience.
- All 12 control pairs matched the expected outcome in both orders across
  24 judgments. For one identical pair, the judge correctly tied the answers
  but incorrectly described their wording as different.

## Compare interview guides

Run from the repository root. Use Python 3 and a command that reads a prompt from stdin and writes only its model answer to stdout.

```sh
python3 evals/interviews/run.py --runner ./model-stdin --judge ./judge-stdin \
  --attempts 3 --repeats 3 --out /tmp/interview-eval-001
```

The runner evaluates the interview template on one-turn dialogue continuations. It generates baseline questions on the development cases, proposes a small template addition, and compares both versions using the same respondent turn. For each generated pair, the judge sees the same two answers in both orders without the guide labels. Conflicting preferences count as disagreements. A candidate advances to manual review only if it wins more often than it loses on both splits, all judge outputs are valid and consistent, and all candidate questions pass the format check. If development results do not improve, the next revision receives the development failures. The final candidate is frozen before opening the holdout. The live template is never overwritten. Reusing the same holdout while editing the skill makes it a development case.

Supply private cases with `--cases /private/path/cases.json` and a local-only model runner. Keep `--out` outside the public checkout. The included cases are fictional. Each case has an id, split and dialogue ending with a respondent turn. Set distinct commands for generation and judging to compare model families. With no separate judge, the same model judges in a fresh invocation. The output records the candidate, raw model interactions, pairwise outcomes and original template checksum. Each repeated trial on one dialogue still represents a single case.

A local ChatML/Qwen instruction model can be used with `--runner "python3 evals/interviews/local_runner.py /path/model.gguf"` when llama.cpp is installed. The included adapter constrains the response format. An embedding, search expansion, or reranking model is unsuitable for judging research quality. Inspect the raw output even when the score looks good. Malformed candidate questions block promotion.
