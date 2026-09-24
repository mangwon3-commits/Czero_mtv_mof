# 배정 — 습윤(RH90) 밀도 격자 **사다리 메우기** (2026-09-24 **14:4x**, 데스크탑 종합자)

**대상 기기**: laptop(8코어) · HKHOME(부수 1건). **등록 덱 확장**이므로 이 문서가 그 등록입니다(CLAUDE.md §8).
**사용자 요청 계보**: 09-23 *"넣어. 습윤조건에서 물이랑 비교할 밀도맵은 만들 수 없는 건가?"* 의 이어짐.

## 0. 지금 있는 것 — **8조성 전부 완주 표지 확인**(14:4x, `Simulation finished`)

    base ✅  nbIm025 ✅  nbIm075 ✅  sa50nb50 ✅  saIm050 ✅  saIm0583 ✅  mslm050 ✅  saIm100 ⚠탈락

산출은 `water_runs_density_v3w/rh90_<조성>/VTK/` 에 있습니다.
⚠ `density_water_v3w/gap_*` 폴더가 **비어 보이지만** 그건 부모 폴더일 뿐입니다 — *"없음" 이 아니라 "못 봄"* 입니다
(오늘 세 번째로 같은 함정. laptop2 14:2x · Junseok 08:3x · 이것).

## 1. 왜 이 셋인가 — **사다리가 한 칸씩 비어 있습니다**

    술폰산 습윤 사다리   base(0 %) ✅ →  **saIm025(25 %) ⬜**  → saIm050(50 %) ✅ → saIm0583(58.3 %) ✅
                        [saIm100 은 관문 탈락 — 사다리 상한 표시로만 씁니다]
    대조 사다리          **mslm025 ⬜** → mslm050 ✅        (술폰산과 견줄 작용기)
    저선택도 끝          **cf3Im025 ⬜**                     (선택도 37.5 — 사다리 아래 끝)

`saIm025` 하나가 **술폰산 습윤 사다리의 유일한 빈칸**입니다. 이것이 있어야
*"치환율을 올리면 물이 어디로 가는가"* 를 **관문 통과 조성만으로** 그릴 수 있습니다.

⚠ **관문 6/6 확인**(14:4x): saIm025 6.69 % · mslm025 5.25 % · cf3Im025 1.27 % — **셋 다 통과**.
아침의 제 밀도맵 배정이 `mslm075`(탈락)를 덱에 넣었던 것과 **같은 실수를 안 하려고 먼저 쟀습니다**.

## 2. 기동

⚠ **기동 줄 보완 (15:0x — laptop 지적)**: `RASPA_DIR` 이 `.bashrc` 에만 있으면 **비대화 셸에서 빠집니다.**
`setsid nohup` 은 비대화 셸이라 그대로 치면 안 잡힙니다. **두 줄을 먼저 주십시오.**

    export RASPA_DIR=$HOME/RASPA/simulations          # share/raspa 의 **부모**
    PY=$(conda run -n czeromof which python 2>/dev/null || echo python)   # 또는 절대경로 명시

그리고 **15:0x 부터 `run_water.py` 에 힘장 관문이 생겼습니다** — 안 고친 `$RASPA_DIR` 사본이면
**실행 폴더를 만들기 전에 멈춥니다**(아래 §2-1). 이미 도는 작업에는 영향이 없습니다.


    laptop (둘을 **동시에**, 8코어에 simulate 2)
        cd 21_ZIF69_MTV
        DW_EXTRA=saIm025 DW_SUB=lap_saIm025 setsid nohup python run_density_water_v3w.py saIm025 \
            < /dev/null >> ../.claude_work_densw_saIm025.out 2>&1 &
        DW_EXTRA=mslm025 DW_SUB=lap_mslm025 setsid nohup python run_density_water_v3w.py mslm025 \
            < /dev/null >> ../.claude_work_densw_mslm025.out 2>&1 &

    HKHOME (부수 1건)
        DW_EXTRA=cf3Im025 DW_SUB=desk_cf3Im025 setsid nohup python run_density_water_v3w.py cf3Im025 …

