# 환경 전제 — 데스크탑에서는 되고 다른 기기에서는 안 되는 것들

2026-08-19~20 이틀 동안 같은 유형이 **네 번** 나왔습니다. 전부 랩탑이
부딪혔고, 전부 데스크탑에서는 보이지 않던 것입니다. 다음 기기(지인 16코어,
새 세션, 복귀 후의 본인)가 같은 자리에서 시간을 버리지 않도록 적어 둡니다.

## 네 건

| # | 자리 | 무엇을 가정했나 | 어떻게 드러났나 |
|---|---|---|---|
| 1 | `relax_fixcell.py:65` | `XTB = '/home/mangwon1/.../envs/spectra/bin/xtb'` 데스크탑 절대경로 하드코딩 (**09-03 5e5d931 에서 `XTB_BIN` 환경변수 폴백으로 고침**) | 랩탑에 그 env 자체가 없음. L1 이 0단계로 실패 |
| 2 | `laptop60.sh:34` | `CZ=czeromof` 하나로 전 단계 실행 | PACMANCharge 는 `coremof_tools` 에 있음. L2 중단 |
| 3 | `charge_v3.py:61` | import 가 스킵 검사보다 **앞** | 35종 전부 충전돼 있어도 import 에서 죽음 |
| 4 | `risk_screen.py:256` | `lmp_serial` bare 호출 | 러너 PATH 에 lammps_mof/bin 없음. **실행 전 차단** |

## 공통 구조 — 세 문장

**하나. 코드가 호출자의 셸 상태에 의존하고 있었습니다.**
4번이 08-19 02:00 에 성공한 것은 그 세션이 conda 활성화 상태에서 띄워졌기
때문입니다. 그런데 이 프로젝트의 무인 실행 규약은 `setsid nohup` 이고
거기엔 그 상태가 없습니다. **규약과 코드가 어긋나 있었고, 그 사실이
한 번의 우연한 성공에 가려져 있었습니다.**

**둘. 성공은 의존을 감춥니다.** 네 건 모두 데스크탑에서 수십 번 돌았고
한 번도 안 드러났습니다. 드러나는 조건은 "기기가 바뀌는 것" 하나뿐입니다.

**셋. 한 파일 안에서도 한쪽만 배웁니다.** `risk_screen.py` 의 `NETWORK` 는
이미 `shutil.which` + 절대경로 폴백을 쓰고 주석까지 달려 있었습니다
("PATH 에 없으면 조용히 실패해 LCD/PLD 가 0 으로 기록된다"). 같은 파일의
`lmp_serial` 만 빠져 있었습니다.

## 규약

**외부 실행파일은 코드 안에서 해석합니다.**

```python
LMP = shutil.which('lmp_serial') or os.path.expanduser(
    '~/miniconda3/envs/lammps_mof/bin/lmp_serial')
```

검증은 **PATH 를 비운 상태**에서 합니다. `which` 만 쳐 보면 자기 셸의
PATH 를 보고 "있다" 고 답합니다 -- 러너가 보는 PATH 가 아닙니다.

```bash
env -i HOME=$HOME python -c "import risk_screen as rs, os; print(rs.LMP, os.path.exists(rs.LMP))"
cat /proc/<러너PID>/environ | tr '\0' '\n' | grep ^PATH=      # 러너의 실제 PATH
```

**무거운 의존은 필요한 분기 안에서 import 합니다.** 스킵 경로가 있는
러너는 스킵만 하고 끝날 때 그 의존을 건드리면 안 됩니다(3번).

**새 기기에 일을 넘기기 전에 의존을 먼저 찍어 봅니다.** 파일 존재가 아니라
**러너가 보는 환경에서** 확인합니다. 정적 검사로 충분한 것은 정적으로만
하세요 -- import 시점에 경로를 계산하는 모듈이 섞여 있습니다.

## 아직 안 고친 것

- ~~**1번**~~ **고쳐짐(09-03, 5e5d931)** — `relax_fixcell.py:65` 가
  `os.environ.get('XTB_BIN', <데스크탑 경로>)` 입니다. laptop2 가 §6 이완 체인을
  `XTB_BIN=~/miniconda3/envs/spectra/bin/xtb` 로 띄워 실제 동작 확인(09-03 13:xx).
  **폴백이 있어도 xtb 가 설치돼 있어야 합니다** — 랩탑은 09-03 현재 env 4개 전수에
  xtb 가 없어(랩탑 2e618ae) GFN-FF 이완을 못 받습니다. 판은 등록 판 **xtb 6.7.1
  conda-forge**(`ASSIGN_20260903.md` 129행, `COMMS/desktop.md` 의 "부피 환산이 6.7.1
  특성")로 맞춰야 하며, 설치 지시 없이 §6 계열을 배정하면 08-19 와 같은 자리에서 죽습니다
- **2번** `laptop60.sh` 의 단일 env 가정도 그대로입니다. 단계별로 다른
  env 가 필요하다는 사실이 문서화되지 않았습니다
