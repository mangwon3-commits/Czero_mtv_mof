# 자동 일일 감사 로그

이 파일은 자동 일일 감사만 씁니다(사람이 쓰지 않음, `COMMS.md` "① 한 파일에
쓰는 사람은 하나" 규약). 최신 항목이 맨 위입니다.

---

## 2026-08-28 00:10 UTC — 일일 감사

**실행 조건**: 클라우드 저장소 체크아웃만으로 확인. 로컬 프로세스·메모리·
미푸시 커밋은 볼 수 없음. 새 계산 없음(`regen_energy_v3.py` 등은 실행하지
않고 파이썬으로 입력 JSON 을 직접 읽어 같은 로직을 재현함). 아래 6개 점검
외 어떤 파일도 수정하지 않음.

### 1) 브랜치 정체

`git fetch --all` 후 (기준 시각 2026-08-28 00:10 UTC):

| 브랜치 | 마지막 커밋 | 경과 | master 대비 뒤처짐 | master 대비 앞섬 |
|---|---|---|---|---|
| `origin/master` | `85b73eb` 2026-08-28 08:27:29 KST | 0.7시간 | — | — |
| `origin/laptop-20260822` | `935df84` 2026-08-28 07:49:09 KST | 1.4시간 | **50커밋** | 203커밋 |
| `origin/junseok-20260822` | `483366b` 2026-08-28 05:53:15 KST | 3.3시간 | 18커밋 | 182커밋 |

(참고, 지시된 세 브랜치 밖: `origin/laptop2-20260825` `684b8ce`
2026-08-28 08:25:52 KST, 0.7시간 경과, master 대비 22커밋 뒤처짐 /
160커밋 앞섬 — 기준 미만.)

**경고: `laptop-20260822` 가 `origin/master` 보다 50커밋 뒤처졌습니다**
(`git rev-list --left-right --count origin/master...origin/laptop-20260822`
→ `50  203`). 08-24 사고 기준(24커밋 이상 경고)을 넘습니다. 전일 감사
(08-27)에서는 6커밋으로 기준 미만이었는데 하루 만에 50으로 급증했습니다.
원인 후보를 확인: `origin/master` 는 지난 24시간(2026-08-27 00:00 KST 이후)
동안 44개의 새 커밋을 받았습니다(`git rev-list --count origin/master
--since="2026-08-27T00:00:00+09:00"`) — 다른 기기·세션의 작업이 master 로
활발히 유입된 결과로 보이며, laptop 자신도 그동안 203개의 자기 커밋을
쌓고 있어 죽은 브랜치는 아닙니다. 다만 **이 브랜치만 읽는 세션은 master 의
최근 판정·문서(예: 오늘 새로 들어온 "판정 문턱의 자가 둘이다", "분할
프로토콜 채택" 등)를 "없다"고 오인할 위험**이 08-24 사고와 같은 형태로
남아 있습니다.

`junseok-20260822`(18커밋)는 기준 미만으로 정상입니다.

### 2) 우편함 침묵

각 우편함 파일의 마지막 갱신 커밋 시각(경과 시간만 보고, 침묵을 "죽었다"로
단정하지 않음):

| 파일 | 마지막 커밋 | 경과 |
|---|---|---|
| `COMMS/desktop.md` | `eaf5467` 2026-08-28 06:14:05 KST | 2.9시간 |
| `COMMS/junseok.md` | `483366b` 2026-08-28 05:53:15 KST | 3.3시간 |
| `COMMS/laptop.md` | `9a0dc14` 2026-08-26 18:56:54 KST | 38.2시간 |
| `COMMS/laptop2.md` (`laptop2-20260825` 브랜치에만 존재, master 미병합) | `684b8ce` 2026-08-28 08:25:52 KST | 0.7시간 |

이상 없음(단정적 "죽었다" 판정 없이 경과만 보고) — 다만 참고할 점: `COMMS/
laptop.md` 는 38.2시간 갱신이 없는데 `laptop-20260822` 브랜치 자체는 1.4시간
전(`935df84`)까지 계속 커밋되고 있습니다(1) 참고). 즉 **랩탑은 계산은
계속하면서 우편함만 갱신을 멈춘 상태**로 읽힙니다 — 장시간 GCMC 작업 중
로그가 뜸한 것과 같은 패턴(CLAUDE.md 4절)일 수 있어 이 자체를 이상으로
단정하지 않습니다.

### 3) 결과 JSON 무결성

`results_v3*.json`, `v3_wc/`, `v3_humid_wc/`, `v4_humid_wc/`, `v3_water_grid*/`
아래 모든 `.json` 을 파이썬으로 파싱(`rows` 키가 있으면 그 배열 길이를
행수로 셈):

| 파일 | 결과 | 행수 |
|---|---|---|
| `results_v3.json` | OK | 31 |
| `results_v3_smoke.json` | OK | 1 |
| `results_v3cliff.json` | OK | 2 |
| `results_v3ens0583.json` | OK | 5 |
| `results_v3grid.json` | OK | 4 |
| `results_v3pctl.json` | OK | 5 |
| `v3_wc/working_capacity.json` | OK | 6 |
| `v3_wc/working_capacity_g0583.json` | OK | 1 |
| `v3_humid_wc/humid_working_capacity.json` | OK | 4 |
| `v3_humid_wc/humid_working_capacity_ext.json` | OK | 1 |
| `v3_humid_wc/humid_working_capacity_g0583.json` | OK | 1 |
| `v3_humid_wc/humid_working_capacity_grid.json` | OK | 1 |
| `v3_humid_wc/humid_working_capacity_mslm075.json` | OK | 1 |
| `v4_humid_wc/humid_working_capacity_v4ext.json` | OK | 2 |
| `v4_humid_wc/humid_working_capacity_v4m1.json` | OK | 1 |
| `v3_water_grid/water_results.json` | OK | 4 |
| `v3_water_grid/water_results_desktop4.json` | OK | 4 |
| `v3_water_grid/water_results_junseok.json` | OK | 4 |
| `v3_water_grid/water_results_laptop.json` | OK | 12 |
| `v3_water_grid_cliff/water_results.json` | OK | 4 |
| `v3_water_grid_cliff/water_results_desktopcliff.json` | OK | 4 |

이상 없음 — 파싱 실패·0행 없음. (전일 대비 `v3_humid_wc/
humid_working_capacity_mslm075.json` 1개가 새로 생겼고 정상 파싱됨.)

### 4) 출처 규약 위반

`merge_water_batches.py` 의 `machine_of()` 는 `water_results_<기기>.json`
형식이 아니면 거부한다(2026-08-23 이중 계수 사고 이후 도입). 태그 붙은
파일만 서로 비교:

- `v3_water_grid/`: `water_results_desktop4.json`(saIm0583) ·
  `water_results_junseok.json`(saIm0875) · `water_results_laptop.json`
  (saIm0625·saIm0667·saIm0875) — (조성,RH) 조합 중 `(saIm0875, 0.0/0.25/
  0.5/0.9)` 4개가 junseok/laptop 양쪽에 있음. **값이 서로 다름**(예: RH0
  junseok 1.2905±0.0333 vs laptop 1.3031±0.0215) → **진짜 교차검증**이지
  중복이 아님.
- `v3_water_grid_cliff/`: 태그 파일이 `water_results_desktopcliff.json`
  하나뿐(saIm0917·saIm0958) — 애초에 중복·교차검증 대상이 없음.

이상 없음 — 태그 붙은 파일 사이에서 값이 동일한 (조성,RH) 중복은 없음.

참고(경고 아님, 전일과 동일): 두 디렉터리 모두 기기 태그 없는
`water_results.json` 이 따로 있고, 값이 각각 `water_results_desktop4.json`,
`water_results_desktopcliff.json` 과 바이트 단위로 동일함. `machine_of()`
가 태그 없는 파일을 구조적으로 거부하므로 `merge_water_batches.py` 를
규약대로(태그 파일만 명시) 쓰는 한 이중 계수로 이어지지 않음.

### 5) 사전 등록 관문 대비 기록

`v3_water_grid*/` 태그 파일에서 RH0·RH90 로딩으로 유지율을 직접 재계산
(각 행의 `CO2_retention_pct` 필드가 이 값과 같음을 확인, 관문 80/50/0):

| 조성 | 출처 | RH0 | RH90 | 재계산 유지율 | 재계산 판정 | 문서 기재값 | 일치 |
|---|---|---|---|---|---|---|---|
| saIm0583 | desktop4 | 1.3188±0.0264 | 1.0010±0.0170 | 75.9% | 조건부 | `COMMS/desktop.md:742` 75.90±1.99% 조건부 | ✅ |
| saIm0625 | laptop | 1.3804±0.0135 | 0.9902±0.0223 | 71.7% | 조건부 | `COMMS/laptop.md:359,366` 71.7% 조건부 | ✅ |
| saIm0667 | laptop | 1.3682±0.0301 | 1.0269±0.0387 | 75.1% | 조건부 | `COMMS/desktop.md:916` 75.05±3.28% 조건부 | ✅ |
| saIm0875 | junseok | 1.2905±0.0333 | 0.9619±0.0181 | 74.5% | 조건부 | `COMMS/junseok.md:8,71` 74.5% 조건부 | ✅ |
| saIm0875 | laptop | 1.3031±0.0215 | 0.9671±0.0482 | 74.2% | 조건부 | `COMMS/laptop.md:320` 74.2±3.9pp | ✅ |
| saIm0917 | desktopcliff | 1.3249±0.0258 | 0.9725±0.0143 | 73.4% | 조건부 | `COMMS/desktop.md:1296,1359` 73.4 | ✅ |
| saIm0958 | desktopcliff | 1.5205±0.0129 | 1.0032±0.0312 | 66.0% | 조건부 | `COMMS/desktop.md:1296,1374` 66.0 | ✅ |

이상 없음 — 확인 가능한 7개 조성/출처 조합 전부 문서 기재와 재계산이
일치함(전일 감사와 동일 수치, 자료 변경 없음). 어긋나는 곳을 찾지 못함.

### 6) WC 자료 공백

`regen_energy_v3.py` 를 실행하지 않고 소스만 읽어, 파일이 실제로 읽는
글롭 패턴(`results_v3*.json`, `v3_wc/*.json`, `v3_humid_wc/*.json`,
`v4_humid_wc/*.json`)을 그대로 재현해 파이썬으로 확인:

| 조성 | 건조 WC | 습윤 WC | Q_st | 재생에너지 계산에 포함되는가 |
|---|---|---|---|---|
| base | ✓ `working_capacity.json` | ✓ `humid_working_capacity.json` | ✓ | ✓ |
| saIm050 | ✓ 〃 | ✓ 〃 | ✓ | ✓ |
| saIm075 | ✓ 〃 | ✓ 〃 | ✓ | ✓ |
| saIm100 | ✓ 〃 | ✓ 〃 | ✓ | ✓ |
| saIm025 | ✓ `working_capacity.json` | ✓ `humid_working_capacity_ext.json` | ✓ | ✓ |
| mslm075 | ✓ `working_capacity.json` | ✓ `humid_working_capacity_mslm075.json` | ✓ | ✓ |
| **saIm0583 (승자 조성)** | ✓ `working_capacity_g0583.json` | ✓ `humid_working_capacity_g0583.json` | ✓ | ✓ |
| saIm0625 | — 없음 | ✓ `humid_working_capacity_grid.json` | ✓ | ✗ (건조 없어 계산 불가) |
| ms50nb50 | — 없음 | ✓ `v4_humid_wc/..._v4ext.json` | — 없음 | ✗ |
| sa25nb75 | — 없음 | ✓ `v4_humid_wc/..._v4ext.json` | — 없음 | ✗ |
| sa50nb50 | — 없음 | ✓ `v4_humid_wc/..._v4m1.json` | — 없음 | ✗ |

**08-26/08-27 감사에서 경고했던 공백(승자 조성 `saIm0583` 이 건조·습윤 WC
가 둘 다 있는데도 `regen_energy_v3.py` 산출물에서 빠져 있던 문제)이
해결되었습니다.** 커밋 `455e5c2` (2026-08-27 13:06:59 KST, "재생에너지
표에서 승자 조성이 빠져 있던 것을 고쳤다 — 하드코딩이 원인이었다")가
하드코딩된 `NAMES`/파일 목록을 글롭 기반으로 바꿨고, 저장소의
`regen_energy_v3.json` 도 같은 커밋에서 함께 갱신되어 현재
`['base', 'mslm075', 'saIm025', 'saIm050', 'saIm0583', 'saIm075',
'saIm100']` 7개 조성을 포함합니다(직접 파싱해 확인). `mslm075` 습윤 WC
파일도 새로 생겨(3절) 포함됨을 확인.

남은 `saIm0625`·`ms50nb50`·`sa25nb75`·`sa50nb50` 4개 조성은 한쪽 자료(건조
WC 또는 Q_st)가 애초에 없어 계산 불가이며, 새 스크립트가 이들을 조용히
반쪽만 채우지 않고 **셋 다(dry_tsa/dry_vsa/wet_tsa/wet_vsa) + Q_st 가 모두
있는 조성만** 포함시키는 것을 소스에서 직접 확인했습니다 — "한쪽만 있는데
완성된 행처럼 보이는" 위험은 없음.

이상 없음(전일 경고가 해결됨).

---

## 사람이 볼 것

- 경고: `laptop-20260822` 브랜치가 `origin/master` 보다 **50커밋** 뒤처짐
  (전일 6커밋에서 급증, 08-24 사고 기준 24커밋 초과). master 가 24시간 새
  44커밋을 받은 정상적 확산으로 보이나, 이 브랜치만 보는 세션은 master
  최신 문서를 "없다"고 오인할 위험이 있음.
- 해결됨(참고): 08-26/27 경고였던 `regen_energy_v3.py` 의 승자 조성
  `saIm0583` 누락은 08-27 13:06 커밋(`455e5c2`)으로 고쳐졌고 산출물도
  갱신됨을 확인.
- 나머지 항목(우편함 침묵·JSON 무결성·출처 중복·사전 등록 관문 기록)은
  이상 없음.

---

## 2026-08-27 00:10 UTC — 일일 감사

**실행 조건**: 클라우드 저장소 체크아웃만으로 확인. 로컬 프로세스·메모리·
미푸시 커밋은 볼 수 없음. 새 계산 없음. 아래 6개 점검 외 어떤 파일도
수정하지 않음.

### 1) 브랜치 정체

`git fetch --all` 후 (기준 시각 2026-08-27 00:10 UTC):

| 브랜치 | 마지막 커밋 | 경과 | master 대비 뒤처짐 | master 대비 앞섬 |
|---|---|---|---|---|
| `origin/master` | `568362d` 2026-08-26 19:55:13 KST | 13.2시간 | — | — |
| `origin/laptop-20260822` | `64ee89f` 2026-08-26 20:00:56 KST | 13.2시간 | 6커밋 | 12커밋 |
| `origin/junseok-20260822` | `4047278` 2026-08-25 17:02:50 KST | 40.1시간 | **36커밋** | 5커밋 |

(참고, 지시된 세 브랜치 밖: `origin/laptop2-20260825` `777cc22`
2026-08-26 14:42:22 KST, 18.4시간 경과, master 대비 **34커밋** 뒤처짐 /
6커밋 앞섬. `COMMS.md` 등록부에 이미 08-26 14:04 하드웨어 불량 확정·배정
제외로 기록돼 있어, 이 정체는 새 이상이 아니라 그 상태와 부합합니다.)

**경고: `junseok-20260822` 가 `origin/master` 보다 36커밋 뒤처졌습니다**
(`git rev-list --left-right --count origin/master...origin/junseok-20260822`
→ `36  5`). 08-24 사고 기준(24커밋 이상 경고)을 넘습니다. `COMMS.md`
기기 등록부에 이미 "🔴 08-26 오전 다운, 마지막 소식 08-25 17:02"로
기록돼 있어 원인은 알려진 상태(기기 정지)이지만, 이 브랜치를 그대로
읽는 세션은 master 에만 있는 최근 문서·판정을 "없다"고 오인할 위험이
여전합니다 — 08-24 사고와 같은 함정.

`laptop-20260822`(6커밋)는 어제(52커밋)에서 크게 줄어 기준 미만으로
정상입니다.

### 2) 우편함 침묵

각 우편함 파일의 마지막 갱신 커밋 시각(경과 시간만 보고, 침묵을 "죽었다"로
단정하지 않음):

| 파일 | 마지막 커밋 | 경과 |
|---|---|---|
| `COMMS/desktop.md` | `bc23042` 2026-08-26 19:32:12 KST | 13.6시간 |
| `COMMS/junseok.md` | `4047278` 2026-08-25 17:02:50 KST | 40.1시간 |
| `COMMS/laptop.md` | `fc1b401` 2026-08-25 22:23:20 KST | 34.8시간 |
| `COMMS/laptop2.md` (`laptop2-20260825` 브랜치에만 존재, master 미병합) | `777cc22` 2026-08-26 14:42:22 KST | 18.4시간 |

이상 없음 — 경과 시간만 보고합니다. junseok·laptop2 의 긴 경과는 1)·
`COMMS.md` 등록부의 기기 상태(각각 다운, 하드웨어 불량 확정)와 부합합니다.
`cloud4c.md`, `external16.md` 는 저장소 어디에도 없는데, 등록부가 두 기기를
각각 🔴 종료 / ⚪ 완료로 적어 두어 부재가 상태와 부합합니다.

### 3) 결과 JSON 무결성

`results_v3*.json`, `v3_wc/`, `v3_humid_wc/`, `v4_humid_wc/`, `v3_water_grid*/`
아래 모든 `.json` 을 파이썬으로 파싱(`rows` 키가 있으면 그 배열 길이를
행수로 셈):

| 파일 | 결과 | 행수 |
|---|---|---|
| `results_v3.json` | OK | 31 |
| `results_v3_smoke.json` | OK | 1 |
| `results_v3cliff.json` | OK | 2 |
| `results_v3ens0583.json` | OK | 5 |
| `results_v3grid.json` | OK | 4 |
| `results_v3pctl.json` | OK | 5 |
| `v3_wc/working_capacity.json` | OK | 6 |
| `v3_wc/working_capacity_g0583.json` | OK | 1 |
| `v3_humid_wc/humid_working_capacity.json` | OK | 4 |
| `v3_humid_wc/humid_working_capacity_ext.json` | OK | 1 |
| `v3_humid_wc/humid_working_capacity_g0583.json` | OK | 1 |
| `v3_humid_wc/humid_working_capacity_grid.json` | OK | 1 |
| `v4_humid_wc/humid_working_capacity_v4ext.json` | OK | 2 |
| `v4_humid_wc/humid_working_capacity_v4m1.json` | OK | 1 |
| `v3_water_grid/water_results.json` | OK | 4 |
| `v3_water_grid/water_results_desktop4.json` | OK | 4 |
| `v3_water_grid/water_results_junseok.json` | OK | 4 |
| `v3_water_grid/water_results_laptop.json` | OK | 12 |
| `v3_water_grid_cliff/water_results.json` | OK | 4 |
| `v3_water_grid_cliff/water_results_desktopcliff.json` | OK | 4 |

이상 없음 — 파싱 실패·0행 없음. (전날 감사는 `results_v3*.json` 과 일부
`v3_humid_wc`/`v4_humid_wc` 파일의 "행수"를 최상위 dict 키 개수로 잘못
세어 전부 3~5로 찍었던 것으로 보임 — 이번엔 실제 데이터 배열인 `rows`
키 길이로 다시 세었고, 파싱 성공·0행 없음이라는 결론 자체는 바뀌지 않음.)

### 4) 출처 규약 위반

`merge_water_batches.py` 의 `machine_of()` 는 `water_results_<기기>.json`
형식이 아니면 거부한다(2026-08-23 이중 계수 사고 이후 도입). 태그 붙은
파일만 서로 비교:

- `v3_water_grid/`: `water_results_desktop4.json`(saIm0583) ·
  `water_results_junseok.json`(saIm0875) · `water_results_laptop.json`
  (saIm0625·saIm0667·saIm0875) — (조성,RH) 조합 중 `(saIm0875, 0.0/0.25/
  0.5/0.9)` 4개가 junseok/laptop 양쪽에 있음. **값이 서로 다름**(예: RH0
  junseok 1.2905±0.0333 vs laptop 1.3031±0.0215) → **진짜 교차검증**이지
  중복이 아님.
- `v3_water_grid_cliff/`: 태그 파일이 `water_results_desktopcliff.json`
  하나뿐(saIm0917·saIm0958) — 애초에 중복·교차검증 대상이 없음.

이상 없음 — 태그 붙은 파일 사이에서 값이 동일한 (조성,RH) 중복은 없음.

참고(경고 아님, 전일과 동일): 두 디렉터리 모두 기기 태그 없는
`water_results.json` 이 따로 있고, 값이 각각 `water_results_desktop4.json`,
`water_results_desktopcliff.json` 과 바이트 단위로 동일함. `machine_of()`
가 태그 없는 파일을 구조적으로 거부하므로 `merge_water_batches.py` 를
규약대로(태그 파일만 명시) 쓰는 한 이중 계수로 이어지지 않음.

### 5) 사전 등록 관문 대비 기록

`v3_water_grid*/` 태그 파일에서 RH0·RH90 로딩으로 유지율을 직접 재계산
(각 행의 `CO2_retention_pct` 필드가 이 값과 같음을 확인, 관문 80/50/0):

| 조성 | 출처 | RH0 | RH90 | 재계산 유지율 | 재계산 판정 | 문서 기재값 | 일치 |
|---|---|---|---|---|---|---|---|
| saIm0583 | desktop4 | 1.3188±0.0264 | 1.0010±0.0170 | 75.9% | 조건부 | `COMMS/desktop.md:742` 75.90±1.99% 조건부 | ✅ |
| saIm0625 | laptop | 1.3804±0.0135 | 0.9902±0.0223 | 71.7% | 조건부 | `COMMS/laptop.md:359,366` 71.7% 조건부 | ✅ |
| saIm0667 | laptop | 1.3682±0.0301 | 1.0269±0.0387 | 75.1% | 조건부 | `COMMS/desktop.md:916` 75.05±3.28% 조건부 | ✅ |
| saIm0875 | junseok | 1.2905±0.0333 | 0.9619±0.0181 | 74.5% | 조건부 | `COMMS/junseok.md:8,71` 74.5% 조건부 | ✅ |
| saIm0875 | laptop | 1.3031±0.0215 | 0.9671±0.0482 | 74.2% | 조건부 | `COMMS/laptop.md:320` 74.2±3.9pp | ✅ |
| saIm0917 | desktopcliff | 1.3249±0.0258 | 0.9725±0.0143 | 73.4% | 조건부 | `COMMS/desktop.md:1296,1359` 73.4 | ✅ |
| saIm0958 | desktopcliff | 1.5205±0.0129 | 1.0032±0.0312 | 66.0% | 조건부 | `COMMS/desktop.md:1296,1374` 66.0 | ✅ |

이상 없음 — 확인 가능한 7개 조성/출처 조합 전부 문서 기재와 재계산이
일치함(전일 감사와 동일 수치, 자료 변경 없음). 어긋나는 곳을 찾지 못함.

### 6) WC 자료 공백

`regen_energy_v3.py` 는 하드코딩된 `NAMES = ['base', 'saIm050', 'saIm075',
'saIm100']` 와 두 파일(`v3_wc/working_capacity.json`,
`v3_humid_wc/humid_working_capacity.json`)만 읽는다(파일 자체·git log 08-23
06:27 이후 무변경 확인).

실제 존재하는 조성:

| 조성 | 건조 WC | 습윤 WC | `regen_energy_v3.py` 가 읽는가 |
|---|---|---|---|
| base | ✓ `working_capacity.json` | ✓ `humid_working_capacity.json` | ✓ |
| saIm050 | ✓ 〃 | ✓ 〃 | ✓ |
| saIm075 | ✓ 〃 | ✓ 〃 | ✓ |
| saIm100 | ✓ 〃 | ✓ 〃 | ✓ |
| saIm025 | ✓ `working_capacity.json` | ✓ `humid_working_capacity_ext.json` | ✗ (습윤 별도 파일 미읽음) |
| **saIm0583 (승자 조성)** | ✓ `working_capacity_g0583.json` | ✓ `humid_working_capacity_g0583.json` | **✗ (둘 다 미읽음)** |
| saIm0625 | — 없음 | ✓ `humid_working_capacity_grid.json` | ✗ (건조 없어 계산 불가) |
| mslm075 | ✓ `working_capacity.json` | — 없음 | ✗ (습윤 없어 계산 불가) |
| ms50nb50 | — 없음 | ✓ `v4_humid_wc/..._v4ext.json` | ✗ |
| sa25nb75 | — 없음 | ✓ `v4_humid_wc/..._v4ext.json` | ✗ |
| sa50nb50 | — 없음 | ✓ `v4_humid_wc/..._v4m1.json` | ✗ |

**경고(전일과 동일, 미해결): 승자 조성 `saIm0583` 은 건조·습윤 WC 가 둘 다
완비되어 있는데(`regen_energy_v3.json` 실제 출력 확인 —
`rows` 의 `name` 이 `['base', 'saIm050', 'saIm075', 'saIm100']` 뿐,
saIm0583 행 없음) `regen_energy_v3.py` 의 `NAMES`/파일 목록에서 완전히
빠져 있어 재생에너지 산출물에 그 행 자체가 없음.** 08-26 감사 이후
`regen_energy_v3.py` 와 관련 JSON 모두 무변경 — 공백이 그대로 남아 있음.

saIm025 도 같은 이유(습윤이 별도 파일)로 빠짐. saIm0625·mslm075·v4 세
조성(ms50nb50/sa25nb75/sa50nb50)은 애초에 한쪽 자료가 없어 계산 불가이므로
별도 조치 불필요(공백이 아니라 미측정).

---

## 사람이 볼 것

- 경고: `junseok-20260822` 브랜치가 `origin/master` 보다 **36커밋** 뒤처짐
  (08-24 사고 기준 초과). 원인은 알려진 기기 다운(08-26 오전~)이지만, 이
  브랜치만 보는 세션은 master 최신 문서를 "없다"고 오인할 위험이 있음.
- 경고: `regen_energy_v3.py` 가 완비된 승자 조성 saIm0583 건조+습윤 WC 를
  여전히 읽지 않아 `regen_energy_v3.json` 에 그 행이 없음(전일 대비 불변).
- 나머지 항목(우편함 침묵·JSON 무결성·출처 중복·사전 등록 관문 기록)은
  이상 없음.

---

## 2026-08-26 00:02 UTC — 일일 감사

**실행 조건**: 클라우드 저장소 체크아웃만으로 확인. 로컬 프로세스·메모리·
미푸시 커밋은 볼 수 없음. 새 계산 없음. 아래 6개 점검 외 어떤 파일도
수정하지 않음.

### 1) 브랜치 정체

`git fetch --all` 후 (기준 시각 2026-08-26 00:02 UTC = 09:02 KST):

| 브랜치 | 마지막 커밋 | 경과 | master 대비 뒤처짐 | master 대비 앞섬 |
|---|---|---|---|---|
| `origin/master` | `a83d7e7` 2026-08-25 22:17:06 KST | 10.7시간 | — | — |
| `origin/laptop-20260822` | `fc1b401` 2026-08-25 22:23:20 KST | 10.6시간 | **52커밋** | 4커밋 |
| `origin/junseok-20260822` | `4047278` 2026-08-25 17:02:50 KST | 15.9시간 | 12커밋 | 5커밋 |

(참고, 지시된 세 브랜치 밖: `origin/laptop2-20260825` `16c8af5` 2026-08-25
21:25:01 KST, 11.6시간 경과, master 대비 10커밋 뒤처짐/2커밋 앞섬 — 정상
범위. 이 브랜치는 registry 에 아직 등록 절차 중이라 판정 대상에 넣지 않음.)

**경고: `laptop-20260822` 가 `origin/master` 보다 52커밋 뒤처졌습니다**
(`git rev-list --left-right --count origin/master...origin/laptop-20260822`
→ `52  4`). 08-24 사고 기준(24커밋 이상 경고)의 두 배가 넘습니다. 이
브랜치를 읽는 세션은 `ERROR_BARS.md` 등 master 에만 있는 최근 문서를
"없다"고 오인할 위험이 있습니다.

`junseok-20260822`(12커밋)는 기준 미만으로 정상입니다.

### 2) 우편함 침묵

각 우편함 파일의 마지막 갱신 커밋 시각(경과 시간만 보고, 침묵을 "죽었다"로
단정하지 않음):

| 파일 | 마지막 커밋 | 경과 |
|---|---|---|
| `COMMS/desktop.md` | `3bcb642` 2026-08-25 21:54:40 KST | 11.1시간 |
| `COMMS/junseok.md` | `1e90ef4` 2026-08-23 19:18:19 KST | 61.7시간 |
| `COMMS/laptop.md` | `b7ad81c` 2026-08-24 18:15:39 KST | 38.7시간 |
| `COMMS/laptop2.md` (`laptop2-20260825` 브랜치에만 존재, master 미병합) | `16c8af5` 2026-08-25 21:25:01 KST | 11.6시간 |

이상 없음 — 경과 시간만 보고합니다. `COMMS.md` 등록부의 `cloud4c.md`,
`external16.md` 는 저장소 어디에도(어느 브랜치에도) 없는데, 등록부 자체가
두 기기를 각각 🔴 종료 / ⚪ 완료로 적어 두어 우편함 부재가 상태와 부합합니다.

### 3) 결과 JSON 무결성

`results_v3*.json`, `v3_wc/`, `v3_humid_wc/`, `v4_humid_wc/`, `v3_water_grid*/`
아래 모든 `.json` 을 파이썬으로 파싱:

| 파일 | 결과 | 행수 |
|---|---|---|
| `results_v3.json` | OK | 3 |
| `results_v3_smoke.json` | OK | 3 |
| `results_v3cliff.json` | OK | 3 |
| `results_v3ens0583.json` | OK | 3 |
| `results_v3grid.json` | OK | 3 |
| `v3_wc/working_capacity.json` | OK | 4 |
| `v3_wc/working_capacity_g0583.json` | OK | 4 |
| `v3_humid_wc/humid_working_capacity.json` | OK | 5 |
| `v3_humid_wc/humid_working_capacity_ext.json` | OK | 5 |
| `v3_humid_wc/humid_working_capacity_g0583.json` | OK | 5 |
| `v3_humid_wc/humid_working_capacity_grid.json` | OK | 5 |
| `v4_humid_wc/humid_working_capacity_v4ext.json` | OK | 5 |
| `v4_humid_wc/humid_working_capacity_v4m1.json` | OK | 5 |
| `v3_water_grid/water_results.json` | OK | 4 |
| `v3_water_grid/water_results_desktop4.json` | OK | 4 |
| `v3_water_grid/water_results_junseok.json` | OK | 4 |
| `v3_water_grid/water_results_laptop.json` | OK | 12 |
| `v3_water_grid_cliff/water_results.json` | OK | 4 |
| `v3_water_grid_cliff/water_results_desktopcliff.json` | OK | 4 |

이상 없음 — 파싱 실패·0행 없음. (`working_capacity*.json`, `humid_working_*`
류는 최상위가 dict 이므로 "행수"는 `rows` 배열 길이.)

### 4) 출처 규약 위반

`merge_water_batches.py` 의 `machine_of()` 는 `water_results_<기기>.json`
형식이 아니면 거부합니다(2026-08-23 이중 계수 사고 이후 도입). 태그 붙은
파일만 서로 비교:

- `v3_water_grid/`: `water_results_desktop4.json`(saIm0583) ·
  `water_results_junseok.json`(saIm0875) · `water_results_laptop.json`
  (saIm0625·saIm0667·saIm0875) — (조성,RH) 16개 중 `(saIm0875, *)` 4개가
  junseok/laptop 양쪽에 있음. **값이 서로 다릅니다** (예: RH0 junseok
  1.2905±0.0333 vs laptop 1.3031±0.0215) → **진짜 교차검증**이지 중복이
  아닙니다.
- `v3_water_grid_cliff/`: 태그 파일 `water_results_desktopcliff.json` 하나뿐
  (saIm0917·saIm0958) — 중복·교차검증 대상 자체가 없음.

이상 없음 — 태그 붙은 파일 사이에서 값이 동일한 (조성,RH) 중복은 없습니다.

참고(경고 아님): 두 디렉터리 모두 기기 태그 없는 `water_results.json` 이
따로 있고, 내용이 각각 `water_results_desktop4.json`,
`water_results_desktopcliff.json` 과 **바이트 단위로 동일**합니다(md5 일치).
이것이 2026-08-23 사고의 원재료였는데, 지금은 `machine_of()` 가 태그 없는
파일을 구조적으로 거부하므로 `merge_water_batches.py` 를 규약대로(태그
파일만 명시) 쓰는 한 이중 계수로 이어지지 않습니다. `water_results*.json`
로 글롭하는 옛 방식을 쓰면 여전히 위험하다는 점만 적어 둡니다.

### 5) 사전 등록 관문 대비 기록

`v3_water_grid*/` 태그 파일에서 RH0·RH90 로딩으로 유지율을 직접 재계산
(`retention = CO2(RH90)/CO2(RH0) × 100`, 관문 80/50/0):

| 조성 | 출처 | RH0 | RH90 | 재계산 유지율 | 재계산 판정 | 문서 기재값 | 일치 |
|---|---|---|---|---|---|---|---|
| saIm0583 | desktop4 | 1.3188±0.0264 | 1.0010±0.0170 | 75.9% | 조건부 | `COMMS/desktop.md:742` 75.90±1.99% 조건부 | ✅ |
| saIm0625 | laptop | 1.3804±0.0135 | 0.9902±0.0223 | 71.7% | 조건부 | `COMMS/laptop.md:359,366` 71.7% 조건부 | ✅ |
| saIm0667 | laptop | 1.3682±0.0301 | 1.0269±0.0387 | 75.1% | 조건부 | `COMMS/desktop.md:916` 75.05±3.28% 조건부 | ✅ |
| saIm0875 | junseok | 1.2905±0.0333 | 0.9619±0.0181 | 74.5% | 조건부 | `COMMS/junseok.md:8,71` 74.5% 조건부 | ✅ |
| saIm0875 | laptop | 1.3031±0.0215 | 0.9671±0.0482 | 74.2% | 조건부 | `COMMS/laptop.md:320` 74.2±3.9pp | ✅ |
| saIm0917 | desktopcliff | 1.3249±0.0258 | 0.9725±0.0143 | 73.4% | 조건부 | `COMMS/desktop.md:1296,1359` 73.4 | ✅ |
| saIm0958 | desktopcliff | 1.5205±0.0129 | 1.0032±0.0312 | 66.0% | 조건부 | `COMMS/desktop.md:1296,1374` 66.0 | ✅ |

이상 없음 — 확인 가능한 7개 조성/출처 조합 전부 문서 기재와 재계산이
일치합니다. 어긋나는 곳을 찾지 못했습니다.

### 6) WC 자료 공백

`regen_energy_v3.py` 는 하드코딩된 `NAMES = ['base', 'saIm050', 'saIm075',
'saIm100']` 와 두 파일(`v3_wc/working_capacity.json`,
`v3_humid_wc/humid_working_capacity.json`)만 읽습니다. `_g0583`, `_ext`,
`_grid` 접미사 파일과 `v4_humid_wc/` 는 이 스크립트 안에서 아예 열리지
않습니다.

실제 존재하는 조성:

| 조성 | 건조 WC | 습윤 WC | `regen_energy_v3.py` 가 읽는가 |
|---|---|---|---|
| base | ✓ `v3_wc/working_capacity.json` | ✓ `v3_humid_wc/humid_working_capacity.json` | ✓ |
| saIm050 | ✓ 〃 | ✓ 〃 | ✓ |
| saIm075 | ✓ 〃 | ✓ 〃 | ✓ |
| saIm100 | ✓ 〃 | ✓ 〃 | ✓ |
| saIm025 | ✓ `working_capacity.json` | ✓ `humid_working_capacity_ext.json`(별도 파일) | ✗ (습윤 파일 미읽음) |
| **saIm0583 (승자 조성)** | ✓ `working_capacity_g0583.json` | ✓ `humid_working_capacity_g0583.json` | **✗ (둘 다 미읽음)** |
| saIm0625 | — 없음 | ✓ `humid_working_capacity_grid.json` | ✗ (건조 자체가 없어 계산 불가) |
| mslm075 | ✓ `working_capacity.json` | — 없음 | ✗ (습윤 자체가 없어 계산 불가) |
| ms50nb50 | — 없음 | ✓ `v4_humid_wc/..._v4ext.json` | ✗ |
| sa25nb75 | — 없음 | ✓ `v4_humid_wc/..._v4ext.json` | ✗ |
| sa50nb50 | — 없음 | ✓ `v4_humid_wc/..._v4m1.json` | ✗ |

**경고: 승자 조성 `saIm0583` 은 건조·습윤 WC 가 둘 다 완비되어 있는데
(`v3_wc/working_capacity_g0583.json` tsa=1.1267±0.0258,
`v3_humid_wc/humid_working_capacity_g0583.json` tsa=0.8328±0.0252 —
`COMMS/desktop.md:20` 의 헤드라인 수치와 일치) `regen_energy_v3.py` 의
현재 `NAMES`/파일 목록에서 완전히 빠져 있어 `regen_energy_v3.json` 에
saIm0583 행 자체가 존재하지 않습니다** (실제 산출물 확인:
`['base', 'saIm050', 'saIm075', 'saIm100']`). 이번 점검에서는 "한쪽만
있어 절반만 찬 행"은 발견하지 못했습니다(스크립트가 그런 조성 자체를
건너뜀) — 대신 **양쪽 다 있는데도 통째로 빠지는** 더 조용한 형태의 공백입니다.

saIm025 도 같은 이유(습윤이 별도 파일)로 빠져 있습니다. saIm0625·mslm075·
v4 세 조성(ms50nb50/sa25nb75/sa50nb50)은 애초에 한쪽 자료가 없어 계산
불가이므로 별도 조치가 필요 없습니다(공백이 아니라 미측정).

---

## 사람이 볼 것

- 경고: `laptop-20260822` 브랜치가 `origin/master` 보다 **52커밋** 뒤처짐
  (08-24 사고 기준의 2배 이상).
- 경고: `regen_energy_v3.py` 가 완비된 saIm0583(승자 조성) 건조+습윤 WC 를
  읽지 않아 `regen_energy_v3.json` 에 그 행이 아예 없음.
- 나머지 4개 항목(우편함 침묵/JSON 무결성/출처 중복/사전 등록 관문 기록)은
  이상 없음.
