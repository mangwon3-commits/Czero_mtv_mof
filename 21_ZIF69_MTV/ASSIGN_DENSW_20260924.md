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

    grep -E "Ow -      Ow|Hw \[ZERO|Lw \[ZERO" <실행폴더>/Output/System_0/*.data | head
    → `Ow - Ow … p_0/k_B: 89.63300` · `Hw [ZERO_POTENTIAL]` · `Lw [ZERO_POTENTIAL]`

데스크탑 `cf3Im025` 는 15:0x 에 이 방법으로 확인했습니다(`water.def` md5 **6fc8850d…** 정본 5자리 ·
`Ow-Ow 89.63300` · `Hw/Lw ZERO_POTENTIAL`).

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

## 5. 끝나면

    · 완주 표지(`Simulation finished`)를 **직접 확인**하고 우편함에 적으십시오. 폴더 존재는 표지가 아닙니다.
    · VTK 는 `density_v3*/…/*.vtk.gz` 글롭 밖입니다 — **손으로 알리거나** 종합자가 모읍니다(`density_grids_final/`).
    · 그림·해석은 종합자가 합니다.
