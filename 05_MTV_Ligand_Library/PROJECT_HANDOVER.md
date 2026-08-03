# MTV-ZIF CCUS 스크리닝 파이프라인 — 핸드오버 문서

Claude(대화형)와 진행한 논의를 Claude Code로 이어받기 위한 요약입니다. 이 문서 + 첨부된
3개 스크립트만으로 지금까지의 맥락을 파악할 수 있도록 작성했습니다.

## 1. 프로젝트 개요

- **목표**: CCUS(Flue gas, 분압 ~0.15 bar CO2)를 위한 MOF/ZIF 고속 스크리닝. 핵심 전략은
  ZIF-8(sod) 골격의 2-메틸이미다졸레이트(mIm)를 다른 리간드로 부분 치환하는 MTV(Multivariate)
  블렌딩.
- **핵심 가설**: EWG 계열 치환기가 국소 쌍극자를 만들어 CO2 사극자와 강하게 상호작용하고,
  나머지 소수성 리간드(mIm)가 수분 차단 역할을 하면서, 전체 Qst는 30~40 kJ/mol의
  "Goldilocks Zone"에 들어오도록 조성비를 튜닝한다.
- **팀 구성**: 팀장(사용자) + 코딩(사용자+Claude 대화형+Claude Code), 조원 3명은 리간드
  후보 문헌조사 담당 (ZIF-8 / ZIF-67 / ZIF-69 각 1명).

## 2. 파이프라인 현황

### 2.1 RASPA 버그 이력 (완료 상태 확인 필요)
- 증상: Widom insertion 결과 K_H가 항상 0.0000으로 나옴.
- 가장 유력했던 원인: (1) subprocess가 stderr를 캡처하지 않아 실제 크래시를 놓침,
  (2) 새 치환기(nIm 등)의 원자 타입이 forcefield의 `pseudo_atoms.def`에 미정의.
- 진단 스크립트: `raspa_diagnostic.py` (첨부) — 환경변수, forcefield 매칭, 실제 실행 로그를
  한번에 확인.
- **Claude Code가 지금 이 복구 작업을 수행 중이라고 들었음. 복구 완료 여부와 원인이
  무엇이었는지부터 확인할 것.**

### 2.2 완성된 코드 자산

**`tag_zif_linkers.py`** — 1회성 유틸리티. 기존 mIm 전용 ZIF-8 P1 CIF에서 각 링커의 고리
원자(C2,N3,C4,C5,N1)와 치환기 원자를 자동 인식해 `site_map.json`으로 저장.
- 핵심 설계: Zn(또는 Co)을 그래프에서 제외하고 C,N만으로 결합 그래프를 만들면 각 이미다졸
  고리가 독립된 5-사이클로 떨어짐 (금속 포함 시 N1-금속-...-금속-N3 같은 가짜 큰 고리로 오탐).
- **중요한 규약**: 고리 원자를 `[C2, N3, C4, C5, N1]` 순서로 정렬해서 저장함
  (N3=H 없는 질소, N1=H 있는 질소). 이 순서가 `mtv_cif_builder.py`의 RDKit SMARTS 매칭
  순서와 반드시 일치해야 Kabsch 정합이 올바르게 됨. 순서가 깨지면 조용히 틀린 회전을 냄 —
  검증 없이 넘어가지 말 것.
- 한계: 링커 고리가 단일 unit cell 안에 있다고 가정(일반적 ZIF-8 슈퍼셀에서는 성립). 명시적
  H 원자가 CIF에 있어야 함.

**`mtv_cif_builder.py`** — `site_map.json` + 목표 조성비(dict)를 받아 RDKit으로 리간드
프래그먼트를 생성하고 Kabsch 정합으로 결정구조에 치환, 최종 CIF를 출력.
- `LIGAND_LIBRARY`에 SMILES로 등록된 후보: mIm, nIm(기존), clIm, cnIm, tfIm, etIm, amIm
  (근거는 4절 참고).
- `composition` 인자는 `{"mIm": 0.5, "clIm": 0.5}` 처럼 2종 이상 임의 개수 지원 —
  3원 조성(예: mIm+nIm+amIm)도 코드 수정 없이 바로 실행 가능.
- **아직 안 된 것**: 부분전하 계산이 빠져 있음. `UseChargesFromCIFFile no`로 두면
  RASPA가 EWG 후보들 간 정전기적 차이를 전혀 못 보게 됨 — 이 프로젝트 가설 전체가
  정전기 메커니즘이므로 이건 치명적 결함. **CIF 생성 직후 EQeq(Wilmer et al.,
  Extended Charge Equilibration)로 부분전하를 계산해 반영하는 단계가 다음 최우선 과제.**

두 스크립트 모두 문법 검사(`py_compile`)는 통과했고, Kabsch 함수는 합성 좌표로 회전 복원
오차 ~1e-16 수준까지 검증함. rdkit/ase는 (검증 당시) 네트워크 제한으로 실제 설치 테스트는
못 했음 — Claude Code 환경에서 `pip install rdkit ase networkx --break-system-packages`
후 실제 ZIF-8 CIF로 end-to-end 검증 필요.

## 3. 다음 작업 우선순위

1. **[최우선] EQeq 부분전하 통합**: `mtv_cif_builder.py`의 `write(output_cif, atoms)` 직후에
   EQeq(또는 유사 도구)를 호출해 charge를 CIF에 기록하는 단계 추가. 이게 없으면 이후 모든
   스크리닝 결과가 무의미함.
