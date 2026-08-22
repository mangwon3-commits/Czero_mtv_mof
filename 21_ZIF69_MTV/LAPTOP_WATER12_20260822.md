# 랩탑 지시서 — 수분 격자 12작업 (2026-08-22)

**이 문서 하나만 읽고 시작할 수 있게 썼습니다.** 대화 맥락을 옮기려 하지
마세요. 세션은 서로의 대화를 모릅니다.

---

# 0. 한 줄 요약

`saIm0625` · `saIm0667` · `saIm0875` **3종 × RH 0/25/50/90 = 12작업**의
CO₂/H₂O 이원 GCMC. 러너는 이미 저장소에 있고 **검증됐습니다.**

승자 조성 `saIm0583` 4작업은 **데스크탑이 맡습니다.** 겹치지 않습니다.

---

# 1. ⚠️ 먼저 — 이 기기는 잠들면 안 됩니다

**오늘 이 프로젝트가 이 실패로 하루를 잃었습니다.**

4코어 클라우드 컨테이너가 55분마다 재부팅되는 기기였는데, 작업 하나에
**연속** 2.9~23.1시간이 필요합니다. 결과는 4작업 전멸이었습니다.
디스크가 살아남았는데도 소용이 없었습니다 —

> **RASPA 체크포인트는 분자 배치만 복원하고 진행도는 복원하지 않습니다**
> (`run_water.py:163`). 중단될 때마다 생산 15,000 사이클이 **0 으로**
> 돌아갑니다. 게다가 `.resume_attempted` 표식 때문에 **두 번째 실패부터는
> 체크포인트를 폐기하고** 배치 복원조차 없습니다.

08-17 정전 때 19작업을 살린 이어받기는 **작업 *경계*에서만** 작동합니다.
**작업 *내부*에는 그물이 없습니다.**

**랩탑은 정확히 이 위험을 갖고 있습니다.** 12작업이 **26~33시간** 걸립니다.

시작 전에 사용자에게 확인하세요:

- [ ] **전원 어댑터 연결**
- [ ] **덮개를 닫아도 절전으로 들어가지 않게** 설정
- [ ] 윈도우 절전/최대 절전 차단 (`powercfg /change standby-timeout-ac 0`)
- [ ] 자동 업데이트 재부팅 연기 — 08-07 에 `TrustedInstaller.exe` 가
      강제 재부팅을 걸어 6작업(그중 셋은 19시간짜리)을 날렸습니다

**하나라도 확실하지 않으면 시작하지 말고 사용자에게 물으세요.**
26시간 뒤에 아무것도 없는 것보다 지금 30분 늦는 편이 낫습니다.

---

# 2. 준비

```bash
cd ~/mof_project
git fetch origin '+refs/heads/*:refs/remotes/origin/*'
git status --short          # 계산 중이 아니면 pull, 돌고 있으면 fetch 만
git merge --ff-only origin/master
export RASPA_DIR=$HOME/RASPA/simulations
export PATH=$HOME/miniconda3/envs/czeromof/bin:$PATH
```

> **계산 중에는 `git pull` 을 쓰지 마세요.** 작업 트리가 바뀝니다.
> 지금은 시작 전이라 괜찮습니다.

## 검증 넷 — 전부 통과시키고 넘어가세요

