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

> **`conda env create` 가 pip 섹션을 건너뛸 수 있습니다.** 실제로 데스크탑 이전 때
> `coremof_tools` 가 numpy 만 든 채로 만들어졌습니다. conda 패키지 개수만 보면
> 정상으로 보이니 **반드시 import 로 확인**하세요. 보충은 아래처럼 합니다.
>
> ```bash
> ~/miniconda3/envs/coremof_tools/bin/pip install --no-deps -r coremof_tools.pip.txt
> ```
>
> **`--no-deps` 가 필수입니다.** `coremof_tools==0.3.5` 가 molSimplify·matminer·
> phonopy 를 의존성으로 선언하는데 원본 환경에는 그것들이 없습니다(freeze 에 없음).
> 의존성 해석을 켜면 phonopy 소스빌드에서 죽고, pip 는 원자적이라 **아무것도**
> 설치되지 않습니다. `*.pip.txt` 는 원본 환경의 완전한 freeze 이므로 `--no-deps` 로
> 그대로 넣는 것이 맞습니다.

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

> conda 로 깐 RASPA 의 `share/raspa/forcefield/` 에는 배포 기본 힘장 8종만 있고
> **`UFF_MOF` 는 없습니다.** "RASPA 바이너리가 실행되니까 됐다"고 넘어가면
> 계산 단계에서 막힙니다. 확인:
> ```bash
> ls $RASPA_DIR/share/raspa/forcefield/UFF_MOF
> ```

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

### 3-2-1. `lammps-interface` 의 group 이 LAMMPS 상한(32)을 넘는다

큰 셀에서 걸립니다. `lammps-interface` 는 사이트마다 `group` 을 하나씩 뱉는데
ZIF-69(600원자)에서는 **98개**가 나와 LAMMPS 가 죽습니다.

```
ERROR: Too many groups (max 32) (src/group.cpp:154)
```

ZIF-8(276원자)에서는 그룹 수가 적어 안 걸렸으므로 **ZIF-8 계열만 돌려 본 사람은
이 함정을 모릅니다.** 새 모체로 넘어갈 때 처음 만납니다.

이 `group` 들은 `#### Atom Groupings ####` 주석이 붙은 **편의용 메타데이터일 뿐**
실제로 참조하는 명령이 없습니다(유일한 `fix` 가 `all` 을 씁니다). 그래서 제거해도
이완 결과가 달라지지 않습니다. 확인 방법:

```bash
grep -vE '^group' in.<name> | grep -E '\b1-[0-9]+\b'   # 비어 있어야 안전
```

`21_ZIF69_MTV/risk_screen.py` 에 제거 로직이 들어 있습니다.

> **`lmp_serial` 의 출력을 DEVNULL 로 버리지 마세요.** 이 오류를 처음 만났을 때
> "LAMMPS 출력 없음" 이라는 무의미한 메시지만 남아 원인 파악이 늦어졌습니다.

### 3-2-2. 큰 모체로 넘어갈 때 워커 수를 그대로 쓰면 OOM 이 난다

ZIF-8 은 셀당 276원자라 2×2×2 슈퍼셀이 2,208원자입니다. **ZIF-69 는 600원자라
4,800원자**가 됩니다. 같은 `max_workers=12` 로 돌렸다가 15 GB 머신에서 터졌습니다.

```
Out of memory: Killed process 23142 (python)
  total-vm:22074316kB, anon-rss:14419068kB
```

**단순히 그 작업만 죽는 게 아닙니다.** 메모리 압박이 systemd 까지 불안정하게 만들어
`/tmp` 가 비워지고(작업 스크립트 소실), 실행 중이던 LAMMPS 가 SIGTERM 을 받고,
백그라운드 프로세스 트리가 통째로 무너졌습니다. 원인을 한참 환경 탓으로 오해했습니다.

**범인은 RASPA 가 아니라 ASE 의 `get_all_distances(mic=True)` 입니다.** 실제로
재보니 RASPA 한 프로세스는 ZIF-69(4,800원자 슈퍼셀, 이원 GCMC)에서 **471 MB**
밖에 안 씁니다. 12개를 띄워도 5.6 GB 라 한도와 거리가 멉니다.

14.4 GB 를 쓴 것은 **구조 감사 루프**였습니다. ZIF-69 처럼 skew 가 큰 삼사정계
셀에서 `mic=True` 는 주기 이미지를 대량 전개하고, 구조 여러 개를 **한 프로세스에서
연달아** 감사하면 누적돼 터집니다. 구조 감사 배치가 조용히 `exit 1` 로 죽으면
이걸 의심하세요 — 개별 실행은 프로세스가 끝날 때 메모리가 반환되므로 멀쩡합니다.

