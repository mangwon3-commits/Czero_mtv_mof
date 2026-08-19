# 계산 지원 관련 회신 (2026-08-19)

세 가지 지적 모두 정확했습니다. 확인한 내용을 순서대로 답하되,
**질문보다 먼저 말씀드려야 할 것이 하나** 있어 0번으로 올립니다.

---

## 0. 먼저 — `run_gcmc_v3.py` 는 돌리지 말아 주십시오

**v3 GCMC 는 이미 완료되었습니다.** 저희 쪽 `results_v3.json` 에 31종 전부
`status: ok` 로 들어 있고 08-18 새벽에 완주했습니다. 지금 실행하시면 이미
끝난 계산을 반복하는 것이 되어 며칠을 소모하게 됩니다.

READ ME 2 는 꾸러미를 만들 당시의 문서이고, 그 사이 저희 쪽에서 해당
계산이 끝났습니다. 최신 배정을 반영하지 못한 문서를 보내드린 점 죄송합니다.

**현재 부탁드리는 작업은 수분 경쟁 v3 하나입니다** (`EXTERNAL_WATER_V3.md`).

```bash
cd ~/mof_project/21_ZIF69_MTV
export RASPA_DIR=$HOME/RASPA/simulations
export PATH=$HOME/miniconda3/envs/czeromof/bin:$PATH
WATER_V3_WORKERS=16 python run_water_v3.py 2>&1 | tee water_v3.log
```

- 대상: 5조성 x RH 0/25/50/90 = 20 작업, 16코어에서 약 24시간
- 완료 파일: `v3_water/water_results.json`
- 회신 시 `water_results.json` + `water_v3.log` 를 tar.gz 로 묶고
  sha256 을 동봉해 주시면 감사하겠습니다

**이미 이 작업을 시작하셨다면 그대로 두시고**, 아직이라면 이것부터
시작해 주십시오. 현재 진행 상황을 알려 주시면 저희 일정을 맞추겠습니다.

---

## 1. `charged_v3.json` / `rebuild_index.json` — 꾸러미 누락입니다

두 파일 모두 저희 저장소에는 있고 git 으로 추적 중입니다
(각각 778 B, 12.6 kB). 꾸러미 제작 스크립트가 담지 않았습니다.

다만 **0번대로 GCMC 를 돌리지 않으시면 두 파일 모두 필요 없습니다.**
`run_water_v3.py` 는 이 파일들을 읽지 않습니다.

---

## 2. Zeo++ — 수분 경쟁 러너는 아예 호출하지 않습니다

`run_water.py` 와 `run_water_v3.py` 에는 `zeo()` 호출도 `network` 실행도
**없습니다.** 부탁드린 작업에는 Zeo++ 메모리 위험이 없습니다.

그리고 **스크립트 주석의 "건당 3.2 GB" 는 오래된 값입니다.** 그 수치는
이완 전(v1) 구조에서 측정한 것이고, v3 구조는 이완으로 셀이 34% 수축해
슈퍼셀 원자 수가 늘었습니다. 저희가 어제 다른 기기에서 실측한 값은
**건당 10.29 GB** 였습니다. 즉 지적하신 위험이 문서에 적힌 것보다
3배 이상 큽니다. 주석을 신뢰하고 워커 수를 잡으면 위험합니다.

선택지 중에서는 **(a) 가 맞습니다.** LCD / PLD / AV 는 저희 쪽
`results_v3.json` 에 31종 전부 들어 있습니다. 필요하시면 보내드리겠습니다.

---

## 3. `molecules/TraPPE/` 가 맞습니다 — 다만 수치는 바뀌지 않습니다

탐색 순서 분석이 정확합니다. `$RASPA_DIR/share/raspa/molecules/CO2.def`
는 읽히지 않습니다. 올바른 위치는 다음 둘입니다.

```
$RASPA_DIR/share/raspa/molecules/TraPPE/CO2.def
$RASPA_DIR/share/raspa/molecules/TraPPE/N2.def
```

**그런데 확인해 보니 꾸러미의 두 파일은 RASPA 배포본의
`molecules/TraPPE/` 아래 같은 이름 파일과 바이트 단위로 동일했습니다.**

CO2 / N2 는 def 파일에서 **기하만** 오고 Lennard-Jones 계수와 부분전하는
`forcefield/UFF_MOF/` 의 두 파일에서 옵니다. 배포본 TraPPE 기하를 그대로
쓰는 것이 원래 의도이므로, 위치가 잘못되어 배포본 파일이 읽히더라도
**조용히 다른 값이 실리지는 않습니다.** 옮겨 두시면 의도가 명시적이 되지만
결과는 같습니다.

### 정작 중요한 것은 물이고, 그것은 다른 경로로 처리되어 있습니다

`run_water.py` 는 실행 폴더에 CIF 와 **`water.def` 를 함께 복사합니다**
(190~191행). 그러면 탐색 순서 1번(`./water.def`)이 이기므로 저희
**TIP5P-Ew 5사이트** 파일이 사용되고, 배포본의 3사이트
`molecules/TraPPE/water.def` 는 읽히지 않습니다.

CO2 와 달리 물은 **def 파일이 사이트 개수 자체를 정하므로**, 여기서
틀리면 결과가 통째로 무효가 됩니다. 확인 방법은 두 가지입니다.

```bash
grep -A1 "Number Of Atoms" 19_WaterCompetition/water.def   # 5 가 나와야 합니다
ls water_runs_v3/*/water.def                                # 실행 폴더마다 있어야 합니다
```

**`19_WaterCompetition/water.def` 를 옮기거나 이름을 바꾸지 말아 주십시오.**
러너가 상대경로로 찾습니다.

---

## 마지막으로

세 지적 모두 스크립트를 실제로 읽지 않으면 나올 수 없는 것들이었고,
특히 3번은 저희도 파일을 대조하기 전에는 "결과가 같다" 고 말할 수
없었습니다. 실행 전에 확인해 주신 덕분에 불확실한 상태로 24시간을
돌리는 일을 피했습니다. 감사합니다.

문의사항이 있으시면 언제든 알려 주십시오.
