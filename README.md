# chimera-defenses

Defense suite for the **CHIMERA** project — memory-poisoning of LLM agents.
Prompt-level (KAD, Spotlighting, Instruction Hierarchy) and sub-agent memory
governance (A-MemGuard) defenses, benchmarked against **MINJA** and **CHIMERA**.

핵심 가설:
기존 방어(KAD, Instruction Hierarchy, Spotlighting, A-MemGuard)는
MINJA(단일 divergent 기록)에는 효과적이지만, CHIMERA(개별 무해·상호 정합적인 조각들의
결합 창발)에는 상대적으로 취약할 것으로 예상한다.

## 구조 — 각 층 = [엔진 + 실행기]

| 파일 | 역할 | 근거(권위) |
|---|---|---|
| `prompt_level_defenses.py` | **2차a 엔진** — KAD 탐지 + aux(엔티티 정합성) + 예방(Instruction Hierarchy + Spotlighting) | Liu et al. USENIX Sec'24 / OpenAI / Microsoft |
| `integration_test.py` | **2차a 실행기** — 실제 `.md` 노트(exp2 poison / exp1 benign)에 통과 | — |
| `subagent_memory_governance.py` | **2차b 엔진** — sub-agent R/W 검열 + A-MemGuard consensus + lesson | A-MemGuard (arXiv:2510.02373) |
| `governance_integration.py` | **2차b 실행기(King_Stub 실배선)** — 실제 `.md` 노트에 통과 | — |
| `list_gemini_models.py` | (유틸) 현재 키로 사용 가능한 Gemini 모델 목록 출력 | — |

- **엔진**은 판정 로직을 정의(단독 실행 시 손으로 쓴 예시로 데모).
- **실행기**가 엔진을 import 해서 **진짜 공격 산출물**에 돌린다 → 실제 평가는 실행기 2개로.
- 엔진은 같은 폴더에 있기만 하면 됨.

## 방어 사다리 (Defense ladder)

No defense
→ Prompt detection (KAD)
→ Prompt prevention (Instruction Hierarchy + Spotlighting)
→ Sub-agent memory governance (A-MemGuard: consensus + lesson)
→ Commercial agents

## 실행

직접 실행하는 파일은 **실행기 2개**: `integration_test.py`(2차a), `governance_integration.py`(2차b).
백엔드는 주입식 — **mock / gemini / gpt** 중 환경변수로 선택.
자세한 실행 조건·주의사항은 [`README_실행조건.md`](README_실행조건.md) 참고.

**mock (키 불필요, 동작 확인)**
```bash
python integration_test.py
python governance_integration.py
```

**GPT**
```bash
export USE_GPT=1
export OPENAI_API_KEY=sk-...          # openai 패키지 필요: pip install openai
python integration_test.py
python governance_integration.py
```

**Gemini** (`chimera_core` 재사용)
```bash
export USE_GEMINI=1
export GOOGLE_API_KEY=AIza...         # chimera_core가 읽음 (google-genai 필요)
export PYTHONPATH=/path/to/CHIMERA    # chimera_core.py 위치
export GEMINI_MODEL=<사용 가능한 모델> # gemini-2.5-flash 는 신규 키에서 단종(404) → list_gemini_models.py 로 확인
python integration_test.py
python governance_integration.py
```

옵션 환경변수: `DIVERSE=1`(harm 유형당 1개), `MAX=N`(그룹당 트라이얼 제한),
`SOURCE=db`+`STRATEGY_DB=...`(2차a 옛 방식: strategy_db 조각으로 검사).

백엔드 선택 우선순위: `LLM_BACKEND > USE_GPT > USE_GEMINI > mock`.
> 판정(judge) 모델은 백엔드로 결정 — GPT는 `OPENAI_MODEL`(기본 gpt-4o), Gemini는 `GEMINI_MODEL`.
> 코드 교체 없이 환경변수만으로 모델 전환 가능.

## 관찰 (예비 — mock/GPT 소규모)

- **대조군으로 검사기 생존 확인**: 명령형 주입·엔티티 치환은 잡히고(aux FLAG 등), 정상 노트는 통과.
- **프롬프트단(2차a)은 실제 CHIMERA 노트를 사실상 못 잡음** (survived ≈ 전부), benign 오탐 0.
- **거버넌스(2차b)는 '파괴 규칙 단일 노트'형만 write-gate가 부분 차단**, 조합·탈취형은 생존.
- **KAD는 강한 모델(GPT-4o)에서 명령형 주입도 잘 못 잡음(높은 FNR)** → 실질 탐지는 aux가 담당.
- 정량 수치(ISR/ASR/FPR)와 공격 루프 내 방어(ASR) 검증은 랩 서버(King_Stub 라이브) 몫.

## 한계

- The asymmetric defense profile remains a hypothesis and should be validated using ISR, ASR, and false-positive measurements.
- **각색**: KAD·Instruction Hierarchy·Spotlighting은 원래 *프롬프트 인젝션* 방어 →
  *메모리 포이즈닝* 맥락으로 각색(검색 메모리 = in-context 비신뢰 콘텐츠). Instruction
  Hierarchy는 훈련 기법 → 프롬프트 정책으로 각색.
- **우리 add-on(논문 아님)**: `prompt_level_defenses.py`의 엔티티 정합성 보조검사,
  `subagent_memory_governance.py`의 write-time 게이트.
- **b안**: 실전은 저자 코드(https://github.com/TangciuYueng/AMemGuard) 사용 권장;
  CHIMERA 생존은 A-MemGuard의 "악성=소수 divergent" 가정 위반이라는 가설 → ablation 필요.
- **실배선 범위**: 정적 산출물(strategy_db, 저장된 `.md` 노트)에 대한 탐지/오탐 평가까지가 이 레포.
  방어를 공격 루프에 끼워 창발(ASR)을 막는지는 King_Stub 라이브 환경(랩 서버) 필요.

## 참고문헌

- KAD: Liu et al., *Formalizing and Benchmarking Prompt Injection Attacks and Defenses*, USENIX Security 2024. arXiv:2310.12815
- Spotlighting: Hines et al. (Microsoft). arXiv:2403.14720
- Instruction Hierarchy: Wallace et al. (OpenAI). arXiv:2404.13208
- A-MemGuard: arXiv:2510.02373
- 비교: MINJA arXiv:2503.03704 · OEP arXiv:2605.18930
