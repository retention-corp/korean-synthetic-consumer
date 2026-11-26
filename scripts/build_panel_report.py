#!/usr/bin/env python3
"""Build a markdown scaffold/prompt for a Korean synthetic consumer panel."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

MODES = ["message-test", "product-fit", "objection-map", "persona-panel", "interview-script", "full-report"]


def load_personas(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        for key in ("personas", "items", "rows", "data"):
            if isinstance(data.get(key), list):
                data = data[key]
                break
    if not isinstance(data, list):
        raise ValueError("persona JSON must be a list or an object with personas/items/rows/data list")
    return [item for item in data if isinstance(item, dict)]


def val(persona: Dict[str, Any], *keys: str, default: str = "-") -> str:
    lowered = {str(k).lower(): v for k, v in persona.items()}
    for key in keys:
        if key in persona and persona[key] not in (None, ""):
            return str(persona[key])
        lk = key.lower()
        if lk in lowered and lowered[lk] not in (None, ""):
            return str(lowered[lk])
    return default


def persona_card(persona: Dict[str, Any], idx: int) -> str:
    name = val(persona, "name", "이름", "persona", default=f"Persona {idx}")
    basics = ", ".join(
        part for part in [
            val(persona, "age", "나이", default=""),
            val(persona, "gender", "성별", default=""),
            val(persona, "region", "location", "거주", "지역", default=""),
            val(persona, "occupation", "job", "직업", default=""),
        ] if part
    )
    summary = val(persona, "summary", "description", "persona", "source_excerpt", default="")
    source_id = f"- 원본 UUID: {persona['uuid']}\n" if persona.get("uuid") else ""
    return f"### P{idx}. {name}\n{source_id}- 기본: {basics or '-'}\n- 세그먼트: {val(persona, 'persona_type', 'type', 'segment', default='-')}\n- 라이프스테이지: {val(persona, 'life_stage', 'lifeStage', 'age_group', default='-')}\n- 배경/단서: {summary[:700] or '-'}\n"


def mode_questions(mode: str) -> str:
    blocks = {
        "message-test": [
            "첫 문장을 보고 드는 즉각적 감정/오해는?",
            "무엇이 설득되고 무엇이 과장처럼 들리는가?",
            "더 믿기 위해 필요한 증거/표현은?",
            "카카오톡/랜딩페이지/제안서 문구라면 어디에서 이탈할까?",
        ],
        "product-fit": [
            "현재 생활/업무에서 이 제품이 들어갈 실제 순간은?",
            "기존 대안 대비 바꿀 만큼 강한 이유가 있는가?",
            "초기 사용 장벽과 반복 사용 조건은?",
            "WTP 또는 도입 승인 조건은?",
        ],
        "objection-map": [
            "가장 먼저 반대할 이유 3가지는?",
            "돈/시간/신뢰/조직정치/학습비용 중 무엇이 병목인가?",
            "반박 메시지 중 무엇이 먹히고 무엇은 역효과인가?",
            "세일즈/제안서에서 먼저 제거해야 할 표현은?",
        ],
        "persona-panel": [
            "각 페르소나의 첫 반응을 한 문장으로 말하라.",
            "서로 다른 찬반 이유를 비교하라.",
            "강한 지지자/조건부 지지자/회의론자를 분류하라.",
            "다음 검증 질문 5개를 제안하라.",
        ],
        "interview-script": [
            "문제 경험을 확인하는 비유도 질문은?",
            "현재 대안과 지출을 캐는 질문은?",
            "컨셉 반응을 확인하되 긍정 편향을 줄이는 질문은?",
            "구매/도입 조건을 구체화하는 후속 질문은?",
        ],
        "full-report": [
            "반응 분포(긍정/조건부/부정)와 이유는?",
            "핵심 인사이트와 blind spot은?",
            "WTP/도입 조건/거부 조건은?",
            "GO/PIVOT/KILL 판정과 다음 실제 검증은?",
        ],
    }
    return "\n".join(f"{i}. {q}" for i, q in enumerate(blocks[mode], 1))


def build_report(personas: Sequence[Dict[str, Any]], product: str, mode: str, title: str) -> str:
    cards = "\n".join(persona_card(p, i) for i, p in enumerate(personas, 1))
    return f"""# Korean Synthetic Consumer Panel — {title}

- Date: {date.today().isoformat()}
- Mode: `{mode}`
- Personas: {len(personas)}
- Safety: Synthetic personas generate hypotheses. They are not proof of real market demand.

## Product / Message Under Test

{product.strip()}

## Persona Panel

{cards if cards else '_No personas provided._'}

## Analyst Instructions

Use the personas as grounded role cards for a Korean consumer panel. Stay concrete and skeptical. Avoid polite default positivity. For each persona, answer from their lived constraints, not from the product team's hopes.

### Questions for `{mode}`

{mode_questions(mode)}

## Response Capture Template

| Persona | First reaction | Use intent | Payment/adoption condition | Main objection | Quote |
|---|---|---|---|---|---|
{''.join(f"| P{i} |  |  |  |  |  |\n" for i, _ in enumerate(personas, 1))}

## Synthesis Template

### Reaction Distribution
- Positive:
- Conditional:
- Negative:

### Strongest Signals
1.
2.
3.

### Objection Map
1.
2.
3.

### Message/Product Revisions
- Keep:
- Change:
- Remove:

### Decision
**GO / PIVOT / KILL:**

### Next Real-World Validation
- Interview/survey target:
- Prototype or message test:
- Evidence needed before decision:

---
Generated scaffold only. No paid LLM/API call was made by this script.
"""


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a markdown synthetic consumer panel report scaffold.")
    parser.add_argument("--personas", required=True, help="persona JSON file")
    parser.add_argument("--product", required=True, help="product/message description text or @path/to/file")
    parser.add_argument("--mode", choices=MODES, default="full-report")
    parser.add_argument("--title", default="Panel Report")
    parser.add_argument("--output", help="write markdown to file instead of stdout")
    return parser.parse_args(argv)


def read_product(value: str) -> str:
    if value.startswith("@"):
        return Path(value[1:]).read_text(encoding="utf-8")
    return value


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        personas = load_personas(Path(args.personas))
        report = build_report(personas, read_product(args.product), args.mode, args.title)
        if args.output:
            Path(args.output).write_text(report, encoding="utf-8")
        else:
            print(report)
    except Exception as exc:  # noqa: BLE001
        print(f"build_panel_report.py: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
