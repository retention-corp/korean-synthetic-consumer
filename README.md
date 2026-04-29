# korean-synthetic-consumer

**EN:** Portable Claude/OpenClaw skill package for building **Korean synthetic consumer/persona panels** grounded in the Hugging Face dataset [`nvidia/Nemotron-Personas-Korea`](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea).

**KR:** 한국 소비자/페르소나 패널을 빠르게 구성해 메시지 테스트, 제품 적합성 점검, 반대 논리 맵핑, 인터뷰 설계에 활용하는 Claude/OpenClaw용 스킬 패키지입니다. 기본 예제는 오프라인으로 동작하고, 선택적으로 Hugging Face 데이터셋을 샘플링할 수 있습니다.

---

## Overview / 개요

**EN:** This package combines:

- a Claude/OpenClaw skill workflow,
- a lightweight Python persona sampler,
- optional Hugging Face/DuckDB/parquet tooling,
- report/prompt templates for message testing, product-fit checks, objection mapping, interview design, and full reports.

**KR:** 이 패키지는 다음을 포함합니다.

- Claude/OpenClaw 스킬 워크플로,
- 가벼운 Python 페르소나 샘플러,
- 선택형 Hugging Face/DuckDB/parquet 도구,
- 메시지 테스트, 제품 적합성, 반대 논리, 인터뷰 설계, 전체 리포트용 템플릿.

## Why / 왜 쓰는가

**EN:** Paul's team often needs fast directional feedback for Phai, WAINBOX, ARMY, proposal-review, AX consulting, and sales/message testing. Real interviews still matter, but synthetic panels are useful for finding blind spots before spending recruiting time and budget.

**KR:** Phai, WAINBOX, ARMY, 제안서 리뷰, AX 컨설팅, 세일즈/메시지 테스트처럼 빠른 방향성 피드백이 필요한 작업에서 쓸 수 있습니다. 실제 인터뷰를 대체하지는 않지만, 리크루팅 시간과 비용을 쓰기 전에 약한 주장·오해·반대 포인트를 찾는 데 유용합니다.

## What this is not / 한계

**EN:** Synthetic personas are **hypothesis generation**, not statistically valid market research proof. Do not use outputs as the sole basis for investment, hiring, legal, medical, financial, or major go/no-go decisions.

**KR:** 합성 페르소나는 **가설 생성 도구**이지 통계적으로 검증된 시장조사 증거가 아닙니다. 투자, 채용, 법률, 의료, 금융, 중대한 go/no-go 결정의 유일한 근거로 쓰면 안 됩니다.

---

## Install / 설치

**EN:** Clone and install optional dependencies:

```bash
git clone https://github.com/hackinggrowth/korean-synthetic-consumer.git korean-synthetic-consumer
cd korean-synthetic-consumer
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

**KR:** 저장소를 받은 뒤 선택 의존성을 설치합니다.

```bash
git clone https://github.com/hackinggrowth/korean-synthetic-consumer.git korean-synthetic-consumer
cd korean-synthetic-consumer
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

**EN:** For offline-only usage with `examples/example-personas.json`, you can skip `requirements.txt` and use Python 3 standard library only. The package does **not** download the full dataset during install or build.

**KR:** `examples/example-personas.json`만 쓰는 오프라인 테스트는 `requirements.txt` 설치 없이 Python 3 표준 라이브러리만으로 가능합니다. 설치/빌드 중 전체 데이터셋을 다운로드하지 않습니다.

---

## Quickstart / 빠른 시작

### 1) Offline persona sample / 오프라인 페르소나 샘플링

```bash
python3 scripts/sample_personas.py \
  --dataset examples/example-personas.json \
  --n 2 \
  --output markdown
```

### 2) Build a panel scaffold / 패널 리포트 스캐폴드 생성

**EN:** This does not call any paid LLM API.

**KR:** 아래 명령은 유료 LLM API를 호출하지 않습니다.

```bash
python3 scripts/build_panel_report.py \
  --personas examples/example-personas.json \
  --product "WAINBOX: 제안서 초안을 고객사 맥락에 맞게 자동 리뷰하는 AI 워크플로" \
  --mode full-report \
  --title "WAINBOX Proposal Review" \
  --output examples/example-report.md
```

### 3) Run the offline self-check / 오프라인 자체 점검

```bash
scripts/self_check.sh
python3 -m py_compile scripts/sample_personas.py scripts/build_panel_report.py
```

---

## Use as an OpenClaw / Claude skill / OpenClaw·Claude 스킬로 사용

### Option A — Use directly from this repository / 옵션 A — 저장소에서 직접 사용

```bash
git clone https://github.com/hackinggrowth/korean-synthetic-consumer.git
cd korean-synthetic-consumer
python3 scripts/self_check.sh
```

### Option B — Install as a local OpenClaw skill / 옵션 B — 로컬 OpenClaw 스킬로 설치

```bash
mkdir -p ~/.openclaw/skills/korean-synthetic-consumer
cp -R SKILL.md README.md scripts templates examples requirements.txt LICENSE docs ~/.openclaw/skills/korean-synthetic-consumer/
```

**EN prompt example:**

```text
Use korean-synthetic-consumer in message-test mode.
Product/message: <paste copy or concept>
Target segment: Korean SMB owners / B2B SaaS marketers / etc.
Panel size: 5 personas.
Output: skeptical reactions, objection map, revised message, next real-world validation.
```

**KR 프롬프트 예시:**

```text
korean-synthetic-consumer를 message-test 모드로 사용해줘.
제품/메시지: <검증할 문구 또는 콘셉트>
대상 세그먼트: 한국 SMB 대표 / B2B SaaS 마케터 / 기타
패널 수: 5명
출력: 회의적인 첫 반응, 반대 논리 맵, 수정 메시지, 다음 실제 검증 단계.
```

