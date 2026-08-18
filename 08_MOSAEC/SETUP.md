# MOSAEC 세팅 — 평가판 라이선스로 금속 산화수 검사 넣기

> MOSAEC (Metal Oxidation State Automated Error Checker)
> White, Gibaldi, Burner, Mayo, Woo, *JACS* **2025**, 147, 17579–17583
> [doi:10.1021/jacs.5c04914](https://doi.org/10.1021/jacs.5c04914) ·
> [github.com/uowoolab/MOSAEC](https://github.com/uowoolab/MOSAEC)

## 무엇이 빠져 있었나

구조 평가 지표를 세 개 돌렸고 **MOSAEC 만 빠져 있었습니다.**

| 지표 | 무엇을 보나 | 상태 |
|---|---|---|
| Chen & Manz 결합차수 | 결합차수 이상 | ✅ `04_CoreMOF_Validation/` |
| MOFChecker 2.0 | 원자 겹침 · 배위수 · 고아 원자 | ✅ 〃 |
| MOFClassifier (ML) | computation-ready 판별 | ✅ 〃 |
| **MOSAEC** | **화학적으로 불가능한 산화수 조합** | ⛔ 라이선스 대기 |

그리고 더 큰 문제가 있었습니다. **위 셋은 `03_Generated_MTV_ZIFs`(초기
MTV-ZIF-8)를 대상으로 돌았고, 08-21 장표에 들어가는 것은 `21_ZIF69_MTV` 의
v3 후보입니다.** 지표와 대상이 어긋나 있었습니다. `run_mosaec.py` 의
대상 목록을 v3 우선으로 다시 짰습니다.

## 라이선스 — 이 부분은 사용자 본인이 하셔야 합니다

CCDC 계정 로그인과 약관 동의가 필요하고, 그것은 대리 수행 대상이 아닙니다.
아래는 절차만 적은 것입니다.

1. [CSD Python API](https://www.ccdc.cam.ac.uk/solutions/csd-core/components/csd-python-api/)
   에서 **30일 평가판**(또는 기관 라이선스) 신청
2. CCDC 포털에서 리눅스용 CSD Portfolio 설치본 내려받기
3. 활성화

   ```bash
   ccdc_activator -a -k <라이선스키>
   # 또는
   export CCDC_LICENSING_CONFIGURATION=la-code:<키>
   ```

4. 이 conda 환경에 API 설치 (경로는 설치본 위치에 맞게)

   ```bash
   conda activate coremof_tools
   pip install /opt/CCDC/Python_API_<버전>/csd-python-api/*.whl
   ```

5. 확인

   ```bash
   python ~/mof_project/08_MOSAEC/preflight.py
   ```

### CSD 데이터베이스는 필요 없습니다

`CoREMOF/mosaec.py` 의 `readentry()` 는 `io.CrystalReader(cif, format="cif")`
로 **로컬 CIF 를 읽습니다.** refcode 로 DB 를 조회하는 `read_CSD_entry()` 는
`check()` 경로에서 쓰이지 않습니다. 즉 필요한 것은 **API 패키지와 라이선스**
이지 CSD 전체 데이터베이스 설치가 아닙니다.

### 지금 상태

```
[ OK ] mendeleev 1.1.0 / typing_extensions / numpy 1.26.4 / pandas 2.2.3
[라이선스] ccdc          <- 이것 하나만 남았습니다
```

무료 의존성은 전부 들어가 있습니다. 라이선스가 켜지면 바로 돕니다.

## 켜지면 이 순서로

```bash
conda activate coremof_tools
python ~/mof_project/08_MOSAEC/preflight.py                       # 확인
python ~/mof_project/08_MOSAEC/run_mosaec.py --only v3_charged    # 장표 후보 먼저
python ~/mof_project/08_MOSAEC/run_mosaec.py                      # 나머지 전부
python ~/mof_project/08_MOSAEC/join_scores.py                     # 통합표
```

대상은 우선순위 순으로 **193 CIF** 입니다.

| 라벨 | CIF | 무엇 |
|---|---|---|
| `v3_charged` | 31 | **v3 최종 계산 입력.** GCMC 가 실제로 읽은 파일 |
| `v3_relaxed` | 30 | GFN-FF 이완 직후, 전하 전 |
| `v3_built` | 34 | 빌더 출력(이완 전) — 대조군 |
| `v3_parent` | 1 | 이완된 무치환 모체 |
| `aryl_zif69` | 32 | v1 구조 (08-14 폐기본) — 대조로만 |
| `generated_zif8` | 11 | 초기 MTV-ZIF-8 |
| `bracketed` | 14 | 괄호 조성 쌍 |
| `ligand_library` | 7 | 모체·라이브러리 원본 |
| `zif8_sources` | 6 | ZIF-8 실험 구조 |
| `source_cifs` | 27 | 정리된 원본 CIF |

**세 판본(빌더 출력 / 이완본 / 전하본)을 다 돌리는 이유**가 있습니다.
MOSAEC 은 기하에서 결합을 인식해 산화수를 매기므로, **이완이 판정을 바꾸는지**
가 그 자체로 결과입니다. v2→v3 에서 이완이 흡착 순위를 뒤집었으니
(`V3_RESULT_NOTE.md`), 산화수 판정에도 같은 질문을 해야 합니다.

## 여덟 개 깃발과 우리가 읽는 법

```
impossible   unknown   zero_valence   noint_flag      <- 굳은 실패
low_prob_1   low_prob_2   low_prob_3   low_prob_multi  <- 확률적 경고
```

앞의 넷은 "그런 산화수는 없다" 류이고, 뒤의 넷은 "가능하지만 드물다" 입니다.

> **이 둘로 나눈 것은 우리가 읽는 방식이고 MOSAEC 이 정한 합격선이 아닙니다.**
> 논문은 깃발을 그대로 보고하며 무엇을 탈락으로 볼지는 쓰는 쪽이 정합니다.
> 그래서 결과 표는 여덟 개를 **전부** 남기고, 요약에서만 둘로 나눕니다.
> 장표에 쓸 때도 "MOSAEC 통과" 가 아니라 어느 깃발이 섰는지로 적으세요.

## 상류 코드의 함정 두 개 — 감싸 두었습니다

### 1. 금속 없는 CIF 하나가 폴더 전체 요약을 죽입니다

`CoREMOF.mosaec.check()` 는 금속 자리가 없거나 읽기에 실패하면 **빈 dict** 를
돌려주고, `worker()` 가 그것을 문자열 `"unknown"` 으로 채웁니다. 그러면 요약
루프의 `for metal in data[col]` 이 문자열을 글자 단위로 돌다가
`data[col][metal]` 에서 `TypeError` 로 죽습니다.

`run_mosaec.py` 는 **금속이 있는 CIF 만 staging 폴더로 복사해** 돌립니다.
원본은 건드리지 않습니다.

### 2. 그래도 죽으면 — 요약을 우리가 다시 만듭니다

per-CIF JSON 은 요약 루프보다 **먼저** 기록됩니다. 그래서 상류가 터져도
결과는 디스크에 남아 있습니다. `run_mosaec.py` 는 상류 반환값을 믿지 않고
언제나 그 JSON 들에서 `flags.json` 을 다시 만듭니다.

### 곁가지로 잡은 것 — CSD 가 내려주는 CIF 는 빈 줄이 있습니다

금속 검사를 처음에 ASE 로 짰더니 193개에 몇 분이 걸려(대칭 전개) 텍스트
스캐너로 바꿨는데, 그 스캐너가 **머리글과 데이터 사이의 빈 줄**에서 끊겨
`01_CIF_Cleaned` 의 Co-MOF 네 개를 "금속 없음" 으로 분류했습니다. 그대로
뒀다면 실제 코발트 구조 네 개가 조용히 검사에서 빠졌을 것입니다.
고친 뒤 ASE 판정과 193/193 일치를 확인했습니다.

## 통합표

```bash
python ~/mof_project/08_MOSAEC/join_scores.py
```

v3 후보를 행으로 놓고 Q_st · 로딩 · PLD · 이완 판정 · 안정성 관문 · MOSAEC
깃발을 한 줄에 놓습니다. **없는 칸은 `—` 로 비워 둡니다** — 채워진 것처럼
보이게 만들지 않습니다.

**가중합 점수를 만들지 않습니다.** 지표들은 단위도 방향도 다르고, 가중치를
정하는 순간 그 가중치가 결론을 정합니다. 그것을 정당화할 근거가 우리에게
없습니다. 관문의 통과·탈락과 원 수치를 나란히 보이는 데서 멈춥니다.

## 라이선스가 끝내 안 나오면

MOSAEC 없이도 장표는 성립합니다 — 다만 **그 칸을 비워 두고 왜 비었는지
적으세요.** "산화수 검사는 CSD Python API 라이선스가 필요해 이번 범위에서
제외" 라고 쓰는 것이, 안 한 검사를 안 한 채로 넘어가는 것보다 낫습니다.
