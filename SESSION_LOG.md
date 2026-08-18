# 세션 로그 — 누가 무엇을 하고 있는가

**여러 Claude 세션이 같은 작업 디렉터리(`~/mof_project`)를 공유합니다.**
별도 클론이 아니라 한 트리를 나눠 쓰므로 git 병합 충돌은 안 생기지만,
**같은 파일 동시 편집**과 **같은 코어 경합**은 실재합니다.

새 세션은 이 파일을 **가장 먼저** 읽으세요. 그리고 작업을 시작·종료할 때
맨 위에 한 항목씩 추가하세요(최신이 위).

## 규약

```
## MM-DD HH:MM · <세션>  [진행중|완료|중단]
하는 일:
건드리는 파일:
쓰는 코어:
다음:
```

- **코어 예산은 물리 8개입니다**(논리 16). 시작 전에 `pgrep -c simulate`,
  `pgrep -c lmp_serial` 로 남은 여유를 확인하고, 여유만큼만 워커를 잡으세요.
- **Zeo++(`network`)는 한 건에 3.2 GB** 입니다. RASPA 가 무겁게 돌 때
  `risk_screen.py` 를 동시에 띄우지 마세요 — 2026-08-12 에 이 조합이 OOM 을 냈고
  `dbus-daemon` 까지 죽어 WSL 배포판이 통째로 먹통이 됐습니다.
- RASPA `simulate` 는 한 건에 약 471 MB 라 메모리가 병목이 아닙니다. 8이 상한.

## 08-18 00:48 · laptop (Windows 11 + WSL2, Ryzen 9 5900HS)  [진행중]

하는 일: **작업 용량 v3** — `run_wc_v3.py`, 6종 × 4조건 = **24작업**.
  데스크탑의 임계 경로에서 떼어낸 배치입니다(`LAPTOP_QUICKSTART.md`).

건드리는 파일: `21_ZIF69_MTV/wc_runs_v3/`, `v3_wc/working_capacity.json`,
  `wc_v3.log`, `wc_v3_status.log`

쓰는 코어: **6** (물리 8 중). **다른 기기입니다** — 저장소는 같지만 작업
  디렉터리를 공유하지 않으므로 데스크탑과 코어 경합이 없습니다. 스로틀링을
  60초 창으로 계측 중이며 성능비 110% 대로 여유가 있습니다(공칭 클럭 위).

다음: 완주하면 `v3_wc/working_capacity.json` 을 전달합니다. 비교표는 앞의
  다섯만 v2 와 나란히 놓고 saIm100 은 신규 항목으로 답니다. saIm100 행에는
  "습윤 조건에서 여유가 가장 적은 조성"(RH90 유지율 58.5%, 물 2.7887 mol/kg)을
  함께 적습니다.

### 인계 과정에서 확인한 것

- 꾸러미 `MTV-ZIF_계산지원` 에 `run_working_capacity.py` 와 `run_gcmc_v2.py` 가
  빠져 있었습니다. `_fixed` 로 다시 받아 해결했습니다(해시 `1f3a9c73…` 일치).
- 빠진 동안 복원판으로 잠시 돌렸다가 원본으로 교체하면서 **`wc_runs_v3/` 를
  통째로 비웠습니다**(CLAUDE.md §3). 완료 작업 0건 시점이라 손실 없습니다.
- 대조 결과: CIF 6종 SHA256 · `run_working_capacity.py` · `run_aryl_gcmc.py`
  모두 원격과 **일치**. `run_wc_v3.py` 만 달랐는데 docstring 단일 헝크이고
  `TARGETS`·`MAX_WORKERS`·경로 등 실행 코드는 동일합니다.
- 힘장은 랩탑 설치본이 꾸러미와 바이트 단위로 같았습니다. `C_co2` ε 29.933 /
  σ 2.745, `q_C` +0.6512 확인.

### 랩탑 환경 함정 (다음 사람을 위해)

- **`RASPA_DIR` 이 비대화형 셸에서 안 잡힙니다.** 우분투 `.bashrc` 는 비대화형
  셸에서 조기 return 합니다. 게다가 conda 배포본 `share/raspa` 에는 `UFF_MOF` 가
  **없어서** export 없이 띄우면 조용히 틀리는 게 아니라 즉시 실패합니다.
- 한글이 든 경로(`~/MTV-ZIF_계산지원`)를 피해 `~/mof_project/21_ZIF69_MTV/` 에서
  실행합니다.
- CLAUDE.md §4 를 읽기 전에 §4 의 함정에 걸렸습니다 — `.data` **파일 개수**를
  완료 건수로 세어 7/24 로 오보했습니다. RASPA 는 `.data` 를 시작할 때 만듭니다.
  완료 판정은 `Average loading absolute [mol/kg framework]` 블록의 유무로 해야
  합니다. 감시기를 그렇게 고쳤습니다.

### 이 저장소에 아직 없는 랩탑 작업

