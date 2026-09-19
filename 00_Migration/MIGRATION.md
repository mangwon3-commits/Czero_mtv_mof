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

> **2026-08-07 실측 — RASPA 에는 20 GB 도 남아돕니다.** 늘려도 소용없습니다.
>
> | | |
> |---|---|
> | `simulate` 프로세스당 | 437~580 MB |
> | 10프로세스 합계 | **5.0 GB** |
> | 20 GB 중 사용 | 6.2 GB (가용 13.8 GB) |
> | **스왑 사용** | **0 MB** ← 부족한 적이 없다는 뜻 |
>
> 16프로세스까지 늘려도 9.1 GB 입니다. **병목은 물리 코어 8개**이므로 RAM 을
> 올려도 처리량은 그대로입니다.
>
> **딱 하나 필요한 경우가 ASE 구조 감사입니다.** `get_all_distances(mic=True)` 가
> skew 큰 삼사정계 셀의 주기 이미지를 대량 전개하고, 여러 구조를 **한 프로세스에서
> 연달아** 감사하면 누적돼 14.4 GB 까지 갑니다.
>
> 그때만 24 GB 로 올리세요. 전환 스크립트가 준비돼 있습니다.
>
> ```bash
> bash ~/.claude_work/wsl_mem.sh status   # 현재 값과 적용값 확인
> bash ~/.claude_work/wsl_mem.sh 24       # 감사 전
> # 윈도우 PowerShell: wsl --shutdown
> bash ~/.claude_work/wsl_mem.sh 20       # 감사 후 되돌리기
> ```
>
> 계산이 돌고 있으면 스크립트가 **거부합니다**(`--force` 로 무시 가능). 그리고
> 저장 전에 비ASCII 문자를 검사해, 섞여 있으면 되돌립니다 — 한글 주석 때문에 WSL 이
> 파일을 통째로 무시했던 전례가 있어서입니다.
>
> **호스트가 31.9 GB 이므로 24 GB 를 넘기지 마세요.** 윈도우 몫이 8 GB 이하로
> 떨어지면 호스트 쪽에서 스와핑이 시작됩니다.
>
> > **더 나은 해법은 증설이 아닙니다.** 감사 루프를 **구조마다 별도 프로세스**로
> > 쪼개면 프로세스 종료 시 메모리가 반환돼 누적 자체가 없어집니다. 개별 실행이
> > 멀쩡했던 것이 그 증거입니다. 증설은 임시방편이고, 이 수정이 근본 해결입니다.

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
> | ZIF-69 CO₂ GCMC (Q_st 31.07) | 0~3회 | +0.000000 | ⟨Q_st 절대값은 RT 부호 정정 전, +4.96 — QST_RT_SIGN_20260911⟩
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

### 3-8. `subprocess.run` 의 timeout 은 결과를 조용히 지운다

**2026-08-06 에 수분 경쟁 결과 5개를 이렇게 잃었습니다.** 원인은 상수 하나였습니다.

```python
subprocess.run([SIMULATE, 'simulation.input'], ..., timeout=28800)  # 8시간
```

이 값은 단일 성분 CO₂ GCMC 스크립트에서 복사해 온 것이고, 거기서는 넉넉했습니다.
그런데 5사이트 물이 붙은 **이원 GCMC** 는 술폰산이 많을수록 물 삽입 수용률이 떨어져
같은 15000 사이클이 몇 배로 길어집니다.

| 조건 | 실측 소요 |
|---|---|
| 건조, 무치환 | 77분 |
| 습윤, −SO₃H 50% | **8시간 초과** ← 여기서부터 죽었다 |

**죽는 방식이 더 나빴습니다.** `timeout` 은 프로세스를 죽이고 `TimeoutExpired` 를
던지는데, 워커가 그걸 잡아 다음 작업으로 넘어갑니다. 예외도 로그도 안 남고
**결과에 구멍만 생깁니다.** `rh50/rh90_saIm025` 와 `rh25/rh50/rh90_saIm050` 이
사라져 50% 조성의 습윤 계열이 통째로 비었습니다.