⚠ **`DW_EXTRA` 없이 주면 러너가 막습니다** — `run_density_water_v3.py:110` 이 등록 덱(`base·nbIm025·saIm050`)
밖 대상을 거부합니다. **관문이 맞게 동작하는 것이고**, `DW_EXTRA` 가 이 문서로 등록된 확장입니다.
⚠ **`DW_SUB` 를 꼭 주십시오** — 안 주면 두 프로세스가 같은 결과 JSON 을 잡습니다(러너 주석의 그 이유).

## 2-1. ★ 힘장 관문을 `run_water.py` 에 넣었습니다 (15:0x — laptop 지적에서 나온 것)

**이 러너는 `water.def`(5자리 분자 정의)는 저장소에서 복사해 지켰지만 힘장 파일은 안 봤습니다.**
`Hw none`/`Lw none` 는 `$RASPA_DIR` 에서 오고 **기기마다 따로 고쳐야 합니다**(CLAUDE.md §1).
안 고친 기기에서 돌면 **수소결합이 없는 물**(친화도 약 8.6배 과소)이 나오는데
**결과는 완전히 정상으로 보입니다** — §0 의 그 무늬입니다.

    `run_water_v3w.py`        09-07 부터 관문 있음
    `run_water.py`            **없었음**  ← 여기
    `run_density_water_v3.py` 가 `run_water` 를 import  →  **습윤 밀도 격자 전체가 관문 밖**이었습니다

**두 길을 다 쟀습니다**(15:0x):

    통과하는 길   정본 md5 8e8ec933… → `ff_gate_once() -> True`                       ✓
    막는 길       **있지만 안 고친 사본**(정본에서 `Hw none`/`Lw none` 두 줄 뺀 것,
                  66줄 → 64줄, md5 4d428e02…) → **실행 폴더를 만들기 전에 중단**      ✓
    ⚠ 첫 시험은 `RASPA_DIR=/tmp/nope` 로 쟀는데 **안 막혔습니다** — `ff_gate.ff_path()` 가
      없는 경로면 홈으로 되돌아가기 때문입니다. 그건 **무해한 쪽**(RASPA 도 못 찾아 죽음)이고,
      **위험한 쪽은 "있지만 안 고친 사본"** 입니다. 재서 확인했습니다.