`21_LinkerDesign/` (`DESIGN_BRIEF.md`, `evidence.json`, `collect_evidence.py`) 이
로컬 커밋 `30b811e` 에만 있고 원격에는 없습니다. 랩탑 계보(2커밋)와 원격
계보(73커밋)가 `fec3c3a` 에서 갈라져 있어 이번에는 합치지 않았습니다 —
계산이 도는 중에 `21_ZIF69_MTV/` 45개 파일이 체크아웃 충돌 대상이기 때문입니다.
완주 후 정리 예정.

## 08-16 23:55 · 무인 v3 파이프라인  [진행중]

하는 일: `overnight.sh` 가 v3 를 끝까지 잇습니다 — 이완 30종 완주 대기 → 판정 →
  정리 → PACMAN 전하 → **연기 시험(모체 1종)** → GCMC v3 90작업. 단계마다
  관문이 있고 못 넘으면 다음으로 안 갑니다. 수분 v2 는 **떼어내서 병렬**입니다
  (마지막 1건이 22~26시간이라 v3 를 묶어 두면 하루를 서서 기다립니다).

건드리는 파일: `21_ZIF69_MTV/relax_v3/`, `charged_v3/`, `runs_v3/`,
  `relax_v3_judged.json`, `charged_v3.json`, `results_v3.json`,
  `water_runs_v2/`(수분), `.claude_work/{overnight,relax_v3,water_v2}.log`

쓰는 코어: 이완 3워커×2스레드(nice 19) → 끝나면 **GCMC v3 7워커**(nice 0)
  + 수분 v2 RASPA 1 = 물리 8 포화. 9시간 무인 운전 전제로 잡은 값입니다.

  ⚠️ **Zeo++ 는 이제 스스로 줄입니다.** `run_gcmc_v3.py` 가 `pgrep simulate` 와
  `/proc/meminfo` 를 재서 RASPA 가 돌면 워커를 4→2(6.4 GB)로 낮춥니다.
  무인 실행이라 08-12 조합을 사람이 못 막으므로 코드에 넣었습니다.

끄는 법: `pkill -f "bash overnight.sh"` (단계 사이면 손실 없음).
  이완·수분은 **작업 단위 이어받기**가 있어 다시 띄우면 완주분을 캐시로 회수합니다.

다음: GCMC v3 결과 → v2 대비 비교(1.5σ 미만은 순위 매기지 않음) → 습윤 작업
  용량 v3, 구조 안정성. 노션은 `mof-overnight-sync` 예약 작업이 3시간마다 반영.

## 배경 문서 (맥락을 한 번에 불러오려면 이 순서로)

| 문서 | 무엇이 있나 |
|---|---|
| `21_ZIF69_MTV/STRUCTURE_DEFECT.md` | **2026-08-14 발견. 치환 구조 전부 재계산 필요** |
| `TOOLING.md` | **셸 호출이 깨지는 이유와 확정된 패턴.** 자주 걸립니다 |
| `21_ZIF69_MTV/AUDIT_20260814.md` | **위 결함과 같은 종류를 훑은 감사. 미수정 2건 있음** |
| `00_Migration/MIGRATION.md` 3절 | 계산 환경의 함정 전부(조용한 timeout, OOM, WSL 종료 등) |
| `21_ZIF69_MTV/DRYING_PLAN.md` | 건조 비용 판단 절차와 사전 등록 기준 |
| `21_ZIF69_MTV/DAC_PLAN.md` | DAC 조건 검토 구상(실행 보류) |
| `21_ZIF69_MTV/LINKER_DESIGN_BRIEF.md` | 링커 설계와 빌더 한계 |

---

## 08-14 21:1x · desktop  [진행중] 밀도맵 v2

**`nice 19` 로 돌고 있습니다.** 대기열(`queue_density_v2.sh`)은 **껐습니다** --
살려 두면 나중에 조용해졌을 때 두 번째로 발사합니다.

* 대상: `21_ZIF69_MTV/run_density_v2.py` (`charged_v2` -> `density_v2/`)
* 조성 5 x 전하 ON/OFF = **10작업**, 워커 **4**, 격자 90³, 5000 사이클
* 진행: `~/.claude_work/density_v2.log`

**왜 nice 19 인가** -- 물리 코어 8개에 본 계산(원격 GCMC 6 + 수분 v2 4)이 이미
차 있습니다. nice 19 는 남는 CPU 만 받으므로 본 계산이 느려지지 않습니다.
C-H A/B 4건이 같은 방식으로 완주한 전례가 있습니다.
확인법: `ps -eo ni,cmd | grep simulate` 에서 본 계산이 0, 밀도맵이 19.

**다른 세션에 부탁**: 이건 최저 우선순위라 그냥 두셔도 됩니다. 급하면
`pkill -f run_density_v2` 로 끄세요 -- 이어받기가 되므로 다시 띄우면 됩니다.

