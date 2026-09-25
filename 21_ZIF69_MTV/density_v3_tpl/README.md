# `density_v3_tpl/` — 형판 Zn(bib)(bdtdc) 모체 · 4,8-치환체 CO₂ 밀도 격자 (E-28, 2026-09-26)

`run_density_tpl.py` 산출(`run_density_map` 무수정 import). 5구조(e22_parent · e24_ch3_100 · e24_cn_100 · e24_f_100 · e22_no2_100)
× 전하 ON/OFF = 10작업. 밀도맵 규약 초기화 2,000 + 생산 5,000 · CO₂ 단성분 0.15 bar · 298 K · 90³ 격자 · DDEC6(`charged_v3/`).
판정: `../MAGI5_E22_VERDICT_20260925.md` §13 · 등록 `../ASSIGN_MAGI5B_20260925.md` §HKHOME 15차.

## 무엇이 커밋돼 있나
    density_results.json                                           스칼라(로딩 ON/OFF · 정전기 몫)
    <이름>__q_{on,off}/VTK/System_0/COMDensityProfile_CO2.vtk.gz    질량중심 CO₂ 격자 10개(`density_v3/` 관례)
    <이름>__q_{on,off}/simulation.input                            RASPA 가 실제로 읽은 설정 10개
    diff_vtk/<이름>__ELECTROSTATIC_GAIN.vtk · __RHO_total.vtk       `10_DensityMap/export_diff_vtk.py density_v3_tpl` 산출(ParaView 용)

## 주의
- 격자는 **1×2×3 슈퍼셀**(24.404 / 28.362 / 27.912 Å, **β 99.608°**) 위, 분율 좌표 등간격. VTK STRUCTURED_POINTS 는
  직교로 그리므로 ParaView 에서 ac 면이 9.6° 틀어져 보입니다 — 정확한 그림은 셀 행렬로 변환하십시오.
  ab 면(γ 90°)은 직교라 c 투영 그림은 왜곡이 없습니다(`../plot_density_tpl.py`).
- 통로 축은 **c**(모체 ON c 투영 빈칸 90.5 %).
- 단일 복셀로 자리를 지목하지 마십시오(`../DENSITY_GRID_TWO_GENERATIONS_20260906.md`).
- 습윤(RH90) 격자는 `../water_runs_density_v3w/rh90_{e22_parent,e24_ch3_100,e24_cn_100}/`.
