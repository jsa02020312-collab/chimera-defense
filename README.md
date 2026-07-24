# chimera-defenses

Defense suite for the **CHIMERA** project — memory-poisoning of LLM agents.
Prompt-level (KAD, Spotlighting, Instruction Hierarchy) and sub-agent memory
governance (A-MemGuard) defenses, benchmarked against **MINJA** and **CHIMERA**.

핵심 가설: 각 방어는 **MINJA는 붕괴시키고 CHIMERA는 통과**시킨다 (비대칭).
CHIMERA가 생존하는 이유는 방어가 약해서가 아니라, 조각이 개별 무해·참이고 악성이
**결합에서 창발**하기 때문 — 즉 기존 방어 지형(프롬프트단·구조적) 밖의 위협.

## 파일

| 파일 | 방어 | 근거(권위) |
|---|---|---|
| `prompt_level_defenses.py` | **a안**(KAD 탐지) + **a′안**(Instruction Hierarchy + Spotlighting 예방) | Liu et al. USENIX Sec'24 / OpenAI / Microsoft |
| `subagent_memory_governance.py` | **b안**(sub-agent R/W 검열 + A-MemGuard consensus + lesson) | A-MemGuard (arXiv:2510.02373) |

## 방어 사다리

무방어(MINJA) → **a안**(per-item 탐지) → **a′안**(per-item 예방) → **b안**(cross-item 합의) → 상용.
baseline(OEP식 naive auditor)은 비교축.

## 실행

**mock (키 불필요, 메커니즘 시연)**
```bash
python prompt_level_defenses.py
python subagent_memory_governance.py
```
→ MINJA 기록은 차단(FLAG/BLK), CHIMERA·정상 기록은 통과(pass/OK).

**실전 (Gemini, CHIMERA 기반)**
LLM 백엔드가 CHIMERA의 `chimera_core`(Gemini 헬퍼 `C.gj`/`C.pj`)를 재사용한다.
```bash
export GOOGLE_API_KEY=...            # chimera_core가 읽음
export PYTHONPATH=/path/to/CHIMERA   # chimera_core.py 위치
USE_GEMINI=1 python prompt_level_defenses.py
USE_GEMINI=1 python subagent_memory_governance.py
```
> 참고: 실전 실행은 `chimera_core.py`에 의존. 이 레포에 CHIMERA를 서브모듈로 두거나
> `chimera_core.py`를 함께 배치해야 한다. judge 모델은 `chimera_core`의 `gemini-2.5-flash`.
> 논문 비교 시 judge를 GPT-4o로 바꾸려면 `gemini_text`/`gemini_json`만 교체.

## 정직한 한계 (논문에 명시)

- **비대칭은 가설** → ISR/ASR/false-positive 실측 필요.
- **각색**: KAD·Instruction Hierarchy·Spotlighting은 원래 *프롬프트 인젝션* 방어 →
  *메모리 포이즈닝* 맥락으로 각색(검색 메모리 = in-context 비신뢰 콘텐츠). Instruction
  Hierarchy는 훈련 기법 → 프롬프트 정책으로 각색.
- **우리 add-on(논문 아님)**: `prompt_level_defenses.py`의 엔티티 정합성 보조검사,
  `subagent_memory_governance.py`의 write-time 게이트.
- **b안**: 실전은 저자 코드(https://github.com/TangciuYueng/AMemGuard) 사용 권장;
  CHIMERA 생존은 A-MemGuard의 "악성=소수 divergent" 가정 위반이라는 가설 → ablation 필요.

## 참고문헌

- KAD: Liu et al., *Formalizing and Benchmarking Prompt Injection Attacks and Defenses*, USENIX Security 2024. arXiv:2310.12815
- DataSentinel (KAD 발전형): IEEE S&P 2025. arXiv:2504.11358
- Spotlighting: Hines et al. (Microsoft). arXiv:2403.14720
- Instruction Hierarchy: Wallace et al. (OpenAI). arXiv:2404.13208
- A-MemGuard: arXiv:2510.02373
- 비교: MINJA arXiv:2503.03704 · OEP arXiv:2605.18930
