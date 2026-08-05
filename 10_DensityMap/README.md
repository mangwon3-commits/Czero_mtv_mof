# 밀도맵 — CO₂가 "어디에" 붙는지 공간으로 보는 방법

ParaView로 열어 보는 VTK 파일을 만들고 해석하는 절차입니다.

> [!WARNING]
> **현재 저장된 결과는 무효입니다.** `07_Bracketed_MTV/` 구조로 계산했는데 그 구조들이 주기경계 버그의 영향을 받았습니다(`HANDOVER.md` 4절). **절차와 스크립트는 그대로 유효**하니, 구조를 재생성한 뒤 다시 돌리면 됩니다. 특히 **"−Cl enrichment E = 1.66~1.98"은 인용하지 마세요** — 공동에 떠 있던 Cl이 만든 허상입니다.

---

## 1. 왜 밀도맵을 보는가

Q_st나 흡착량은 **숫자 하나**라서, 그 값이 어디서 왔는지 말해주지 않습니다. 밀도맵을 보면 "여기 CO₂가 몰려 있다"까지는 알 수 있지만, 그것만으로는 세 가지가 구별되지 않습니다.

1. 그 자리가 단지 **넓어서**인가
2. 특정 작용기가 **실제로 끌어당겨서**인가
3. 그 인력이 **분산력**인가 **정전기**인가

이 셋을 분리하는 것이 여기 있는 스크립트들의 목적입니다.

---

## 2. 3단계 절차

### 단계 1 — GCMC로 밀도 격자 뽑기 (`run_density_map.py`)

0.15 bar, 298 K에서 GCMC를 돌리면서 CO₂가 어디 있었는지 3차원 격자에 누적합니다.

```bash
conda activate czeromof
cd ~/mof_project/10_DensityMap
python run_density_map.py
```

**핵심 설정**

| 항목 | 값 |
|---|---|
| 힘장 / 컷오프 | `UFF_MOF` / 12.0 Å |
| 온도 · 압력 | 298 K · 0.15 bar (배가스 CO₂ 분압) |
| 사이클 | 5,000 (초기화 2,000) |
| 격자 | `DensityProfile3DVTKGridPoints 90 90 90` |
| 기록 주기 | `WriteDensityProfile3DVTKGridEvery 500` |

RASPA 입력에 들어가는 결정적인 세 줄:

```
ComputeDensityProfile3DVTKGrid       yes
WriteDensityProfile3DVTKGridEvery    500
DensityProfile3DVTKGridPoints        90 90 90
```

**각 구조를 전하 ON / OFF 두 번 돌립니다.** 이게 3단계 차분맵의 전제입니다.

```python
jobs.append((t, True,  'q_on',  True))   # 전하 O
jobs.append((t, False, 'q_off', True))   # 전하 X
```

결과는 `<구조>__q_on/VTK/System_0/` 아래에 생깁니다.

| 파일 | 내용 |
|---|---|
| `COMDensityProfile_CO2.vtk` | **CO₂ 무게중심** 분포 — 분석에 이걸 씁니다 |
| `DensityProfile_CO2.vtk` | CO₂ 모든 원자 분포 |
| `FrameworkAtoms.vtk`, `FrameworkBonds.vtk` | 골격 (ParaView 배경용) |

> 위치를 보려면 **무게중심(COM)** 쪽이 맞습니다. 원자 분포는 배향까지 섞여 있어 자리를 흐립니다.

### 단계 2 — 수치 해석 (`analyze_density.py`)

```bash
python analyze_density.py
```

`density_analysis.json`과 콘솔 표를 만듭니다. 세 가지를 계산합니다.

**① 접촉 선호도 (enrichment)** — "넓어서"와 "끌려서"의 분리

각 복셀에서 가장 가까운 골격 원자가 어느 작용기인지로 공간을 분할하고(최근접 = 보로노이),

$$E_F = \frac{N_F/N_{\text{tot}}}{V_F/V_{\text{tot}}}$$

부피로 나누기 때문에 **원자 수가 많은 작용기가 유리해지는 편향이 제거**됩니다. E > 1이면 자리가 넓어서가 아니라 실제로 끌어당긴 것입니다.

**② 정전기 차분맵** — 분산력과 정전기의 분리

$$\Delta\rho(\mathbf{r}) = \rho_{\text{on}}(\mathbf{r}) - \rho_{\text{off}}(\mathbf{r})$$

각각 총합 1로 정규화한 뒤 뺍니다. **LJ 항은 전하와 무관하므로 차분에서 완전히 소거**되고, 남는 것은 정전기가 CO₂를 어디로 옮겼는지뿐입니다. 실험으로는 분리할 수 없고 계산에서만 가능한 양입니다.