2. **ZIF-67 어댑테이션**: Co(mIm)2, sod, ZIF-8과 등구조. `tag_zif_linkers.py`에서 그래프
   제외 대상 금속을 Co로 바꾸고, 실제 ZIF-67 CCDC 구조를 base_cif로 확보하면 나머지 로직은
   그대로 재사용 가능. 난이도 낮음, 가장 빠른 확장.
3. **ZIF-69 이환식 고리 인식 (설계 확정 후 착수)**: ZIF-69 = Zn(cbIm)(nIm) 1:1 고정, gme
   토폴로지. cbIm(5-클로로벤즈이미다졸레이트)은 벤젠고리가 융합된 이환식 구조라 지금의
   5원자 단일 고리 인식 로직(`find_imidazole_rings`)이 그대로 안 통함. 코딩 시작 전에
   "cbIm 자리의 치환기만 바꾸는 것"(문헌상 SALE로 5-CF3-벤즈이미다졸 95% 치환 사례 있음,
   권장 방향)인지 "cbIm:nIm 비율 자체를 바꾸는 것"(검증 안 됨, 비권장)인지 팀 내 확정 필요.
4. **Zeo++ PLD false-negative 처리**: 호흡효과/게이트오프닝으로 실제로는 열리는 구조가 정적
   스냅샷 하나로 PLD<3.4Å 판정돼 0으로 채워지는 문제. CCDC에 열린 상/닫힌 상이 둘 다
   등록된 구조는 열린 상으로 재확인, 없으면 0이 아니라 "결측/후속검증필요"로 Master CSV에
   구분 표시.
5. **위상 드리프트 위험 플래그**: nIm 비율이 높아질수록 문헌상 sod가 아닌 gme로 결정화
   편향되는 경향이 보고돼 있음. 완전한 예측(CSP)은 하지 말고, 아래처럼 알려진 경향만
   태그로 남기는 수준으로 구현:

```python
TOPOLOGY_BIAS_NOTES = {
    "nIm": {"note": "혼합 리간드 반응에서 GME 쪽으로 편향된다는 문헌 보고 있음", "risk_above": 0.5},
}
```

## 4. 리간드 후보 라이브러리 (SMILES 및 근거 요약)

| 약어 | SMILES | 설계 근거 |
|---|---|---|
| clIm | `Clc1ncc[nH]1` | 중간 EWG, 메틸보다 입체 부피 작음 (PV 손실 대비 EWG 효율 최고) |
| cnIm | `N#Cc1ncc[nH]1` | 선형이라 입체 페널티 최소, EWG는 NO2에 근접 |
| tfIm | `FC(F)(F)c1ncc[nH]1` | 순수 유도효과 EWG + 소수성 동시 확보 |
| etIm | `CCc1ncc[nH]1` | 순수 입체 스페이서(3원 MTV 확장용), 문헌상 ZIF-8 SALE 사례 있음 |
| amIm | `Nc1ncc[nH]1` | EDG 음성 대조군 — 단, 최근 문헌(EWG-EDG 교대 배치 시너지)에
  따르면 nIm과 함께 넣었을 때 대조군이 아니라 시너지 파트너일 가능성도 있음. 3원 조성
  {mIm, nIm, amIm}으로 반드시 별도 테스트할 것. |

스크리닝은 전수 정밀계산 대신 깔때기 전략 권장: Widom insertion(빠름)으로 1차 스크리닝 →
상위 1~2종만 GCMC/IAST 정밀 계산.

## 5. 검증된 배경 사실 (문헌 확인 완료)

- ZIF-8: Zn(mIm)2, sod. ZIF-67: Co(mIm)2, sod, ZIF-8과 등구조.
- ZIF-69: Zn(cbIm)(nIm) 1:1 고정, gme 토폴로지.
- 순수 100% Zn(nIm)2도 실제로 존재함(ZIF-108, sod 토폴로지) — 100% 조성 자체가 불가능한
  건 아님. 다만 같은 조성이 완전히 다른 토폴로지(ZIF-65, tridymite 계열)로도 다형체를
  이루는 사례가 있고, 2-니트로이미다졸이 혼합 리간드 반응을 gme 쪽으로 편향시킨다는
  경향이 문헌에 보고돼 있음 (3-5절 참고).
- Qst 등 목표 수치의 실제 벤치마크: TAEA@MIL-101 -120 kJ/mol (화학흡착형 상한 참고치),
  이미다졸+메틸 혼합 채널 MOF 사례에서 CO2 Qst 43.7 vs CH4 16.4 kJ/mol (물리흡착
  기반 목표치와 근접, 좋은 참고 사례).

## 6. 팀 커뮤니케이션 관련 메모

- 조원들의 문헌조사 결과(공통과제)에서 "금속:리간드 비율", "용매 조건" 같은 언급이
  나오는데, 이건 계산 파이프라인이 다룰 변수가 아니라 별도의 합성조건 문헌조사
  트랙임. 계산에 넣으려 하지 말 것.
- 보고서/발표 전략: 한계점(수분-가수분해, 위상 드리프트, PLD false-negative 등)은
  삭제하지 말고 "future work"로 명시. 장점 데이터(IAST 등)를 먼저 확보하되 한계 언급
  자체를 피하지는 말 것 — 심사 대응상 유리함.
