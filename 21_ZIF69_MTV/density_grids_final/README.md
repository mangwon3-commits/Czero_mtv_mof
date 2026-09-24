# ⚠ 이 폴더의 여섯 격자는 **물 힘장 수정 *이전*** 판입니다 (표지 추가 2026-09-24 15:59)

    COMDensityProfile_{CO2,water}__{base,nbIm025,saIm050}.vtk.gz   — 커밋 `c97f8f36` (09-05 13:18)

**폴더 이름이 `final` 이지만 현재 계열이 아닙니다.** `T4_PRIME_VERDICT_20260907.md §40` 이 이미
*"옛(**결함 힘장**) 물 격자(`density_grids_final/`, 수정 이전)"* 로 못 박아 뒀는데, **폴더 안에는
아무 표지가 없어** 파일만 보면 현재 판으로 읽힙니다. 이 README 가 그 표지입니다.

무엇이 달랐나 (CLAUDE.md §1): 2026-09-06 에 `force_field_mixing_rules.def` 에 `Hw none`/`Lw none`
두 줄이 들어갔습니다(항 55→57). **그 전에는 물 수소에 UFF `H_` 의 LJ 가 붙어 수소결합이 없는 물**
이었고 물 친화도가 약 **8.6배 과소**였습니다. **RH>0 결과는 `v3w_*` 계열로만 인용합니다.**

## 쓸 것 — 현재 계열(v3w, 수정 후)

    건조 CO₂    `density_v3*/<조성>__q_{on,off}/VTK/System_0/COMDensityProfile_CO2.vtk.gz`
    습윤 RH90   `water_runs_density_v3w/rh90_<조성>/VTK/System_0/COMDensityProfile_{CO2,water}.vtk.gz`

습윤 8조성(**완주 표지 확인됨**): base · mslm050 · nbIm025 · nbIm075 · sa50nb50 · saIm050 · saIm0583 · saIm100
⚠ `saIm100` 은 **구조 관문 탈락**(LCD 감소 22.5 %) — 격자는 있으나 **"우리 물질" 로 인용 금지**
(`GATE_SAIM100_20260924.md`). 사다리 상한을 보이는 용도로만 씁니다.
⚠ 도는 중인 조성(`cf3Im025`·`saIm025`·`mslm025`)은 **아직 안 올렸습니다** — VTK 는 500사이클마다
쓰여 **끊긴 실행에도 남습니다**(CLAUDE.md §0). 완주 표지를 본 뒤 올립니다.