**긴 배치를 돌릴 때 지킬 것:**

1. **timeout 은 최악의 조성 기준으로 잡으세요.** 대표 조성으로 재면 안 됩니다.
   현재 `run_water.py` 는 72시간입니다.
2. **timeout 이 걸리면 반드시 로그를 남기세요.** 조용한 실패가 이 사고의 본질입니다.
3. **작업 단위 이어받기를 넣으세요.** 결과 JSON 은 전부 끝나야 쓰이므로, 그것만
   보고 건너뛰면 19개를 끝내고 죽었을 때 이어받을 지점이 0 입니다.

### 3-9. 진행 감시는 '완주 수'만 세면 안 된다

위 사고를 **4시간 늦게** 발견한 이유입니다. 완주 수만 세면 죽은 작업이 완주 수를
올리지도, 프로세스로 남지도 않아 **"느린 것"과 "죽은 것"이 화면상 똑같습니다.**

세 갈래로 나눠 세세요.

| 분류 | 판정 |
|---|---|
| 완주 | 출력에 최종 로딩 줄이 있다 |
| 실행 | 그 디렉터리에서 `simulate` 가 돌고 있다 |
| 대기 | 둘 다 아니다 |

> **대기를 곧바로 '죽었다'고 하면 오탐이 납니다.** 워커가 8개인데 할 일이 12개면
> 4개는 당연히 아무 데서도 안 돕니다. 가르는 기준은 **풀에 빈 자리가 있는가** 입니다.
> `실행 == 워커수` 면 대기열이고, `실행 < 워커수` 면 버려진 작업입니다.

구현: `~/.claude_work/watch_pipeline.sh`

### 3-10. 여러 세션이 같은 호스트를 공유한다 — 시작 전에 알릴 것

**2026-08-06, 실제로 충돌 직전까지 갔습니다.** 이 프로젝트는 데스크탑 터미널
세션과 Remote Control로 붙은 세션이 **같은 물리 머신**(같은 파일시스템, 같은
CPU 코어, 같은 GPU)을 동시에 씁니다. 격리된 컨테이너가 아닙니다.

한 세션이 새 후보 링커(cf3Im_aryl 등)로 `run_candidate_gcmc.py` 를 돌리기
시작했는데, 다른 세션이 대기 중이던 구 아릴 시리즈로 `run_aryl_gcmc.py` 를
돌리려 했습니다. 둘 다 같은 `aryl_runs/` 밑에 같은 `{mode}_{gas}_{tag}` 규약으로
결과를 씁니다. 겹쳤다면 RASPA 프로세스 두 개가 한 디렉터리에서 같은 파일명을
놓고 경쟁했을 것이고, **크래시가 아니라 결과가 조용히 뒤섞이는** — 3-8과 같은
부류의, 가장 늦게 발견되는 사고로 이어졌을 것입니다. `run_aryl_gcmc.py` 에
다른 스크립트의 생존을 폴링하는 가드를 추가해(`629d1ed`) 이번엔 막았지만,
이건 프로세스명 기준 폴링이지 락이 아니라 **완벽한 보장이 아닙니다.**

**그래서 지키는 규칙:** 어느 세션이든 CPU/GPU를 오래 점유하는 백그라운드
계산(RASPA, PACMAN, LAMMPS)을 새로 시작하기 전에

1. `ps aux | grep -E "simulate|pmcharge|lmp_serial"` 로 상대 세션이 뭘 돌리고
   있는지 먼저 확인하고,
2. 겹치는 출력 경로(`aryl_runs/`, `water_runs/` 등)를 쓰는 작업이면 대화창에
   "지금 X를 백그라운드로 시작합니다"라고 먼저 알린 뒤 시작한다.

락 파일을 새로 만들지 않는 이유는 3-8과 같습니다 — 비정상 종료 시 남은 락이
다음 세션을 막는 부작용이 3-9의 "느림과 죽음을 구별 못 하는" 문제보다 더 흔합니다.

