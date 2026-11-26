# Interview follow-up evaluation

Run from the repository root. Use Python 3 and a command that reads a prompt from stdin and writes only its model answer to stdout.

```sh
python3 evals/interviews/run.py --runner ./model-stdin --judge ./judge-stdin \
  --attempts 3 --repeats 3 --out /tmp/interview-eval-001
```

The runner evaluates the interview template on one-turn dialogue continuations. It generates baseline questions on the development cases, proposes a small template addition, and compares both versions using the same respondent turn. The judge sees the dialogue and two unlabeled answers. If development results do not improve, the next revision receives the development failures. The final candidate is frozen before opening the holdout. A result of `review_candidate` requires more wins than losses on both splits and still needs an examination of the generated questions and judge reasons. The live template is never overwritten. Reusing the same holdout while editing the skill makes it a development case.

Supply private cases with `--cases /private/path/cases.json` and a local-only model runner. Keep `--out` outside the public checkout. The included cases are fictional. Each case has an id, split and dialogue ending with a respondent turn. Set distinct commands for generation and judging to compare model families. With no separate judge, the same model judges in a fresh invocation. The output records the candidate, raw model interactions, pairwise outcomes and original template checksum. Each repeated trial on one dialogue still represents a single case.

A local ChatML/Qwen instruction model can be used with `--runner "python3 evals/interviews/local_runner.py /path/model.gguf"` when llama.cpp is installed. The included adapter constrains the response format. An embedding, search expansion, or reranking model is unsuitable for judging research quality. Inspect the raw output even when the score looks good. Malformed candidate questions block promotion.
