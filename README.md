# korean-synthetic-consumer

Portable Claude/OpenClaw skill package for building **Korean synthetic consumer/persona panels** grounded in the Hugging Face dataset [`nvidia/Nemotron-Personas-Korea`](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea).

It combines:

- a Claude/OpenClaw skill workflow,
- a lightweight Python persona sampler,
- optional Hugging Face/DuckDB/parquet tooling,
- report/prompt templates for message testing, product-fit checks, objection mapping, interview design, and full reports.

## Why

Paul's team often needs fast directional feedback for Phai, WAINBOX, ARMY, proposal-review, AX consulting, and sales/message testing. Real interviews still matter, but synthetic panels are useful for finding blind spots before spending recruiting time and budget.

## What this is not

Synthetic personas are **hypothesis generation**, not statistically valid market research proof. Do not use outputs as the sole basis for investment, hiring, legal, medical, financial, or major go/no-go decisions.

## Install

```bash
git clone <your-repo-url> korean-synthetic-consumer
cd korean-synthetic-consumer
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

For offline-only usage with `examples/example-personas.json`, you can skip `requirements.txt` and use Python 3 standard library only. Install optional dependencies only when you want Hugging Face/DuckDB access.

The package is light by default. It does **not** download the full dataset during install or build.

## Quickstart

Offline test with bundled sample personas:

```bash
python scripts/sample_personas.py --dataset examples/example-personas.json --n 2 --output markdown
```

Sample from Hugging Face when optional dependencies and network are available:

```bash
python scripts/sample_personas.py \
  --n 5 \
  --seed 7 \
  --region 서울 \
  --occupation 마케터 \
  --output json \
  --cache-dir .cache/huggingface > personas.json
```

Build a panel scaffold without calling any paid LLM API:

```bash
python scripts/build_panel_report.py \
  --personas examples/example-personas.json \
  --product "WAINBOX: 제안서 초안을 고객사 맥락에 맞게 자동 리뷰하는 AI 워크플로" \
  --mode full-report \
  --title "WAINBOX Proposal Review" \
  --output examples/example-report.md
```

Then paste the generated scaffold into Claude/OpenClaw or use it as a report skeleton.

Run the offline self-check:

```bash
scripts/self_check.sh
```

## Use as an OpenClaw / Claude skill

Option A — use directly from this repository:

```bash
git clone https://github.com/hackinggrowth/korean-synthetic-consumer.git
cd korean-synthetic-consumer
python3 scripts/self_check.sh
```

Option B — install as a local skill copy:

```bash
mkdir -p ~/.openclaw/skills/korean-synthetic-consumer
cp -R SKILL.md README.md scripts templates examples requirements.txt LICENSE ~/.openclaw/skills/korean-synthetic-consumer/
```

Suggested prompt:

```text
Use korean-synthetic-consumer in message-test mode.
Product/message: <paste copy or concept>
Target segment: Korean SMB owners / B2B SaaS marketers / etc.
Panel size: 5 personas.
Output: skeptical reactions, objection map, revised message, next real-world validation.
```

## Real-data smoke test

After installing optional dependencies, run a tiny Hugging Face smoke test:

```bash
python3 scripts/sample_personas.py \
  --dataset nvidia/Nemotron-Personas-Korea \
  --n 2 \
  --seed 7 \
  --region 서울 \
  --output markdown \
  --cache-dir .cache/huggingface
```

If this fails because of network, Hugging Face auth, or schema changes, continue with local JSON examples and re-check the dataset card before production use.

## Recommended validation ladder

1. Synthetic panel: find likely objections and weak claims.
2. Real customer interviews: validate whether objections actually appear.
3. Small message/prototype test: measure behavior, not just stated preference.
4. Decision memo: mark findings as `[hypothesis]`, `[verified]`, or `[experimental]`.

## Use modes

- `message-test`: copy, outreach, landing page, proposal message testing
- `product-fit`: concept fit, adoption trigger, WTP, workflow integration
- `objection-map`: sales/proposal objections and proof requirements
- `persona-panel`: quick multi-persona first read
- `interview-script`: convert synthetic findings into real interview questions
- `full-report`: full panel scaffold with distribution, WTP, objections, decision, next validation
- `setup`: install optional dependencies, cache data, verify CLI

## Architecture

Recommended pattern:

```text
Claude/OpenClaw skill
  ├─ reads SKILL.md workflow and templates
  ├─ calls scripts/sample_personas.py for a small panel
  ├─ calls scripts/build_panel_report.py to create a scaffold
  └─ runs synthesis/interview prompts in the assistant environment

Hugging Face / DuckDB sampler
  ├─ default dataset: nvidia/Nemotron-Personas-Korea
  ├─ optional local cache for team/shared machine
  └─ no need for every individual teammate to manually download the full dataset
```

For a team, one operator can maintain a shared cache or sampled persona packs. Everyone else can use small JSON panels committed to projects or generated on demand.

## Dataset and license notes

- Code in this repository is MIT licensed.
- The upstream dataset has its own license. The Hugging Face page was checked on 2026-04-30 and displayed `cc-by-4.0`; always verify the current dataset card before redistribution or commercial use.
- Do not commit large dataset files or private customer/persona data.

## Limitations

- Dataset schemas may change; the sampler uses best-effort field discovery and may return `source_excerpt` when exact fields are unknown.
- Hugging Face access requires optional Python packages and network availability.
- Synthetic persona reactions can amplify dataset/model bias and should be paired with real interviews, sales calls, surveys, or prototype tests.