> **2026-08-06 23:14 보강 — 가드가 이제 양방향입니다 (`3b6fe82`).**
>
> 위 문단이 지적한 "한 방향만 보호된다"를 고쳤습니다. 방법은 두 스크립트의
> 관계에서 나왔습니다 — `run_candidate_gcmc.py` 는 `run_aryl_gcmc` 를 **import 해서
> `run_one` 을 그대로 씁니다**(`MAX_WORKERS` 와 `RUNS` 만 덮어씀). 따라서
> **`run_one` 안에 넣은 검사는 한 번 고치면 양쪽 모두에 적용됩니다.**
>
> `occupied_by_other(d)` 가 살아 있는 `simulate` 프로세스들의 `/proc/<pid>/cwd` 를
> 읽어, 목표 디렉터리를 이미 누가 쓰고 있으면 그 작업을 건너뜁니다. 락 파일이
> 아니므로 stale 문제가 없습니다 — cwd 는 프로세스가 죽으면 함께 사라집니다.
>
> 단위 시험을 통과했습니다(빈 디렉터리 → False / 실행 중 디렉터리 → True /
> 없는 경로 → 예외 없이 False). 구문 검사만으로는 부족합니다. 술어가 틀리면
> 조용히 False 를 돌려주고 그대로 충돌하기 때문입니다.
>
> **그래도 위의 사람 규칙은 유지하세요.** 검사와 실행 사이에 틈이 있어(TOCTOU),
> 두 프로세스가 같은 순간에 같은 디렉터리를 집으면 둘 다 비어 있다고 볼 수
> 있습니다. 실제로 그럴 확률은 낮지만 0은 아니고, 무엇보다 이 가드는 **코어 경합**을
> 막지 못합니다 — 오늘 8코어에 10프로세스가 몰린 것은 충돌이 아니라 자원 문제였고,
> 그건 미리 알리는 것 말고 자동으로 막을 방법이 없습니다.

### 3-11. 순차 파이프라인의 꼬리에서 코어가 논다 — 기회주의 스케줄러

**앞으로 모든 긴 배치에 적용하는 원칙입니다.**

파이프라인은 단계를 순차로 돕니다(수분 → LAMMPS → 밀도맵 → 아릴). 그런데 각 단계의
**끝자락에는 남은 작업이 워커 수보다 적어집니다.** 실측으로 수분 경쟁의 마지막
구간은 saIm100 3~4개만 남는데, 다음 단계는 STAGE1 이 완전히 끝나야 시작하므로
**코어 4~5개가 약 19시간 놉니다.** 전체 소요의 3~5시간에 해당합니다.

`~/.claude_work/opportunistic.sh` 가 이 유휴를 메웁니다. 5분마다 계산 프로세스 수를
세어 여유 코어가 **3개 이상, 3회 연속(15분)** 확인되면 다음 단계를 그 워커 수로
띄웁니다. 연속 확인을 요구하는 것은 작업 교체 순간의 빈틈에 반응해 과다 기동하는
것을 막기 위해서입니다.

> **아무 스크립트나 이렇게 띄우면 안 됩니다.** 파이프라인이 나중에 같은 것을 또
> 돌리기 때문에, **겹쳐도 사고가 안 나는 스크립트만** 대상입니다.
>
> | 스크립트 | 기회주의 대상 | 이유 |
> |---|---|---|
> | `run_density_map.py` | **O** | 이어받기 + `already_running()` 단일 인스턴스 검사 |
> | `run_aryl_gcmc.py` | **O** | 이어받기 + `occupied_by_other()` 디렉터리 점유 검사 |
> | `risk_screen.py` | **X** | **둘 다 없음.** `lmp/` 에서 겹치면 이완이 깨짐 |
>
> 나중에 시작한 쪽이 물러나는 구조라, 파이프라인 STAGE3 이 뒤늦게 떠도 즉시
> 종료하고 STAGE4 로 넘어갑니다. 그때 `run_aryl_gcmc.py` 의
> `wait_for_other_writers()` 가 밀도맵 종료를 기다리므로 **순서는 지켜집니다.**

