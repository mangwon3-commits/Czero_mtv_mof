# 랩탑 10시간 세션 계획 (2026-08-18)

**전제:** 랩탑은 dry-WC 24작업을 끝내 넘겼습니다(V3_WC_LAPTOP_VALIDATION.md).
이번 세션의 주 산출물은 **v3 밀도맵**이고, 남는 시간은 **구조 안정성 관문**에
씁니다. 두 번째가 중요합니다 -- 지금 v3 관문 중 **아무에게도 배정되지 않은
유일한 항목**이고, 데스크탑은 RASPA 가 계속 돌아 Zeo++ 를 못 올립니다.

## 왜 랩탑이어야 하는가

Zeo++ 는 한 건에 3.2 GB 입니다. 08-12 에 RASPA 위에 8워커로 얹었다가 OOM 이
나고 dbus 까지 죽어 WSL 이 통째로 멈췄습니다. 그래서 규칙이 **RASPA 가 도는
기기에서는 Zeo++ 금지**입니다. 데스크탑은 습윤 WC v3 다음에 수분 백업까지
물려 있어 08-20 까지 RASPA 가 빌 틈이 없습니다.
**밀도맵이 끝난 뒤의 랩탑만이 Zeo++ 를 올릴 수 있는 자리입니다.**

## 시간표 (T = 세션 시작)

| 구간 | 할 일 | 관문 |
|---|---|---|
| T+0:00~0:20 | 사전 점검 | 아래 A |
| T+0:20~0:50 | 밀도맵 연기 시험 1작업 | VTK 파일이 실제로 생겼나 |
| T+0:50~3:30 | 밀도맵 10작업 (워커 8) | density_results.json + VTK 10폴더 |
| T+3:30~4:00 | 밀도맵 검증·포장 | 아래 C |
| T+4:00~4:30 | **안정성 연기 시험 1종** | 아래 D. 여기서 막히면 중단 |
| T+4:30~9:00 | 안정성 v3 전체 (워커 4) | risk_results_v3.json |
| T+9:00~10:00 | 포장·인계 | 해시 동봉 |

밀도맵 추정치는 실측 기반입니다 -- v2 가 10작업/4워커로 약 3.3시간이었으므로
8워커면 약 1.7~2.5시간입니다. 넉넉히 잡아 3.5시간을 씁니다.

## A. 사전 점검 (건너뛰지 마세요)

```bash
cd ~/mof_project/21_ZIF69_MTV
pgrep -x simulate | wc -l          # 0 이어야 합니다
df -h .                            # 5 GB 이상 여유
export RASPA_DIR=$HOME/RASPA/simulations
export PATH=$HOME/miniconda3/envs/czeromof/bin:$PATH
grep C_co2 $RASPA_DIR/share/raspa/forcefield/UFF_MOF/force_field_mixing_rules.def
#   29.933  2.745  가 나와야 합니다. 아니면 여기서 멈추세요
```

**`.bashrc` 는 비대화형 셸에서 조기 return 하므로 RASPA_DIR 이 안 잡힙니다.**
conda 배포본 share/raspa 에는 UFF_MOF 가 아예 없어서, export 를 빠뜨리면
조용히 틀리는 게 아니라 즉시 실패합니다(랩탑에서 이미 겪음).

## B. 밀도맵 (주 산출물)

```bash
setsid nohup env DENSITY_V3_WORKERS=8   python -u run_density_v3.py > density_v3.log 2>&1 < /dev/null &
```

5구조(base/saIm025/050/075/100) x 전하 ON/OFF = 10작업.
**ON-OFF 정규화 차이가 LJ 항을 상쇄하고 정전기 재분포만 남깁니다.**
이것은 흡착 순위를 만드는 계산이 아니라 **이미 나온 순위를 설명하는** 그림입니다.

## C. 밀도맵 검증

```bash
test -s density_v3/density_results.json && echo RESULT_JSON_READY
find density_v3 -name '*DensityProfile*' | wc -l    # 10 이상
du -sh density_v3
```

**VTK 격자를 지우지 마세요.** 진행률 표시를 깔끔하게 만들려고 지우면 그림의
원본이 사라집니다. v2 때 density_v2/ 를 보존한 이유와 같습니다.

## D. 안정성 연기 시험 -- 이 관문이 핵심입니다

```bash
pgrep -x simulate | wc -l          # 반드시 0. 아니면 시작 금지
RISK_V3_SMOKE=1 RISK_WORKERS=1 python risk_screen_v3.py 2>&1 | tee risk_v3_smoke.log
```