> **워커 수를 메모리로 정하지 마세요.** RASPA 는 작업당 단일 스레드 CPU 바운드라
> **물리 코어 수**가 처리량 상한입니다(이 데스크탑은 물리 8 / 논리 16).
> `21_ZIF69_MTV/run_water.py` 를 8 로 둔 것은 이 이유이지 메모리 때문이 아닙니다.
>
> 실제 사용량 확인:
> ```bash
> ps -eo rss,args --sort=-rss | grep simulate | head -3
> ```

### WSL 메모리 설정

기본값은 호스트 RAM 의 50% 입니다(31.9 GB 중 약 16 GB). `C:\Users\<사용자>\.wslconfig`
로 올릴 수 있고, 현재 20 GB + 스왑 8 GB 로 잡아 두었습니다.

> **이 파일은 ASCII 로만 쓰세요.** 한글 주석을 넣었더니 WSL 파서가 파일을 통째로
> 무시하고 기본값(15 GB)을 유지했습니다. BOM 이 없어도 그렇습니다.

적용하려면 `wsl --shutdown` 후 재접속해야 하고, **실행 중인 계산이 전부 죽습니다.**
`free -g` 로 반영을 확인하세요.

### 3-3. RASPA `.def` 파서는 주석 위치에 엄격하다

주석과 데이터를 **정해진 순서로** 읽습니다. 설명 주석을 몇 줄 덧붙이면 정렬이 깨져 "원자 수 0" 으로 읽힙니다. `*.def` 파일에는 원본 레이아웃을 그대로 유지하고, 설명은 스크립트 쪽에 쓰세요.

### 3-4. 물 모델은 배포본을 쓰면 안 된다

RASPA 배포본 `TraPPE/water.def` 는 3원자(Ow, Hw, Hw)인데 `UFF_MOF` 의 물 파라미터는 **TIP5P-Ew** 용입니다. 음전하가 전부 더미 사이트 `Lw` 에 있어서, 3원자 파일을 쓰면 물 한 분자가 **알짜전하 +0.482** 를 갖습니다. 주기계 Ewald 합에 하전 입자를 넣는 셈이라 결과가 무의미해집니다.

**반드시 `19_WaterCompetition/water.def`(5사이트) 를 쓰세요.** RASPA 는 실행 디렉터리의 `.def` 를 먼저 찾으므로 공유 설치본을 건드릴 필요가 없습니다. 정상이면 출력에 `Component has a net charge of 0.000000` 이 찍힙니다.

> **혼동 주의 — 두 메시지는 다릅니다.** 출력에는 이런 줄도 나옵니다.
>
> ```
> WARNING: THE SYSTEM HAS A NET CHARGE
> ```
>
> **이건 이 함정과 무관하고 무해합니다.** 골격 전하를 CIF 에 6자리로 반올림해 적은
> 것이 수천 원자에 걸쳐 누적돼 뜨는 것이라, 실제 알짜전하는 1e-5 수준입니다.
> 정상 완료해 Part 3 의 근거가 된 ZIF-8 수분 계산에도 **전 실행에 3회씩** 찍혀
> 있습니다.
>
> | | SYSTEM 경고 | Component 알짜전하 |
> |---|---|---|
> | ZIF-8 수분 20/20 (검증 완료) | 3회씩 전부 | +0.000000 |
> | ZIF-69 수분 | 0~1회 | +0.000000 |
> | ZIF-69 CO₂ GCMC (Q_st 31.07) | 0~3회 | +0.000000 |
>
> **판정은 반드시 `Component has a net charge of` 로 하세요.** 이 값이 0 이 아니면
> 물 모델이 3원자짜리라는 뜻이고, 그때만 결과가 무의미합니다. SYSTEM 경고를 보고
> 계산을 중단하지 마세요 — 실제로 그렇게 판단할 뻔했습니다.
>
> 확인 명령:
> ```bash
> grep "Component has a net charge" <실행디렉터리>/Output/System_0/*.data
> ```

### 3-5. PACMAN 은 입력 CIF 를 덮어쓴다

반드시 사본에서 작업하세요. 기존 스크립트는 이미 그렇게 되어 있습니다.

### 3-6. 이완 후 구조로 창구 크기를 판정하면 안 된다

빈 골격의 UFF 에너지 최소점은 닫힌 상이라, 자유 이완을 걸면 게이트가 열린 상이 스스로 닫힙니다(실측 PLD 3.95 → 3.24). 그래서

- **PLD / 접근가능부피** → 이완 **전**(as-built) 값으로 판정
- **LCD 감소율 / 최소 원자간 거리** → 이완 **후** 값으로 판정

`18_PoreNarrowing/risk_screen.py` 에 이 분리가 구현되어 있습니다.

### 3-7-1. PyCifRW 는 소스빌드가 안 되니 conda-forge 것을 쓴다

