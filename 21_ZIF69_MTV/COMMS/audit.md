# 자동 일일 감사 로그

이 파일은 자동 일일 감사만 씁니다(사람이 쓰지 않음, `COMMS.md` "① 한 파일에
쓰는 사람은 하나" 규약). 최신 항목이 맨 위입니다.

---

## 2026-09-12 00:12 UTC — 일일 감사

**실행 조건**: 클라우드 저장소 체크아웃만으로 확인. 로컬 프로세스·메모리·
미푸시 커밋은 볼 수 없음. 새 계산 없음 — `merge_water_batches.py`는 태그
붙은 파일만 넘겨 실제로 실행(식을 손으로 재현하지 않음, COMMS.md ⑨-1 "있는
자를 부른다"), `regen_energy_v3.py`는 모듈로 임포트해 `NAMES`/`QST`/
`load_wc()`만 조회(`main()` 미실행, 새 산출물 없음). 아래 6개 점검 외 어떤
파일도 수정하지 않음.

**방법 메모(경고 아님, 반복되는 검사기 함정)**: 이 컨테이너 체크아웃이
또 얕은 클론이었다(`git rev-parse --is-shallow-repository` → `true`,
09-06~09-11 감사가 반복 기록한 것과 같음). unshallow 전
`git merge-base origin/master origin/laptop-20260822`·
`origin/junseok-20260822` 둘 다 공통 조상을 못 찾아 rc=1을 반환했고,
`git rev-list --left-right --count`는 각각 "50 323"·"50 409"로 마치
두 브랜치가 master와 아예 다른 뿌리에서 갈라진 것처럼 보였다. `git fetch
--unshallow` 후 재계산하니 각각 정상적인 조상 관계로 정정됐다(아래 1절 수치는
전부 unshallow 이후 값). **얕은 클론 상태에서 `merge-base` 실패나 큰 뒤처짐
수치만 보고 "master가 강제 푸시로 분리됐다"고 단정하면 안 된다** — 그 자체가
이 프로젝트가 반복해서 데인 "실패가 결과처럼 보이는 것" 유형이다.

### 1) 브랜치 정체

`git fetch --all` + `git fetch --unshallow` 후 (기준 시각 2026-09-12
00:12 UTC = 09:12 KST):

| 브랜치 | 마지막 커밋 | 경과 | master 대비 뒤처짐 | master 대비 앞섬 |
|---|---|---|---|---|
| `origin/master` | `472b7f5` 2026-09-11 23:25:00 UTC (09-12 08:25:00 KST) | 0.8시간 | — | — |
| `origin/laptop-20260822` | `408c09f` 2026-09-11 21:32:09 UTC (09-12 06:32:09 KST) | 2.6시간 | **62커밋** | 32커밋 |
| `origin/junseok-20260822` | `41fb1b7` 2026-08-28 15:54:23 UTC (2026-08-29 00:54:23 KST) | **344.3시간(14.34일)** | **885커밋** | 0커밋 |

**경고: `laptop-20260822`가 master 대비 62커밋 뒤처짐** — 08-24 사고 기준
(24커밋)의 2.6배. `git merge-base`는 `03d9ccc`로 정상 조상을 찾았고
(정상적인 분기, 강제 푸시 아님), 최근 커밋은 2.6시간 전으로 활발히
진행 중 — 계속 뒤처짐이 벌어지지 않는지 지켜볼 필요는 있지만 "죽었다"는
아니다.

**경고: `junseok-20260822`가 마지막 커밋 14.34일 경과, master 대비 885커밋
뒤처짐** — 08-24 사고 기준의 36.9배. 다만 `git merge-base`가
`41fb1b7`(junseok 자기 브랜치 끝점) 그 자체를 반환했고 "앞섬"이 0커밋이라,
이 브랜치의 내용은 전부 이미 `master`에 흡수돼 있다 — junseok이 08-29
"가지 취합 종결 확인(master md5 일치)"으로 스스로 접은 뒤 그 브랜치에
새 활동이 없는 것이지, master가 만들어낸 뒤처짐을 놓치고 있는 08-24 유형
사고는 아니다. 다만 **뒤처짐 수치 자체는 그대로 경고선을 넘는다** — 지시된
문턱(24커밋)을 그대로 적용해 경고로 남긴다.

### 2) 우편함 침묵

`--all`(모든 브랜치 통틀어 그 경로를 마지막으로 건드린 커밋) 기준, 기준
시각 2026-09-12 00:12 UTC:

| 파일 | 마지막 커밋(전체 브랜치) | 소속 브랜치 | 경과 | 참고: `master`만 보면 |
|---|---|---|---|---|
| `COMMS/desktop.md` | `6eb087c` 2026-09-10 08:22:35 UTC | master (외 다수) | 39.8시간(1.66일) | 동일 |
| `COMMS/laptop.md` | `6a934c0` 2026-09-10 07:43:27 UTC | **laptop-20260822 전용** | 40.5시간(1.69일) | `a30745b` 09-07, **4.93일** |
| `COMMS/laptop2.md` | `220a88c` 2026-09-11 16:40:53 UTC | **laptop2-20260825 전용** | 7.5시간(0.31일) | `558fff3` 09-10, **2.33일** |
| `COMMS/junseok.md` | `be2bede` 2026-08-29 02:32:05 UTC | master (외 다수) | **333.6시간(13.90일)** | 동일 |
| `COMMS/cloud4c.md` | `84cfdde` 2026-09-04 08:49:13 UTC | master (외 다수) | 183.4시간(7.64일) | 동일 |

계산 중이면 침묵이 정상일 수 있어 "죽었다"고 단정하지 않음. `desktop.md`·
`laptop2.md`는 하루 이내로 정상 범위. `laptop.md`(1.69일)는 계산 소요
시간을 감안하면 경고 아님이나, **`master`만 보면 4.93일 침묵으로 잘못
보인다** — 09-11 감사가 기록한 것과 같은 함정(각 기기가 자기 브랜치에
쓰고 아직 master에 병합 안 됨)이 계속되고 있다. `cloud4c`는 이미 은퇴된
임시 기기라 침묵이 예상된 상태(경고 아님). `junseok.md`(13.90일)는 1절의
`junseok-20260822` 정체(14.34일)와 같은 방향으로 겹치고, 위에서 확인했듯
자발적 종결 이후의 침묵이지 응답 없음이 아니다 — 그래도 "확인했고
문제없음"과 "확인 안 함"을 구별해야 하므로 경고로 남긴다.

### 3) 결과 JSON 무결성

`results_v3*.json`(9개), `v3_wc/`(2개), `v3_humid_wc/`(5개),
`v3_humid_wc_ens/`(2개, 지시 범위 밖이라 참고만), `v4_humid_wc/`(2개),
`v3_water_grid/`(4개), `v3_water_grid_cliff/`(2개) — 총 26개 JSON을 전부
파이썬 `json.load`로 파싱하고 `rows`(dict 형태) 또는 리스트 자체(list
형태)의 길이를 셌다.

**이상 없음** — 26개 전부 파싱 성공, 0행인 파일 없음(최소 1행: `results_v3_smoke.json`,
`humid_working_capacity_ext.json` 등 / 최대 31행: `results_v3.json`).

### 4) 출처 규약 위반

`v3_water_grid/`의 태그 파일 셋(`water_results_desktop4.json`,
`water_results_junseok.json`, `water_results_laptop.json`)을
`merge_water_batches.py`에 직접 넘겨 실행(글롭 아님 — 도구 자신의 경고대로
태그 없는 `water_results.json`은 제외).

**이상 없음** — 같은 (조성, RH)이 두 "태그" 파일에서 값까지 완전히 같게
중복된 사례는 없음. `saIm0875`(RH 0/25/50/90)가 `junseok`·`laptop` 두
태그 파일에 모두 있으나 **값이 서로 다르다**(예: RH0 1.2905 vs 1.3031,
0.32σ) — 도구가 정확히 이를 "교차 검증 쌍"으로 분리해 표시했고 4점 전부
0.03~0.75σ로 "일관" 판정. 이는 08-23 사고(값이 완전히 같은데 두 기기로
잘못 셈)와 다른, **진짜 독립 재현**이다.

참고로 `v3_water_grid/water_results.json`(태그 없음, `saIm0583` 4행)은
`water_results_desktop4.json`과 **값까지 완전히 동일**하고,
`v3_water_grid_cliff/water_results.json`도 `water_results_desktopcliff.json`과
완전히 동일하다 — 이는 08-23에 기록된 "러너가 태그 없는 사본도 같이 쓴다"는
알려진 동작이고, `merge_water_batches.py`의 `machine_of()`가 태그 없는
파일을 `SystemExit`으로 거부하도록 이미 막아 두어 도구를 통해 병합하는 한
이중 계수로 이어지지 않는다. `v3_water_grid_cliff/`에는 태그 파일이
`desktopcliff` 하나뿐이라 태그 파일 간 비교 대상 자체가 없음.

### 5) 사전 등록 관문 대비 기록

`v3_water_grid/`·`v3_water_grid_cliff/`의 태그 파일에서 조성별 RH0·RH90
`CO2_molkg`로 유지율(RH90/RH0×100)을 직접 재계산(`run_water.py:325`와 같은
식, `merge_water_batches.py`의 `retention()`으로 재현):

| 조성 | 출처 | RH0 CO2 | RH90 CO2 | 재계산 유지율 | 관문 재판정 | 저장소 기록 | 일치 |
|---|---|---|---|---|---|---|---|
| `saIm0583` | desktop4 | 1.3188 | 1.0010 | 75.90% | 조건부(50~80%) | `COMMS/desktop.md` 75.90% 조건부 | ✅ |
| `saIm0625` | laptop | 1.3804 | 0.9902 | 71.74% | 조건부 | `COMMS/laptop.md` 71.7% 조건부 | ✅ |
| `saIm0667` | laptop | 1.3682 | 1.0269 | 75.06% | 조건부 | `COMMS/desktop.md` 75.05~75.1% 조건부 | ✅ |
| `saIm0875` | junseok | 1.2905 | 0.9619 | 74.54% | 조건부 | `COMMS/junseok.md` 74.5% 조건부 | ✅ |
| `saIm0875` | laptop | 1.3031 | 0.9671 | 74.21% | 조건부 | `COMMS/laptop.md` 74.2% 조건부 | ✅ |
| `saIm0917` | desktopcliff | 1.3249 | 0.9725 | 73.41% | 조건부 | `COMMS/desktop.md` 73.41% 조건부 | ✅ |
| `saIm0958` | desktopcliff | 1.5205 | 1.0032 | 65.98% | 조건부 | `COMMS/desktop.md` 65.98% 조건부 | ✅ |

**이상 없음** — 7행(조성 6종 + `saIm0875` 두 기기) 전부 관문 재판정과
저장소에 적힌 기존 판정이 일치. 어긋난 곳 없음.

- **참고(지속 4일째, 새 경고 아님 — 09-09 감사부터 반복)**: 위 표의 모든
  행은 `v3_water_grid*/`에서 나왔고, 그 안의 RH>0 행 전부가 파일 자체에
  `"WARN_forcefield": "수소결합이 없는 물로 계산한 값(Hw→H_, 2026-09-05
  발견, 09-06 수정)"`을 달고 있다(직접 확인: `water_results_desktopcliff.json`
  등). 즉 이 표 전체가 `CLAUDE.md` §1이 "결함판"으로 지목한 **2026-09-06
  물 힘장 수정 이전** 값이다. 수정 힘장 계열 `v3w_water/`가 존재하지만
  이 감사 지시가 지정한 범위(`v3_water_grid*/`) 밖이라 위 표에는 넣지
  않았다. 관문 등급 자체(조건부)는 기존 기록과 일치하므로 "어긋남"으로
  적지 않되, **이 표의 절대 수치를 새 결론에 그대로 인용하지 말 것** —
  `v3w_water/`로 재계산된 일부 조성(`saIm0583` 등)은 더 높은 유지율을 낸
  바 있다(과거 감사 기록).

### 6) WC 자료 공백

`v3_wc/*.json`(건조)·`v3_humid_wc/*.json`+`v4_humid_wc/*.json`(습윤)의
모든 파일에서 `rows[].name`을 모아 조성 집합을 비교. `regen_energy_v3.py`를
모듈로 임포트해 실제 `NAMES`(건조·습윤·Q_st **셋 다** 있어야 포함,
08-27 수정)도 대조:

| 조성 | 건조 WC | 습윤 WC | `regen_energy_v3.py` NAMES 포함 |
|---|---|---|---|
| `base` | ✅ (`working_capacity.json`) | ✅ (`humid_working_capacity.json`) | ✅ |
| `mslm075` | ✅ | ✅ (`humid_working_capacity_mslm075.json`) | ✅ |
| `saIm025` | ✅ | ✅ (`humid_working_capacity_ext.json`) | ✅ |
| `saIm050` | ✅ | ✅ (`humid_working_capacity.json`) | ✅ |
| `saIm0583` | ✅ (`working_capacity_g0583.json`) | ✅ (`humid_working_capacity_g0583.json`) | ✅ |
| `saIm075` | ✅ | ✅ (`humid_working_capacity.json`) | ✅ |
| `saIm100` | ✅ | ✅ (`humid_working_capacity.json`) | ✅ |
| `saIm0625` | ❌ | ✅ (`humid_working_capacity_grid.json`) | ❌ (건조 없음) |
| `sa50nb50` | ❌ | ✅ (`v4_humid_wc/humid_working_capacity_v4m1.json`) | ❌ (건조 없음) |
| `ms50nb50` | ❌ | ✅ (`v4_humid_wc/humid_working_capacity_v4ext.json`) | ❌ (건조 없음) |
| `sa25nb75` | ❌ | ✅ (`v4_humid_wc/humid_working_capacity_v4ext.json`) | ❌ (건조 없음) |

**이상 없음** — 건조만 있고 습윤이 없는 조성은 없음(건조 7종 전부 습윤도
있음). 습윤만 있는 조성 4종(`saIm0625`·`sa50nb50`·`ms50nb50`·`sa25nb75`)이
있으나, `regen_energy_v3.py`의 `NAMES`는 08-27 수정 이후 "건조·습윤·Q_st
셋 다 있는 조성만" 교집합으로 걸러 실제로 이 4종을 **전부 정확히 제외**하고
있음을 모듈 임포트로 직접 확인했다(`NAMES = ['base', 'mslm075', 'saIm025',
'saIm050', 'saIm0583', 'saIm075', 'saIm100']`, 7종 = 건조∩습윤 그대로).
절반만 찬 행이 완성된 행처럼 나오는 사고는 현재 재현되지 않는다.

## 사람이 볼 것

1. `laptop-20260822`가 master 대비 **62커밋** 뒤처짐(활발히 진행 중, 08-24
   기준선의 2.6배) — 계속 벌어지는지만 지켜보면 됨.
2. `junseok-20260822`가 마지막 커밋 **14.34일** 경과·885커밋 뒤처짐이지만,
   그 내용은 이미 master에 전부 흡수돼 있음(08-29 자발적 종결) — 응답
   없음이 아니라 종료된 가지로 보임.
3. 5절 관문 판정은 저장소 기록과 전부 일치하나, 그 기반 자료
   (`v3_water_grid*/`)가 09-06 이전 결함 물 힘장 값이라는 점은 4일째
   지속되는 기존 경고(새로운 문제 아님) — `v3w_water/` 재계산 완료 전까지
   이 표의 절대 수치를 새 결론에 쓰지 말 것.

---

## 2026-09-11 00:11 UTC — 일일 감사

**실행 조건**: 클라우드 저장소 체크아웃만으로 확인. 로컬 프로세스·메모리·
미푸시 커밋은 볼 수 없음. 새 계산 없음(`regen_energy_v3.py`는 실행하지 않고
파이썬으로 모듈 임포트해 `NAMES`만 대조, `merge_water_batches.py`의
`machine_of()`는 같은 식을 손으로 재현해 태그 파일만 넘겨 확인). 아래 6개
점검 외 어떤 파일도 수정하지 않음.

**방법 메모 1(경고 아님, 검사기 함정 재현)**: 오늘도 컨테이너 체크아웃이
얕은 클론이었다(`git rev-parse --is-shallow-repository` → `true`). unshallow
전 `git rev-list --left-right --count origin/master...origin/junseok-20260822`는
52(뒤처짐)/409(앞섬)로 나왔고 `git merge-base`는 공통 조상을 못 찾아 rc=1을
반환했다 — 09-06~09-10 감사가 반복해서 기록한 것과 같은 착시. `git fetch
--unshallow` 후 재계산하니 **842(뒤처짐)/0(앞섬)**으로 정정됐다. 아래 1절
수치는 전부 unshallow 이후 값이다.

**방법 메모 2(신규 발견, 검사기 함정 후보)**: 2절 우편함 침묵을 처음에
`git log -1 -- 21_ZIF69_MTV/COMMS/<파일>` (현재 체크아웃, 즉 `origin/master`
기준)으로만 쟀더니 `laptop.md`는 `a30745b`(09-07 10:46 KST, 3.94일 경과),
`laptop2.md`는 `558fff3`(09-09 10:13 KST, 1.33일 경과)로 나왔다. 그런데
`git log -1 --all -- <같은 경로>`로 **모든 브랜치**를 보니 `laptop.md`는
`6a934c0`(09-10 16:43 KST, `origin/laptop-20260822`에만 존재, master엔 아직
미병합)로, `laptop2.md`는 `6d8ffee`(09-11 06:25 KST, `origin/laptop2-20260825`
에만 존재)로 갱신 시각이 각각 68시간·29시간 더 최근이었다. **`master`만 보고
침묵을 재면 아직 병합 안 된 기기 브랜치의 최신 활동을 놓쳐 실제보다 훨씬
오래 침묵한 것처럼 오판한다** — `COMMS.md` §2가 원래 "읽는 쪽이 모든 브랜치를
가져온다"고 규정한 이유와 정확히 같은 함정이다. 아래 2절은 `--all` 기준
(진짜 최신) 값을 쓰고, 참고로 `master`만의 값도 병기한다.

### 1) 브랜치 정체

`git fetch --all` + `git fetch --unshallow` 후 (기준 시각 2026-09-11
00:11 UTC = 09:11 KST):

| 브랜치 | 마지막 커밋 | 경과 | master 대비 뒤처짐 | master 대비 앞섬 |
|---|---|---|---|---|
| `origin/master` | `6056e0c` 2026-09-10 23:18:21 UTC (08:18:21 KST) | 0.8시간 | — | — |
| `origin/laptop-20260822` | `38dccc0` 2026-09-10 23:16:20 UTC (08:16:20 KST) | 0.9시간 | 19커밋 | 18커밋 |
| `origin/junseok-20260822` | `41fb1b7` 2026-08-28 15:54:23 UTC (2026-08-29 00:54:23 KST) | **320.2시간(13.34일)** | **842커밋** | 0커밋 |

**경고: `junseok-20260822`가 마지막 커밋 13.34일 경과, master 대비 842커밋
뒤처짐** — 08-24 사고 기준(24커밋)의 35.1배. 09-10 감사(12.34일/760커밋)
대비 정확히 하루 더 지났고 뒤처짐도 82커밋 늘었다. `laptop-20260822`는
master 대비 19커밋 뒤처짐·18커밋 앞섬 — 24커밋 경보선 아래, 경고 아님(최근
커밋 시각이 master와 2분 1초 차이로 활발히 동기화 중임을 확인).

(참고, 지시된 세 브랜치 밖) `git branch -r`에 `origin/junseok`(접미사 없음),
`origin/laptop2-20260825`, `origin/magi004-hkhome`, `origin/magi004-laptop`,
`origin/magi004-laptop2`도 존재하나 지시된 점검 대상이 아니라 표에 넣지
않았다.

### 2) 우편함 침묵

기준 시각 2026-09-11 00:11 UTC. `--all`(모든 브랜치 통틀어 그 경로를 마지막
으로 건드린 커밋) 기준:

| 파일 | 마지막 커밋(전체 브랜치) | 소속 브랜치 | 경과 | 참고: `master`만 보면 |
|---|---|---|---|---|
| `COMMS/desktop.md` | `6eb087c` 2026-09-10 08:22:35 UTC | master (외 2곳) | 15.8시간(0.66일) | 동일 |
| `COMMS/laptop.md` | `6a934c0` 2026-09-10 07:43:27 UTC | **laptop-20260822 전용** | 16.4시간(0.68일) | `a30745b` 09-07, **3.94일** |
| `COMMS/laptop2.md` | `6d8ffee` 2026-09-10 21:25:00 UTC | **laptop2-20260825 전용** | 2.7시간(0.11일) | `558fff3` 09-09, **1.33일** |
| `COMMS/junseok.md` | `be2bede` 2026-08-29 02:32:05 UTC | master (외 다수) | **309.6시간(12.90일)** | 동일 |
| `COMMS/cloud4c.md` | `84cfdde` 2026-09-04 08:49:13 UTC | master (외 다수) | 159.3시간(6.64일) | 동일 |

`COMMS/junseok.md` 침묵(12.90일)이 1절의 `junseok-20260822` 정체(13.34일)와
같은 방향으로 겹친다. "죽었다"고 단정하지 않되 경고로 유지 — 09-10 감사
(11.90일) 대비 정확히 하루 더 방치, 새 활동 없음. `cloud4c`는 이미 은퇴
처리된 임시 기기라 침묵이 예상된 상태(경고 아님). `desktop.md`·`laptop.md`·
`laptop2.md`는 진짜 최신 기준으로 모두 17시간 이내로, 계산 중이면 정상일 수
있는 범위(경고 아님) — **다만 `laptop.md`·`laptop2.md`는 방법 메모 2에서
보였듯 각 기기 자기 브랜치에서는 활발한데 아직 `master`에 병합되지 않아
`master`만 보면 각각 3.94일·1.33일 침묵한 것으로 잘못 보인다.**

### 3) 결과 JSON 무결성

`results_v3*.json`, `v3_wc/`, `v3_humid_wc/`, `v4_humid_wc/`,
`v3_water_grid*/` 아래 모든 `.json`(24개 파일)을 파이썬으로 파싱:
`results_v3.json`(31행)·`results_v3_smoke.json`(1)·`results_v3cliff.json`(2)·
`results_v3ens0583.json`(5)·`results_v3ens075.json`(5)·
`results_v3ens_mix10.json`(10)·`results_v3ens_nb050.json`(5)·
`results_v3grid.json`(4)·`results_v3pctl.json`(5)·
`v3_wc/working_capacity.json`(6)·`v3_wc/working_capacity_g0583.json`(1)·
`v3_humid_wc/humid_working_capacity.json`(4)·
`v3_humid_wc/humid_working_capacity_ext.json`(1)·
`v3_humid_wc/humid_working_capacity_g0583.json`(1)·
`v3_humid_wc/humid_working_capacity_grid.json`(1)·
`v3_humid_wc/humid_working_capacity_mslm075.json`(1)·
`v4_humid_wc/humid_working_capacity_v4ext.json`(2)·
`v4_humid_wc/humid_working_capacity_v4m1.json`(1)·
`v3_water_grid/water_results.json`(4)·
`v3_water_grid/water_results_desktop4.json`(4)·
`v3_water_grid/water_results_junseok.json`(4)·
`v3_water_grid/water_results_laptop.json`(12)·
`v3_water_grid_cliff/water_results.json`(4)·
`v3_water_grid_cliff/water_results_desktopcliff.json`(4).

이상 없음 — 24개 파일 전부 파싱 성공, 파싱 실패도 0행도 없음(어제 감사와
파일 구성·행수 전부 동일 — 그리드/절벽 계열에 새 완주가 없었다는 뜻).

### 4) 출처 규약 위반

`merge_water_batches.py`의 `machine_of()`(파일명이 `water_results_<기기>`
형식이 아니면 거부)를 그대로 재현해 `v3_water_grid/`의 태그 파일
3개(desktop4/laptop/junseok)와 `v3_water_grid_cliff/`의 태그 파일
1개(desktopcliff)를 (조성, RH)로 묶어 대조:

- `saIm0875`가 `water_results_laptop.json`과 `water_results_junseok.json`
  양쪽에 등장하지만 RH 0/0.25/0.5/0.9 네 점 모두 값이 다르다(예: RH0 CO2
  1.303150 대 1.290482, RH90 0.967070 대 0.961905 — 소수점 넷째 자리까지
  전부 불일치) → **중복이 아니라 실제 교차 검증**(다른 기기가 같은 조성을
  독립 계산).
- 각 디렉터리의 태그 없는 `water_results.json`은 같은 디렉터리의
  `desktop4.json`/`desktopcliff.json`과 바이트 단위로 완전히 동일하다
  (파이썬 `==` 비교 참) — 러너가 이어받기 상태 파일과 기기 태그 사본을 같이
  쓰는 정상 부산물이고, `machine_of()`가 이 파일명(접미사 없음)을 거부하므로
  병합 인자로 넘기면 즉시 걸러진다.
- 나머지 조성(`saIm0583`/`saIm0625`/`saIm0667`/`saIm0917`/`saIm0958`)은 각각
  1개 태그 파일에만 등장 — 단일 출처, 중복도 교차검증도 아님.

이상 없음 — 값이 완전히 같은 진짜 중복(이중 계수)은 없다. `saIm0875` 쌍은
값이 다른 정상 교차 검증이다(09-09·09-10 감사와 동일 결론, 새 파일 추가 없음).

### 5) 사전 등록 관문 대비 기록

`v3_water_grid*/`의 태그 파일에서 RH0·RH90 CO₂로 유지율(RH90/RH0)을 직접
재계산해 저장소 기록(`NEW_MACHINE_20260822.md` 67~72행)과 대조:

| 조성 | 출처 | RH0 CO2 | RH90 CO2 | 유지율(재계산) | 판정 | 저장소 기록 | 일치 |
|---|---|---|---|---|---|---|---|
| `saIm0583` | desktop4 | 1.3188 | 1.0010 | 75.90% | 조건부(50~80%) | 75.90 ± 1.99 pp | ✅ |
| `saIm0625` | laptop | 1.3804 | 0.9902 | 71.74% | 조건부 | 71.73 ± 1.76 pp | ✅ |
| `saIm0667` | laptop | 1.3682 | 1.0269 | 75.06% | 조건부 | 75.06 ± 3.28 pp | ✅ |
| `saIm0875` | junseok | 1.2905 | 0.9619 | 74.54% | 조건부 | 74.2 ± 3.9 pp | ✅ |
| `saIm0875` | laptop | 1.3031 | 0.9671 | 74.21% | 조건부 | 74.2 ± 3.9 pp | ✅ |
| `saIm0917` | desktopcliff | 1.3249 | 0.9725 | 73.41% | 조건부 | 73.41 ± 1.79 pp | ✅ |
| `saIm0958` | desktopcliff | 1.5205 | 1.0032 | 65.98% | 조건부 | 65.98 ± 2.13 pp | ✅ |

이상 없음 — 7개 행(조성 6종 + `saIm0875` 두 기기) 전부 관문(≥80% 유효/
50~80% 조건부/<50% 종료) 재계산 판정과 저장소 기록이 일치한다. 유효로
잘못 올렸거나 종료로 잘못 내린 곳은 없다. 값은 09-10 감사와 동일(그리드/
절벽 계열에 새 실현 없음).

**참고(새 경고 아님, 09-09 감사가 처음 올리고 오늘로 사흘째 미해결)**:
위 표는 이 감사 지시 범위(`v3_water_grid*/`, 2026-09-06 물 힘장 수정
**이전**의 결함판)만 다룬다. 수정 힘장 새 계열 `v3w_water/water_results.json`
을 오늘 다시 확인해도 `saIm0583`(RH90 CO2 1.1514) · `saIm0625`(1.1477) ·
`saIm0667`(1.0845) mol/kg으로 09-09·09-10과 값이 동일하고, 09-09 감사가
계산한 재등급(`saIm0583` 87.3%·`saIm0625` 82.0~83.1%로 조건부→유효,
`saIm0667`은 기기별 79.3~83.0%로 80% 문턱을 사이에 두고 갈림)을 공식
등급으로 반영한 문서는 여전히 없다(`grep -rl "조건부→유효\|재등급\|조건부에서
유효"` 결과 이 `audit.md` 자신 외 무매치, `CAND_VERDICT_20260908.md` 재확인).
**`v3w_water/`는 이 감사 지시 범위 밖이라 위 표에는 넣지 않지만, 관문 등급
자체가 아직 안 갱신됐다는 사실은 사흘째 이어진다.**

### 6) WC 자료 공백

`v3_wc/`(건조)·`v3_humid_wc/`+`v4_humid_wc/`(습윤) 각 JSON의 `rows[].name`
필드 대조:

| 구분 | 조성 |
|---|---|
| 건조·습윤 둘 다 있음(7종) | `base, mslm075, saIm025, saIm050, saIm0583, saIm075, saIm100` |
| 습윤만 있음(4종) | `saIm0625, ms50nb50, sa25nb75, sa50nb50` |
| 건조만 있음 | 없음 |

`regen_energy_v3.py`를 실행하지 않고 모듈로 임포트해 `NAMES`를 확인하니
`['base', 'mslm075', 'saIm025', 'saIm050', 'saIm0583', 'saIm075', 'saIm100']`
로, 습윤만 있는 4종은 이미 자동으로 제외돼 있다(08-27 수정 필터, 09-09·
09-10 감사와 동일 결과).

이상 없음 — 한쪽만 있는 조성(4종)이 실재하지만 기존 필터가 걸러내고 있어
"절반만 찬 행이 완성된 행처럼 보이는" 위험은 현재 코드 경로에서 발생하지
않는다.

## 사람이 볼 것

- **경고**: `junseok-20260822` 13.34일/842커밋 정체 + `COMMS/junseok.md`
  12.90일 침묵 — 09-10 대비 정확히 하루 더 방치, 계속 심화 중(1절·2절)
- **방법론(신규)**: `master`만으로 우편함 침묵을 재면 `laptop.md`·`laptop2.md`
  가 각각 3.94일·1.33일 침묵한 것으로 오판된다 — 실제(모든 브랜치 기준)는
  16.4시간·2.7시간이다. 각 기기 브랜치가 아직 master에 안 병합됐을 뿐 죽은
  것이 아니다(2절)
- **참고(지속 사흘째, 새 경고 아님)**: `v3w_water/`(수정 힘장) 재계산으로
  `saIm0583`·`saIm0625`는 조건부→유효 상당, `saIm0667`은 기기별로 80% 문턱을
  사이에 두고 갈리는데, 이 재등급을 공식화한 문서가 여전히 없음(5절)
- 나머지(JSON 무결성·출처 중복·WC 공백)는 전부 이상 없음, 09-10과 동일

---

## 2026-09-10 00:12 UTC — 일일 감사

**실행 조건**: 클라우드 저장소 체크아웃만으로 확인. 로컬 프로세스·메모리·
미푸시 커밋은 볼 수 없음. 새 계산 없음(`regen_energy_v3.py`는 실행하지 않고
파이썬으로 모듈 임포트해 `NAMES`만 대조, `merge_water_batches.py`의
`machine_of()`는 같은 식을 손으로 재현해 태그 파일만 넘겨 확인). 아래 6개
점검 외 어떤 파일도 수정하지 않음.

**방법 메모(경고 아님, 검사기 함정 재현)**: 이번에도 컨테이너 체크아웃이
얕은 클론이었다(`git rev-parse --is-shallow-repository` → `true`). unshallow
전 `git rev-list --left-right --count origin/master...origin/junseok-20260822`는
193(뒤처짐)/409(앞섬)로 나왔고, `git merge-base`는 공통 조상을 찾지 못해
rc=1을 반환해 `junseok-20260822`가 마치 master와 이력을 공유하지 않는 별개
가지처럼 보였다(실제로는 얕은 클론 경계가 만든 착시). `git fetch --unshallow`
후 재계산하니 760(뒤처짐)/0(앞섬)으로 정정됐다 — 09-06~09-09 감사가 이미
기록한 것과 같은 함정이고, 이번에는 merge-base 자체가 못 찾는 형태로
나타나 조금 더 극단적이었다. 아래 모든 수치는 unshallow 이후 값이다.

### 1) 브랜치 정체

`git fetch --all` + `git fetch --unshallow` 후 (기준 시각 2026-09-10
00:12 UTC = 09:12 KST):

| 브랜치 | 마지막 커밋 | 경과 | master 대비 뒤처짐 | master 대비 앞섬 |
|---|---|---|---|---|
| `origin/master` | `c0f801b` 2026-09-10 08:51:11 KST | 0.3시간 | — | — |
| `origin/laptop-20260822` | `5ee6793` 2026-09-10 08:51:02 KST | 0.3시간 | 12커밋 | 13커밋 |
| `origin/junseok-20260822` | `41fb1b7` 2026-08-29 00:54:23 KST | **296.3시간(12.34일)** | **760커밋** | 0커밋 |

**경고: `junseok-20260822`가 마지막 커밋 12.34일 경과, master 대비
760커밋 뒤처짐** — 08-24 사고 기준(24커밋)의 31.7배. 09-09 감사
(11.34일/691커밋) 대비 정확히 하루 더 지났고 뒤처짐도 69커밋 늘었다.
`laptop-20260822`는 master 대비 12커밋 뒤처짐·13커밋 앞섬 — 24커밋
경보선 아래, 경고 아님(어제는 21커밋 뒤처짐·0커밋 앞섬이었는데, 오늘
`laptop-20260822`에 병합 커밋을 포함한 자체 작업 13건이 새로 쌓이고
master도 그만큼 전진해 발산 폭이 재조정됐다 — 최근 커밋 시각이 master와
9초 차이로 활발히 동기화 중임을 확인).

(참고, 지시된 세 브랜치 밖) `git branch -r`에 `origin/junseok`(접미사
없음)과 `origin/laptop2-20260825`도 존재하나 지시된 점검 대상이 아니라
표에 넣지 않았다.

### 2) 우편함 침묵

| 파일 | 마지막 커밋 | 경과 |
|---|---|---|
| `COMMS/desktop.md` | `fc86a75` 2026-09-09 11:19:32 KST | 21.9시간(0.91일) |
| `COMMS/laptop.md` | `a30745b` 2026-09-07 10:46:36 KST | 70.4시간(2.93일) |
| `COMMS/junseok.md` | `be2bede` 2026-08-29 11:32:05 KST | **285.6시간(11.90일)** |
| `COMMS/laptop2.md` | `558fff3` 2026-09-10 01:13:30 KST | 8.0시간(0.33일) |
| `COMMS/cloud4c.md` | `84cfdde` 2026-09-04 17:49:13 KST | 135.4시간(5.64일) |

`COMMS/junseok.md` 침묵(11.90일)이 1절의 `junseok-20260822` 정체(12.34일)와
같은 방향으로 겹친다 — 09-09 감사(10.90일) 대비 정확히 하루 더 방치, 새
활동 없음. "죽었다"고 단정하지 않되 경고로 유지. `cloud4c`는 이미 은퇴
처리된 임시 기기라 침묵이 예상된 상태(경고 아님). `desktop.md`·`laptop.md`·
`laptop2.md`는 모두 3일 이내로, 계산 중이면 정상일 수 있는 범위(경고 아님).

### 3) 결과 JSON 무결성

`results_v3*.json`, `v3_wc/`, `v3_humid_wc/`, `v4_humid_wc/`,
`v3_water_grid*/` 아래 모든 `.json`(24개 파일)을 파이썬으로 파싱:
`results_v3.json`(31행)·`results_v3_smoke.json`(1)·`results_v3cliff.json`(2)·
`results_v3ens0583.json`(5)·`results_v3ens075.json`(5)·
`results_v3ens_mix10.json`(10)·`results_v3ens_nb050.json`(5)·
`results_v3grid.json`(4)·`results_v3pctl.json`(5)·
`v3_wc/working_capacity.json`(6)·`v3_wc/working_capacity_g0583.json`(1)·
`v3_humid_wc/humid_working_capacity.json`(4)·
`v3_humid_wc/humid_working_capacity_ext.json`(1)·
`v3_humid_wc/humid_working_capacity_g0583.json`(1)·
`v3_humid_wc/humid_working_capacity_grid.json`(1)·
`v3_humid_wc/humid_working_capacity_mslm075.json`(1)·
`v4_humid_wc/humid_working_capacity_v4ext.json`(2)·
`v4_humid_wc/humid_working_capacity_v4m1.json`(1)·
`v3_water_grid/water_results.json`(4)·
`v3_water_grid/water_results_desktop4.json`(4)·
`v3_water_grid/water_results_junseok.json`(4)·
`v3_water_grid/water_results_laptop.json`(12)·
`v3_water_grid_cliff/water_results.json`(4)·
`v3_water_grid_cliff/water_results_desktopcliff.json`(4).

이상 없음 — 24개 파일 전부 파싱 성공, 파싱 실패도 0행도 없음(어제 감사와
파일 구성·행수 전부 동일).

### 4) 출처 규약 위반

`merge_water_batches.py`의 `machine_of()`(파일명이 `water_results_<기기>`
형식이 아니면 `None` 반환)를 그대로 재현해 `v3_water_grid/`의 태그 파일
3개(desktop4/laptop/junseok)와 `v3_water_grid_cliff/`의 태그 파일
1개(desktopcliff)를 (조성, RH)로 묶어 대조:

- `saIm0875`가 `water_results_laptop.json`과 `water_results_junseok.json`
  양쪽에 등장하지만 RH 0/0.25/0.5/0.9 네 점 모두 값이 다르다(예: RH0
  CO2 1.303150 대 1.290482, RH90 0.967070 대 0.961905 — 소수점 넷째
  자리까지 전부 불일치) → **중복이 아니라 실제 교차 검증**(다른 기기가
  같은 조성을 독립 계산).
- 각 디렉터리의 태그 없는 `water_results.json`은 같은 디렉터리의
  `desktop4.json`/`desktopcliff.json`과 바이트 단위로 완전히 동일하다
  (`diff -q` 무출력) — 러너가 이어받기 상태 파일과 기기 태그 사본을 같이
  쓰는 정상 부산물이고, `machine_of()`가 이 파일명(접미사 없음)을
  거부하므로 병합 인자로 넘기면 즉시 걸러진다.
- 나머지 조성(`saIm0583`/`saIm0625`/`saIm0667`/`saIm0917`/`saIm0958`)은
  각각 1개 태그 파일에만 등장 — 단일 출처, 중복도 교차검증도 아님.

이상 없음 — 값이 완전히 같은 진짜 중복(이중 계수)은 없다. `saIm0875` 쌍은
값이 다른 정상 교차 검증이다(어제 감사와 동일 결론, 새 파일 추가 없음).

### 5) 사전 등록 관문 대비 기록

`v3_water_grid*/`의 태그 파일에서 RH0·RH90 CO₂로 유지율(RH90/RH0)을
직접 재계산해 저장소 기록(`NEW_MACHINE_20260822.md`)과 대조:

| 조성 | 출처 | RH0 CO2 | RH90 CO2 | 유지율(재계산) | 판정 | 저장소 기록 | 일치 |
|---|---|---|---|---|---|---|---|
| `saIm0583` | desktop4 | 1.3188 | 1.0010 | 75.90% | 조건부(50~80%) | 75.90 ± 1.99 pp, 조건부 | ✅ |
| `saIm0625` | laptop | 1.3804 | 0.9902 | 71.74% | 조건부 | 71.73 ± 1.76 pp, 조건부 | ✅ |
| `saIm0667` | laptop | 1.3682 | 1.0269 | 75.06% | 조건부 | 75.06 ± 3.28 pp, 조건부 | ✅ |
| `saIm0875` | junseok | 1.2905 | 0.9619 | 74.54% | 조건부 | 74.2 ± 3.9 pp, 조건부 | ✅ |
| `saIm0875` | laptop | 1.3031 | 0.9671 | 74.21% | 조건부 | 74.2 ± 3.9 pp, 조건부 | ✅ |
| `saIm0917` | desktopcliff | 1.3249 | 0.9725 | 73.41% | 조건부 | 73.41 ± 1.79 pp, 조건부 | ✅ |
| `saIm0958` | desktopcliff | 1.5205 | 1.0032 | 65.98% | 조건부 | 65.98 ± 2.13 pp, 조건부 | ✅ |

이상 없음 — 7개 행(조성 6종 + `saIm0875` 두 기기) 전부 관문(≥80% 유효/
50~80% 조건부/<50% 종료) 재계산 판정과 저장소 기록이 일치한다. 유효로
잘못 올렸거나 종료로 잘못 내린 곳은 없다. 값은 어제 감사와 동일(새로
갱신된 실현 없음).

**참고(새 경고 아님, 09-09 감사가 이미 올린 항목의 지속 확인)**:
09-09 감사가 `v3w_water/`(2026-09-06 물 힘장 수정 이후 새 계열)로
`saIm0583`·`saIm0625`·`saIm0667` 세 조성의 유지율을 재계산해 각각
87.31%·83.14%(desktop)/82.02%(hkhome)·79.27%(desktop)/83.04%(hkhome)를
얻었고, 앞 두 조성은 조건부→유효로, `saIm0667`은 기기 간 80% 문턱을
사이에 두고 갈린다고 기록했다. 오늘 `v3w_water/water_results.json`을
다시 확인하니 세 조성의 RH90 값이 어제와 동일(`saIm0583` 1.1514,
`saIm0625` 1.1477, `saIm0667` 1.0845 mol/kg)하고, 저장소 어디에도 이
세 조성의 관문 등급을 공식으로 "조건부"에서 "유효"로 갱신한 문서는 여전히
없다(`CAND_VERDICT_20260908.md` 재확인, `grep -l "조건부→유효\|재등급"`
전체 `.md` 무매치). **`v3w_water/`는 이 감사 지시가 지정한 범위
(`v3_water_grid*/`) 밖이라 5절 표에는 넣지 않았지만, 관문 등급 자체가
아직 안 갱신됐다는 사실은 하루 더 이어진다.**

### 6) WC 자료 공백

`v3_wc/`(건조)·`v3_humid_wc/`+`v4_humid_wc/`(습윤) 각 JSON의 `rows[].name`
필드 대조:

건조·습윤 둘 다 있는 조성(7종): `base, saIm025, saIm050, saIm075, saIm100,
mslm075, saIm0583`. 습윤만 있는 조성(4종): `saIm0625, ms50nb50, sa25nb75,
sa50nb50`. 건조만 있는 조성: 없음(어제와 동일).

`regen_energy_v3.py`를 실행하지 않고 모듈로 임포트해 `NAMES`를 확인하니
`['base', 'mslm075', 'saIm025', 'saIm050', 'saIm0583', 'saIm075', 'saIm100']`
로, 습윤만 있는 4종은 이미 자동으로 제외돼 있다(08-27 수정 필터,
어제와 동일 결과).

이상 없음 — 한쪽만 있는 조성(4종)이 실재하지만 기존 필터가 걸러내고
있어 "절반만 찬 행이 완성된 행처럼 보이는" 위험은 현재 코드 경로에서
발생하지 않는다.

## 사람이 볼 것

- **경고**: `junseok-20260822` 12.34일/760커밋 정체 + `COMMS/junseok.md`
  11.90일 침묵 — 09-09 대비 정확히 하루 더 방치, 계속 심화 중(1절·2절)
- **참고(지속, 새 경고 아님)**: `v3w_water/`(수정 힘장) 재계산으로
  `saIm0583`(87.3%)·`saIm0625`(82.0~83.1%)는 조건부→유효 상당, `saIm0667`은
  기기별로 80% 문턱을 사이에 두고 갈리는데, 이 재등급을 공식화한 문서가
  아직 없음(5절 — 09-09 감사가 처음 올렸고 오늘도 미해결)
- 나머지(JSON 무결성·출처 중복·WC 공백)는 전부 이상 없음, 어제와 동일

---

## 2026-09-09 00:12 UTC — 일일 감사

**실행 조건**: 클라우드 저장소 체크아웃만으로 확인. 로컬 프로세스·메모리·
미푸시 커밋은 볼 수 없음. 새 계산 없음. 아래 6개 점검 외 어떤 파일도
수정하지 않음.

**방법 메모(경고 아님, 검사기 함정 재현)**: 이번에도 컨테이너 체크아웃이
얕은 클론이었다(`git rev-parse --is-shallow-repository` → `true`,
`git merge-base origin/master origin/junseok-20260822` → 공통 조상을
못 찾고 rc=1). 이번에는 브랜치 rev-list뿐 아니라 **우편함 파일의
`git log -- <path>`도 같이 오염됐다** — unshallow 전에는 `cloud4c.md`·
`junseok.md`·`laptop.md` 세 파일 전부 "마지막 커밋 2026-09-07 15:32:34"로
나왔는데, 이는 실제로 그 세 파일을 건드리지 않은 병합 커밋이 얕은 클론의
경계에서 "이 파일들을 마지막으로 스친 커밋"처럼 잘못 보고된 것이었다.
`git fetch --unshallow` 후 재확인하니 `cloud4c.md`(09-04 17:49)·
`junseok.md`(08-29 11:32)·`laptop.md`(09-07 10:46)로 각각 갈라졌고, 이
값들이 09-07·09-08 감사가 보고한 값과 정확히 일치한다(재현 확인).
**교훈**: 브랜치 divergence뿐 아니라 경로별 `git log`도 unshallow 이후에만
믿을 것 — 이 저장소의 검사기 함정 목록에 추가할 만하다. 아래 수치는 전부
unshallow 이후 값이다.

### 1) 브랜치 정체

`git fetch --all` + `git fetch --unshallow` 후 (기준 시각 2026-09-09
00:12 UTC = 09:12 KST):

| 브랜치 | 마지막 커밋 | 경과 | master 대비 뒤처짐 | master 대비 앞섬 |
|---|---|---|---|---|
| `origin/master` | `925a033` 2026-09-08 17:00:51 KST | 16.2시간 | — | — |
| `origin/laptop-20260822` | `f20b806` 2026-09-08 11:58:37 KST | 21.2시간 | 21커밋 | 0커밋 |
| `origin/junseok-20260822` | `41fb1b7` 2026-08-29 00:54:23 KST | **272.3시간(11.34일)** | **691커밋** | 0커밋 |

**경고: `junseok-20260822`가 마지막 커밋 11.34일 경과, master 대비
691커밋 뒤처짐** — 08-24 사고 기준(24커밋)의 28.8배. 09-08 감사
(10.35일/641커밋) 대비 정확히 하루 더 지났고 뒤처짐도 50커밋 늘었다.
`laptop-20260822`는 master 대비 21커밋 뒤처짐·0커밋 앞섬 — 24커밋
경보선 아래(어제는 3커밋 뒤처짐·1커밋 앞섬이었는데, 그 1커밋이 master로
합류되며 앞섬이 0으로 줄고 master가 그만큼 더 전진해 뒤처짐이 늘었다) —
경고 아님.

(참고, 지시된 세 브랜치 밖) `origin/junseok`(접미사 없음)은 644커밋
뒤처짐·0커밋 앞섬, 마지막 커밋 08-29 11:32 KST(10.90일)로 `junseok-20260822`와
같은 방향으로 정체돼 있다. `origin/laptop2-20260825`는 32커밋 뒤처짐·
0커밋 앞섬, 마지막 커밋 09-08 11:54 KST(21.3시간)로 최근성은 정상이지만
24커밋 선은 넘었다 — 지시된 세 브랜치가 아니라 표에는 넣지 않았고
경고로 세지 않는다.

### 2) 우편함 침묵

| 파일 | 마지막 커밋 | 경과 |
|---|---|---|
| `COMMS/desktop.md` | 2026-09-07 15:37:29 KST | 41.6시간(1.73일) |
| `COMMS/laptop.md` | 2026-09-07 10:46:36 KST | 46.4시간(1.93일) |
| `COMMS/junseok.md` | 2026-08-29 11:32:05 KST | **261.7시간(10.90일)** |
| `COMMS/laptop2.md` | 2026-09-08 11:51:06 KST | 21.3시간(0.88일) |
| `COMMS/cloud4c.md` | 2026-09-04 17:49:13 KST | 111.4시간(4.64일) |

`COMMS/junseok.md` 침묵(10.90일)이 1절의 `junseok-20260822` 정체(11.34일)와
같은 방향으로 겹친다 — "죽었다"고 단정하지 않되 경고로 유지(09-08 대비
정확히 하루 더 방치, 새로운 활동 없음). `cloud4c`는 이미 은퇴 처리된
임시 기기라 침묵이 예상된 상태(경고 아님). `desktop.md`·`laptop.md`·
`laptop2.md`는 모두 48시간 이내로 정상 범위(계산 중이면 침묵이 정상일 수
있어 이것만으로 "죽었다"고 하지 않음).

### 3) 결과 JSON 무결성

`results_v3*.json`, `v3_wc/`, `v3_humid_wc/`, `v4_humid_wc/`,
`v3_water_grid*/` 아래 모든 `.json`을 파이썬으로 파싱(23개 파일):
`results_v3.json`(31행)·`results_v3_smoke.json`(1)·`results_v3cliff.json`(2)·
`results_v3ens0583.json`(5)·`results_v3ens075.json`(5)·
`results_v3ens_mix10.json`(10)·`results_v3ens_nb050.json`(5)·
`results_v3grid.json`(4)·`results_v3pctl.json`(5)·
`v3_wc/working_capacity.json`(6)·`v3_wc/working_capacity_g0583.json`(1)·
`v3_humid_wc/*.json`(4개 파일, 각 4/1/1/1/1행)·
`v4_humid_wc/*.json`(2개 파일, 2/1행)·`v3_water_grid/water_results*.json`
(4개 파일, 4/4/4/12행)·`v3_water_grid_cliff/water_results*.json`
(2개 파일, 4/4행).

이상 없음 — 전부 파싱 성공, 파싱 실패도 0행도 없음(어제 감사와 파일
구성·행수 전부 동일).

### 4) 출처 규약 위반

`merge_water_batches.py`의 `machine_of()` 기준으로 `v3_water_grid/`의
태그 파일 3개(desktop4/laptop/junseok)와 `v3_water_grid_cliff/`의 태그
파일 1개(desktopcliff)를 서로 비교:

- `saIm0875`가 `water_results_laptop.json`과 `water_results_junseok.json`
  양쪽에 등장하지만 값이 다르다(RH0 1.303150 대 1.290482, RH25/50/90도
  전부 넷째 자리까지 다름) → **중복이 아니라 실제 교차 검증**(다른 기기가
  같은 조성을 독립 계산).
- 각 디렉터리의 태그 없는 `water_results.json`은 같은 디렉터리의
  `desktop4.json`/`desktopcliff.json`과 바이트 단위로 완전히 동일하다
  (`diff` 무출력) — 러너가 이어받기 상태 파일과 기기 태그 사본을 같이 쓰는
  정상 부산물이고, `machine_of()`가 이 파일명 형식(`water_results.json`,
  접미사 없음)을 거부하도록 되어 있어 병합 인자로 넘기면 즉시 중단된다.
- 나머지 조성(`saIm0583`/`saIm0625`/`saIm0667`/`saIm0917`/`saIm0958`)은
  각각 1개 태그 파일에만 등장 — 단일 출처.

이상 없음 — 값이 같은 진짜 중복은 없다. `saIm0875` 쌍은 값이 다른 정상
교차 검증이다(어제 감사와 동일한 결론, 새 파일 추가 없음).

### 5) 사전 등록 관문 대비 기록

옛 계열(`v3_water_grid*/`, 태그 파일)에서 RH0·RH90 CO₂로 유지율을 직접
재계산해 저장소 기록과 대조:

| 조성 | 출처 | RH0 CO2 | RH90 CO2 | 유지율(재계산) | 판정 | 저장소 기록 | 일치 |
|---|---|---|---|---|---|---|---|
| `saIm0583` | desktop4 | 1.3188 | 1.0010 | 75.90% | 조건부 | `NEW_MACHINE_20260822.md` 75.90% 조건부 | ✅ |
| `saIm0625` | laptop | 1.3804 | 0.9902 | 71.74% | 조건부 | `NEW_MACHINE_20260822.md` 71.73% 조건부 | ✅ |
| `saIm0667` | laptop | 1.3682 | 1.0269 | 75.06% | 조건부 | `NEW_MACHINE_20260822.md` 75.06% 조건부 | ✅ |
| `saIm0875` | 랩탑/junseok | 1.3031 / 1.2905 | 0.9671 / 0.9619 | 74.21% / 74.54% | 조건부(양쪽) | `NEW_MACHINE_20260822.md` 74.2% 조건부 | ✅ |
| `saIm0917` | desktopcliff | 1.3249 | 0.9725 | 73.41% | 조건부 | `NEW_MACHINE_20260822.md` 73.41% 조건부 | ✅ |
| `saIm0958` | desktopcliff | 1.5205 | 1.0032 | 65.98% | 조건부 | `NEW_MACHINE_20260822.md` 65.98% 조건부 | ✅ |

이 옛 계열 여섯 칸 자체는 이상 없음 — 값이 어제와 동일하고, 재계산과
기록이 일치한다.

**경고(새로 발견, 어제 감사가 "아직 안 채워짐"이라 넘긴 부분이 오늘
채워짐)**: `v3w_water/`(2026-09-06 물 힘장 수정 이후 새 계열)에 위 여섯
조성 중 세 개(`saIm0583`·`saIm0625`·`saIm0667`)가 이제 RH90 값을 갖고
있다(`CAND_VERDICT_20260908.md` §4, 09-08 12:12 재착수·완주). RH0는
힘장 수정과 무관(물 분자 0)해 옛 값을 분모로 그대로 쓸 수 있다
(`WATER_FIX_20260906.md` §2 "RH0 행 무관 — 옛 값 재사용"). 이 분모로
새 유지율을 재계산하면:

| 조성 | 새 RH90 CO2(출처) | 옛 RH0 CO2 | 새 유지율 | 옛 유지율(조건부 판정) | 새 판정 |
|---|---|---|---|---|---|
| `saIm0583` | 1.1514±0.0245(desktop, `v3w_water/water_results.json`) | 1.3188 | **87.31%** | 75.90% | **유효(≥80%)** |
| `saIm0625` | 1.1477±0.0328(desktop) / 1.1322±0.0126(hkhome) | 1.3804 | **83.14% / 82.02%** | 71.74% | **유효(≥80%), 두 기기 일치** |
| `saIm0667` | 1.0845±0.0417(desktop) / 1.1361±0.0094(hkhome) | 1.3682 | **79.27% / 83.04%** | 75.06% | **desktop=조건부, hkhome=유효 — 두 기기가 80% 문턱을 사이에 두고 갈린다** |

세 조성 전부 옛(결함) 힘장 값보다 유지율이 높게 나왔고(치환기 자리가
물을 과흡착하던 결함이 고쳐졌기 때문 — `WATER_FIX_20260906.md` §5 "결함
힘장이 가짜 신호를 만들고 있었다"와 방향이 일치), `saIm0583`·`saIm0625`는
새 계열에서 조건부→유효로 등급이 바뀐다. `saIm0667`은 desktop(79.27%,
조건부)과 hkhome(83.04%, 유효)이 80% 문턱을 사이에 두고 갈려 아직
해소되지 않았다. 세 값 모두 CAND_VERDICT_20260908.md §1이 "물 미평형
상한"·"조각 1"로 표기한 값이고(§4 "셋이 같은 씨앗(1788750777)이라
분산 논거에는 안 씀"), 현재 저장소 어디에도 이 세 조성의 관문 등급을
"조건부"에서 "유효"로 공식 갱신한 문서가 없다(위 표는 이 감사가 직접
재계산한 것). `saIm0875`·`saIm0917`·`saIm0958` 세 조성은 `v3w_water/`에
아직 RH90 값이 없다.

### 6) WC 자료 공백

`v3_wc/`(건조)·`v3_humid_wc/`+`v4_humid_wc/`(습윤) 각 JSON의 `rows[].name`
필드 대조:

건조·습윤 둘 다 있는 조성(7종): `base, saIm025, saIm050, saIm075, saIm100,
mslm075, saIm0583`. 습윤만 있는 조성(4종): `saIm0625, ms50nb50, sa25nb75,
sa50nb50`. 건조만 있는 조성: 없음(어제와 동일).

`regen_energy_v3.py`를 실행하지 않고 모듈로 임포트해 `NAMES`를 확인하니
`['base', 'mslm075', 'saIm025', 'saIm050', 'saIm0583', 'saIm075', 'saIm100']`
로, 습윤만 있는 4종은 이미 자동으로 제외돼 있다(08-27 수정 필터,
어제와 동일 결과).

이상 없음 — 한쪽만 있는 조성(4종)이 실재하지만 기존 필터가 걸러내고
있어 "절반만 찬 행이 완성된 행처럼 보이는" 위험은 현재 코드 경로에서
발생하지 않는다.

## 사람이 볼 것

- **새 경고**: `v3w_water/`(수정 힘장) 새 값으로 `saIm0583`(87.3%)·
  `saIm0625`(82.0~83.1%)는 관문이 조건부→유효로 바뀌고, `saIm0667`은
  기기별로 80% 문턱을 사이에 두고 갈린다(desktop 79.3% 조건부 대 hkhome
  83.0% 유효) — 어디에도 공식 재등급 문서가 없다(5절)
- `junseok-20260822` 11.34일/691커밋 정체 + `COMMS/junseok.md` 10.90일
  침묵 — 09-08 대비 정확히 하루 더 방치, 계속 심화 중(1절·2절)
- 나머지(JSON 무결성·출처 중복·WC 공백)는 전부 이상 없음, 어제와 동일

---

## 2026-09-08 00:11 UTC — 일일 감사

**실행 조건**: 클라우드 저장소 체크아웃만으로 확인. 로컬 프로세스·메모리·
미푸시 커밋은 볼 수 없음. 새 계산 없음(`regen_energy_v3.py`는 실행하지
않고 파이썬으로 모듈 임포트해 `load_wc()`/`QST`/`NAMES`를 그대로 대조).
`merge_water_batches.py`는 기존 도구에 태그 붙은 파일만 넘겨 그대로
호출함(⑥-(가), 손으로 다시 짜지 않음). 아래 6개 점검 외 어떤 파일도
수정하지 않음.

**방법 메모(경고 아님, 검사기 함정 기록)**: 컨테이너 체크아웃이 얕은
클론이었다(depth 50, `git rev-parse --is-shallow-repository` → `true`).
unshallow 전 `git merge-base origin/master origin/junseok-20260822`는
공통 조상을 못 찾았고(rc=1), `rev-list --left-right`는 83/409로 나와
정체된 가지가 최근 대량 작업을 한 것처럼 보였다 — 09-06·09-07 감사가
이미 기록한 것과 같은 얕은-클론 함정이다. `git fetch --unshallow`로
전체 이력(83→1050커밋)을 받은 뒤 재계산하니 641/0(순수 뒤처짐)으로
정정됐다. 아래 모든 수치는 unshallow 이후 값이다.

### 1) 브랜치 정체

`git fetch --all` + `git fetch --unshallow` 후 (기준 시각 2026-09-08
00:11 UTC = 09:11 KST):

| 브랜치 | 마지막 커밋 | 경과 | master 대비 뒤처짐 | master 대비 앞섬 |
|---|---|---|---|---|
| `origin/master` | `987df2c` 2026-09-08 08:14:39 KST | 0.9시간 | — | — |
| `origin/laptop-20260822` | `3ad850b` 2026-09-08 01:39:57 KST | 7.5시간 | 3커밋 | 1커밋 |
| `origin/junseok-20260822` | `41fb1b7` 2026-08-29 00:54:23 KST | **248.3시간(10.35일)** | **641커밋** | 0커밋 |

**경고: `junseok-20260822`가 마지막 커밋 10.35일 경과, master 대비
641커밋 뒤처짐** — 08-24 사고 기준(24커밋)의 26.7배. 09-07 감사
(9.3일/544커밋) 대비 정확히 하루 더 지났고 뒤처짐도 97커밋 늘었다
(master가 그 사이 다른 가지를 흡수하며 전진했기 때문 — `junseok-20260822`
자신의 앞섬은 09-07과 마찬가지로 계속 0커밋이라, 그 가지에 남아 있던
고유 작업은 이미 전부 master에 흡수돼 fast-forward로 합류 가능한
상태다). `laptop-20260822`는 master 대비 3커밋 뒤처짐·1커밋 앞섬 —
24커밋 경보선 아래라 경고 아님.

(참고, 지시된 세 브랜치 밖) `git branch -r`에 `origin/junseok`(접미사
없음, 594커밋 뒤처짐·0 앞섬, 마지막 커밋 08-29 11:32 KST)과
`origin/laptop2-20260825`(139커밋 뒤처짐·0 앞섬, 마지막 커밋 09-07
15:14 KST)도 존재한다. 둘 다 `CLAUDE.md`가 지정한 점검 대상 세 브랜치가
아니라 표에는 넣지 않았지만, `origin/junseok`도 유사하게 정체돼 있다는
점은 기록해 둔다.

### 2) 우편함 침묵

각 우편함을 master 기준으로 확인(경과 시간만 보고, 침묵을 "죽었다"로
단정하지 않음 — 기기가 계산 중이면 정상일 수 있음):

| 파일 | 마지막 커밋 | 경과 |
|---|---|---|
| `COMMS/desktop.md` | `9006fce` 2026-09-07 15:37:29 KST | 17.6시간(0.73일) |
| `COMMS/laptop.md` | `a30745b` 2026-09-07 10:46:36 KST | 22.4시간(0.93일) |
| `COMMS/junseok.md` | `be2bede` 2026-08-29 11:32:05 KST | **237.7시간(9.90일)** |
| `COMMS/laptop2.md` | `7dbe5b7` 2026-09-05 07:08:29 KST | 74.1시간(3.09일) |
| `COMMS/cloud4c.md` | `84cfdde` 2026-09-04 17:49:13 KST | 87.4시간(3.64일) |

`COMMS/junseok.md` 침묵(9.90일)이 1절의 `junseok-20260822` 정체(10.35일)와
같은 방향으로 겹친다 — 09-07 감사(8.9일) 대비 정확히 하루 늘어 새
활동이 없었다는 뜻으로 읽힌다. "죽었다"고 단정하지 않되 경고로 유지.
`cloud4c`는 registry상 "🔴 이 노선은 종료"로 이미 은퇴 처리된 임시
기기라 침묵이 예상된 상태(경고 아님). 나머지 두 우편함은 모두
24시간 이내 정상 범위.

### 3) 결과 JSON 무결성

`results_v3*.json`(dict, `rows` 키), `v3_wc/`, `v3_humid_wc/`,
`v4_humid_wc/`, `v3_water_grid*/` 아래 모든 `.json`을 파이썬으로 파싱
(dict면 `rows`/최상위 키 수, 순수 리스트면 원소 수를 행수로 셈):

| 파일 | 결과 | 행수 |
|---|---|---|
| `results_v3.json` | OK | 31 |
| `results_v3_smoke.json` | OK | 1 |
| `results_v3cliff.json` | OK | 2 |
| `results_v3ens0583.json` | OK | 5 |
| `results_v3ens075.json` | OK | 5 |
| `results_v3ens_mix10.json` | OK | 10 |
| `results_v3ens_nb050.json` | OK | 5 |
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

이상 없음 — 24개 파일 전부 파싱 성공, 파싱 실패도 0행도 없음.

### 4) 출처 규약 위반

`merge_water_batches.py`의 `machine_of()`는 `water_results_<기기>.json`
형식만 받는다. `v3_water_grid/`의 태그 파일 3개(desktop4/laptop/junseok)와
`v3_water_grid_cliff/`의 태그 파일 1개(desktopcliff)를 서로 비교:

- `v3_water_grid/`: `saIm0875` 조성이 `water_results_laptop.json`과
  `water_results_junseok.json` 양쪽에 등장. 값을 대조하면 RH0
  1.303150(laptop) vs 1.290482(junseok)로 시작해 RH25/50/90 전부
  소수점 넷째 자리까지 서로 다르다 → **같은 행의 이중 계수가 아니라
  실제 교차 검증**(다른 기기가 같은 조성을 독립 계산). 4점의 편차를
  `merge_water_batches.py`와 같은 식(`|Δ|/sqrt(e1²+e2²)`)으로 재계산하면
  0.03~0.75σ로 등록 문턱(2.0σ) 아래 — 일관.
- 각 디렉터리의 태그 없는 `water_results.json`은 같은 디렉터리의
  `desktop4.json`/`desktopcliff.json`과 내용이 바이트 단위로 완전히
  동일함을 확인했다(`diff` 무출력) — `v3_water_grid/README.md`가 이미
  설명하는 정상 부산물(러너가 이어받기 상태 파일과 기기 태그 사본을
  같이 쓴다)이고, `machine_of()`가 이 파일명 형식을 거부하도록 되어
  있어 병합 인자로 넘기면 즉시 중단된다. `v3_water_grid_cliff/`에는
  같은 취지의 README가 없다는 점만 사소한 격차로 적어 둔다(경고는
  아님 — 거부 로직 자체는 디렉터리와 무관하게 파일명만 본다).
- 그 외 조성(`saIm0583`/`saIm0625`/`saIm0667`/`saIm0917`/`saIm0958`)은
  각각 1개 태그 파일에만 등장 — 중복도 교차검증도 아닌 단일 출처.

이상 없음 — 값이 같은 진짜 중복(이중 계수)은 발견되지 않았다. `saIm0875`
쌍은 값이 서로 다른 정상적인 교차 검증이고 0.75σ 이내로 일관이다.

### 5) 사전 등록 관문 대비 기록

`merge_water_batches.py`(러너 `run_water.py:325`와 같은 유지율·σ 정의,
⑥-(가))를 태그 파일만 넘겨 그대로 실행해 재계산:

| 조성 | 출처 | RH0 CO2 | RH90 CO2 | 유지율(재계산) | 판정(재계산) | 저장소 기록 | 일치 |
|---|---|---|---|---|---|---|---|
| `saIm0583` | desktop4 | 1.3188±0.0264 | 1.0010±0.0170 | 75.9% | 조건부 | `COMMS/desktop.md` 75.90±1.99% 조건부 | ✅ |
| `saIm0625` | laptop | 1.3804±0.0135 | 0.9902±0.0223 | 71.7% | 조건부 | `COMMS/laptop.md` 71.7% 조건부 | ✅ |
| `saIm0667` | laptop | 1.3682±0.0301 | 1.0269±0.0387 | 75.1% | 조건부 | `COMMS/desktop.md` 75.05~75.1% 조건부 | ✅ |
| `saIm0875` | junseok*/laptop | 1.2905±0.0333 / 1.3031±0.0215 | 0.9619±0.0181 / 0.9671±0.0482 | 74.5% / 74.2% | 조건부(양쪽 다) | `COMMS/junseok.md`·`laptop.md` 74.5%·74.2% 조건부 | ✅ |
| `saIm0917` | desktopcliff | 1.3249±0.0258 | 0.9725±0.0143 | 73.4% | 조건부 | `COMMS/desktop.md` 73.41% 조건부 | ✅ |
| `saIm0958` | desktopcliff | 1.5205±0.0129 | 1.0032±0.0312 | 66.0% | 조건부 | `COMMS/desktop.md` 65.98% 조건부 | ✅ |

이상 없음 — 6개 조성 전부 관문(≥80% 유효/50~80% 조건부/<50% 종료)
재계산 판정과 저장소 기록이 일치한다. 전부 50~80% 조건부 구간이고,
유효로 잘못 올렸거나 종료로 잘못 내린 곳은 없다.

**주의(경고 아님, 인용 범위 표시)**: 이 6개 조성 값은 전부
2026-08-23~25에 산출됐다 — `CLAUDE.md` §1·`WATER_FIX_20260906.md`가
결함판으로 지목한 **2026-09-06 물 힘장 수정 이전** 값이다(당시
`Hw`가 UFF `H_`의 LJ를 물려받아 수분 친화도가 약 8.6배 과소). 이
값들과 저장소 기록이 "일치"한다는 것은 **그 시점 이후로 이 여섯 칸이
바뀌거나 흘러들지 않았다는 뜻**일 뿐, 현재 힘장으로 유효하다는
뜻이 아니다. `WATER_FIX_20260906.md` §3은 이 여섯 조성(및 그 이상)의
RH90 유지율 재계산을 이미 필수 항목으로 등록해 두었고, 새 계열
`v3w_water/`가 존재하지만 지금은 다른 조성(`saIm0583` 등 일부)만
채워져 있다 — 이 여섯 칸을 v3w 계열로 갱신하는 것은 이미 등록된
할 일이지 이번 감사가 새로 만드는 요구가 아니다.

### 6) WC 자료 공백

`v3_wc/`(건조), `v3_humid_wc/`+`v4_humid_wc/`(습윤) 각 JSON의 `rows[].name`
필드를 나열해 조성별 유무를 대조:

| 조성 | 건조 WC | 습윤 WC |
|---|---|---|
| `base` | ✅ | ✅ |
| `saIm025` | ✅ | ✅ |
| `saIm050` | ✅ | ✅ |
| `saIm075` | ✅ | ✅ |
| `saIm100` | ✅ | ✅ |
| `mslm075` | ✅ | ✅ |
| `saIm0583` | ✅ | ✅ |
| `saIm0625` | ❌ | ✅ |
| `ms50nb50` | ❌ | ✅ |
| `sa25nb75` | ❌ | ✅ |
| `sa50nb50` | ❌ | ✅ |

건조·습윤 둘 다 있는 조성(7종): `base, saIm025, saIm050, saIm075,
saIm100, mslm075, saIm0583`.
습윤만 있는 조성(4종): `saIm0625, ms50nb50, sa25nb75, sa50nb50`.
건조만 있는 조성: 없음.

`regen_energy_v3.py`를 실행하지 않고 모듈로 임포트해 실제 `NAMES`
(재생에너지 계산 대상 — `dry_tsa`/`dry_vsa`/`wet_tsa`/`wet_vsa`/`Qst`
5개 전부 있어야 포함됨, 2026-08-27 수정)를 확인하니
`['base', 'mslm075', 'saIm025', 'saIm050', 'saIm0583', 'saIm075', 'saIm100']`
로 나와, 습윤만 있는 4종(`saIm0625` 포함 — `saIm0625`는 `Qst`는
있지만 건조 WC가 없어 제외됨)은 이미 자동으로 제외돼 있었다.

이상 없음 — 건조·습윤 한쪽만 있는 조성(4종)이 실재하지만,
`regen_energy_v3.py`의 기존 필터(08-27 수정)가 이를 걸러내고 있어
"절반만 찬 행이 완성된 행처럼 보이는" 위험은 현재 코드 경로에서는
발생하지 않는다. 이 필터 로직이 바뀌면 재검사가 필요하다.

## 사람이 볼 것

- `junseok-20260822` 브랜치 10.35일/641커밋 정체 + `COMMS/junseok.md`
  9.90일 침묵 — 09-07 대비 정확히 하루 더 방치(경고, 지속 중, 매일 심화)
- 나머지 5개 항목(JSON 무결성·출처 중복·수분 관문·WC 공백·다른 브랜치)은
  전부 이상 없음. 다만 5절 수분 관문 여섯 칸은 09-06 물 힘장 수정 **이전**
  값이라 인용 시 그 사실을 병기할 것(새 경고 아님, 기존 등록 사항 재확인)

---

## 2026-09-07 00:12 UTC — 일일 감사

**실행 조건**: 클라우드 저장소 체크아웃만으로 확인. 로컬 프로세스·메모리·
미푸시 커밋은 볼 수 없음. 새 계산 없음(`regen_energy_v3.py`는 실행하지
않고 파이썬으로 모듈 임포트해 `load_wc()`/`QST`/`NAMES` 를 그대로 대조).
`merge_water_batches.py`는 기존 도구에 태그 붙은 파일만 넘겨 그대로
호출함(⑥-(가), 손으로 다시 짜지 않음 — 아래 5절 표가 그 실제 실행 결과).
아래 6개 점검 외 어떤 파일도 수정하지 않음.

**방법 메모(경고 아님, 검사기 함정 기록)**: 컨테이너 체크아웃이 얕은
클론이었다(`git rev-parse --is-shallow-repository` → `true`). unshallow
전에 잰 `git rev-list --left-right`로는 `junseok-20260822` 발산이
142(뒤처짐)/409(앞섬)로 나와 정체된 가지가 최근 대량으로 새 작업을 한
것처럼 보였다 — 09-06 감사가 이미 기록한 것과 같은 얕은-클론 함정이다.
`git fetch --unshallow`로 전체 이력(870→953커밋)을 받은 뒤 재계산하니
544/0(순수 뒤처짐, 앞섬 없음)으로 정정됐다. **같은 오염이 2절의
우편함 조회에도 번져 있었다** — unshallow 전 `git log -1 -- <path>`가
`desktop.md`·`junseok.md`·`laptop2.md`·`cloud4c.md` **네 파일 모두**를
동일한 커밋(2026-09-06 03:19:14 KST, "§8-3: 데스크탑 기기 축 첫 실측")이
마지막으로 고친 것처럼 가리켰다. 그대로 냈으면 "한 파일 한 필자" 위반
(한 커밋이 네 우편함을 동시에 고침)으로 오보할 뻔했다. unshallow 후
같은 조회를 다시 하니 네 파일 전부 서로 다른, 훨씬 이전의 실제 커밋을
가리켰고 규약 위반은 없었다 — **얕은 클론에서 병합 베이스·경로 이력
둘 다 틀어질 수 있다.** 아래 모든 수치는 unshallow 이후 값이다.

### 1) 브랜치 정체

`git fetch --all` + `git fetch --unshallow` 후 (기준 시각 2026-09-07
00:11 UTC = 09:11 KST):

| 브랜치 | 마지막 커밋 | 경과 | master 대비 뒤처짐 | master 대비 앞섬 |
|---|---|---|---|---|
| `origin/master` | `ab3e92d` 2026-09-07 08:50:48 KST | 0.3시간 | — | — |
| `origin/laptop-20260822` | `d5c9f63` 2026-09-07 06:51:04 KST | 2.3시간 | 6커밋 | 1커밋 |
| `origin/junseok-20260822` | `41fb1b7` 2026-08-29 00:54:23 KST | **224.3시간(9.3일)** | **544커밋** | 0커밋 |

**경고: `junseok-20260822`가 마지막 커밋 9.3일 경과, master 대비
544커밋 뒤처짐** — 08-24 사고 기준(24커밋)의 22.7배. 09-06 감사
(8.3일/461커밋) 대비 정확히 하루 더 지났고 뒤처짐도 83커밋 늘었다
(master가 그 사이 다른 가지를 흡수하며 전진했기 때문 — `junseok-20260822`
자신의 앞섬은 09-06과 마찬가지로 계속 0커밋이라, 그 가지에 남아 있던
고유 작업은 이미 전부 master에 흡수돼 fast-forward로 합류 가능한
상태다). `laptop-20260822`는 master 대비 6커밋 뒤처짐·1커밋 앞섬 —
24커밋 경보선 아래라 경고 아님(09-06 감사 때 0/0 완전 합류에서 하루치
정상 발산).

### 2) 우편함 침묵

각 우편함을 master 기준으로 확인(경과 시간만 보고, 침묵을 "죽었다"로
단정하지 않음 — 기기가 계산 중이면 정상일 수 있음):

| 파일 | 마지막 커밋 | 경과 |
|---|---|---|
| `COMMS/desktop.md` | `775309a` 2026-09-04 23:56:00 KST | 57.3시간(2.4일) |
| `COMMS/laptop.md` | `fdabdf1` 2026-09-06 06:36:42 KST | 26.6시간(1.1일) |
| `COMMS/junseok.md` | `be2bede` 2026-08-29 11:32:05 KST | **213.7시간(8.9일)** |
| `COMMS/laptop2.md` | `7dbe5b7` 2026-09-05 07:08:29 KST | 50.1시간(2.1일) |
| `COMMS/cloud4c.md` | `84cfdde` 2026-09-04 17:49:13 KST | 63.4시간(2.6일) |

`COMMS/junseok.md` 침묵(8.9일)이 1절의 `junseok-20260822` 정체(9.3일)와
같은 방향으로 겹친다 — 09-06 감사(7.9일) 대비 정확히 하루 늘어 새
활동이 없었다는 뜻으로 읽힌다. "죽었다"고 단정하지 않되 경고로 유지.
나머지 네 우편함은 모두 63.4시간(2.6일) 이내로 정상 범위.

### 3) 결과 JSON 무결성

`results_v3*.json`(dict, `rows` 키), `v3_wc/`, `v3_humid_wc/`,
`v4_humid_wc/`, `v3_water_grid*/` 아래 모든 `.json`을 파이썬으로 파싱
(dict면 `rows` 배열 길이, 순수 리스트면 원소 수를 행수로 셈):

| 파일 | 결과 | 행수 |
|---|---|---|
| `results_v3.json` | OK | 31 |
| `results_v3_smoke.json` | OK | 1 |
| `results_v3cliff.json` | OK | 2 |
| `results_v3ens0583.json` | OK | 5 |
| `results_v3ens075.json` | OK | 5 |
| `results_v3ens_mix10.json` | OK | 10 |
| `results_v3ens_nb050.json` | OK | 5 |
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

이상 없음 — 24개 파일 전부 파싱 성공, 파싱 실패도 0행도 없음.

### 4) 출처 규약 위반

`merge_water_batches.py`의 `machine_of()`는 `water_results_<기기>.json`
형식만 받는다. `v3_water_grid/`의 태그 파일 3개(desktop4/laptop/junseok)와
`v3_water_grid_cliff/`의 태그 파일 1개(desktopcliff)를 서로 비교:

- `v3_water_grid/`: `saIm0875` 조성이 `water_results_laptop.json`과
  `water_results_junseok.json` 양쪽에 등장. 값을 대조하면 RH0
  1.303150(laptop) vs 1.290482(junseok)로 시작해 RH25/50/90 전부
  소수점 넷째 자리까지 서로 다르다 → **같은 행의 이중 계수가 아니라
  실제 교차 검증**(다른 기기가 같은 조성을 독립 계산). `merge_water_batches.py`를
  이 두 파일로 그대로 실행해 재현한 편차는 4점 모두 0.03~0.75σ로
  등록 문턱(2.0σ) 아래 — 일관.
- 각 디렉터리의 태그 없는 `water_results.json`은 같은 디렉터리의
  `desktop4.json`/`desktopcliff.json`과 내용이 바이트 단위로 완전히
  동일함을 확인했다 — 도구 자체 문서가 설명하는 정상 부산물(러너가
  최근 실행 기기 몫을 태그 없는 사본으로도 쓴다)이고, `machine_of()`가
  이 파일명 형식을 거부하도록 되어 있어 병합 인자로 넘기면 즉시
  중단된다. 이번 점검에서도 태그 없는 파일은 병합 인자로 넘기지
  않았으므로 이중 계수 경로는 열리지 않았다.
- 그 외 조성(`saIm0583`/`saIm0625`/`saIm0667`/`saIm0917`/`saIm0958`)은
  각각 1개 태그 파일에만 등장 — 중복도 교차검증도 아닌 단일 출처.

이상 없음 — 값이 같은 진짜 중복(이중 계수)은 발견되지 않았다. `saIm0875`
쌍은 값이 서로 다른 정상적인 교차 검증이고 0.75σ 이내로 일관이다.

### 5) 사전 등록 관문 대비 기록

`merge_water_batches.py`(러너 `run_water.py:325`와 같은 유지율·σ 정의,
⑥-(가))를 태그 파일만 넘겨 그대로 실행해 재계산:

| 조성 | 출처 | RH0 CO2 | RH90 CO2 | 유지율(재계산) | 판정(재계산) | 저장소 기록 | 일치 |
|---|---|---|---|---|---|---|---|
| `saIm0583` | desktop4 | 1.3188±0.0264 | 1.0010±0.0170 | 75.9% | 조건부 | `COMMS/desktop.md` 75.90±1.99% 조건부 | ✅ |
| `saIm0625` | laptop | 1.3804±0.0135 | 0.9902±0.0223 | 71.7% | 조건부 | `COMMS/laptop.md` 71.7% 조건부 | ✅ |
| `saIm0667` | laptop | 1.3682±0.0301 | 1.0269±0.0387 | 75.1% | 조건부 | `COMMS/desktop.md` 75.05~75.1% 조건부 | ✅ |
| `saIm0875` | junseok*/laptop | 1.2905±0.0333 / 1.3031±0.0215 | 0.9619±0.0181 / 0.9671±0.0482 | 74.5% / 74.2% | 조건부(양쪽 다) | `COMMS/junseok.md`·`laptop.md` 74.5%·74.2% 조건부 | ✅ |
| `saIm0917` | desktopcliff | 1.3249±0.0258 | 0.9725±0.0143 | 73.4% | 조건부 | `COMMS/desktop.md` 73.41% 조건부 | ✅ |
| `saIm0958` | desktopcliff | 1.5205±0.0129 | 1.0032±0.0312 | 66.0% | 조건부 | `COMMS/desktop.md` 65.98% 조건부 | ✅ |

이상 없음 — 6개 조성 전부 관문(≥80% 유효/50~80% 조건부/<50% 종료)
재계산 판정과 저장소 기록이 일치한다. 전부 50~80% 조건부 구간이고,
유효로 잘못 올렸거나 종료로 잘못 내린 곳은 없다.

### 6) WC 자료 공백

`v3_wc/`(건조), `v3_humid_wc/`+`v4_humid_wc/`(습윤) 각 JSON의 `name`
필드를 나열해 조성별 유무를 대조:

| 조성 | 건조 WC | 습윤 WC |
|---|---|---|
| `base` | ✅ | ✅ |
| `saIm025` | ✅ | ✅ |
| `saIm050` | ✅ | ✅ |
| `saIm075` | ✅ | ✅ |
| `saIm100` | ✅ | ✅ |
| `mslm075` | ✅ | ✅ |
| `saIm0583` | ✅ | ✅ |
| `saIm0625` | ❌ | ✅ |
| `ms50nb50` | ❌ | ✅ |
| `sa25nb75` | ❌ | ✅ |
| `sa50nb50` | ❌ | ✅ |

건조·습윤 둘 다 있는 조성(7종): `base, saIm025, saIm050, saIm075,
saIm100, mslm075, saIm0583`.
습윤만 있는 조성(4종): `saIm0625, ms50nb50, sa25nb75, sa50nb50`.
건조만 있는 조성: 없음.

`regen_energy_v3.py`를 실행하지 않고 모듈로 임포트해 실제 `NAMES`
(재생에너지 계산 대상 — `dry_tsa`/`dry_vsa`/`wet_tsa`/`wet_vsa`/`Qst`
5개 전부 있어야 포함됨, 2026-08-27 수정)를 확인하니
`['base','mslm075','saIm025','saIm050','saIm0583','saIm075','saIm100']`
로 나와, 습윤만 있는 4종은 이미 자동으로 제외돼 있었다.

이상 없음 — 건조·습윤 한쪽만 있는 조성(4종)이 실재하지만,
`regen_energy_v3.py`의 기존 필터(08-27 수정)가 이를 걸러내고 있어
"절반만 찬 행이 완성된 행처럼 보이는" 위험은 현재 코드 경로에서는
발생하지 않는다. 이 필터 로직이 바뀌면 재검사가 필요하다.

## 사람이 볼 것

- `junseok-20260822` 브랜치 9.3일/544커밋 정체 + `COMMS/junseok.md` 8.9일
  침묵 — 09-06 대비 정확히 하루 더 방치(경고, 지속 중)
- 나머지 5개 항목(JSON 무결성·출처 중복·수분 관문·WC 공백·다른 브랜치)은
  전부 이상 없음
- (검사기 함정) 이 컨테이너의 얕은 클론이 브랜치 발산 수치와 우편함
  최종수정 커밋 둘 다를 오염시켰음 — `git fetch --unshallow` 후 재계산해
  정정함. 결론은 바뀌지 않았음(둘 다 "이상 없음"→"경고"가 뒤바뀌진 않음)

---

## 2026-09-06 00:15 UTC — 일일 감사

**실행 조건**: 클라우드 저장소 체크아웃만으로 확인. 로컬 프로세스·메모리·
미푸시 커밋은 볼 수 없음. 새 계산 없음(`regen_energy_v3.py` 는 실행하지
않고 파이썬으로 그 글롭 패턴과 로직을 그대로 임포트해 대조함).
`merge_water_batches.py` 는 기존 도구를 태그 붙은 파일만 넘겨 그대로
호출함(⑥-(가), 손으로 다시 짜지 않음, 아래 4·5절 출력이 그 실제 실행
결과). 아래 6개 점검 외 어떤 파일도 수정하지 않음.

**방법 메모(경고 아님)**: 컨테이너 초기 체크아웃이 얕은 클론(depth 50)이라
`git rev-list --left-right` 값이 처음에 134/62(발산으로 오판)로 나왔다.
`git fetch --unshallow` 로 전체 이력(870커밋)을 받은 뒤 재계산하니
461/0(순수 뒤처짐)으로 정정됐다. 얕은 클론에서 병합 베이스 계산이
틀어질 수 있다는 것 자체가 검사기 함정이라 기록해 둔다 — 아래 수치는
전부 unshallow 이후 값이다.

### 1) 브랜치 정체

`git fetch --all` (+`--unshallow`) 후 (기준 시각 2026-09-06 00:11 UTC =
09:11 KST):

| 브랜치 | 마지막 커밋 | 경과 | master 대비 뒤처짐 | master 대비 앞섬 |
|---|---|---|---|---|
| `origin/master` | `fdabdf1` 2026-09-06 06:36:42 KST | 2.6시간 | — | — |
| `origin/laptop-20260822` | `fdabdf1` 2026-09-06 06:36:42 KST (master 와 동일 커밋) | 2.6시간 | 0커밋 | 0커밋 |
| `origin/junseok-20260822` | `41fb1b7` 2026-08-29 00:54:23 KST | **200.3시간(8.3일)** | **461커밋** | 0커밋 |

**경고: `junseok-20260822` 가 마지막 커밋 8.3일 경과, master 대비
461커밋 뒤처짐** — 08-24 사고 기준(24커밋)의 19배. 09-05 감사(194커밋/
7.3일) 대비 뒤처진 커밋 수가 크게 늘었지만, 이는 그 사이 `master` 가
다른 가지(들)를 활발히 흡수하며 전진했기 때문이고(정상 동작),
`junseok-20260822` 자신의 앞섬은 09-05 감사 때와 마찬가지로 계속
**0커밋**이다 — 즉 그 가지에 남아 있던 고유 작업은 이미 전부 master 에
흡수되어 있고, fast-forward 로 합류 가능한 상태다("가지 취합 지연"이
아니라 그 가지 자체가 8일 넘게 새 작업 없이 방치돼 있다는 뜻). `laptop-20260822`
는 master 와 완전히 동일한 커밋(0/0) — 09-05 감사가 기록한 19커밋
뒤처짐에서 완전히 합류함, 경고 아님.

(참고, 지시된 세 브랜치 밖: `origin/junseok`(날짜 미부착) `be2bede`
2026-08-29 11:32:05 KST, 189.6시간(7.9일) 경과, master 대비 414커밋
뒤처짐/0커밋 앞섬 — `junseok-20260822` 와 같은 시기에 같은 방향으로
멈춰 있음. `origin/laptop2-20260825` `1c51ab1` 2026-09-06 06:28:22 KST,
2.7시간 경과, master 대비 201커밋 뒤처짐/0커밋 앞섬 — 최근 커밋인데도
뒤처짐이 큰 것은 master 가 병합 직후 다른 가지에서 더 전진했기 때문으로
보이며, 0커밋 앞섬이라 실질적 발산은 없음.)

### 2) 우편함 침묵

각 우편함 파일을 **모든 브랜치**에서 찾은 가장 최근 커밋 기준으로 보고
(경과 시간만 보고, 침묵을 "죽었다"로 단정하지 않음):

| 파일 | 마지막 커밋 | 경과 |
|---|---|---|
| `COMMS/desktop.md` | `775309a` 2026-09-04 23:56:00 KST (master) | 33.2시간(1.4일) |
| `COMMS/laptop.md` | `fdabdf1` 2026-09-06 06:36:42 KST (master/`laptop-20260822`) | 2.6시간 |
| `COMMS/junseok.md` | `be2bede` 2026-08-29 11:32:05 KST (`origin/junseok`; `junseok-20260822` 는 더 오래된 `41fb1b7` 뿐) | **189.6시간(7.9일)** |
| `COMMS/laptop2.md` | `7dbe5b7` 2026-09-05 07:08:29 KST (master) | 26.0시간(1.1일) |
| `COMMS/cloud4c.md` | `84cfdde` 2026-09-04 17:49:13 KST (master) | 39.4시간(1.6일) |

`COMMS/junseok.md` 침묵(7.9일)이 1절의 `junseok-20260822`·`junseok` 두
브랜치 정체(8.3일·7.9일)와 계속 같은 방향으로 겹친다 — 09-05 감사(6.9일)
대비 정확히 하루 늘어 새 활동이 없다는 뜻으로 읽힌다. "죽었다"고 단정하지
않되 경고로 유지한다. 나머지 네 우편함은 모두 39.4시간 이내로 정상 범위.

### 3) 결과 JSON 무결성

`results_v3*.json`, `v3_wc/`, `v3_humid_wc/`, `v4_humid_wc/`, `v3_water_grid*/`
아래 모든 `.json` 을 파이썬으로 파싱(`{"rows": [...]}` dict 는 `rows` 배열
길이, 순수 리스트는 원소 수를 행수로 셈):

| 파일 | 결과 | 행수 |
|---|---|---|
| `results_v3.json` | OK | 31 |
| `results_v3_smoke.json` | OK | 1 |
| `results_v3cliff.json` | OK | 2 |
| `results_v3ens0583.json` | OK | 5 |
| `results_v3ens075.json` | OK | 5 |
| `results_v3ens_mix10.json` | OK | 10 |
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

이상 없음 — 파싱 실패·0행 없음. **09-05 감사 대비 새 파일 1건**:
`results_v3ens_mix10.json`(10행) — 커밋 `5c024e9`(MIX10 혼합 판정, 오늘
이전 작업)로 추가됨. 새 파일도 정상 파싱, 0행 아님. 나머지 파일은
09-05 감사 표와 목록·행수 동일.

### 4) 출처 규약 위반

`merge_water_batches.py` 를 태그 붙은 파일만 넘겨 직접 호출(⑥-(가), 손으로
다시 짜지 않음):

```
$ python merge_water_batches.py v3_water_grid/water_results_desktop4.json \
    v3_water_grid/water_results_laptop.json v3_water_grid/water_results_junseok.json
교차 검증 쌍 4개 — saIm0875 RH0/25/50/90 모두 junseok·laptop 양쪽에 존재
  RH0  junseok 1.2905±0.0333 vs laptop 1.3031±0.0215  -> 0.32σ 일관
  RH25 junseok 1.1743±0.0222 vs laptop 1.1498±0.0240  -> 0.75σ 일관
  RH50 junseok 1.0564±0.0373 vs laptop 1.0582±0.0423  -> 0.03σ 일관
  RH90 junseok 0.9619±0.0181 vs laptop 0.9671±0.0482  -> 0.10σ 일관

$ python merge_water_batches.py v3_water_grid_cliff/water_results_desktopcliff.json
조성 2종 · 점 4개 · 파일 1개 (태그 파일이 이 디렉터리엔 하나뿐이라 중복·
교차검증 대상 자체가 없음)
```

**값이 서로 다르므로 진짜 교차검증**이지 중복이 아님(4쌍 전부 0.03~0.75σ
로 일관). 태그 붙은 파일 사이에서 값이 완전히 같은 (조성,RH) 중복은 없음.

참고(경고 아님, 08-29 이후 매 감사와 동일): `v3_water_grid/`·
`v3_water_grid_cliff/` 각각의 태그 없는 `water_results.json` 이 대응하는
`water_results_desktop4.json`/`water_results_desktopcliff.json` 과 파이썬
`json.load` 비교로 완전히 동일함(이어받기 체크포인트 사본). `machine_of()`
가 태그 없는 파일을 구조적으로 거부하므로(코드 60~87행 확인)
`merge_water_batches.py` 를 규약대로 쓰는 한 이중 계수로 이어지지 않음.
저장소 안에서 `water_results*.json` 와일드카드로 두 파일을 함께 넘기는
스크립트도 없음(`grep` 확인). `v3_water_grid/` 에는 이 상태를 설명하는
`README.md` 가 있는 반면 `v3_water_grid_cliff/` 에는 같은 설명 문서가
여전히 없음 — 지금은 도구가 태그 없는 파일을 거부해 위험이 실현되지
않지만, 사람이 손으로 글롭해 들여다볼 경우 `v3_water_grid_cliff/` 쪽에서
더 헷갈릴 여지(경고까지는 아니고 참고, 09-05 감사와 동일).

### 5) 사전 등록 관문 대비 기록

`v3_water_grid*/` 태그 파일을 4절과 같은 `merge_water_batches.py` 실행
결과에서 그대로 가져와(직접 재구현 안 함) 문서 기재값과 대조:

| 조성 | 출처 | RH0 | RH90 | 유지율 | 판정 | 문서 기재값 | 일치 |
|---|---|---|---|---|---|---|---|
| saIm0583 | desktop4 | 1.3188±0.0264 | 1.0010±0.0170 | 75.9% | 조건부 | `COMMS/desktop.md` 75.90±1.99% 조건부 | ✅ |
| saIm0625 | laptop | 1.3804±0.0135 | 0.9902±0.0223 | 71.7% | 조건부 | `COMMS/desktop.md`/`laptop.md` 71.7% 조건부 | ✅ |
| saIm0667 | laptop | 1.3682±0.0301 | 1.0269±0.0387 | 75.1% | 조건부 | `COMMS/desktop.md` 75.05~75.1% 조건부 | ✅ |
| saIm0875 | junseok*/laptop | 1.2905±0.0333 / 1.3031±0.0215 | 0.9619±0.0181 / 0.9671±0.0482 | 74.5% / 74.2% | 조건부 | `COMMS/junseok.md`/`laptop.md` 74.5%·74.2% 조건부 | ✅ |
| saIm0917 | desktopcliff | 1.3249±0.0258 | 0.9725±0.0143 | 73.4% | 조건부 | `COMMS/desktop.md` 73.41% 조건부 | ✅ |
| saIm0958 | desktopcliff | 1.5205±0.0129 | 1.0032±0.0312 | 66.0% | 조건부 | `COMMS/desktop.md` 65.98% 조건부 | ✅ |

* saIm0875 는 교차 검증 쌍이라 두 기기 값을 함께 적음(4절, 둘 다
0.03~0.75σ 로 일관).

이상 없음 — 6개 조성 전부 문서 기재와 재계산이 일치함(자료·문서 모두
변경 없음, 09-05 감사와 동일). 관문 80/50/0 기준으로 전부 "50~80% 조건부"
구간에 있고 "유효"·"종료" 경계를 넘는 곳은 없음. 어긋나는 곳을 찾지
못함.

### 6) WC 자료 공백

`regen_energy_v3.py:load_wc()`/`NAMES` 를 직접 임포트해(재구현 안 함) 실제
읽는 글롭 패턴(`v3_wc/*.json`, `v3_humid_wc/*.json`, `v4_humid_wc/*.json`)
결과를 그대로 씀:

| 조성 | 건조 WC | 습윤 WC | 재생에너지 계산에 포함되는가 |
|---|---|---|---|
| base | ✓ `working_capacity.json` | ✓ `humid_working_capacity.json` | ✓ |
| saIm025 | ✓ 〃 | ✓ `humid_working_capacity_ext.json` | ✓ |
| saIm050 | ✓ 〃 | ✓ `humid_working_capacity.json` | ✓ |
| saIm075 | ✓ 〃 | ✓ 〃 | ✓ |
| saIm100 | ✓ 〃 | ✓ 〃 | ✓ |
| mslm075 | ✓ 〃 | ✓ `humid_working_capacity_mslm075.json` | ✓ |
| **saIm0583 (승자 조성)** | ✓ `working_capacity_g0583.json` | ✓ `humid_working_capacity_g0583.json` | ✓ |
| saIm0625 | — 없음 | ✓ `humid_working_capacity_grid.json` | ✗ (건조 없어 계산 불가) |
| ms50nb50 | — 없음 | ✓ `v4_humid_wc/..._v4ext.json` | ✗ |
| sa25nb75 | — 없음 | ✓ `v4_humid_wc/..._v4ext.json` | ✗ |
| sa50nb50 | — 없음 | ✓ `v4_humid_wc/..._v4m1.json` | ✗ |

건조·습윤이 둘 다 있는 조성 7개(base, saIm025, saIm050, saIm075, saIm100,
mslm075, saIm0583)와 습윤만 있는 조성 4개(saIm0625, ms50nb50, sa25nb75,
sa50nb50)로 나뉜다. 건조만 있고 습윤이 없는 조성은 없음.

`load_wc()`/`NAMES` 를 직접 임포트해 확인: 산출되는 `NAMES` 가 위 표의
"둘 다 있음" 7개와 정확히 일치(`saIm0625` 는 Q_st·습윤 WC 는 있어도 건조
WC 가 없어 `NAMES` 에서 정확히 제외됨) — "한쪽만 있는데 완성된 행처럼
보이는" 위험 없음(2026-08-27 수정으로 이미 닫힌 구멍, 오늘도 재확인).

이상 없음(09-05 감사와 동일, 자료 변경 없음).

---

## 사람이 볼 것

- 경고: `junseok-20260822`(+`junseok`) 브랜치가 8.3일/7.9일째 정지(461·414
  커밋 뒤처짐, 08-24 기준의 19배), `COMMS/junseok.md` 도 7.9일째 침묵 —
  09-05 대비 정확히 하루 늘어 회복 신호 없음.
- 참고(경고 아님): `laptop-20260822` 가 master 와 완전히 합류(0/0);
  `results_v3ens_mix10.json` 신규 추가(정상 파싱, 10행).
- 나머지(JSON 무결성·출처 중복·사전 등록 관문·WC 자료 공백)는 이상 없음.

---

## 2026-09-05 00:10 UTC — 일일 감사

**실행 조건**: 클라우드 저장소 체크아웃만으로 확인. 로컬 프로세스·메모리·
미푸시 커밋은 볼 수 없음. 새 계산 없음(`regen_energy_v3.py` 는 실행하지
않고 파이썬으로 그 글롭 패턴과 로직을 그대로 재현해 대조함). `merge_water_batches.py`
는 기존 도구를 태그 붙은 파일만 넘겨 그대로 호출함(⑥-(가), 손으로 다시
짜지 않음, 아래 4·5절 출력이 그 실제 실행 결과). 아래 6개 점검 외 어떤
파일도 수정하지 않음.

### 1) 브랜치 정체

`git fetch --all` 후 (기준 시각 2026-09-05 00:09 UTC, `HEAD` 는
`origin/master` 와 동일 커밋):

| 브랜치 | 마지막 커밋 | 경과 | master 대비 뒤처짐 | master 대비 앞섬 |
|---|---|---|---|---|
| `origin/master` | `9723a21` 2026-09-05 07:10:18 KST | 2.0시간 | — | — |
| `origin/laptop-20260822` | `f909af8` 2026-09-05 03:29:48 KST | 5.7시간 | 19커밋 | 10커밋 |
| `origin/junseok-20260822` | `41fb1b7` 2026-08-29 00:54:23 KST | **176.2시간(7.3일)** | **194커밋** | 0커밋 |

**경고: `junseok-20260822` 가 `origin/master` 보다 194커밋 뒤처졌고, 마지막
커밋이 7.3일 전이다.** 08-24 사고 기준(24커밋)의 8배를 넘는다. 09-03
감사(50커밋/5.3일) → 09-04 감사(196커밋/6.3일) → 오늘(194커밋/7.3일)로,
날짜 경과는 계속 늘어나는데 뒤처진 커밋 수는 196→194로 거의 그대로다 —
정체가 새로 생긴 게 아니라 09-03 이후 전혀 회복되지 않고 있다는 뜻(1~2커밋
차이는 병합 방식에 따른 계수 흔들림으로 보이며 실질적 변화는 아님).

`laptop-20260822` 는 19커밋 뒤처짐으로 08-24 기준(24) 미만이다. 09-04
감사가 기록한 37커밋보다 줄었고, 5.7시간 전까지 그 브랜치에 직접 커밋되고
있다 — 09-04 감사가 짚은 "격차→병합→재축적" 패턴대로 그 사이 `master` 로
병합이 있었던 것으로 보인다. 경고 아님.

(참고, 지시된 세 브랜치 밖: `origin/junseok`(날짜 미부착) `be2bede`
2026-08-29 11:32:05 KST, 165.6시간 경과, master 대비 159커밋 뒤처짐 /
0커밋 앞섬 — `junseok-20260822` 와 같은 시기에 같은 방향으로 멈춰 있다.
`origin/laptop2-20260825` `d1ef6bd` 2026-09-05 01:07:02 KST, 8.0시간 경과,
master 대비 8커밋 뒤처짐 / 4커밋 앞섬 — 기준 미만.)

### 2) 우편함 침묵

각 우편함 파일을 **모든 브랜치**에서 찾은 가장 최근 커밋 기준으로 보고
(경과 시간만 보고, 침묵을 "죽었다"로 단정하지 않음):

| 파일 | 마지막 커밋 | 경과 |
|---|---|---|
| `COMMS/desktop.md` | `7753098` 2026-09-04 23:56:00 KST (master) | 9.2시간 |
| `COMMS/laptop.md` | `2f3ccde` 2026-09-05 03:17:07 KST (`laptop-20260822`) | 5.9시간 |
| `COMMS/junseok.md` | `be2bede` 2026-08-29 11:32:05 KST (`origin/junseok`; `junseok-20260822` 는 더 오래된 `41fb1b7` 뿐) | **165.6시간(6.9일)** |
| `COMMS/laptop2.md` | `82afe50` 2026-09-05 00:40:33 KST (master) | 8.5시간 |
| `COMMS/cloud4c.md` | `84cfdde` 2026-09-04 17:49:13 KST (master) | 15.3시간 |

`COMMS/junseok.md` 침묵(6.9일)이 1절의 `junseok-20260822`·`junseok` 두
브랜치 정체(7.3일·6.9일)와 계속 같은 방향으로 겹친다 — 09-03(4.9일) →
09-04(5.9일) → 오늘(6.9일)로 침묵이 하루씩 그대로 늘어나고 있어 새 활동이
없다는 뜻으로 읽힌다. "죽었다"고 단정하지는 않되 경고로 유지한다. 나머지
네 우편함은 모두 15.3시간 이내로 정상 범위.

### 3) 결과 JSON 무결성

`results_v3*.json`, `v3_wc/`, `v3_humid_wc/`, `v4_humid_wc/`, `v3_water_grid*/`
아래 모든 `.json` 을 파이썬으로 파싱(`{"rows": [...]}` dict 는 `rows` 배열
길이, 순수 리스트는 원소 수를 행수로 셈):

| 파일 | 결과 | 행수 |
|---|---|---|
| `results_v3.json` | OK | 31 |
| `results_v3_smoke.json` | OK | 1 |
| `results_v3cliff.json` | OK | 2 |
| `results_v3ens0583.json` | OK | 5 |
| `results_v3ens075.json` | OK | 5 |
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

이상 없음 — 파싱 실패·0행 없음. 09-04 감사 표와 파일 목록·행수 전부 동일
(새 파일 없음, 자료 변경 없음).

### 4) 출처 규약 위반

`merge_water_batches.py` 를 태그 붙은 파일만 넘겨 직접 호출(⑥-(가), 손으로
다시 짜지 않음):

```
$ python merge_water_batches.py v3_water_grid/water_results_desktop4.json \
    v3_water_grid/water_results_laptop.json v3_water_grid/water_results_junseok.json
교차 검증 쌍 4개 — saIm0875 RH0/25/50/90 모두 junseok·laptop 양쪽에 존재
  RH0  junseok 1.2905±0.0333 vs laptop 1.3031±0.0215  -> 0.32σ 일관
  RH25 junseok 1.1743±0.0222 vs laptop 1.1498±0.0240  -> 0.75σ 일관
  RH50 junseok 1.0564±0.0373 vs laptop 1.0582±0.0423  -> 0.03σ 일관
  RH90 junseok 0.9619±0.0181 vs laptop 0.9671±0.0482  -> 0.10σ 일관

$ python merge_water_batches.py v3_water_grid_cliff/water_results_desktopcliff.json
조성 2종 · 점 4개 · 파일 1개 (태그 파일이 이 디렉터리엔 하나뿐이라 중복·
교차검증 대상 자체가 없음)
```

**값이 서로 다르므로 진짜 교차검증**이지 중복이 아님(4쌍 전부 0.03~0.75σ
로 일관). 태그 붙은 파일 사이에서 값이 완전히 같은 (조성,RH) 중복은 없음.

참고(경고 아님, 08-29 이후 매 감사와 동일): `v3_water_grid/`·
`v3_water_grid_cliff/` 각각의 태그 없는 `water_results.json` 이 대응하는
`water_results_desktop4.json`/`water_results_desktopcliff.json` 과 바이트
단위로 동일함(이어받기 체크포인트 사본, `diff` 로 재확인). `machine_of()`
가 태그 없는 파일을 구조적으로 거부하므로(코드 60~75행 확인)
`merge_water_batches.py` 를 규약대로 쓰는 한 이중 계수로 이어지지 않음.
저장소 안에서 `water_results*.json` 와일드카드로 두 파일을 함께 넘기는
스크립트도 없음(`grep` 확인). 다만 `v3_water_grid/` 에는 이 상태를 설명하는
`README.md` 가 있는 반면 `v3_water_grid_cliff/` 에는 같은 설명 문서가
없다 — 지금은 도구가 태그 없는 파일을 거부해 위험이 실현되지 않지만,
사람이 `water_results*.json` 을 손으로 글롭해 들여다볼 경우 문서 부재가
`v3_water_grid_cliff/` 쪽에서 더 헷갈릴 여지가 있다(경고까지는 아니고 참고).

### 5) 사전 등록 관문 대비 기록

`v3_water_grid*/` 태그 파일을 4절과 같은 `merge_water_batches.py` 실행
결과에서 그대로 가져와(직접 재구현 안 함) 문서 기재값과 대조:

| 조성 | 출처 | RH0 | RH90 | 유지율 | 판정 | 문서 기재값 | 일치 |
|---|---|---|---|---|---|---|---|
| saIm0583 | desktop4 | 1.3188±0.0264 | 1.0010±0.0170 | 75.9% | 조건부 | `COMMS/desktop.md` 75.90±1.99% 조건부 | ✅ |
| saIm0625 | laptop | 1.3804±0.0135 | 0.9902±0.0223 | 71.7% | 조건부 | `COMMS/desktop.md`/`laptop.md` 71.7% 조건부 | ✅ |
| saIm0667 | laptop | 1.3682±0.0301 | 1.0269±0.0387 | 75.1% | 조건부 | `COMMS/desktop.md` 75.05~75.1% 조건부 | ✅ |
| saIm0875 | junseok*/laptop | 1.2905±0.0333 / 1.3031±0.0215 | 0.9619±0.0181 / 0.9671±0.0482 | 74.5% / 74.2% | 조건부 | `COMMS/junseok.md`/`laptop.md` 74.5%·74.2% 조건부 | ✅ |
| saIm0917 | desktopcliff | 1.3249±0.0258 | 0.9725±0.0143 | 73.4% | 조건부 | `COMMS/desktop.md` 73.41% 조건부 | ✅ |
| saIm0958 | desktopcliff | 1.5205±0.0129 | 1.0032±0.0312 | 66.0% | 조건부 | `COMMS/desktop.md` 65.98% 조건부 | ✅ |

* saIm0875 는 교차 검증 쌍이라 두 기기 값을 함께 적음(4절, 둘 다
0.03~0.75σ 로 일관).

이상 없음 — 6개 조성 전부 문서 기재와 재계산이 일치함(자료·문서 모두
변경 없음, 09-04 감사와 동일). 관문 80/50/0 기준으로 전부 "50~80% 조건부"
구간에 있고 "유효"·"종료" 경계를 넘는 곳은 없음. 어긋나는 곳을 찾지
못함.

### 6) WC 자료 공백

`regen_energy_v3.py:load_wc()` 가 실제로 읽는 글롭 패턴(`v3_wc/*.json`,
`v3_humid_wc/*.json`, `v4_humid_wc/*.json`)을 그대로 파이썬으로 재현:

| 조성 | 건조 WC | 습윤 WC | 재생에너지 계산에 포함되는가 |
|---|---|---|---|
| base | ✓ `working_capacity.json` | ✓ `humid_working_capacity.json` | ✓ |
| saIm025 | ✓ 〃 | ✓ `humid_working_capacity_ext.json` | ✓ |
| saIm050 | ✓ 〃 | ✓ `humid_working_capacity.json` | ✓ |
| saIm075 | ✓ 〃 | ✓ 〃 | ✓ |
| saIm100 | ✓ 〃 | ✓ 〃 | ✓ |
| mslm075 | ✓ 〃 | ✓ `humid_working_capacity_mslm075.json` | ✓ |
| **saIm0583 (승자 조성)** | ✓ `working_capacity_g0583.json` | ✓ `humid_working_capacity_g0583.json` | ✓ |
| saIm0625 | — 없음 | ✓ `humid_working_capacity_grid.json` | ✗ (건조 없어 계산 불가) |
| ms50nb50 | — 없음 | ✓ `v4_humid_wc/..._v4ext.json` | ✗ |
| sa25nb75 | — 없음 | ✓ `v4_humid_wc/..._v4ext.json` | ✗ |
| sa50nb50 | — 없음 | ✓ `v4_humid_wc/..._v4m1.json` | ✗ |

건조·습윤이 둘 다 있는 조성 7개(base, saIm025, saIm050, saIm075, saIm100,
mslm075, saIm0583)와 습윤만 있는 조성 4개(saIm0625, ms50nb50, sa25nb75,
sa50nb50)로 나뉜다. 건조만 있고 습윤이 없는 조성은 없음.

`load_wc()`/`NAMES` 정의(코드 47~69행)를 직접 임포트해 재확인: 산출되는
`NAMES` 가 위 표의 "둘 다 있음" 7개와 정확히 일치하고, `regen_energy_v3.json`
에 실제로 담긴 7개 행도 이와 일치함 — "한쪽만 있는데 완성된 행처럼 보이는"
위험 없음(2026-08-27 `c`언저리 수정으로 이미 닫힌 구멍).

이상 없음(09-04 감사와 동일, 자료 변경 없음).

---

## 사람이 볼 것

- 경고: `junseok-20260822`(+`junseok`) 브랜치가 7.3일/6.9일째 정지(194·159
  커밋 뒤처짐, 08-24 기준의 8배), `COMMS/junseok.md` 도 6.9일째 침묵 — 09-03
  이후 회복 신호 없이 그대로 굳어 있음.
- 참고(경고 아님): `laptop-20260822` 뒤처짐이 37→19커밋으로 줄어 기준 밖으로
  돌아옴; `v3_water_grid_cliff/` 에 `v3_water_grid/README.md` 같은 설명
  문서가 없어 사람이 손으로 글롭할 때 헷갈릴 여지(도구 자체는 안전).
- 나머지(JSON 무결성·출처 중복·사전 등록 관문·WC 자료 공백)는 이상 없음.

---

## 2026-09-04 00:10 UTC — 일일 감사

**실행 조건**: 클라우드 저장소 체크아웃만으로 확인. 로컬 프로세스·메모리·
미푸시 커밋은 볼 수 없음. 새 계산 없음(`regen_energy_v3.py` 는 실행하지
않고 파이썬으로 그 글롭 패턴과 로직만 그대로 재현함). `merge_water_batches.py`
는 기존 도구를 그대로 호출함(⑥-(가), 새로 짜지 않음). 아래 6개 점검 외
어떤 파일도 수정하지 않음.

### 1) 브랜치 정체

`git fetch --all` 후 (기준 시각 2026-09-04 00:10 UTC):

| 브랜치 | 마지막 커밋 | 경과 | master 대비 뒤처짐 | master 대비 앞섬 |
|---|---|---|---|---|
| `origin/master` | `f3afacf` 2026-09-03 18:27:34 KST | 14.7시간 | — | — |
| `origin/laptop-20260822` | `97176fe` 2026-09-03 13:08:35 KST | 20.0시간 | **37커밋** | 8커밋 |
| `origin/junseok-20260822` | `41fb1b7` 2026-08-29 00:54:23 KST | **152.3시간(6.3일)** | **196커밋** | 0커밋 |

**경고: `laptop-20260822` 가 08-24 사고 기준(24커밋)을 넘는 37커밋 뒤처짐.**
다만 20시간 전까지 그 브랜치에 직접 커밋되고 있어(위 표) 정지가 아니라
`master` 로 아직 병합 안 된 로컬 진행분이 쌓인 것으로 보임 — 08-29 감사가
기록한 laptop 의 "격차→병합→재축적" 패턴과 같은 모양.

**경고: `junseok-20260822` 가 `origin/master` 보다 196커밋 뒤처졌고, 마지막
커밋이 6.3일 전이다.** 08-24 사고 기준의 여덟 배를 넘는다. 08-29 감사가
50커밋/5.3일로 기록했던 것이 09-03 감사(50커밋/5.3일, 자동 감사 루틴 자체가
5일 쉰 뒤 첫 재개)를 거쳐 오늘 196커밋/6.3일로 계속 벌어지고 있다 — 정체가
새로 생긴 게 아니라 그때 이후로도 회복되지 않고 있다는 뜻.

(참고, 지시된 세 브랜치 밖: `origin/junseok`(날짜 미부착) `be2bede`
2026-08-29 11:32:05 KST, 141.6시간 경과, master 대비 133커밋 뒤처짐 / 3커밋
앞섬 — junseok-20260822 보다는 덜 뒤처졌지만 여전히 기준 초과. 같은 기기의
다른 브랜치도 같은 시기에 멈췄다는 같은 방향 신호. `origin/laptop2-20260825`
`71e9ad1` 2026-09-03 18:17:26 KST, 14.9시간 경과, master 대비 9커밋 뒤처짐 /
0커밋 앞섬 — 기준 미만, 완전히 병합된 상태.)

### 2) 우편함 침묵

각 우편함 파일을 **모든 브랜치**에서 찾은 가장 최근 커밋 기준으로 보고
(경과 시간만 보고, 침묵을 "죽었다"로 단정하지 않음):

| 파일 | 마지막 커밋 | 경과 |
|---|---|---|
| `COMMS/desktop.md` | `5e5d931` 2026-09-03 11:57:51 KST (master) | 21.2시간 |
| `COMMS/laptop.md` | `97176fe` 2026-09-03 13:08:35 KST (`laptop-20260822`; `master` 는 아직 `01cf1e0` 11:58:06 KST 까지만 반영) | 20.0시간 |
| `COMMS/junseok.md` | `be2bede` 2026-08-29 11:32:05 KST (`origin/junseok`; `junseok-20260822` 는 더 오래된 `41fb1b7` 00:54:23 뿐) | **141.6시간(5.9일)** |
| `COMMS/laptop2.md` | `71e9ad1` 2026-09-03 18:17:26 KST (master, 자기 브랜치와 동일) | 14.9시간 |

`COMMS/junseok.md` 침묵(5.9일)이 1절의 `junseok-20260822`·`junseok` 두
브랜치 정체(6.3일·5.9일)와 같은 방향으로 겹친다 — 우편함도 두 브랜치도
같은 시기(08-29 전후)에 함께 멈췄고 그 뒤로 회복 신호가 없다. "죽었다"고
단정하지는 않되, 이 겹침 자체는 경고로 올린다. 나머지 세 우편함은 모두
21시간 이내로 정상 범위.

### 3) 결과 JSON 무결성

`results_v3*.json`, `v3_wc/`, `v3_humid_wc/`, `v4_humid_wc/`, `v3_water_grid*/`
아래 모든 `.json` 을 파이썬으로 파싱(`{"rows": [...]}` dict 는 `rows` 배열
길이, 순수 리스트는 원소 수를 행수로 셈):

| 파일 | 결과 | 행수 |
|---|---|---|
| `results_v3.json` | OK | 31 |
| `results_v3_smoke.json` | OK | 1 |
| `results_v3cliff.json` | OK | 2 |
| `results_v3ens0583.json` | OK | 5 |
| `results_v3ens075.json` | OK | **5 (신규)** |
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

이상 없음 — 파싱 실패·0행 없음. `results_v3ens075.json`(saIm075 e1~e5 건조
GCMC, 5행)이 09-03 감사 이후 새로 생긴 파일이나 정상 파싱됨. 나머지는
09-03 감사 표와 행수 전부 동일.

### 4) 출처 규약 위반

`merge_water_batches.py` 를 태그 붙은 파일만 넘겨 직접 호출(⑥-(가), 손으로
다시 짜지 않음):

```
$ python merge_water_batches.py v3_water_grid/water_results_desktop4.json \
    v3_water_grid/water_results_laptop.json v3_water_grid/water_results_junseok.json
교차 검증 쌍 4개 — saIm0875 RH0/25/50/90 모두 junseok·laptop 양쪽에 존재
  RH0  junseok 1.2905±0.0333 vs laptop 1.3031±0.0215  -> 0.32σ 일관
  RH25 junseok 1.1743±0.0222 vs laptop 1.1498±0.0240  -> 0.75σ 일관
  RH50 junseok 1.0564±0.0373 vs laptop 1.0582±0.0423  -> 0.03σ 일관
  RH90 junseok 0.9619±0.0181 vs laptop 0.9671±0.0482  -> 0.10σ 일관

$ python merge_water_batches.py v3_water_grid_cliff/water_results_desktopcliff.json
조성 2종 · 점 4개 · 파일 1개 (태그 파일이 이 디렉터리엔 하나뿐이라 중복·
교차검증 대상 자체가 없음)
```

**값이 서로 다르므로 진짜 교차검증**이지 중복이 아님(4쌍 전부 0.03~0.75σ
로 일관). 태그 붙은 파일 사이에서 값이 완전히 같은 (조성,RH) 중복은 없음.

참고(경고 아님, 08-29·09-03 감사와 동일): `v3_water_grid/`·
`v3_water_grid_cliff/` 각각의 태그 없는 `water_results.json` 이 대응하는
`water_results_desktop4.json`/`water_results_desktopcliff.json` 과 바이트
단위로 동일함(이어받기 체크포인트 사본). `machine_of()` 가 태그 없는
파일을 구조적으로 거부하므로(코드 확인) `merge_water_batches.py` 를
규약대로 쓰는 한 이중 계수로 이어지지 않음. 저장소 안에서 `water_results*.json`
와일드카드로 두 파일을 함께 넘기는 스크립트도 없음(`grep` 확인).

### 5) 사전 등록 관문 대비 기록

`v3_water_grid*/` 태그 파일의 RH0·RH90 로딩으로 유지율을
`merge_water_batches.py` 의 `retention()`(러너 `run_water.py:325` 와 같은
정의)으로 직접 재계산해 문서 기재값과 대조:

| 조성 | 출처 | RH0 | RH90 | 재계산 유지율 | 재계산 판정 | 문서 기재값 | 일치 |
|---|---|---|---|---|---|---|---|
| saIm0583 | desktop4 | 1.3188±0.0264 | 1.0010±0.0170 | 75.9% | 조건부 | `COMMS/desktop.md:940,996,1112` 75.90±1.99% 조건부 | ✅ |
| saIm0625 | laptop | 1.3804±0.0135 | 0.9902±0.0223 | 71.7% | 조건부 | `COMMS/desktop.md:997,1113` 71.73% 조건부 | ✅ |
| saIm0667 | laptop | 1.3682±0.0301 | 1.0269±0.0387 | 75.1% | 조건부 | `COMMS/desktop.md:1092,1114` 75.05~75.1% 조건부 | ✅ |
| saIm0875 | junseok | 1.2905±0.0333 | 0.9619±0.0181 | 74.5% | 조건부 | `COMMS/junseok.md:3620` 74.5% 조건부 | ✅ |
| saIm0917 | desktopcliff | 1.3249±0.0258 | 0.9725±0.0143 | 73.4% | 조건부 | `COMMS/desktop.md:1494,1557` 73.41% | ✅ |
| saIm0958 | desktopcliff | 1.5205±0.0129 | 1.0032±0.0312 | 66.0% | 조건부 | `COMMS/desktop.md:1494,1579,1982` 65.98% | ✅ |

이상 없음 — 확인 가능한 6개 조성/출처 조합 전부 문서 기재와 재계산이
일치함(09-03 감사와 동일, 자료 변경 없음). 관문 80/50/0 기준으로 전부
"50~80% 조건부" 구간에 있고 "유효"·"종료" 경계를 넘는 곳은 없음. 어긋나는
곳을 찾지 못함.

### 6) WC 자료 공백

`regen_energy_v3.py:load_wc()` 가 실제로 읽는 글롭 패턴(`v3_wc/*.json`,
`v3_humid_wc/*.json`, `v4_humid_wc/*.json`)을 그대로 파이썬으로 재현:

| 조성 | 건조 WC | 습윤 WC | 재생에너지 계산에 포함되는가 |
|---|---|---|---|
| base | ✓ `working_capacity.json` | ✓ `humid_working_capacity.json` | ✓ |
| saIm025 | ✓ 〃 | ✓ `humid_working_capacity_ext.json` | ✓ |
| saIm050 | ✓ 〃 | ✓ `humid_working_capacity.json` | ✓ |
| saIm075 | ✓ 〃 | ✓ 〃 | ✓ |
| saIm100 | ✓ 〃 | ✓ 〃 | ✓ |
| mslm075 | ✓ 〃 | ✓ `humid_working_capacity_mslm075.json` | ✓ |
| **saIm0583 (승자 조성)** | ✓ `working_capacity_g0583.json` | ✓ `humid_working_capacity_g0583.json` | ✓ |
| saIm0625 | — 없음 | ✓ `humid_working_capacity_grid.json` | ✗ (건조 없어 계산 불가) |
| ms50nb50 | — 없음 | ✓ `v4_humid_wc/..._v4ext.json` | ✗ |
| sa25nb75 | — 없음 | ✓ `v4_humid_wc/..._v4ext.json` | ✗ |
| sa50nb50 | — 없음 | ✓ `v4_humid_wc/..._v4m1.json` | ✗ |

건조·습윤이 둘 다 있는 조성 7개(base, saIm025, saIm050, saIm075, saIm100,
mslm075, saIm0583)와 습윤만 있는 조성 4개(saIm0625, ms50nb50, sa25nb75,
sa50nb50)로 나뉜다. 건조만 있고 습윤이 없는 조성은 없음.

`regen_energy_v3.json` 을 직접 파싱해 재확인: 산출된 7개 조성이 위 표의
"둘 다 있음" 7개와 정확히 일치. `load_wc()`/`NAMES` 정의(코드 확인,
66~69행)가 `dry_tsa/dry_vsa/wet_tsa/wet_vsa` 넷이 **모두 있는 조성만** 걸러
넣는 것도 재확인 — "한쪽만 있는데 완성된 행처럼 보이는" 위험 없음.

이상 없음(09-03 감사와 동일, 자료 변경 없음).

---

## 사람이 볼 것

- 경고: `junseok-20260822`/`junseok` 두 브랜치 모두 6.3일/5.9일째 정지(196·
  133커밋 뒤처짐, 08-24 기준의 8배·5배), 같은 기기의 `COMMS/junseok.md`
  우편함도 5.9일 침묵 — 세 신호가 같은 시기(08-29)에 함께 멈춰 회복 안 됨.
- 경고: `laptop-20260822` 가 37커밋 뒤처짐(08-24 기준 24 초과)이나 20시간
  전까지 그 브랜치에 직접 커밋 중 — 정지가 아니라 병합 지연으로 보임.
- 나머지(JSON 무결성·출처 중복·사전 등록 관문·WC 자료 공백)는 이상 없음.

---

## 2026-09-03 00:12 UTC — 일일 감사

**실행 조건**: 클라우드 저장소 체크아웃만으로 확인. 로컬 프로세스·메모리·
미푸시 커밋은 볼 수 없음. 새 계산 없음(`regen_energy_v3.py` 등은 실행하지
않고 파이썬으로 입력 JSON 을 직접 읽어 같은 로직을 재현함). 아래 6개 점검
외 어떤 파일도 수정하지 않음.

**방법 참고**: 직전 감사 항목이 **2026-08-29**로, 이번 감사까지 **5일 공백**이
있었다(자동 감사 루틴 자체가 그동안 돌지 않음 — 대상 계산이나 저장소
문제가 아니라 이 스케줄 실행의 공백). 이 컨테이너도 얕은 클론으로
시작했고, `git fetch --all` 직후 브랜치 비교 수치가 `laptop-20260822`
앞섬 346커밋처럼 비정상으로 나와(08-29 감사가 기록한 것과 같은 종류의
얕은 클론 아티팩트) `git fetch --unshallow` 로 다시 계산했다. 아래 1절은
**언셸로우 후** 값이다.

### 1) 브랜치 정체

`git fetch --all` (+ `--unshallow`) 후 (기준 시각 2026-09-03 00:11 UTC):

| 브랜치 | 마지막 커밋 | 경과 | master 대비 뒤처짐 | master 대비 앞섬 |
|---|---|---|---|---|
| `origin/master` | `4f41696` 2026-09-03 08:30:43 KST | 0.6시간 | — | — |
| `origin/laptop-20260822` | `fcd7313` 2026-09-03 03:10:13 KST | 6.0시간 | **4커밋** | 50커밋 |
| `origin/junseok-20260822` | `41fb1b7` 2026-08-29 00:54:23 KST | **128.2시간(5.3일)** | **50커밋** | 0커밋 |

(참고, 지시된 세 브랜치 밖: `origin/laptop2-20260825` `ad931aa`
2026-09-03 09:10:35 KST, 1.0시간 경과, master 대비 99커밋 뒤처짐 /
25커밋 앞섬 — 기준(24)을 넘지만 지시 범위 밖이라 경고에 안 넣음.)

**경고: `junseok-20260822` 가 `origin/master` 보다 50커밋 뒤처졌고, 마지막
커밋이 5.3일 전이다.** 08-24 사고 기준(24커밋 이상 경고)의 두 배를 넘는다.
`laptop-20260822` 는 4커밋 뒤처짐으로 기준 미만이며 6시간 전까지 계속
커밋되고 있어 정상 범위. (참고: 08-29 감사는 laptop 이 77커밋 뒤처졌다고
기록했는데, 지금은 4커밋뿐이다 — 그 사이 laptop 의 커밋 다수가 `master` 에
병합됐고(예: `9c8bb3e Merge remote-tracking branch 'origin/master' into
laptop-20260822`), laptop 은 그 뒤로도 50커밋을 새로 쌓았다. 격차가 좁혀진
것이지 이상이 아니다.)

### 2) 우편함 침묵

각 우편함 파일의 마지막 갱신 커밋 시각(경과 시간만 보고, 침묵을 "죽었다"로
단정하지 않음):

| 파일 | 마지막 커밋 | 경과 |
|---|---|---|
| `COMMS/desktop.md` | `30e2ef4` 2026-09-03 02:50:56 KST | 6.3시간 |
| `COMMS/junseok.md` | `c557111` 2026-08-29 11:19:28 KST | 117.8시간(4.9일) |
| `COMMS/laptop.md` | `d5dd7f7` 2026-08-28 05:35:52 KST | 147.5시간(6.1일) |

`COMMS/junseok.md` 침묵(117.8시간)이 1절의 `junseok-20260822` 브랜치 정체
(128.2시간)와 같은 방향으로 겹친다 — 브랜치도 우편함도 같은 시기(08-29
전후)에 멈췄다. "죽었다"고 단정하지는 않되, 두 신호가 같은 기기에서 함께
멈췄다는 사실 자체는 경고로 올린다.

`COMMS/laptop.md` 는 147.5시간 침묵이지만 `laptop-20260822` 브랜치 자체는
6시간 전까지 계속 커밋되고 있다(1절 참고) — 08-29 감사가 기록한 "계산은
계속하면서 우편함만 갱신을 멈춘" 패턴이 그대로 이어지고 있고, 침묵 기간이
82.8시간(08-29) → 147.5시간(오늘)으로 더 길어졌다.

### 3) 결과 JSON 무결성

`results_v3*.json`, `v3_wc/`, `v3_humid_wc/`, `v4_humid_wc/`, `v3_water_grid*/`
아래 모든 `.json` 을 파이썬으로 파싱(`{"rows": [...]}` dict 는 `rows` 배열
길이, 순수 리스트는 원소 수를 행수로 셈):

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

이상 없음 — 파싱 실패·0행 없음. 08-29 감사 표와 행수 전부 동일. `git log`
로 확인한 결과 `origin/master` 기준 이 경로들을 마지막으로 건드린 커밋은
`a118db7`(2026-08-27 12:40:42 KST)로, 08-29 감사 이후는 물론 이번 감사
시점까지도 이 자료들에 변경이 없었다.

### 4) 출처 규약 위반

`merge_water_batches.py` 의 `machine_of()` 는 `water_results_<기기>.json`
형식이 아니면 거부한다(2026-08-23 이중 계수 사고 이후 도입). 태그 붙은
파일만 서로 비교:

- `v3_water_grid/`: `water_results_desktop4.json`(saIm0583) ·
  `water_results_junseok.json`(saIm0875) · `water_results_laptop.json`
  (saIm0625·saIm0667·saIm0875) — (조성,RH) 조합 중 `(saIm0875, 0.0/0.25/
  0.5/0.9)` 4개가 junseok/laptop 양쪽에 있음. **값이 서로 다름**(RH0 junseok
  1.2905±0.0333 vs laptop 1.3031±0.0215, RH90 junseok 0.9619±0.0181 vs
  laptop 0.9671±0.0482) → **진짜 교차검증**이지 중복이 아님.
- `v3_water_grid_cliff/`: 태그 파일이 `water_results_desktopcliff.json`
  하나뿐(saIm0917·saIm0958) — 애초에 중복·교차검증 대상이 없음.

이상 없음 — 태그 붙은 파일 사이에서 값이 동일한 (조성,RH) 중복은 없음.

참고(경고 아님, 08-29 감사와 동일): 두 디렉터리 모두 기기 태그 없는
`water_results.json` 이 따로 있고, 값이 각각 `water_results_desktop4.json`,
`water_results_desktopcliff.json` 과 바이트 단위로 동일함(이어받기 체크포인트
사본). `machine_of()` 가 태그 없는 파일을 구조적으로 거부하므로
`merge_water_batches.py` 를 규약대로(태그 파일만 명시) 쓰는 한 이중 계수로
이어지지 않음.

### 5) 사전 등록 관문 대비 기록

`v3_water_grid*/` 태그 파일에서 RH0·RH90 로딩으로 유지율을 직접 재계산
(각 행의 `CO2_retention_pct` 필드가 `RH90_CO2/RH0_CO2*100` 재계산값과 같음을
확인, 관문 80/50/0):

| 조성 | 출처 | RH0 | RH90 | 재계산 유지율 | 재계산 판정 | 문서 기재값 | 일치 |
|---|---|---|---|---|---|---|---|
| saIm0583 | desktop4 | 1.3188±0.0264 | 1.0010±0.0170 | 75.90% | 조건부 | `COMMS/desktop.md:742` 75.90±1.99% 조건부 | ✅ |
| saIm0625 | laptop | 1.3804±0.0135 | 0.9902±0.0223 | 71.74% | 조건부 | `COMMS/laptop.md:359,366` 71.7% 조건부 | ✅ |
| saIm0667 | laptop | 1.3682±0.0301 | 1.0269±0.0387 | 75.06% | 조건부 | `COMMS/desktop.md:916` 75.05±3.28% 조건부 | ✅ |
| saIm0875 | junseok | 1.2905±0.0333 | 0.9619±0.0181 | 74.54% | 조건부 | `COMMS/junseok.md:8,71` 74.5% 조건부 | ✅ |
| saIm0875 | laptop | 1.3031±0.0215 | 0.9671±0.0482 | 74.21% | 조건부 | `COMMS/laptop.md:320` 74.2±3.9pp | ✅ |
| saIm0917 | desktopcliff | 1.3249±0.0258 | 0.9725±0.0143 | 73.41% | 조건부 | `COMMS/desktop.md:1296,1359` 73.4 | ✅ |
| saIm0958 | desktopcliff | 1.5205±0.0129 | 1.0032±0.0312 | 65.98% | 조건부 | `COMMS/desktop.md:1296,1374` 66.0 | ✅ |

이상 없음 — 확인 가능한 7개 조성/출처 조합 전부 문서 기재와 재계산이
일치함(08-29 감사와 동일 수치, 자료 변경 없음). 관문 80/50/0 기준으로 전부
"50~80% 조건부" 구간에 있고 "유효"·"종료" 경계를 넘는 곳은 없음. 어긋나는
곳을 찾지 못함.

### 6) WC 자료 공백

`regen_energy_v3.py` 를 실행하지 않고 소스만 읽어, 실제로 읽는 글롭 패턴
(`v3_wc/*.json`, `v3_humid_wc/*.json`, `v4_humid_wc/*.json`)을 그대로
재현해 파이썬으로 확인:

| 조성 | 건조 WC | 습윤 WC | 재생에너지 계산에 포함되는가 |
|---|---|---|---|
| base | ✓ `working_capacity.json` | ✓ `humid_working_capacity.json` | ✓ |
| saIm050 | ✓ 〃 | ✓ 〃 | ✓ |
| saIm075 | ✓ 〃 | ✓ 〃 | ✓ |
| saIm100 | ✓ 〃 | ✓ 〃 | ✓ |
| saIm025 | ✓ `working_capacity.json` | ✓ `humid_working_capacity_ext.json` | ✓ |
| mslm075 | ✓ `working_capacity.json` | ✓ `humid_working_capacity_mslm075.json` | ✓ |
| **saIm0583 (승자 조성)** | ✓ `working_capacity_g0583.json` | ✓ `humid_working_capacity_g0583.json` | ✓ |
| saIm0625 | — 없음 | ✓ `humid_working_capacity_grid.json` | ✗ (건조 없어 계산 불가) |
| ms50nb50 | — 없음 | ✓ `v4_humid_wc/..._v4ext.json` | ✗ |
| sa25nb75 | — 없음 | ✓ `v4_humid_wc/..._v4ext.json` | ✗ |
| sa50nb50 | — 없음 | ✓ `v4_humid_wc/..._v4m1.json` | ✗ |

건조·습윤이 둘 다 있는 조성 7개(base, saIm050, saIm075, saIm100, saIm025,
mslm075, saIm0583)와 습윤만 있는 조성 4개(saIm0625, ms50nb50, sa25nb75,
sa50nb50)로 나뉜다. 건조만 있고 습윤이 없는 조성은 없음.

`regen_energy_v3.json` 을 직접 파싱해 재확인: 산출된 7개 조성이 위 표의
"둘 다 있음" 7개와 정확히 일치. 소스(`regen_energy_v3.py:66-69`)도
`dry_tsa/dry_vsa/wet_tsa/wet_vsa` 넷과 `Q_st` 가 **모두 있는 조성만** 걸러
넣는 것을 재확인 — "한쪽만 있는데 완성된 행처럼 보이는" 위험 없음.

이상 없음(08-29 감사와 동일, 자료 변경 없음).

---

## 사람이 볼 것

- 경고: `junseok-20260822` 브랜치가 `origin/master` 보다 **50커밋** 뒤처졌고
  마지막 커밋이 **5.3일 전**(08-24 사고 기준 24커밋의 두 배 초과). 같은
  기기의 `COMMS/junseok.md` 우편함도 **4.9일** 침묵 — 브랜치·우편함이 같은
  시기에 함께 멈춰, 그 기기가 5일 넘게 실제로 정지했을 가능성이 있음.
- 참고: `laptop-20260822` 브랜치는 6시간 전까지 활동 중(4커밋 뒤처짐,
  정상)이나 `COMMS/laptop.md` 우편함은 **6.1일** 침묵 — "계산은 계속,
  우편함만 멈춤" 패턴이 08-29 대비 더 길어짐(82.8h → 147.5h).
- 나머지(JSON 무결성·출처 중복·사전 등록 관문·WC 자료 공백)는 이상 없음,
  08-29 감사 이후 관련 자료 변경 없음.

---

## 2026-08-29 00:11 UTC — 일일 감사

**실행 조건**: 클라우드 저장소 체크아웃만으로 확인. 로컬 프로세스·메모리·
미푸시 커밋은 볼 수 없음. 새 계산 없음(`regen_energy_v3.py` 등은 실행하지
않고 파이썬으로 입력 JSON 을 직접 읽어 같은 로직을 재현함). 아래 6개 점검
외 어떤 파일도 수정하지 않음.

**방법 참고**: 이 컨테이너의 최초 클론이 `--depth 50` 얕은 클론이라 첫
`git fetch --all` 직후 `origin/master` 가 "forced-update"로 보고됐다(캐시된
얕은 히스토리 기준으로는 조상 관계를 판단할 수 없어서). 실제 강제 푸시가
아니라 얕은 클론의 로컬 아티팩트임을 `git fetch --unshallow` 로 확인했고,
아래 브랜치 비교(1절)는 전부 **언셸로우 후** 재계산한 값이다.

### 1) 브랜치 정체

`git fetch --all` (+ `--unshallow`) 후 (기준 시각 2026-08-29 00:11 UTC):

| 브랜치 | 마지막 커밋 | 경과 | master 대비 뒤처짐 | master 대비 앞섬 |
|---|---|---|---|---|
| `origin/master` | `4c8afa2` 2026-08-29 05:59:21 KST | 3.2시간 | — | — |
| `origin/laptop-20260822` | `41947e5` 2026-08-29 05:57:01 KST | 3.2시간 | **77커밋** | 45커밋 |
| `origin/junseok-20260822` | `41fb1b7` 2026-08-29 00:54:23 KST | 8.3시간 | 13커밋 | 49커밋 |

(참고, 지시된 세 브랜치 밖: `origin/laptop2-20260825` `0cb88fe`
2026-08-29 02:17:51 KST, 6.9시간 경과, master 대비 13커밋 뒤처짐 /
13커밋 앞섬 — 기준 미만.)

**경고: `laptop-20260822` 가 `origin/master` 보다 77커밋 뒤처졌습니다**
(`git rev-list --left-right --count origin/master...origin/laptop-20260822`
→ `77  45`). 08-24 사고 기준(24커밋 이상 경고)을 크게 넘고, 전일 감사
(08-28, 50커밋)보다도 더 벌어졌습니다. `origin/master` 는 지난 24시간
(2026-08-28 00:00 KST 이후) 동안 49개의 새 커밋을 받아(`git rev-list --count
origin/master --since="2026-08-28T00:00:00+09:00"`) 계속 빠르게 확산 중이고,
`laptop-20260822` 자신도 그 사이 45개의 자기 커밋을 쌓고 있어 죽은 브랜치는
아니다(최근 커밋이 3.2시간 전). 다만 **이 브랜치만 읽는 세션은 master 의
최근 판정·문서를 "없다"고 오인할 위험**이 08-24 사고와 같은 형태로 남아
있고, 격차가 이틀 연속(50 → 77) 벌어지고 있어 다음 인계 때 더 커질 수 있다.

`junseok-20260822`(13커밋)는 기준 미만으로 정상.

### 2) 우편함 침묵

각 우편함 파일의 마지막 갱신 커밋 시각(경과 시간만 보고, 침묵을 "죽었다"로
단정하지 않음):

| 파일 | 마지막 커밋 | 경과 |
|---|---|---|
| `COMMS/desktop.md` | `9a3ef6e` 2026-08-28 20:36:55 KST | 12.6시간 |
| `COMMS/junseok.md` | `9ef61ae` 2026-08-29 06:05:12 KST | 3.1시간 |
| `COMMS/laptop.md` | `fc1b401` 2026-08-25 22:23:20 KST | 82.8시간 |
| `COMMS/laptop2.md` (`laptop2-20260825` 브랜치에만 존재, master 미병합) | `0cb88fe` 2026-08-29 02:17:51 KST | 6.9시간 |

이상 없음(단정적 "죽었다" 판정 없이 경과만 보고) — 다만 전일과 같은 패턴이
이어짐: `COMMS/laptop.md` 는 82.8시간(3.4일) 갱신이 없는데
`laptop-20260822` 브랜치 자체는 3.2시간 전(`41947e5`)까지 계속 커밋되고
있다(1절 참고). **랩탑은 계산은 계속하면서 우편함만 갱신을 멈춘 상태**로
읽히고, 1절의 77커밋 격차와 결합하면 랩탑 세션이 master 의 최신 문서를
놓치고 있을 가능성과 다른 세션이 랩탑의 최신 진행을 놓치고 있을 가능성이
동시에 커지고 있다.

### 3) 결과 JSON 무결성

`results_v3*.json`, `v3_wc/`, `v3_humid_wc/`, `v4_humid_wc/`, `v3_water_grid*/`
아래 모든 `.json` 을 파이썬으로 파싱(`{"rows": [...]}` dict 는 `rows` 배열
길이, 순수 리스트는 원소 수를 행수로 셈):

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

이상 없음 — 파싱 실패·0행 없음. 전일(08-28) 표와 행수 전부 동일 — 이
구간(`results_v3*.json`/`v3_wc/`/`v3_humid_wc/`/`v4_humid_wc/`/
`v3_water_grid*/`)에는 자료 변경이 없었음.

### 4) 출처 규약 위반

`merge_water_batches.py` 의 `machine_of()` 는 `water_results_<기기>.json`
형식이 아니면 거부한다(2026-08-23 이중 계수 사고 이후 도입). 태그 붙은
파일만 서로 비교:

- `v3_water_grid/`: `water_results_desktop4.json`(saIm0583) ·
  `water_results_junseok.json`(saIm0875) · `water_results_laptop.json`
  (saIm0625·saIm0667·saIm0875) — (조성,RH) 조합 중 `(saIm0875, 0.0/0.25/
  0.5/0.9)` 4개가 junseok/laptop 양쪽에 있음. **값이 서로 다름**(RH0 junseok
  1.2905±0.0333 vs laptop 1.3031±0.0215, RH90 junseok 0.9619±0.0181 vs
  laptop 0.9671±0.0482) → **진짜 교차검증**이지 중복이 아님
  (`v3_water_grid/README.md` 도 같은 결론, 0.03σ 로 문서화돼 있음).
- `v3_water_grid_cliff/`: 태그 파일이 `water_results_desktopcliff.json`
  하나뿐(saIm0917·saIm0958) — 애초에 중복·교차검증 대상이 없음.

이상 없음 — 태그 붙은 파일 사이에서 값이 동일한 (조성,RH) 중복은 없음.

참고(경고 아님, 전일과 동일): 두 디렉터리 모두 기기 태그 없는
`water_results.json` 이 따로 있고, 값이 각각 `water_results_desktop4.json`,
`water_results_desktopcliff.json` 과 바이트 단위로 동일함(이어받기 체크포인트
사본, `v3_water_grid/README.md` 에 그 경위가 문서화돼 있음). `machine_of()`
가 태그 없는 파일을 구조적으로 거부하므로 `merge_water_batches.py` 를
규약대로(태그 파일만 명시) 쓰는 한 이중 계수로 이어지지 않음.

### 5) 사전 등록 관문 대비 기록

`v3_water_grid*/` 태그 파일에서 RH0·RH90 로딩으로 유지율을 직접 재계산
(각 행의 `CO2_retention_pct` 필드가 `RH90_CO2/RH0_CO2*100` 재계산값과 같음을
확인, 관문 80/50/0):

| 조성 | 출처 | RH0 | RH90 | 재계산 유지율 | 재계산 판정 | 문서 기재값 | 일치 |
|---|---|---|---|---|---|---|---|
| saIm0583 | desktop4 | 1.3188±0.0264 | 1.0010±0.0170 | 75.90% | 조건부 | `COMMS/desktop.md:914` 75.90±1.99% 조건부 | ✅ |
| saIm0625 | laptop | 1.3804±0.0135 | 0.9902±0.0223 | 71.74% | 조건부 | `COMMS/laptop.md:359,366` 71.7% 조건부 | ✅ |
| saIm0667 | laptop | 1.3682±0.0301 | 1.0269±0.0387 | 75.06% | 조건부 | `COMMS/desktop.md:916` 75.05±3.28% 조건부 | ✅ |
| saIm0875 | junseok | 1.2905±0.0333 | 0.9619±0.0181 | 74.54% | 조건부 | `COMMS/junseok.md:72` 74.5% 조건부 | ✅ |
| saIm0875 | laptop | 1.3031±0.0215 | 0.9671±0.0482 | 74.21% | 조건부 | `COMMS/laptop.md:320` 74.2±3.9pp | ✅ |
| saIm0917 | desktopcliff | 1.3249±0.0258 | 0.9725±0.0143 | 73.41% | 조건부 | `COMMS/desktop.md:1296,1359` 73.4 | ✅ |
| saIm0958 | desktopcliff | 1.5205±0.0129 | 1.0032±0.0312 | 65.98% | 조건부 | `COMMS/desktop.md:1296,1374` 66.0 | ✅ |

이상 없음 — 확인 가능한 7개 조성/출처 조합 전부 문서 기재와 재계산이
일치함(전일 감사와 동일 수치, 자료 변경 없음). 어긋나는 곳을 찾지 못함.

### 6) WC 자료 공백

`regen_energy_v3.py` 를 실행하지 않고 소스만 읽어, 실제로 읽는 글롭 패턴
(`results_v3*.json`, `v3_wc/*.json`, `v3_humid_wc/*.json`,
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

`regen_energy_v3.json` 을 직접 파싱해 재확인: 산출된 7개 조성이 위 표에서
"✓/✓/✓" 인 7개(base, mslm075, saIm025, saIm050, saIm0583, saIm075, saIm100)와
정확히 일치. 소스(`regen_energy_v3.py:66-69`)도 `dry_tsa/dry_vsa/wet_tsa/
wet_vsa` 넷과 `Q_st` 가 **모두 있는 조성만** 걸러 넣는 것을 재확인 — "한쪽만
있는데 완성된 행처럼 보이는" 위험 없음. 08-26/27 경고(승자 조성 누락)는
08-27 `455e5c2` 로 이미 고쳐졌고 이후 변화 없음.

이상 없음(전일과 동일, 자료 변경 없음).

---

## 사람이 볼 것

- 경고: `laptop-20260822` 브랜치가 `origin/master` 보다 **77커밋** 뒤처짐
  (08-27 6커밋 → 08-28 50커밋 → 오늘 77커밋으로 이틀 연속 급증, 08-24 사고
  기준 24커밋의 3배 이상). master 는 24시간 새 49커밋을 받는 정상적 확산
  중이나, 이 브랜치만 보는 세션은 master 최신 문서를 "없다"고 오인할 위험이
  있고 격차가 계속 벌어지는 추세.
- 참고: `COMMS/laptop.md` 우편함이 82.8시간(3.4일) 갱신되지 않음. 브랜치
  자체는 3.2시간 전까지 계속 커밋 중이라 "죽었다"는 아니지만, 위 브랜치
  경고와 겹쳐 랩탑↔다른 기기 간 정보 교환이 함께 막혀 있을 가능성.
- 나머지 항목(JSON 무결성·출처 중복·사전 등록 관문 기록·WC 자료 공백)은
  이상 없음, 전일 대비 자료 변경도 없음.

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