**새 스크립트를 기회주의 대상에 넣으려면 먼저 두 가지를 갖추세요** — 작업 단위
이어받기(3-8)와 단일 인스턴스/디렉터리 점유 검사(3-10). 없으면 넣지 마세요.

> **`pgrep -c` 주의.** 일치가 없으면 `0` 을 찍으면서 **종료코드 1** 을 냅니다.
> `$(pgrep -c x || echo 0)` 로 쓰면 `"0\n0"` 이 되어 산술 확장이 깨집니다.
> 실제로 이 스케줄러 첫 판이 그렇게 죽었습니다. 값이 숫자인지 검사하고 쓰세요.

### 3-12. WSL 을 붙잡는 것은 안쪽 프로세스가 아니라 바깥쪽 클라이언트다

**이것 하나 때문에 LAMMPS 가 39시간 죽어 있었습니다.**

증상은 두 가지로 나타났습니다. 하나는 세션이 "작업 폴더가 더 이상 존재하지 않는다"고
하는 것(작업 디렉터리가 UNC 경로 `\\wsl.localhost\Ubuntu\` 라서, VM 이 꺼지면 공유가
통째로 사라집니다). 다른 하나는 계산이 소리 없이 멈추는 것입니다.

**두 번의 오진을 먼저 적습니다.**

1. `~/.claude_work/wsl_keepalive.sh` — VM 안에서 `while true; do sleep 300; done` 을
   돌리면 유휴 판정이 안 될 것이라 봤습니다. **아닙니다.**
2. `.wslconfig` 의 `vmIdleTimeout=-1` — 이걸 적용하면 끝일 것이라 봤습니다.
   **아닙니다.**

2026-08-10 17:25:06 에 위 둘이 **모두 걸려 있는 상태로** VM 이 꺼졌습니다.
Hyper-V-VmSwitch 포트 삭제 기록으로 확인됩니다. WSL 안에서는 흔적을 남길 수 없으니
(로그를 쓸 프로세스가 같이 죽습니다) 윈도우 이벤트 로그를 봐야 합니다.

```powershell
Get-WinEvent -FilterHashtable @{LogName='System'; StartTime=(Get-Date).AddDays(-3)} |
  Where-Object { $_.ProviderName -match 'VmSwitch' -and $_.Id -in 67,71 }
```
포트 생성(67)과 삭제(71)가 VM 의 수명입니다.

08-12 08:20~08:23 에 세 번 재현했습니다. 윈도우 쪽에 붙어 있는 `wsl.exe` 가 없으면,
`wsl.exe -e` 호출이 끝나는 순간 **`setsid nohup` 으로 떼어 놓은 프로세스까지 전부**
사라집니다. 08:23 에 윈도우에서 `vm_hold.sh` 를 붙잡아 두자 **같은 방법으로 띄운
감시견이 그대로 살아남았습니다.**

**해법 — 되살릴 주체는 반드시 VM 바깥에 있어야 합니다.** VM 이 꺼지면 안에 있던
감시견도 같이 죽으므로, 안쪽 장치만으로는 원리상 복구가 불가능합니다.

| 층 | 위치 | 하는 일 |
|---|---|---|
| 예약 작업 `ClaudeWslHold` (5분) | 윈도우 | `wsl.exe --exec vm_hold.sh` 를 붙잡아 VM 유지 + `ensure_guards.sh` 호출 |
| `ensure_guards.sh` | WSL | keepalive·감시견 중 **없는 것만** 되살림 |
| `lammps_watchdog.sh` | WSL | 1시간마다 **진전**을 보고 멈췄으면 재실행 |
| crontab `@reboot`, `*/10` | WSL | 예약 작업이 안 돌 때의 여벌 |

설치본은 `00_Migration/tools/` 에 있습니다. 윈도우 쪽 등록은 이렇게 합니다.

```powershell
schtasks /create /tn ClaudeWslHold /tr "\"$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe\" -NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File \"C:\Users\mangw\.claude_work\wsl_hold.ps1\"" /sc minute /mo 5 /rl limited /f
```

> **예약 작업은 작업 프로세스가 끝날 때 자식까지 죽입니다.** 처음에는 5분마다
> 실행돼 `Start-Process` 로 홀드를 띄우고 바로 끝나는 형태였습니다. 그러자 홀드가
> **5분마다 죽었습니다**(08-12 12:45~13:25 사이 `wsl_hold.log` 에 "새로 띄움"이
> 9번 연속). 예약 작업은 작업 개체(job object)로 자식을 묶으므로 `Start-Process`
> 로 떼어 놔도 소용없습니다. **작업 프로세스 자신이 홀드를 붙잡고 끝나지 않아야
> 합니다.** 그러려면 XML 로 등록해 `ExecutionTimeLimit` 을 `PT0S`(무제한, 기본값은
> 3일)로, `MultipleInstancesPolicy` 를 `IgnoreNew` 로 둡니다. 살아 있는 동안 5분
> 트리거는 무시되고 죽으면 다음 트리거가 다시 띄우므로 재시작 로직이 따로 필요
> 없습니다. `LogonTrigger` 도 넣으세요 — 08-12 13:31 재부팅 뒤 다음 차례가 14:05
> 여서 30분간 WSL 을 깨우는 것이 아무것도 없었습니다.
>
> 단 `IgnoreNew` 는 **믿을 것이 못 됩니다.** 걸어 두었는데도 14:06 과 14:07 에 두
> 개가 떴습니다. 스크립트 안에서 뮤텍스(`Local\ClaudeWslHold`)로 직접 막습니다.

> **감시견의 확인 간격은 정지 판정과 분리하세요.** 감시견이 1시간마다 확인하는
> 동안 홀드 결함으로 감시견 자신이 5분마다 죽고 되살아났습니다. 새로 뜬 감시견은
> 시작 직후 한 번 보고(그때는 진전이 최근이라 통과) 잠들었다가 1시간을 못 채우고
> 죽었습니다. **감시견이 9번 떴는데 고장을 한 번도 못 잡았고**, LAMMPS 는 12:47 에
> 죽어 76분간 방치됐습니다. 확인은 5분마다, 판정 기준은 1시간 무진전 그대로입니다.

> **`ensure_guards.sh` 에는 잠금이 필요합니다.** 윈도우 예약 작업(5분)과
> crontab(10분)이 둘 다 부르므로 겹치면 같은 감시견을 두 번 띄웁니다.
> `flock -n` 으로 겹친 호출은 물러나게 합니다.

> **`Start-Process wsl.exe` 는 출력 리다이렉트가 없으면 조용히 즉시 죽습니다.**
> 예약 작업에는 콘솔이 없기 때문입니다. `-RedirectStandardOutput` /
> `-RedirectStandardError` 를 반드시 붙이세요. 08-12 08:20 과 08:22 에 이걸
> 빠뜨려 홀드 프로세스가 두 번 즉사했고, 로그에는 "새로 띄움"만 남아 있었습니다.

> **crontab `@reboot` 에는 되살릴 것을 **전부** 넣으세요.** 원래 keepalive 만
> 들어 있었습니다. 그래서 08-10 17:25 에 VM 이 다시 떴을 때 keepalive 만 살아나고
> LAMMPS 는 39시간 방치됐습니다. 지금은 `ensure_guards.sh` 하나를 부릅니다.

> **감시견이 '포기'한 뒤에는 되살리지 마세요.** 바깥의 5분 감시가 감시견을
> 되살리면 재시도 횟수가 0으로 돌아가 사실상 무한 재시도가 됩니다.
> `.watchdog_gave_up` 파일로 막습니다.

**윈도우 빠른 시작(Fast Startup)은 꺼야 합니다.** 켜져 있으면 전원을 껐다 켠 뒤
WSLService 가 30초 타임아웃으로 매달려 **WSL 이 아예 안 뜹니다**(2026-08-12 08:07:40,
`Service Control Manager` 이벤트 7011). 커널 세션을 최대 절전으로 남겨 두는 방식이라
WSL 의 가상화 상태와 어긋납니다. 관리자 권한으로 한 줄이면 됩니다.

```
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Power" /v HiberbootEnabled /t REG_DWORD /d 0 /f
```

확인은 `Get-WinEvent`의 `Microsoft-Windows-Kernel-Boot` 이벤트 27 입니다. 부팅 유형이
`0x1` 이면 빠른 시작, `0x0` 이면 정상 냉부팅입니다.

### 3-12-1. 윈도우 업데이트가 오후에 재부팅한다 — 활성 시간이 거꾸로다

2026-08-12 13:29 과 13:31 에 컴퓨터가 두 번 재부팅했습니다. `TrustedInstaller.exe`
가 `NT AUTHORITY\SYSTEM` 권한으로 건 것이고(User32 이벤트 1074), 원인은
`2026-08 보안 업데이트 (KB5121003)` 입니다. 08:39 에 설치를 시작해 13:34 에
완료됐습니다.

왜 하필 오후였는지가 핵심입니다.

```
ActiveHoursStart = 19시
ActiveHoursEnd   = 13시
-> 재부팅이 허용되는 창 = 13시 ~ 19시
```

활성 시간이 19시~13시로 잡혀 있어, **윈도우가 재부팅해도 된다고 보는 유일한 창이
오후 1시~7시**입니다. 계산을 돌리는 시간대와 정확히 겹칩니다.

활성 시간은 최대 18시간이라 이것만으로는 완전히 막을 수 없습니다. 24시간 계산을
돌린다면 정책으로 막아야 합니다 (Pro 이상, 관리자 권한).

```
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" /v NoAutoRebootWithLoggedOnUsers /t REG_DWORD /d 1 /f
```

로그인한 사용자가 있으면 자동 재부팅을 하지 않습니다. 업데이트 설치 자체는
그대로 되고, 재부팅만 사용자가 직접 할 때까지 미룹니다.

확인은 이렇게 합니다.

```powershell
Get-WinEvent -FilterHashtable @{LogName='System'; StartTime=(Get-Date).AddDays(-3)} |
  Where-Object { $_.Id -in 1074,109,6005,6006 } | Sort-Object TimeCreated
```
1074 에 `TrustedInstaller.exe` 가 보이면 업데이트가 건 재부팅입니다.

### 3-12-2. 메모리 병목은 한 군데 고치면 옆으로 옮겨간다

2026-08-12 하루에 LAMMPS 집계가 **네 번** 죽었습니다. 원인이 매번 달랐습니다.

| 시각 | 죽은 것 | 크기 | 원인 |
|---|---|---|---|
| 14:47 | python | 12.6 GB | `geom()` 의 `get_all_distances(mic=True)` |
| 15:36 | python | 13.5 GB | 같음 |
| 16:41 | network (Zeo++) | 3.2 GB × 8워커 | `geom()` 을 고친 뒤 **제가 워커를 8로 올려서** |
| 18:56 / 20:07 | (OOM 아님) | — | `zeo()` 가 None 을 돌려줄 때 표 출력이 `TypeError` |

**교훈 1 — `get_all_distances(mic=True)` 를 쓰지 마세요.** 5,248원자 슈퍼셀에 기운
육방 셀(γ=120°)이면 ASE 가 주기 이미지를 펼치며 수 GB 를 잡습니다. 최소 원자간
거리는 이웃 목록으로 구하면 **같은 값**이 나오고 메모리는 원자 수에 비례합니다.
실측: 0.946 = 0.946 (동일), 0.36 s → 0.02 s, 12,600 MB → 489 MB.

```python
from ase.neighborlist import neighbor_list
d = neighbor_list('d', atoms, 2.0)   # 결합 거리 1.0~1.6 A 는 항상 걸린다
```

**교훈 2 — 병목을 고쳤으면 워커 수를 다시 재세요.** `geom()` 을 고치자 병목이
파이썬에서 Zeo++ 로 옮겨갔습니다. Zeo++ 는 이완 후 슈퍼셀 한 건에 **3.2 GB** 를
씁니다. 8워커면 25.6 GB 로 20 GB 상한을 넘습니다. 이 단계는 CPU 가 아니라 메모리에
묶여 있어 워커를 늘리면 느려지는 게 아니라 **죽습니다.** 4워커(12.8 GB)가 상한입니다.

**교훈 3 — OOM 은 계산만 죽이지 않습니다.** 16:41 의 OOM 이 `dbus-daemon` 을
죽이자 WSL 배포판이 통째로 먹통이 됐습니다. `wsl.exe --exec` 이 0초 만에 반환하는
상태가 되고, **다시 거는 것만으로는 절대 안 풀립니다.** `wsl --shutdown` 이 유일한
해법입니다. 그런데 이때 세션의 작업 디렉터리가 `\\wsl.localhost\Ubuntu\` 라
PowerShell 도 bash 도 못 뜹니다 — **`echo hello` 조차 실패합니다.** 셸로는 손을 쓸
수 없으므로 복구는 예약 작업 안에 있어야 합니다(`wsl_hold.ps1` 의 자가 복구).

**교훈 4 — 측정 실패는 그 구조만 탈락시키세요.** `zeo()` 는 Zeo++ 가 죽으면
LCD/PLD 를 None 으로 돌려주는데, 표 출력이 `f'{m0["PLD"]:>8.3f}'` 라 None 을
만나면 `TypeError` 로 **집계 전체가 죽습니다.** 이완 17종이 다 끝나 있었는데도
결과가 두 번 통째로 날아갔습니다. 3-8, 3-13 과 같은 계열입니다.

### 3-12-3. 판정 기준이 없으면 '탈락'이 아니라 '판정 불가'다

아릴 인덱스에는 무치환 모체(base)가 없습니다. 그래서 `lcd_ref` 가 None 이 되고,
`drop` 이 nan 이 되고, **`nan < 20.0` 이 False 라서 12종이 전부 탈락**했습니다.
판정이 아니라 부동소수점 부작용입니다. 기준을 saIm 쪽 결과에서 가져오도록 고치자
같은 데이터로 **11종 통과**가 됐습니다.

nan 비교는 항상 False 라, 빠진 기준이 조용히 '전부 탈락'으로 둔갑합니다.
**판정할 수 없는 것과 탈락은 다릅니다.** 판정 불가는 그렇게 기록하세요.

### 3-13. 전멸한 결과가 멀쩡한 결과를 덮는다

2026-08-10 17:29 에 `18_PoreNarrowing/risk_screen.py` 가 `lammps_mof` 환경 없이
실행됐습니다. 16개 구조 **전부** `lammps-interface 실패`로 끝났는데, 스크립트는
그 실패 목록을 그대로 `risk_results.json` 에 썼습니다. 14 KB 의 기하 데이터가
3.8 KB 의 실패 목록으로 바뀌었습니다.

git 이 미커밋 변경으로 잡아 주지 않았으면 모르고 지나갔을 사고입니다. 3-8(조용한
`timeout`)과 같은 종류입니다 — **실패가 결과처럼 보이는 것.**

두 `risk_screen.py` 에 방어를 넣었습니다. **통과가 0개인데 기존 파일에는 통과가
있으면 덮지 않고** `risk_results.allfail.json` 에 따로 쓰고 종료코드 1 을 냅니다.
결과 파일을 쓰는 스크립트를 새로 만들 때 같은 방어를 넣으세요.

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