`PACMANCharge` 가 `from CifFile import ReadCif` 로 **PyCifRW 를 필수 의존**합니다.
그런데 pip 소스빌드는 conda 컴파일러의 sysroot 가 없어 링크에서 죽습니다
(`ld: cannot find /lib64/libc.so.6`). 미리 빌드된 바이너리를 받으세요.

```bash
conda install -n coremof_tools -c conda-forge pycifrw=4.4.6 --no-deps -y
```

`--no-deps` 는 numpy 1.26.4 핀을 지키기 위한 것입니다.

`pyeqeq` 는 pybind11 헤더가 GCC 14 와 호환되지 않아(`std::uint16_t` 미선언)
빌드가 불가능합니다. **EQeq 는 3-1 위 판단 사슬에서 이미 폐기한 전하법이라
현재 파이프라인에 필요 없습니다.** 그냥 빼고 가세요.

### 3-7-2. 14/17 의 전하 부여 단계는 스크립트가 없다

`pmcharge` 를 호출하는 코드는 `13_PACMAN/run_pacman_pipeline.py`(대상: 07 계열)와
`18_PoreNarrowing/charge_and_run.py`(대상: 18 계열) **둘뿐**입니다.
`14_Strategies/charged/` 와 `17_NestEffect/charged/` 는 당시 수동으로 만들어졌고
재현 절차가 저장소에 남아 있지 않습니다. 이 둘을 재계산하려면
`charge_and_run.py` 의 `make_charges()` 를 참고해 충전 단계를 먼저 작성해야 합니다.

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

### 검증 결과 (2026-08-05, 데스크탑)

| 항목 | 기대 | 실측 | 판정 |
|---|---|---|---|
| ① 구조 무결성 | 결함 0 | **67/68 통과** | 아래 주 참조 |
| ② Zeo++ `mIm100__closed` | LCD 11.39 / PLD 3.41 | **11.39286 / 3.40894** | 통과 |
| ③ RASPA 순수 ZIF-8 0.15 bar | 로딩 0.2676 | **0.2723 ± 0.0050** | 통과 (Q_st 14.04 일치) |

③ 은 12개 조성 전체를 다시 돌려 노트북 값과 비교했습니다. **12개 모두 통계오차 내**입니다.
가장 크게 벌어진 두 개도 유의하지 않습니다 — `clIm050_saIm050__closed` 1.2σ,
`mIm050_saIm050__closed` 1.4σ. DDEC6 전하도 재현됩니다(원소별 평균 차이 최대 0.008 e).

> **다만 5000 사이클은 −SO₃H 계열을 서로 순위 매기기엔 부족합니다.** 이 조성들의
> 로딩 상대오차가 8.6~11.0% 라 `mIm050_saIm050`(0.7406 ± 0.0635) 과
> `clIm050_saIm050`(0.6259 ± 0.0688) 의 오차 막대가 겹칩니다. 둘의 우열을
> 주장하려면 사이클을 늘려야 합니다.

① 의 남은 1개는 `17_NestEffect/structures/mIm075_saIm025.cif` 입니다. 주기경계
버그가 아니라 **실제 입체 충돌**입니다 — 술폰산의 −O**H** 수소가 이웃 링커의
Zn 배위 이미다졸레이트 **N** 을 1.569 Å 에서 찌릅니다(4자리 전부 동일 거리이므로
무작위가 아니라 빌더가 S−O−H 이면각을 고정해 놓은 결과). 정상 N···H 수소결합은
1.8~2.0 Å 이므로 이면각 완화가 필요하고, 화학적으로는 양성자 이동
(−SO₃⁻ / N−H⁺)도 가능한 상황입니다. **18_PoreNarrowing 의 −SO₃H 구조들은
이 문제가 없으니 주력 결과는 영향을 받지 않습니다.**

---

## 5. 현재 진행 상황과 다음 할 일

### 확정된 결과 (유효)

| 항목 | 위치 |
|---|---|
| 결손 안정성 — 16.7% 결손까지 OMS 전량 보존, 창구 영구 개방 | `16_DefectStability/stability_results.json` |
| 기공 축소 12종 GCMC — **−SO₃H 최고**(Q_st 24.12, 로딩 0.8321) | `18_PoreNarrowing/narrow_results.json` |
| 위험도 판정 12/16 통과 | `18_PoreNarrowing/risk_results.json` |
| 둥지 효과 8종 | `17_NestEffect/ddec6_results.json` |
| **수분 경쟁 12/20 — RH 90%에서 CO₂ 유지 107\~118%** | `19_WaterCompetition/water_results.json` |
| **모체 공동 크기 모형 — 최적 4.0\~4.5 Å, ZIF-7 예측 34 kJ/mol** | `20_ParentScan/README.md` |

### 재계산이 필요한 것 (주기경계 버그 영향)

