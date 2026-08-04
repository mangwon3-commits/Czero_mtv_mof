# 데스크탑 이전 안내서

노트북(WSL Ubuntu)에서 데스크탑으로 이 프로젝트를 옮겨 이어서 계산하기 위한 문서입니다.

---

## 1. 무엇을 옮기는가

| 항목 | 용량 | 방법 |
|---|---|---|
| 프로젝트 소스·구조·결과 | **76 MB** (672개 파일) | 아카이브로 복사 |
| git 저장소 (`.git`, 커밋 13개) | 39 MB | 함께 복사 — 이력 보존 |
| RASPA 데이터 (`00_Migration/raspa_share`) | 9.8 MB | 함께 복사 |
| conda 환경 3개 | ~~15 GB~~ | **복사하지 않음.** YAML로 재구성 |
| RASPA/LAMMPS 중간 산출물 | 1.4 GB | **복사하지 않음.** 재생성 가능 |

`runs/`, `Output/`, `lmp/`, `Movies/`, `Restart/`, `VTK/` 는 전부 재계산으로 복원되는 중간 산출물이라 제외합니다. 최종 수치는 각 디렉터리의 `*.json` 에 이미 들어 있습니다.

> **예외** — `10_DensityMap/diff_vtk/` 는 ParaView로 열어 보는 **산출물**이므로 포함합니다(정전기 차분맵).

---

## 2. 데스크탑에서 준비하기

### 2-1. 아카이브 풀기

```bash
tar xzf mof_project_migration.tar.gz -C ~/
cd ~/mof_project
git log --oneline | head -3     # 이력이 따라왔는지 확인
```

### 2-2. conda 환경 3개 재구성

환경이 세 개인 것은 **패키지 충돌 때문에 한 환경에 다 넣을 수 없어서**입니다. 반드시 세 개를 따로 만드세요.

```bash
cd ~/mof_project/00_Migration/envs
conda env create -f czeromof.yml
conda env create -f coremof_tools.yml
conda env create -f lammps_mof.yml
```

`*.yml` 이 플랫폼 차이로 실패하면 `*.from-history.yml`(명시적으로 설치한 패키지만)로 만든 뒤 `*.pip.txt` 로 보충하세요.

| 환경 | 담당 | 핵심 바이너리 |
|---|---|---|
| `czeromof` | RASPA, Zeo++, ASE, RDKit | `simulate`, `network`, `obabel` |
| `coremof_tools` | PACMAN(DDEC6 전하), mofchecker (python 3.9) | — |
| `lammps_mof` | LAMMPS, 힘장 입력 생성 | `lmp_serial`, `lammps-interface` |

> **numpy 주의** — `coremof_tools` 는 numpy **1.26.4** 로 고정해야 합니다. `mendeleev` 를 설치하면 numpy 2.0 이 딸려 와서 MOFClassifier/sklearn 이 깨집니다.

### 2-3. RASPA 데이터 경로 설정

```bash
mkdir -p ~/RASPA/simulations
cp -r ~/mof_project/00_Migration/raspa_share ~/RASPA/simulations/share
echo 'export RASPA_DIR=${HOME}/RASPA/simulations' >> ~/.bashrc
source ~/.bashrc
```

`RASPA_DIR` 이 없으면 `simulate` 가 힘장을 못 찾습니다. **`UFF_MOF` 힘장이 여기 들어 있고, 이 프로젝트의 모든 계산이 이걸 씁니다.**

---

## 3. 반드시 알아야 할 함정 (전부 실제로 겪은 것)

### 3-1. 바이너리가 환경마다 흩어져 있다

한 스크립트가 여러 도구를 쓰는데 도구가 서로 다른 환경에만 있습니다. **`PATH` 에 의존하면 조용히 실패합니다.**

| 도구 | 있는 환경 |
|---|---|
| `network` (Zeo++) | `czeromof` 만 |
| `simulate` (RASPA) | `czeromof` 만 |
| `lmp_serial`, `lammps-interface` | `lammps_mof` 만 |
| PACMAN | `coremof_tools` 만 |