**출력에서 이 두 줄을 눈으로 확인하세요.**

```
STRUCT   .../structures_v3_stage      <- structures/ 가 아니어야 합니다
결과     .../risk_results_v3.json
```

risk_screen.py 는 STRUCT 기본값이 v1 폴더입니다. 그대로 부르면 **v3 라고 이름
붙인 결과가 v1 구조에서 나오고 실패하지도 않습니다.** 래퍼가 staging 폴더로
갈아 끼우지만, 사람이 한 번 눈으로 봐야 합니다.

연기 시험이 통과하면 전체:

```bash
setsid nohup env RISK_WORKERS=4   python -u risk_screen_v3.py > risk_v3.log 2>&1 < /dev/null &
```

**워커 수를 문서에서 베끼지 마세요. 이 기기에서 재세요.**

    free -g            # MemAvailable 확인
    # 워커 상한 = (가용 GB - 4) / 3.2

08-18 에 이 자리에 "워커 4" 라고 적었다가 랩탑을 OOM 으로 무너뜨렸습니다.
그 4 는 **20 GB 를 쓰는 데스크탑에서** 나온 값입니다. WSL2 는 기본으로
**호스트 RAM 의 절반**만 쓰므로 16 GB 랩탑이면 WSL 은 8 GB 이고, 4 x 3.2 =
12.8 GB 는 반드시 죽습니다.  가 이제 스스로 계산해
낮추지만, 사람도 시작 전에 한 번 보십시오.

메모리를 늘리고 싶으면 윈도우  에

    [wsl2]
    memory=12GB

## E. 판정 기준 (돌리기 전에 등록됨)

안정성은 **순위를 만들지 않습니다. 탈락시키는 관문입니다.**

| 항목 | 탈락선 |
|---|---|
| LCD 감소 | 20% 초과 |
| 최소 원자간 거리 | 0.7 A 미만 |
| 접근가능부피 | 20 A^3 미만 |

통과한 것들 사이의 순위는 여기서 매기지 않습니다. 그 순위는 GCMC·작업용량·
수분이 정합니다.

## F. 인계

```bash
mkdir -p ~/mof_export
tar czf ~/mof_export/zif69_v3_density_laptop.tar.gz density_v3 density_v3.log
tar czf ~/mof_export/zif69_v3_risk_laptop.tar.gz   risk_results_v3.json lmp_v3 risk_v3.log risk_v3_smoke.log 2>/dev/null
sha256sum ~/mof_export/*.tar.gz > ~/mof_export/SHA256
```

**git pull / rebase / clean 금지.** 랩탑 계보가 데스크탑 생산 커밋 이전에
갈라져 있습니다. 결과 파일만 보내면 데스크탑이 해시 확인 후 정본 경로에
넣고 커밋합니다.

## G. 중단되면

밀도맵과 안정성 둘 다 **작업 단위 이어받기**가 있습니다. 코드나 설정을
바꾸지 않았다면 같은 명령을 다시 치면 됩니다. 설정을 바꿨다면 해당 실행
폴더를 지우고 처음부터 -- 이어받기는 **무슨 설정으로 만든 출력인지 검사하지
않습니다**(CLAUDE.md 3절).

## H. 안정성 단계의 별도 전제 — LAMMPS

밀도맵은 RASPA 만 있으면 되지만 **안정성은 다릅니다.**

    lmp_serial            UFF4MOF 이완용. conda install -c conda-forge lammps
    network (Zeo++)       기공 지표용. czeromof 환경에 있음
    lammps_iface_patched  꾸러미에 동봉됨(18_PoreNarrowing 에서 자동으로 딸려옴)

**황(-SO3H)이 있는 구조 때문에 S_3+6 패치가 필요합니다.** 표준 UFF4MOF 타이핑은
6가 사면체 황을 잘못 잡아 이완이 깨집니다. 그래서 동봉한 래퍼를 씁니다 --
직접 구현하지 마세요.

먼저 확인하세요.

    which lmp_serial && which network

**둘 중 하나라도 없으면 안정성 단계를 건너뛰고 밀도맵만 하십시오.**
LAMMPS 설치는 10시간 세션 안에서 감당할 일이 아니고, 밀도맵이 이번 세션의
주 산출물입니다. 없다고 알려 주시면 안정성은 60시간 무인 운전으로 넘깁니다.