버그는 `05_MTV_Ligand_Library/mtv_cif_builder.py` 에서 **이미 수정**되었습니다. 아래는 **수정 전 구조로 계산된 값**이라 다시 돌려야 합니다.

- `07_Bracketed_MTV/` 전체 → 이것 기반의 **밀도맵 해부**(`10_DensityMap/density_analysis.json`)
- `14_Strategies/StratB_pushpull` (Q_st 23.01)
- `17_NestEffect` 중 `amIm050_nIm050`, `mIm075_saIm025`

재생성 방법: 해당 디렉터리의 `build_*.py` 를 다시 실행 → `audit_orphans.py` 통과 확인 → 전하 → RASPA.

### 다음 작업

**우선순위 1 — ZIF-7 검증** (`20_ParentScan/README.md` 참조)

공동 크기 모형이 ZIF-7(공동 4.3 Å)에서 **작용기 없이 Q_st 34 kJ/mol** 을 예측합니다. ZIF-8 과 같은 sod 위상이고, 우리 파이프라인은 이미 벤즈이미다졸레이트 이환식 고리를 다룹니다(ZIF-69 작업에서 구현).

1. ZIF-7 CIF 확보(CCDC/COD) → `audit_orphans.py` → Zeo++ 로 LCD/PLD 실측, 문헌값 4.3/3.0 확인
2. 닫힌상/열린상 괄호 계산 — 창구 3.0 Å 이 정적 구조 위양성인지 판정
3. PACMAN 전하 → Widom/GCMC 로 예측 34 kJ/mol 검증
4. **로딩과 작업용량 확인** — Q_st 가 올라도 용량이 무너지면 의미 없음
5. 통과하면 수분 경쟁(`19_WaterCompetition` 과 동일 절차)

**우선순위 2 — 미완 계산 마무리**

- 수분 경쟁 남은 8개: `19_WaterCompetition/` 에서 `run_water.py` 실행. 완료된 12개를 자동으로 건너뜁니다
- 위 재계산 목록(주기경계 버그 영향분) 처리

**우선순위 3 — 참고**

- ZIF-90, ZIF-68 도 CIF 를 받아 문헌값 검증. 예측상 ZIF-8 과 큰 차이 없어 우선순위 낮음
- −SO₃H 의 가수분해 안정성 — 고전 계산으로는 불가, 문헌/DFT/실험 필요

> **방향 전환** — 연구가 "ZIF-8 을 화학적으로 개량" 에서 **"작은 공동 모체를 그대로 쓰되 유연성과 용량을 관리"** 로 바뀌었습니다. 근거는 두 가지입니다. (a) C2 치환기가 창구를 향하지 케이지 중심이 아니라 **치환으로는 공동이 안 줄어듭니다**(Part 2, 실측으로 반증). (b) **분산력과 정전기가 같은 부피를 놓고 경쟁합니다** — 공동을 좁히면 작용기 붙일 자리가 없고, 작용기를 붙이려면 공동이 넓어야 합니다(Part 4).

---

## 6. 계산 부하 참고

노트북에서 측정된 값입니다. 데스크탑 코어 수에 맞춰 각 스크립트의 `max_workers` 를 조정하세요.

> 현 데스크탑은 **Ryzen 7 5700X (물리 8 / 논리 16), RAM 15 GB, Quadro P2000** 입니다.
> `18_PoreNarrowing/charge_and_run.py` 와 `19_WaterCompetition/run_water.py` 는
> `max_workers=12` 로 올려 두었습니다. 아직 6~7 로 남아 있는 것:
> `16_DefectStability/relax_and_measure.py`, `18_PoreNarrowing/risk_screen.py`,
> `07_Bracketed_MTV/run_widom_batch.py`, `14_Strategies/run_raspa_strat.py`,
> `17_NestEffect/run_raspa_nest.py`, `10_DensityMap/run_density_map.py`.
>
> **PACMAN 이 GPU 를 씁니다**(`Using device: cuda`). 노트북에는 없던 가속입니다.

| 작업 | 규모 | 소요 |
|---|---|---|
| 구조 생성 16종 | — | 1분 미만 |
| UFF4MOF 이완 + Zeo++ 16종 | 워커 6 | 약 40분 (1종은 수렴 실패로 진동) |
| Widom + GCMC 36작업 (5000 사이클) | 워커 7 | 약 45분 |
| CO₂/H₂O 이원 GCMC 20작업 (15000 사이클) | 워커 6 | 2시간 이상 |

`lammps-interface` 가 생성하는 이완 입력은 에너지 변화 **1e-6 kcal/mol** 까지 반복합니다. 구조 안정성만 보려면 `min_eval` 을 **1e-4** 로 완화해도 판정(LCD 20%, PLD 3.3 Å)에 영향이 없고 시간이 크게 줄어듭니다.