```bash
cd ~/mof_project/21_ZIF69_MTV

# ① 힘장이 우리 것인가 — q 0.6512 / 29.933 2.745 / 38.298 3.306
grep -E "^C_co2" "$RASPA_DIR/share/raspa/forcefield/UFF_MOF/pseudo_atoms.def"
grep -E "C_co2|N_n2" "$RASPA_DIR/share/raspa/forcefield/UFF_MOF/force_field_mixing_rules.def"

# ② 물이 5자리인가 — 5 가 나와야 합니다
awk 'NF>4 && ($2=="Ow"||$2=="Hw"||$2=="Lw")' ../19_WaterCompetition/water.def | wc -l

# ③ 러너가 보는 환경에서 simulate 가 잡히는가 (PATH 를 비우고)
env -i HOME=$HOME PATH=/usr/bin:/bin \
  ~/miniconda3/envs/czeromof/bin/python -c \
  "import sys; sys.path.insert(0,'.'); import run_water as rw, os; \
   print(rw.SIMULATE, os.path.exists(rw.SIMULATE))"

# ④ 전하 CIF 3종이 있는가
ls charged_v3/saIm0625_DDEC6.cif charged_v3/saIm0667_DDEC6.cif charged_v3/saIm0875_DDEC6.cif
```

> `which simulate` 만 쳐 보고 판단하지 마세요 — 그건 당신 셸의 PATH 이고
> 무인 실행(`setsid nohup`) 러너가 보는 PATH 가 아닙니다. 08-19 에 이 차이로
> 배정 하나가 실행 불가였습니다.

힘장 트리가 없으면:

```bash
mkdir -p "$RASPA_DIR/share/raspa"
cp -r ~/mof_project/00_Migration/raspa_share/raspa/* "$RASPA_DIR/share/raspa/"
```

---

# 3. 실행

```bash
cd ~/mof_project/21_ZIF69_MTV
PHYS=$(lscpu -p=Core,Socket | grep -v '^#' | sort -u | wc -l)
echo "물리 코어 $PHYS"          # 논리(하이퍼스레딩) 수를 쓰지 마세요

export WATER_BATCH_TAG=laptop
WATER_V3_WORKERS=$PHYS setsid nohup \
  python -u run_water_v3grid_rest3.py > water12.log 2>&1 < /dev/null &
```

러너가 시작할 때 **힘장·물 정의·전하 CIF·대상 3종**을 스스로 검사하고,
5자리 물이 아니면 계산을 시작하지 않고 종료합니다.

**메모리**: RASPA 는 건당 약 471 MB 입니다. 8워커라도 3.8 GB.
WSL2 는 기본으로 호스트 RAM 의 절반만 쓰므로 16 GB 기기면 WSL 은 8 GB —
충분합니다. **Zeo++ 는 이번 일감에 없습니다. 띄우지 마세요**(건당 9.5 GB).

## 중단되면

**같은 명령을 그대로 다시 치세요.** 완주한 작업은 `cached` 로 건너뜁니다.
다만 **진행 중이던 작업은 처음부터** 돕니다(1절 참조).

⚠️ **설정을 건드렸다면 재개하지 말고** `water_runs_v3grid/` 를 지우고
처음부터 도세요 — 이어받기는 출력 파일의 존재만 보고 무슨 설정으로
만들어졌는지 검사하지 않습니다.

---

# 4. 예상 시간과 진행 확인

외부 기기 실측: **RH0 ≈ 2.9시간, RH90 ≈ 23.1시간**(약 8배 차이).
우리 이력은 작업 길이가 1.5~20.2시간으로 흩어집니다.

| 물리 코어 | 12작업 전체 |
|---|---|
| 8코어 | **26~33시간** |
| 4코어 | 45~60시간 |

`ProcessPoolExecutor` 는 파도로 끊지 않고 **워커가 비는 대로 다음 작업을
집습니다.** RH0 이 먼저 끝나고 RH90 이 꼬리를 만듭니다.

```bash
tail -20 water12.log
pgrep -x simulate | wc -l        # pgrep -f 를 쓰지 마세요 — 자기 명령줄에 걸립니다
python -c "import json;print(len(json.load(open('v3_water_grid/water_results.json'))))"
```

**출력 파일이 몇 시간째 그대로여도 멈춘 게 아닙니다** — `PrintEvery` 가
생산 사이클 수와 같아 처음과 끝에만 씁니다.

## 이 기기 속도를 재 주세요