기존 스크립트는 이미 절대경로로 잡아두었습니다(`shutil.which(...) or 기본경로`). **데스크탑의 conda 설치 경로가 다르면 아래 상수를 고쳐야 합니다.**

```
16_DefectStability/relax_and_measure.py   NETWORK
18_PoreNarrowing/risk_screen.py           NETWORK
18_PoreNarrowing/charge_and_run.py        SIMULATE
19_WaterCompetition/run_water.py          SIMULATE
```

한 번에 확인:
```bash
grep -rn "miniconda3/envs" --include=*.py ~/mof_project
```

> 과거에 이것 때문에 `network` 호출이 실패했는데 `except: pass` 가 삼켜서 **LCD/PLD 가 전부 0 으로 조용히 기록**된 적이 있습니다. 결과가 0 이면 도구 경로부터 의심하세요.

### 3-2. `lammps-interface` 가 황을 잘못 타이핑한다

4배위 황에 `S_3` 라는, UFF·UFF4MOF 어느 테이블에도 없는 타입을 붙여 `KeyError: 'S_3'` 로 죽습니다. 술폰산의 황은 6가 사면체이므로 **`S_3+6`** 이 정답입니다.

우회 래퍼가 이미 있습니다 → `18_PoreNarrowing/lammps_iface_patched.py`. `lammps-interface` 대신 이걸 호출하세요.

### 3-3. RASPA `.def` 파서는 주석 위치에 엄격하다

주석과 데이터를 **정해진 순서로** 읽습니다. 설명 주석을 몇 줄 덧붙이면 정렬이 깨져 "원자 수 0" 으로 읽힙니다. `*.def` 파일에는 원본 레이아웃을 그대로 유지하고, 설명은 스크립트 쪽에 쓰세요.

### 3-4. 물 모델은 배포본을 쓰면 안 된다

RASPA 배포본 `TraPPE/water.def` 는 3원자(Ow, Hw, Hw)인데 `UFF_MOF` 의 물 파라미터는 **TIP5P-Ew** 용입니다. 음전하가 전부 더미 사이트 `Lw` 에 있어서, 3원자 파일을 쓰면 물 한 분자가 **알짜전하 +0.482** 를 갖습니다. 주기계 Ewald 합에 하전 입자를 넣는 셈이라 결과가 무의미해집니다.

**반드시 `19_WaterCompetition/water.def`(5사이트) 를 쓰세요.** RASPA 는 실행 디렉터리의 `.def` 를 먼저 찾으므로 공유 설치본을 건드릴 필요가 없습니다. 정상이면 출력에 `Component has a net charge of 0.000000` 이 찍힙니다.

### 3-5. PACMAN 은 입력 CIF 를 덮어쓴다

반드시 사본에서 작업하세요. 기존 스크립트는 이미 그렇게 되어 있습니다.

### 3-6. 이완 후 구조로 창구 크기를 판정하면 안 된다

빈 골격의 UFF 에너지 최소점은 닫힌 상이라, 자유 이완을 걸면 게이트가 열린 상이 스스로 닫힙니다(실측 PLD 3.95 → 3.24). 그래서

- **PLD / 접근가능부피** → 이완 **전**(as-built) 값으로 판정
- **LCD 감소율 / 최소 원자간 거리** → 이완 **후** 값으로 판정

`18_PoreNarrowing/risk_screen.py` 에 이 분리가 구현되어 있습니다.

### 3-7. 구조 검증은 '전역 최소 거리'로 하면 안 된다

메틸 C–H(0.929 Å)가 항상 최솟값을 차지해서, 1.37 Å 짜리 치환기 충돌도 4.7 Å 짜리 고아 원자도 가려집니다. **비결합 접촉과 그래프 연결성**을 봐야 합니다.

새 구조를 만들면 반드시 실행:
```bash
conda activate czeromof
python ~/mof_project/audit_orphans.py
```
`고아 0 / 충돌 0 / 분리 0` 이 아니면 그 구조로 계산하지 마세요.