**③ 밀도 피크의 화학적 정체** — 극대점 주변 5 Å 안의 골격 원자를 작용기별 최단거리로 조회합니다.

**부수 지표: 평균 벽거리.** 밀도가중 최근접 골격원자 거리입니다. 이 값이 조성과 무관하게 3.3~3.5 Å로 고정이라는 관측이 **"Q_st 천장은 기하학적 한계"** 라는 결론의 근거였습니다(`HANDOVER.md` 3절 6번).

### 단계 3 — ParaView용 VTK 내보내기 (`export_diff_vtk.py`)

```bash
python export_diff_vtk.py
```

`diff_vtk/` 에 구조당 2개씩 만듭니다.

| 파일 | 의미 |
|---|---|
| `*__ELECTROSTATIC_GAIN.vtk` | **Δρ (%p)** — 양수 = 정전기가 끌어온 자리, 음수 = 밀려난 자리 |
| `*__RHO_total.vtk` | 절대 밀도 (%) — 어디에 많은지만 보여주고 원인은 못 가림 |

**ParaView에서 보는 법**

1. 두 파일을 함께 엽니다
2. `ELECTROSTATIC_GAIN`에 **Contour** 필터를 걸고 등고값을 양수/음수 양쪽으로 잡습니다
3. `FrameworkBonds.vtk`를 겹쳐 골격 위치를 확인합니다

두 개를 겹쳐 봐야 "여기 몰린 게 넓어서인지 끌려서인지"가 구별됩니다.

---

## 3. 구현상 주의점

### 격자는 슈퍼셀 위에 정의된다

VTK 헤더의 `CELL_PARAMETERS`가 33.982 Å인데 ZIF-8 단위셀은 16.991 Å입니다 — **2×2×2 슈퍼셀**입니다. 골격 원자와 비교하려면 격자 좌표를 단위셀로 접어야 합니다.

```python
folded = np.mod(cart.reshape(-1, 3), L_unit)
```

`analyze_density.py`가 이걸 처리하고, 최근접 원자 탐색에는 주기 이미지로 ±1셀 패딩한 KD-트리를 씁니다. 안 하면 셀 경계 근처 복셀이 엉뚱한 원자에 배정됩니다.

### 접근가능 복셀만 센다

골격 원자 내부의 복셀까지 부피에 넣으면 enrichment가 원자 부피에 지배됩니다. `ACCESSIBLE_MIN = 3.0` Å(대략 C–O LJ σ) 이내는 제외합니다.

### Δρ의 총합은 0이다

정규화 후 빼므로 **어딘가는 반드시 음수**입니다. 절댓값이 아니라 **부호 패턴**을 봐야 합니다 — 메틸은 항상 주는 쪽, 극성기는 항상 받는 쪽이었습니다.

### VTK 파서

RASPA의 VTK는 `STRUCTURED_POINTS`이고 x가 가장 빠르게 변합니다.

```python
v = vals[:n].reshape(dims[::-1]).transpose(2, 1, 0)
```

---

## 4. 계산 비용

구조 14종 × 전하 2조합 = **28작업**. 5,000 사이클 기준 워커 6~7개로 **약 1시간**입니다.

밀도맵 출력이 켜져 있으면 작업당 VTK가 수십 MB 나옵니다. `10_DensityMap/` 전체가 387 MB였습니다. **`diff_vtk/`만 산출물이고 나머지 실행 디렉터리는 재생성 가능**하므로 아카이브에서 제외해도 됩니다(`.gitignore`에 반영됨).

---

## 5. 재계산할 때

1. `07_Bracketed_MTV`의 구조를 **버그 수정된 빌더로 재생성**
2. `python ~/mof_project/audit_orphans.py` → **고아 0 / 충돌 0 / 분리 0** 확인
3. `run_density_map.py` → `analyze_density.py` → `export_diff_vtk.py`
4. 평균 벽거리가 여전히 3.3~3.5 Å인지 확인 — 이게 유지되면 "Q_st 천장은 기하학적"이라는 결론이 재확인됩니다
5. −Cl enrichment가 정상값(1 근처)으로 내려오는지 확인 — 버그 수정이 제대로 반영됐다는 표지입니다

> `TARGETS` 목록은 `07_Bracketed_MTV` 기준입니다. `18_PoreNarrowing` 구조(−SO₃H 계열)로 돌리려면 `SRC`와 `TARGETS`를 바꾸면 됩니다. **−SO₃H가 최고 작용기로 확인됐으므로, 재계산 시에는 그쪽을 대상에 넣는 편이 낫습니다.**
