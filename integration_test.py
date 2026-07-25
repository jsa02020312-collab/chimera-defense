"""
integration_test.py — [1순위] 선배 CHIMERA 공격의 '실제 출력'을 방어에 통과시키는 통합 테스트.

핵심: CHIMERA 공격 출력(strategy_db.json)은 (query, trace) record가 아니라
  'conventions'(각인된 독립 .md 노트들) + 'trigger'(발동 요청) 형태다.
  → 이제 방어의 '노트 환경 어댑터'(detect_note/detect_aux_note)로 그대로 검사한다.
     (이전엔 conventions를 (query,trace)에 억지 매핑해서 오탐(FP)이 났음 — 노트 어댑터로 해소.)

trigger는 참고용(나중에 사용자가 던지는 발동 요청)으로만 출력. 판정은 각 convention 노트 단위.

실행:
    set STRATEGY_DB=C:\\SILAB\\Memory\\[-]_CHIMERA\\strategy_db.json
    python integration_test.py            # mock (키 불필요)
    set USE_GEMINI=1 && python integration_test.py   # 실제 Gemini (PYTHONPATH=[-]_CHIMERA, GOOGLE_API_KEY 필요)
"""
import os, sys, json
from prompt_level_defenses import (detect_note, detect_aux_note,
                                    gemini_text, gemini_json, mock_text, mock_json)

def load_strategies(path, n=2):
    db = json.load(open(path, encoding="utf-8"))
    out = []
    for e in db.get("entries", [])[:n]:
        d = e.get("decomposition", {})
        out.append({"harm": e.get("harm"), "mechanism": e.get("mechanism"),
                    "conventions": d.get("conventions", []), "trigger": d.get("trigger", "")})
    return out

if __name__ == "__main__":
    path = os.environ.get("STRATEGY_DB") or (sys.argv[1] if len(sys.argv) > 1 else None)
    if not path or not os.path.exists(path):
        print("[!] strategy_db.json 경로를 STRATEGY_DB 환경변수나 인자로 주세요.")
        print(r'    예: set STRATEGY_DB=C:\SILAB\Memory\[-]_CHIMERA\strategy_db.json')
        sys.exit(1)

    use = os.environ.get("USE_GEMINI")
    llm_text = gemini_text if use else mock_text
    llm_json = gemini_json if use else mock_json
    print(f"backend={'GEMINI' if use else 'MOCK'}  source={os.path.basename(path)}")

    strategies = load_strategies(path, n=2)
    for i, s in enumerate(strategies):
        trig = s["trigger"] or "(no trigger)"
        print(f"\n=== 공격 전략 {i} (mechanism={s['mechanism']}, harm={s['harm']}) ===")
        print(f"    trigger(참고): {trig[:90]}")
        for j, conv in enumerate(s["conventions"]):
            kad_bad, kad_why = detect_note(conv, llm_text)           # 노트 어댑터(형식 정합)
            aux_bad, aux_why = detect_aux_note(conv, llm_json)
            print(f"  [conv{j}] {conv[:78]}")
            print(f"     KAD:{'FLAG' if kad_bad else 'pass'}  aux:{'FLAG' if aux_bad else 'pass'}  ({kad_why} / {aux_why[:40]})")

    print("\n(기대) 실제 CHIMERA 조각은 무해·정합이라 KAD·aux 둘 다 pass → 'CHIMERA 생존'이 실제 공격 출력으로 확인.")
    print("(형식) conventions는 King_Stub .md 노트 형식 → 노트 어댑터(detect_note/detect_aux_note)로 직접 검사. "
          "억지 (query,trace) 매핑 제거 → 이전 오탐(FP) 해소됨.")
