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

## 배경 문서 (맥락을 한 번에 불러오려면 이 순서로)

| 문서 | 무엇이 있나 |
|---|---|
| `21_ZIF69_MTV/STRUCTURE_DEFECT.md` | **2026-08-14 발견. 치환 구조 전부 재계산 필요** |
| `21_ZIF69_MTV/AUDIT_20260814.md` | **위 결함과 같은 종류를 훑은 감사. 미수정 2건 있음** |
| `00_Migration/MIGRATION.md` 3절 | 계산 환경의 함정 전부(조용한 timeout, OOM, WSL 종료 등) |
| `21_ZIF69_MTV/DRYING_PLAN.md` | 건조 비용 판단 절차와 사전 등록 기준 |
| `21_ZIF69_MTV/DAC_PLAN.md` | DAC 조건 검토 구상(실행 보류) |
| `21_ZIF69_MTV/LINKER_DESIGN_BRIEF.md` | 링커 설계와 빌더 한계 |

---

## 08-14 · desktop  [대기중] 밀도맵 v2

**대기열이 걸려 있습니다.** `~/.claude_work/queue_density_v2.sh` 가 5분마다 보다가
**연속 3회(15분) 조용하면 스스로 발사**합니다. 조건은 `run_water_v2` 와
`run_gcmc_v2` 가 0개이고 `simulate` 가 2개 이하일 때. 14시간 안에 조용해지지
않으면 발사하지 않고 종료합니다.

* 대상: `21_ZIF69_MTV/run_density_v2.py` (`charged_v2` -> `density_v2/`)
* 워커: 발사 시점에 노는 코어만큼 (2~6)
* 진행: `~/.claude_work/density_v2.log`, 대기 기록은 `density_v2_queue.log`

**다른 세션에 부탁**: 새 RASPA 작업을 띄우실 거면 이 대기열이 먼저 발사되지
않도록 `pkill -f queue_density_v2.sh` 로 껐다가 나중에 다시 켜 주세요.

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