⚠ **파일 관문은 머리말 관문을 대신하지 못합니다**(`ff_gate.py` 자기 주석 · `FF_GATES_20260907 §1`) —
09-05 에 **파일은 맞는데 RASPA 가 지역 힘장을 읽어** 결함판으로 완주한 적이 있습니다.
**끝나면 출력 머리말로 다시 확인하십시오**:

    f=<실행폴더>/Output/System_0/*.data
    md5sum <실행폴더>/water.def                       # 6fc8850d3d22a56a17e5643f35a6f731 (정본 5자리)
    grep -E '^\s*\S+\s+-\s+\S+\s+\[' $f \
      | grep -E '(^\s*(Hw|Lw)\s+-|-\s+(Hw|Lw)\s+\[)' | grep -vc ZERO_POTENTIAL   # → **0** 이어야 합니다
    grep -E '^\s*Ow\s+-\s+Ow\s+\[' $f | head -1  # → p_0/k_B: 89.63300

⚠ **`head` 로 몇 줄만 보면 안 됩니다** (15:0x, laptop 이 더 강하게 재서 드러남). 처음 몇 줄이 `ZERO` 여도
뒤쪽에 아닌 줄이 있을 수 있습니다. **"ZERO 아닌 짝의 수 = 0"** 을 세십시오.
⚠ 그리고 **짝 줄만** 거르십시오. `Hw`·`Lw` 라는 **글자**는 pseudo-atom 표와 분자 원자 목록에도 나옵니다 —
제가 처음에 그걸 같이 세서 *"ZERO 아님 6줄"* 로 읽었습니다(09-24 아침 `water.def` 판별자 둘이 틀렸던 것과 같은 계열:
**세는 대상이 내가 말하는 대상이 아닌** 경우). 짝 줄은 `X  -  Y  [POTENTIAL]` 형식입니다.

데스크탑 `cf3Im025` 는 15:0x 에 이 방법으로 확인했습니다(`water.def` md5 **6fc8850d…** 정본 5자리 ·
`Ow-Ow 89.63300` · `Hw/Lw ZERO_POTENTIAL`).

### 2-2. 왜 `Hw \[ZERO` 같은 한 방향 패턴이 분모를 반쪽으로 만드는가 (15:0x, laptop 이 원인까지 찾음)

세 기기가 같은 검사를 하고 **분모가 달랐습니다** — laptop 17·18 대 데스크탑 647·647.
원인: **짝 표는 pseudo-atom 번호순 삼각형**입니다.

    grep -c 'Hw \[ZERO'      →  `X - Hw` **만** 잡습니다 (Hw 가 오른쪽에 오는 짝)
                                 Hw 는 17번 타입이라 그런 줄은 **앞선 17개뿐**,
                                 나머지는 전부 `Hw - Y` 로 찍힙니다  →  **분모 반쪽**

**판정이 살아남은 까닭**: ZERO 아닌 줄을 **거를 때는** `- Hw` 와 `^Hw -` **두 방향을 다** 봤습니다.
그래서 분자(0)는 맞았고 **분모만 틀렸습니다.** — *"결론이 같았는데도 잰 양은 달랐습니다"*(laptop).

실측(배정문 §2-1 명령 그대로):

    saIm025   Hw/Lw 짝 1305줄 · ZERO 아님 **0** · Ow-Ow 89.63300   (Hw 653 · Lw 653)
    mslm025   Hw/Lw 짝 1329줄 · ZERO 아님 **0** · Ow-Ow 89.63300   (Hw 665 · Lw 665)
    cf3Im025  Hw/Lw 짝 1294줄 · ZERO 아님 **0** · Ow-Ow 89.63300   (Hw 647 · Lw 647)

> **규율(§2 "잰 양" 의 한 사례)**: 대칭 짝 표에서 한쪽 방향 패턴으로 세면 **분모가 조용히 반쪽**이 됩니다.
> **"0 이 나왔다" 만 보고하면 안 드러납니다 — 분모를 같이 적으십시오.**

## 3. 규약 — 건조 밀도맵과 **다릅니다**

    사이클   **초기화 5,000 + 생산 15,000**  (건조 격자의 2,000+5,000 이 아닙니다)
    격자     90³ · RH90 · 298 K · DDEC6 · UFF_MOF · TIP5P-Ew(`Hw none`/`Lw none`)
    출력     `water_runs_density_v3w/rh90_<조성>/VTK/System_0/`
    ⚠ **단일 복셀로 자리를 주장하지 마십시오** (`DENSITY_GRID_TWO_GENERATIONS`).

## 4. 견적 — **출처를 붙입니다**(CLAUDE.md §5)

    데스크탑 실측(09-24, 같은 러너·같은 규약)   mslm050 **452 분** · saIm0583 **552 분**
    → laptop 도 물리 8코어라 **같은 대역으로 봅니다**. 다만 **다른 기기로 옮긴 값**입니다.
      둘을 동시에 띄우면 벽시계는 **max(두 작업)** 이지 합이 아닙니다 — 약 **8~10 h**, 오늘 밤 안.
    ⚠ 첫 `.data` 가 나오는 시점을 보고 **자기 기기 실측으로 갱신**해 주십시오.
    Zeo++ 안 씁니다 — `RISK_WORKERS`·`ZEO_GB_PER_JOB` 손댈 일 없습니다. RASPA 건당 약 471 MB.

## 4-1. 추가 배정 — **Junseok: nb 사다리 완성** (16:0x, 사용자 승인 "do it all")

Junseok 이 Q_st §-보완 18/18 을 **72분**(워커 10 · 작업당 26.5~43.1분 · 씨앗 겹침 0)에 끝내고 비었습니다.

    DW_EXTRA=nbIm050 DW_SUB=jk_nbIm050 setsid nohup <conda python> run_density_water_v3w.py nbIm050 ...
    DW_EXTRA=nbIm100 DW_SUB=jk_nbIm100 setsid nohup <conda python> run_density_water_v3w.py nbIm100 ...

    ⚠ `export RASPA_DIR=$HOME/RASPA/simulations` 를 **먼저** 주십시오(§2). 이제 `run_water.py` 에
      힘장 관문이 있어 안 고친 사본이면 **실행 폴더를 만들기 전에 멈춥니다** — 막히면 그 메시지대로
      고치고 다시 띄우십시오.

**왜**: 습윤 사다리가 **둘**이 되어야 *"물이 술폰산에만 붙는가"* 를 가릅니다.

    술폰산  base ✅ → saIm025(laptop 중) → saIm050 ✅ → saIm0583 ✅   [saIm100 탈락 — 상한 표시용]
    nb      base ✅ → nbIm025 ✅ → **nbIm050 ⬜** → nbIm075 ✅ → **nbIm100 ⬜**

nb 는 **강한 자리가 없는 대조**입니다(§AS 판정 1 에서 base 만 −1.7 로 차가 작았던 그 계열).
둘을 채우면 nb 가 **0→25→50→75→100 다섯 칸 전부** 차는 **유일한 사다리**가 됩니다.

⚠ **관문 확인**(16:0x): nbIm050 LCD 감소 **−0.09 %** · nbIm100 **2.31 %** — **둘 다 통과**. CIF 둘 다 있음.

## 4-2. 추가 — **Junseok: cf3Im 사다리** (16:1x, 남은 논리 코어 10)

nb 둘(16:07·16:08 기동)과 **같이** 돌립니다. simulate 4 / 물리 6코어.

    DW_EXTRA=cf3Im050 DW_SUB=jk_cf3Im050 ... run_density_water_v3w.py cf3Im050
    DW_EXTRA=cf3Im075 DW_SUB=jk_cf3Im075 ... run_density_water_v3w.py cf3Im075

**왜**: 이러면 습윤 사다리가 **셋**이 되고 세 자리가 성질로 갈립니다.

    술폰산  강한 자리 있음      base → saIm025 → saIm050 → saIm0583   [58.3 % 위는 관문 탈락]
    nb      강한 자리 없음      base → nbIm025 → nbIm050 → nbIm075 → nbIm100   (다섯 칸 전부)
    cf3Im   불소 · 저선택도     base → **cf3Im025**(desk 중) → **cf3Im050** → **cf3Im075**

**관문 확인**(16:1x): cf3Im025 1.27 · cf3Im050 4.62 · cf3Im075 7.84 % — **셋 다 통과**. CIF 셋 다 있음.
cf3Im 은 선택도 37.5 로 우리 계열에서 **가장 낮은 축**입니다 — *"물이 강한 자리에 붙는가"* 의 **음성 대조**.

## 4-3. 머리말 확인은 **끝이 아니라 착수 직후**에 합니다 (16:1x — Junseok 개선, 받습니다)

배정문 §2-1 은 *"끝나면 확인"* 이라고 적었는데 **Junseok 이 기동 직후에 했습니다.**

> *"짝 표는 시작 때 찍히므로, 결함판이면 8시간을 버리기 전에 멈출 수 있습니다."*

**맞습니다. 앞으로 그렇게 합니다.** 파일 관문(`run_water.py`)은 md5 만 보고, **머리말은 RASPA 가
실제로 읽은 것**을 보여 줍니다 — 09-05 에 *"파일은 맞는데 RASPA 가 지역 힘장을 읽어"* 결함판으로
완주한 전례가 정확히 그 틈입니다. **착수 직후 머리말**이 그 틈을 8시간이 아니라 1분으로 줄입니다.
(끝나고 한 번 더 보는 것은 그대로 — 중간에 바뀔 일은 없지만 완주 표지와 같이 기록합니다.)

**분모 점검도 Junseok 것을 씁니다**: `Hw-Lw` 짝이 양쪽에 세어지므로 **653+653−1 = 1305** 가 맞습니다
(nbIm100 은 677+677−1 = 1353). **세는 법이 맞는지를 산수로 한 번 더 건 것**이고, 오늘 우리가
분모에서 두 번 틀렸으니(§2-2) 이 습관이 답입니다.

## 5. 끝나면

    · 완주 표지(`Simulation finished`)를 **직접 확인**하고 우편함에 적으십시오. 폴더 존재는 표지가 아닙니다.
    · VTK 는 `density_v3*/…/*.vtk.gz` 글롭 밖입니다 — **손으로 알리거나** 종합자가 모읍니다(`density_grids_final/`).
    · 그림·해석은 종합자가 합니다.