왜 다시 뽑나: 기존 `density/` 의 `saIm*` 여덟 폴더는 깨진 구조에서 나온 것이라
무효입니다. `base` 둘만 유효합니다. 게다가 옛 `saIm050` 은 실제 58.3%,
`saIm075` 는 70.8% 였습니다(`AUDIT_20260814.md` 3절) -- 이름표까지 틀렸습니다.

## 08-14 22:xx · desktop  [진행중] 설정 감사

하는 일: **"틀렸는데 아무 검사에도 안 걸리는 것" 전수 감사** → `AUDIT_20260814.md`
건드리는 파일: `21_ZIF69_MTV/AUDIT_20260814.md`(신규), `chtest/`(신규), `~/.claude_work/audit_*`
쓰는 코어: **4 (nice 19)** — C–H 정규화 A/B Widom 4건. 본 계산에 양보하도록 우선순위 최하

찾은 것 세 가지:
1. **모체 CIF 가 기하 최적화 안 됨** — 헤더에 `not optimized`. C–H 144개 전부
   0.949 Å(X선 riding model, 정상 1.083), 벤조 C–C 1.273~1.465. **미수정. v2 도 물려받음**
2. **손님 힘장이 TraPPE 가 아님** — CO₂ 는 García-Sánchez 2009(q_C +0.6512),
   N₂ 는 q −0.405. `MoleculeDefinition TraPPE` 는 **기하만** 고르고 전하·LJ 는
   `Forcefield` 폴더에서 옵니다. **N₂ 사중극자 16% 약 → 선택도 약 15% 과대.**
   조성 간 순위는 무영향(편향이 균일). **문서 표기만 고치면 됨, 재계산 불필요**
3. v1 치환 개수가 이름과 다름 — 모든 `050`=14개(58.3%), `075`=17개(70.8%), 16개 구조.
   **v2 는 30/30 정확** (부착 원자 수정으로 충돌 로직이 발동하지 않게 됨)

통과: 최소 이미지(45.2/45.2/38.8 > 24) · 전하 중성(max 1e-4) · TIP5P-Ew 진위 ·
모체 조성 · Lorentz-Berthelot · Ewald · mol/kg 환산

**다른 세션에 부탁**: 결과를 적을 때 힘장을 "TraPPE" 로 쓰지 마세요.

## 08-14 21:10 · desktop(데스크탑 앱 세션)  [진행중]

하는 일: **수분 경쟁 v2 재계산** (`run_water_v2.py`, saIm 5종 × RH 0/25/50/90 = 20작업)
건드리는 파일: `21_ZIF69_MTV/run_water_v2.py`(신규), `water_runs_v2/`, `water_results_v2.json`
쓰는 코어: **4** (원격이 6을 쓰고 있어 남은 여유만큼만)
왜 이것을 골랐나: `STRUCTURE_DEFECT.md` 8절의 재계산 순서에서 원격이 1~2단계
(Widom → GCMC)를 잡고 있으므로 **3단계(수분 경쟁)** 를 가져왔습니다. 서로 다른
계산이고 입력이 `charged_v2/` 로 같아 의존성이 없습니다.
다음: 끝나면 작업 용량 v2. **`risk_screen.py`(구조 안정성)는 Zeo++ 메모리 때문에
RASPA 가 끝난 뒤에 돌립니다.**

## 08-14 20:xx · remote(tmux `claude-remote`, 아이패드에서 지시)  [진행중]

하는 일: **Widom K_H + 0.15 bar GCMC 재계산** (`run_gcmc_v2.py`)
건드리는 파일: `21_ZIF69_MTV/run_gcmc_v2.py`, `runs_v2/`
쓰는 코어: 6
관측 근거: `runs_v2/widom_{CO2,N2}_saIm{025,050,075}_DDEC6` 에서 `simulate` 6개 확인

## 08-14 · remote  [완료] 커밋 88228a2 ~ 952573b

**치환 구조 결함 발견과 재구축.** `mtv_cif_builder.py` 가 벤조 고리 부착 원자를
고정 상수(`CBIM_ARYL_ATTACHMENT_INDEX = 4`)로 골라 **24개 자리 중 18개에서 엉뚱한
탄소에 치환기를 달았습니다.** 결과가 `structures_v2/`(30종 전부 통과),
`charged_v2/`(PACMAN 전하 완료). 상세는 `STRUCTURE_DEFECT.md`.

**영향: saIm 전 조성 GCMC / 수분 경쟁 / 작업 용량 / 구조 안정성 / 아릴 12종이
전부 재계산 대상입니다.** 무치환 모체와 gme-vs-sod 위상 논지는 영향 없습니다.

## 08-13~14 · desktop  [완료] 커밋 ~0871336

습윤 작업 용량 9/9, 재생 에너지 수지, 조교님 배경자료 PDF.
**단 위 결함으로 수치가 무효화됐습니다.** PDF 는 방법론·위상 중심으로 축소했습니다.