`WriteBinaryRestartFileEvery 500` 을 시계로 쓸 수 있습니다.
**기동 직후 첫 구간은 쓰지 마세요** — 프로세스 기동 비용이 섞입니다
(08-22 에 그래서 7.3시간이라는 틀린 값이 나왔습니다). 정상 구간 두세 개의
간격을 재서 `500 사이클당 초 × 40 = 20,000 사이클` 로 환산하세요.

```bash
ls -la --time-style=+%H:%M:%S water_runs_v3grid/rh00_saIm0625/CrashRestart/
```

---

# 5. 끝나면

완주 후 러너가 **`v3_water_grid/water_results_laptop.json`** 을 자동으로
만듭니다(`WATER_BATCH_TAG` 에서 이름을 읽습니다).

```bash
cd ~/mof_project/21_ZIF69_MTV
python merge_water_batches.py --selftest        # 먼저 도구 자기 검증
git add v3_water_grid/water_results_laptop.json 21_ZIF69_MTV/COMMS/laptop.md
git commit && git push origin <자기 브랜치>
```

> **`v3_water/water_results.json`(기존 5종)에 합치지 마세요.**
> 그리고 **데스크탑 산출물을 덮지 마세요** — 러너가 전부 같은 경로에 씁니다.
> 기기 이름 붙은 사본만 공유하고, 합치는 것은 `merge_water_batches.py` 가
> 검산하며 합칩니다.

## 결과가 나오면 무엇을 말할 수 있나

사전 등록된 기준을 그대로 적용합니다(**결과를 보고 고치지 않습니다**):

```
유지율 = RH90 CO₂ 로딩 ÷ RH0 CO₂ 로딩 × 100%
  ≥ 80%     유효
  50 ~ 80%  조건부
  < 50%     노선 종료
```

**유지율만 적으면 결론이 거꾸로 읽힙니다.** 비율이라 분모가 조성마다 크게
다릅니다. **표에 절대 로딩을 반드시 병기하세요.**

기존 5종의 결과: 25~75% 구간이 76~80%의 고원이고 100%에서 60.6%로 꺾입니다.
당신의 3종이 그 사이를 채웁니다.

---

# 6. 연락

규약은 `21_ZIF69_MTV/COMMS.md`. **당신 우편함은 `COMMS/laptop.md` 입니다.**

- **한 파일 한 필자** — 자기 우편함만 쓰고 남의 것은 읽기만 합니다
- 자기 브랜치에 푸시하고, 읽을 때는 전 브랜치 fetch
- 데스크탑이 origin 전 브랜치를 5분마다 봅니다. 커밋하면 전달됩니다

첫 글에 적어 주세요: 물리 코어 수 · 커널(`uname -r`) · RAM · 절전 차단 여부.

---

# 7. 하지 말 것

| 금지 | 이유 |
|---|---|
| 구조 생성 | 검사 항목이 다릅니다(충돌·고아 원자·조성 개수). 08-14 결함이 그 자리에서 났습니다 |
| `rebuild_structures.py` 실행 | argparse 가 없어 `--help` 만 줘도 `structures_v2/` 를 덮어씁니다 |
| 돌고 있는 bash 스크립트 편집 | 바이트 오프셋으로 읽어 엉뚱한 줄을 실행합니다 |
| 사이클·힘장·컷오프 조정 | 기존 결과와 합칠 수 없게 됩니다 |
| Zeo++ 실행 | 이번 일감에 없습니다. 건당 9.5 GB |
| 결과 JSON · `charged_v3/` 삭제 | 재생성에 수십 시간 |

---

# 8. 막히면

**추측해서 진행하지 말고 멈추고 물어보세요.** 이 프로젝트에서 가장 비싼
실패는 전부 "그럴듯하게 완주한 계산"이었습니다. 계산이 안 도는 것은 싸게
고칩니다. 틀린 채로 도는 것은 몇 주 뒤에 발견됩니다.
