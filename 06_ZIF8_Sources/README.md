# ZIF-8 원본 구조 수집 폴더

MTV 작업의 모체인 ZIF-8을 **출처가 명확한 구조**로 교체하고, 게이트-오프닝(gate-opening)
열린 상을 확보하기 위한 폴더.

## 배경: 왜 필요한가

현재 파이프라인이 쓰는 `01_CIF_Cleaned/ZIF-8.cif`는 CCDC 다운로드본이 아니라
**RASPA 배포판에 딸려오는 예제 파일**(`_audit_author_name 'David Dubbeldam'`, 2011).
구조 자체는 건전하지만(원자 겹침 0개) 출처를 논문에 인용하기 어렵다.

또한 정적 구조 기준 PLD가 3.409 Å로 N2 프로브 지름(1.82×2 = 3.64 Å)보다 작아
Zeo++가 접근가능부피를 0으로 보고한다. 실제 ZIF-8은 이미다졸레이트 리간드가 회전하는
**게이트-오프닝**으로 N2/CO2를 흡착하므로, 이 0은 물리적 사실이 아니라 정적 스냅샷의 한계다
(`run_master_pipeline.py`의 `Porosity_Flag`가 이 경우를 "결측_재검증필요"로 표시함).

## 현재까지 측정 결과

| 구조 | 출처 | a (Å) | PLD (Å) | PLD/a | AV (Å³) | 판정 |
|---|---|---|---|---|---|---|
| `01_CIF_Cleaned/ZIF-8.cif` | RASPA 예제 | 16.991 | 3.409 | 0.2006 | 0 | 닫힘 |
| `COD_7111973.cif` | ChemComm 2014 (X선) | 17.033 | 3.435 | 0.2017 | 0 | 닫힘 |
| `COD_7249359.cif` | CrystEngComm 2024 (싱크로트론) | 16.902 | 3.260 | 0.1929 | 0 | 닫힘 |
| `COD_7249360.cif` | CrystEngComm 2024 (싱크로트론) | 16.990 | 3.436 | 0.2022 | 0 | 닫힘 |
| `COD_7243939.cif` | CrystEngComm 2021 (**3D 전자회절**) | 17.497 | **3.705** | 0.2118 | **920.5** | 열림 |

`COD_7243939`만 다공성이 잡히지만 **신뢰도 주의**: 200 keV 전자회절(MicroED)로 결정됐고
R factor가 0.1644(all)/0.1137(gt)로 X선 단결정 기준으로는 상당히 높다. 셀도 표준 상온
구조보다 3% 크다. 정규화 PLD(PLD/a)가 0.2118로 다른 구조들(0.193~0.202)보다 약 5% 높아
리간드 재배향이 일부 실재하는 것으로 보이나, PLD 증가분의 상당 부분은 셀 팽창 때문이다.
**"게이트 열린 상"의 근거로 단독 인용하기엔 약하다.**

## 받아야 할 것: CCDC 739161–739168

진짜 게이트-오프닝 구조는 아래 논문이 원본이며 CCDC에만 있다.

> Moggach, Bennett, Cheetham,
> *"The Effect of Pressure on ZIF-8: Increasing Pore Size with Pressure and the
> Formation of a High-Pressure Phase at 1.47 GPa"*,
> Angew. Chem. Int. Ed. **2009**, 48, 7087–7089. DOI: `10.1002/anie.200902643`
> CCDC 등재번호: **739161 – 739168** (압력 시리즈 8개)

- ZIF-8 phase-I (상압): 입방 I-43m, a = 16.9856(16) Å, V = 4900.5(8) Å³
- **ZIF-8-II (1.47 GPa)**: 공간군은 I-43m 그대로지만 이미다졸레이트가 비틀려
  재배향하면서 접근 가능 기공이 커짐 ← 이것이 목표 구조

## 다운로드 방법 (CCDC는 CAPTCHA + 약관 동의가 필요해 사용자 본인이 받아야 함)

1. https://www.ccdc.cam.ac.uk/structures/ 접속
2. "CCDC Number" 칸에 `739161-739168` 입력 (또는 DOI `10.1002/anie.200902643`로 검색)
3. 8개 전부 CIF로 다운로드 (로봇 확인 + 약관 동의 필요)
4. **이 폴더(`06_ZIF8_Sources/`)에 그대로 넣기** — 파일명은 바꾸지 않아도 됨

넣은 뒤 아래로 압력별 PLD를 일괄 측정하면 어느 것이 1.47 GPa 열린 상인지 바로 나온다:

```bash
conda activate czeromof && python ~/mof_project/06_ZIF8_Sources/measure_candidates.py
```

## 참고: 함께 확인해볼 만한 것

원래 목록에 있던 DOI `10.1021/ja202154j` (Fairen-Jimenez et al., *JACS* 2011,
"Opening the Gate: Framework Flexibility in ZIF-8")는 위 Moggach 구조를 활용한
실험+시뮬레이션 논문이다. 이 논문이 자체 구조를 등재했는지도 CCDC에서 같이 확인해볼 것
(가스 흡착으로 유도된 게이트-오프닝 구조가 있다면 압력 유도보다 우리 조건에 더 가깝다).