---

## 4. 이전 후 검증 (순서대로)

```bash
conda activate czeromof

# ① 구조 무결성 — 전부 OK 여야 함 (03/16/17/18 계열)
python ~/mof_project/audit_orphans.py | tail -5

# ② Zeo++ 동작
network -ha -res /tmp/t.res ~/mof_project/18_PoreNarrowing/structures/mIm100__closed.cif && cat /tmp/t.res
#   기대: LCD 11.39, PLD 3.41 부근

# ③ RASPA 동작 — 짧은 CO2 GCMC 재현
#   기대: 순수 ZIF-8 0.15 bar 로딩 0.2676 mol/kg 부근
```

LAMMPS 쪽:
```bash
conda activate lammps_mof
python ~/mof_project/18_PoreNarrowing/lammps_iface_patched.py --help
```

---

## 5. 현재 진행 상황과 다음 할 일

### 확정된 결과 (유효)

| 항목 | 위치 |
|---|---|
| 결손 안정성 — 16.7% 결손까지 OMS 전량 보존, 창구 영구 개방 | `16_DefectStability/stability_results.json` |
| 기공 축소 12종 GCMC — **−SO₃H 최고**(Q_st 24.12, 로딩 0.8321) | `18_PoreNarrowing/narrow_results.json` |
| 위험도 판정 12/16 통과 | `18_PoreNarrowing/risk_results.json` |
| 둥지 효과 8종 | `17_NestEffect/ddec6_results.json` |

### 재계산이 필요한 것 (주기경계 버그 영향)

버그는 `05_MTV_Ligand_Library/mtv_cif_builder.py` 에서 **이미 수정**되었습니다. 아래는 **수정 전 구조로 계산된 값**이라 다시 돌려야 합니다.

- `07_Bracketed_MTV/` 전체 → 이것 기반의 **밀도맵 해부**(`10_DensityMap/density_analysis.json`)
- `14_Strategies/StratB_pushpull` (Q_st 23.01)
- `17_NestEffect` 중 `amIm050_nIm050`, `mIm075_saIm025`

재생성 방법: 해당 디렉터리의 `build_*.py` 를 다시 실행 → `audit_orphans.py` 통과 확인 → 전하 → RASPA.

### 다음 작업

1. **CO₂/H₂O 경쟁 흡착 마무리** (`19_WaterCompetition/`) — 노트북에서 진행 중이던 것. 결과가 `water_results.json` 에 있으면 완료된 것이고, 없거나 20행 미만이면 `run_water.py` 재실행
2. 위 재계산 목록 처리
3. −SO₃H 가 수분 시험을 통과하면 → DFT 결합에너지, 합성 가능성 검토
4. 통과 못 하면 → 케이지가 작은 모체(ZIF-7 등)로 전환. **6 Å 급 공동은 ZIF-8 을 치환해서 얻을 수 없음이 확인되었습니다** — C2 치환기는 창구를 향하지 공동 중심이 아니라서, 치환하면 창구만 막히고 공동은 안 줄어듭니다

---

## 6. 계산 부하 참고

노트북에서 측정된 값입니다. 데스크탑 코어 수에 맞춰 각 스크립트의 `max_workers` 를 조정하세요.

| 작업 | 규모 | 소요 |
|---|---|---|
| 구조 생성 16종 | — | 1분 미만 |
| UFF4MOF 이완 + Zeo++ 16종 | 워커 6 | 약 40분 (1종은 수렴 실패로 진동) |
| Widom + GCMC 36작업 (5000 사이클) | 워커 7 | 약 45분 |
| CO₂/H₂O 이원 GCMC 20작업 (15000 사이클) | 워커 6 | 2시간 이상 |

`lammps-interface` 가 생성하는 이완 입력은 에너지 변화 **1e-6 kcal/mol** 까지 반복합니다. 구조 안정성만 보려면 `min_eval` 을 **1e-4** 로 완화해도 판정(LCD 20%, PLD 3.3 Å)에 영향이 없고 시간이 크게 줄어듭니다.
