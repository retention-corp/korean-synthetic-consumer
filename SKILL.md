---
name: korean-synthetic-consumer
description: Korean synthetic consumer/persona panel skill using Hugging Face nvidia/Nemotron-Personas-Korea plus lightweight report templates. Use for message-test, product-fit, objection-map, persona-panel, interview-script, full-report, setup.
---

# Korean Synthetic Consumer / 한국형 가상 소비자 패널

Purpose: create a Korean synthetic consumer/persona panel grounded in Korean demographic synthetic data, then use the panel to pressure-test products, sales messages, proposals, and interview plans.

This skill is a portable version of Paul's synthetic-consumer workflow with dataset access added. It is especially useful for Phai/WAINBOX/ARMY ideas, proposal review, AX consulting, and Korean market message testing.

## Safety caveat

Synthetic personas are for **hypothesis generation**. They are not proof of market demand and do not replace real customer interviews, surveys, sales calls, or behavioral data.

## Recommended architecture

```text
Claude/OpenClaw skill
  + Hugging Face/DuckDB sampler
  + markdown report templates
```

- The assistant uses this `SKILL.md` to choose the right mode and questions.
- `scripts/sample_personas.py` samples a small panel from `nvidia/Nemotron-Personas-Korea` or a local JSON file.
- `scripts/build_panel_report.py` prepares a structured prompt/report scaffold.
- DuckDB/parquet caching is optional. A shared team cache is preferred; every individual does **not** need to manually install or commit the full dataset.

## Modes

### `message-test`
Use for landing copy, KakaoTalk outreach, sales one-liners, proposal intro, Phai/WAINBOX/ARMY positioning.

### `product-fit`
Use for concept fit, actual usage moment, adoption trigger, workflow friction, WTP.

### `objection-map`
Use before sales/proposal review to map budget, trust, security, workflow, approval, and outcome objections.

### `persona-panel`
Use for quick first reactions from 3-7 diverse personas.

### `interview-script`
Turn synthetic signals into non-leading real customer interview questions.

### `full-report`
Produce a full report: persona table, reaction distribution, quotes, WTP/adoption conditions, objections, recommendation, next validation.

### `setup`
Install optional dependencies and verify scripts:

```bash
python -m pip install -r requirements.txt
python scripts/sample_personas.py --dataset examples/example-personas.json --n 2 --output markdown
```

## Workflow

1. Clarify target: product/message, audience, business context, decision needed.
2. Sample personas:
   ```bash
   python scripts/sample_personas.py --n 5 --region 서울 --output json > personas.json
   ```
   For downloaded NVIDIA shards use `--dataset /path/to/data` (PyArrow required).
   Keep each returned UUID alongside the synthetic answers in your report.
   If zero records match, report zero and describe the filter before changing it.

   Offline fallback:
   ```bash
   python scripts/sample_personas.py --dataset examples/example-personas.json --n 3 --output json
   ```
3. Build scaffold:
   ```bash
   python scripts/build_panel_report.py --personas personas.json --product "..." --mode full-report
   ```
4. Run the actual reasoning/interview synthesis in Claude/OpenClaw using the scaffold and relevant template.
5. End with: what to test with real customers next.

## Anti-bias rules

- Include at least one skeptical persona.
- Avoid polite positivity; ask what feels overclaimed, risky, or not worth changing behavior for.
- Separate `positive`, `conditional`, and `negative` reactions.
- Treat WTP as directional only.
- Always state the next real-world validation step.

## Validation ladder

Before treating outputs as business evidence, follow `docs/validation-ladder.md`: synthetic panel → real interview → behavioral test → decision memo.