---

## ARMY message-test example / ARMY 메시지 테스트 예시

```bash
python3 scripts/sample_personas.py \
  --dataset examples/example-personas.json \
  --n 3 \
  --seed 42 \
  --output json > /tmp/army-personas.json

python3 scripts/build_panel_report.py \
  --personas /tmp/army-personas.json \
  --product "ARMY는 마케팅팀이 매주 반복하는 리서치, 메시지 테스트, 실험 설계, 리포팅을 AI 에이전트 분대가 대신 실행해주는 성장 운영 시스템입니다. 대시보드 하나에서 고객 반응을 모으고, 다음 실험을 제안하고, 실행 결과를 누적해 팀의 마케팅 속도를 높입니다." \
  --mode message-test \
  --title "ARMY Message Test" \
  --output _workspace/army-message-test.md
```

**EN:** The generated markdown is a scaffold for human/LLM synthesis, not a completed market verdict.

**KR:** 생성된 Markdown은 사람 또는 LLM이 이어서 종합하기 위한 스캐폴드이며, 완성된 시장 판단이 아닙니다.

---

## Real-data smoke test / 실제 데이터 스모크 테스트

**EN:** After installing optional dependencies, run a tiny Hugging Face smoke test:

**KR:** 선택 의존성을 설치한 뒤 Hugging Face 데이터셋으로 작은 스모크 테스트를 실행할 수 있습니다.

```bash
python3 scripts/sample_personas.py \
  --dataset nvidia/Nemotron-Personas-Korea \
  --n 2 \
  --seed 7 \
  --region 서울 \
  --output markdown \
  --cache-dir .cache/huggingface
```

**EN:** If this fails because of network, Hugging Face auth, or schema changes, continue with local JSON examples and re-check the dataset card before production use.

**KR:** 네트워크, Hugging Face 인증, 스키마 변경으로 실패하면 로컬 JSON 예제로 계속 진행하고, 운영 사용 전 데이터셋 카드를 다시 확인하세요.

---

## Recommended validation ladder / 권장 검증 단계

1. **Synthetic panel / 합성 패널:** likely objections and weak claims / 예상 반대와 약한 주장 찾기.
2. **Real customer interviews / 실제 고객 인터뷰:** validate whether objections actually appear / 실제로 같은 반응이 나오는지 확인.
3. **Small message/prototype test / 소규모 메시지·프로토타입 테스트:** measure behavior, not just stated preference / 말보다 행동 측정.
4. **Decision memo / 의사결정 메모:** mark findings as `[hypothesis]`, `[verified]`, or `[experimental]` / 발견사항을 신뢰도 태그로 구분.

## Use modes / 사용 모드

- `message-test`: copy, outreach, landing page, proposal message testing / 카피·아웃리치·랜딩·제안서 메시지 테스트
- `product-fit`: concept fit, adoption trigger, WTP, workflow integration / 콘셉트 적합성·도입 트리거·지불의사·업무흐름 통합
- `objection-map`: sales/proposal objections and proof requirements / 세일즈·제안 반대 논리와 필요한 증거
- `persona-panel`: quick multi-persona first read / 빠른 다중 페르소나 1차 반응
- `interview-script`: convert synthetic findings into real interview questions / 합성 패널 결과를 실제 인터뷰 질문으로 전환
- `full-report`: full panel scaffold with distribution, WTP, objections, decision, next validation / 전체 리포트 스캐폴드
- `setup`: install optional dependencies, cache data, verify CLI / 선택 의존성 설치·캐시·CLI 검증

## Architecture / 구조

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

**EN:** For a team, one operator can maintain a shared cache or sampled persona packs. Everyone else can use small JSON panels committed to projects or generated on demand.

**KR:** 팀에서는 한 명이 공유 캐시나 샘플 페르소나 팩을 관리하고, 나머지는 프로젝트에 포함된 작은 JSON 패널이나 필요할 때 생성한 패널을 쓰는 방식이 안전합니다.

## Dataset and license notes / 데이터셋·라이선스 메모

- **EN:** Code in this repository is MIT licensed.  
  **KR:** 이 저장소의 코드는 MIT 라이선스입니다.
- **EN:** The upstream dataset has its own license. The Hugging Face page was checked on 2026-04-30 and displayed `cc-by-4.0`; always verify the current dataset card before redistribution or commercial use.  
  **KR:** 업스트림 데이터셋은 별도 라이선스를 가집니다. Hugging Face 페이지는 2026-04-30 기준 `cc-by-4.0`으로 표시되었지만, 재배포·상업적 사용 전 최신 데이터셋 카드를 확인하세요.
- **EN:** Do not commit large dataset files or private customer/persona data.  
  **KR:** 대용량 데이터셋 파일이나 비공개 고객/페르소나 데이터는 커밋하지 마세요.

## Limitations / 제한사항

- **EN:** Dataset schemas may change; the sampler uses best-effort field discovery and may return `source_excerpt` when exact fields are unknown.  
  **KR:** 데이터셋 스키마는 바뀔 수 있으며, 샘플러는 best-effort로 필드를 찾고 정확한 필드를 모르면 `source_excerpt`를 반환할 수 있습니다.
- **EN:** Hugging Face access requires optional Python packages and network availability.  
  **KR:** Hugging Face 접근에는 선택 Python 패키지와 네트워크가 필요합니다.
- **EN:** Synthetic persona reactions can amplify dataset/model bias and should be paired with real interviews, sales calls, surveys, or prototype tests.  
  **KR:** 합성 페르소나 반응은 데이터셋/모델 편향을 증폭할 수 있으므로 실제 인터뷰, 세일즈 콜, 설문, 프로토타입 테스트와 함께 사용해야 합니다.
