# `density_v3/` — v3 전하 ON/OFF 밀도 격자 (2026-09-05)

`run_density_v3.py` 산출. 6조성(base · saIm025 · saIm050 · saIm075 · saIm100 ·
**nbIm025**) × 전하 ON/OFF = 12작업. 밀도맵 규약 초기화 2,000 + 생산 5,000,
0.15 bar, 298 K, 90³ 격자, DDEC6 전하.

판정문: `../MECHANISM_VERDICT_20260905.md` (정전기 기여율 f = 0.71~0.85, **정전기 지배**).

## 무엇이 커밋돼 있나

    density_results.json                                   스칼라 결과 (로딩·정전기 몫)
    <조성>__q_{on,off}/VTK/System_0/COMDensityProfile_CO2.vtk.gz   **질량중심 CO₂ 격자 12개**

**질량중심(COM) 판만 커밋합니다.** 분석 규약이 COM 이고
(`10_DensityMap/README.md` 66행, `export_diff_vtk.py:84` 가 COM 을 하드코딩),
T-4·T-6 도 COM 으로 판정합니다. 전원자 판(`DensityProfile_CO2.vtk`)은
데스크탑 로컬에만 있습니다 — 필요하면 요청하십시오.

**gzip 으로 넣었습니다**: 원본 2.0 MB → 0.062 MB (**32배**). 12개 합쳐 856 KB.

## 쓰는 법

```bash
gunzip -k <조성>__q_on/VTK/System_0/COMDensityProfile_CO2.vtk.gz
```

`10_DensityMap/export_diff_vtk.py <폴더>` 로 ON−OFF 차분맵을 재생성할 수 있습니다
— **원산출물이 여기 있으므로 차분맵은 사본 없는 자료가 아닙니다.**

## 주의

- 격자는 **2×2×2 슈퍼셀** 위에 정의돼 있습니다(52.168 / 52.168 / 38.816 Å).
  단위셀로 접을 때는 **셀 행렬**을 쓰십시오 — ZIF-69 는 γ=120° 육방이라
  길이만으로 접으면 최대 24 Å 틀립니다(09-05 `092788e` 에서 고친 결함).
- 전하 OFF 는 **LJ 만 남긴 가상의 계**입니다. 분해용 대조이지 물질이 아닙니다.
- 값은 최대 1 로 정규화된 분수입니다. 최소단위의 역수가 최대 복셀 원계수입니다.
