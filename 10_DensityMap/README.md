# 밀도맵 — CO₂가 "어디에" 붙는지 공간으로 보는 방법

ParaView로 열어 보는 VTK 파일을 만들고 해석하는 절차입니다.

> [!WARNING]
> **현재 저장된 결과는 무효입니다.** `07_Bracketed_MTV/` 구조로 계산했는데 그 구조들이 주기경계 버그의 영향을 받았습니다(`HANDOVER.md` 4절). **절차와 스크립트는 그대로 유효**하니, 구조를 재생성한 뒤 다시 돌리면 됩니다. 특히 **"−Cl enrichment E = 1.66~1.98"은 인용하지 마세요** — 공동에 떠 있던 Cl이 만든 허상입니다.

> [!NOTE]
> **2026-08-05 진행 상황** — `07_Bracketed_MTV` 구조 14종은 수정판 빌더로 **재생성을 마쳤고 감사도 통과**했습니다(5절 1·2번 완료). 남은 것은 3번부터, 즉 이 문서의 계산을 다시 돌리는 것입니다.

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

### ⚠️ 위 항목은 절반만 맞았다 — **분석 코드에도 같은 가정이 있었다** (2026-09-05)

2026-08-22 항목은 육방 셀 문제를 **ParaView 표시 문제**로만 적었다. 그러나 같은 가정이
`analyze_density.py` 의 **분석 경로**에도 들어가 있었다 — 좌표 환원(`cart = idx/dims*L_sup`,
`np.mod(cart, L_unit)`), **원자 위치**(`pos % L_unit`), **주기 패딩**(`shifts * L_unit`)이
전부 셀 **길이만** 썼다(주석: "정방정계").

실측 차이 (dims 12³, 2×2×2 슈퍼셀):

| 셀 | 격자 좌표 최대차 | 원자 패딩 최대차 |
|---|---|---|
| 입방 ZIF-8 (16.991 Å) | **0.00000 Å** | **0.00000 Å** |
| 정방 (10, 10, 15) | **0.00000 Å** | **0.00000 Å** |
| **육방 ZIF-69** (γ=120°) | **10.87 Å** | **24.29 Å** |

**T-4 판정 문턱이 3 Å** 이므로 육방 구조에서는 판정이 성립하지 않는다.

**처분**: `analyze_density.py` 를 **셀 행렬 기반으로 고쳤다**(분율좌표에서 접고
`frac @ cell` 로 데카르트 변환, 원자·패딩도 분율에서 처리). **입방·정방에서는 두 방식이
수치적으로 완전히 일치**하므로 과거 ZIF-8 계열 결과는 바뀌지 않는다(위 표 1·2행이 증명).

**감사**: 이 함수를 지난 구조는 `density_analysis.json` 의 14종이고 **전부 입방**
(a=b=c=16.991 또는 17.071, 각 90°)이다. **육방 구조가 이 분석을 지난 적은 없으므로
오염된 과거 결론은 없다.** ZIF-69 의 `density_results.json`·`density_v2/` 는
`run_density_map.py` 산출(로딩·정전기 분율)이고 거리 기반 항목이 없어 무관하다.

### ParaView 에 그냥 넣으면 격자가 골격과 어긋난다 (2026-08-22)

RASPA 는 밀도맵을 `DATASET STRUCTURED_POINTS` 로 씁니다. **그 형식은 직교 격자만 표현합니다.** ZIF-69 는 γ = 120° 인 육방 셀이라, ParaView 는 이 파일을 0..a × 0..b 인 **직사각 상자**로 놓습니다. 같은 폴더의 `FrameworkBonds.vtk` 는 진짜 데카르트 좌표(평행사변형)입니다.

실측 (`density_v2/saIm100`):

| | x | y |
|---|---|---|
| 밀도 격자 상자 | 0 .. 51.59 | 0 .. 51.59 |
| 골격 좌표 | -35.37 .. 61.46 | -6.79 .. 51.97 |

헤더의 `CELL_PARAMETERS` 줄에 각도가 있지만 **VTK 는 그것을 읽지 않습니다.**

> 겹쳐 보면 등고면이 기공에 앉은 것처럼 **보입니다.** 주기 구조라 눈이 채웁니다.
> 판별법은 대칭입니다 — **대칭적으로 같은 기공에 같은 덩어리가 나오는가.**
> 어긋나 있으면 한쪽 기공에만 걸리고 반대편은 빕니다.

`vtk_to_cartesian.py` 가 셀 행렬을 적용해 `STRUCTURED_GRID` 로 다시 씁니다. 값은 건드리지 않습니다.

```bash
python vtk_to_cartesian.py ../21_ZIF69_MTV/density_v2/diff_vtk   # 폴더 전체
```

분율 좌표는 `i / N` 입니다(`i / (N-1)` 이 아닙니다). `SPACING = a/N` 이므로 격자는 [0,1) 을 N 등분한 것입니다.

`*_cart.vtk` 는 이진이라 원본의 5배 크기입니다. **재생성되므로 커밋하지 않습니다**(`.gitignore`).

### ParaView 를 코드로 몰 때 — 첫 Render() 가 카메라를 되돌린다

`v.CameraParallelScale = 25.0` 을 주고 `Render()` 하면 자동 맞춤 값(61.9)으로 덮입니다. **Render() 뒤에 한 번 더 주고 다시 Render()** 해야 합니다. 두 장을 같은 배율로 뽑아야 하는 대비 그림에서 이걸 놓치면 한 장만 확대돼 나옵니다.

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

> `TARGETS` 목록은 `07_Bracketed_MTV` 기준입니다. **−SO₃H가 최고 작용기로 확인됐는데 밀도맵은 아직 −Cl·−NO₂ 시절 목록이라, 왜 술폰산이 강한지를 공간적으로 본 적이 한 번도 없습니다.** `18_PoreNarrowing` 의 −SO₃H 계열로 대상을 바꾸는 편이 낫습니다.

### 리타깃 — 상수 두 개가 아니라 2개 파일 4곳입니다

`SRC` 와 `TARGETS` 만 고치면 **조용히 EQeq 기반 밀도맵이 나오고 아무도 눈치채지 못합니다.**

| 파일 | 줄 | 무엇을 |
|---|---|---|
| `run_density_map.py` | 26 | `SRC` → `../18_PoreNarrowing/charged` |
| `run_density_map.py` | 33 | `TARGETS` → `_DDEC6` 접미사 포함 |
| `run_density_map.py` | 168 | 기준선 `mIm100__{ph}` → `mIm100__{ph}_DDEC6` |
| `analyze_density.py` | 48 | `SRC` (같은 값) |
| `analyze_density.py` | 250 | `f'{tag}__{phase}.cif'` 에 `_DDEC6` 반영 |

**왜 `structures/` 가 아니라 `charged/` 인가.** `run_density_map.py:103` 이 `SRC/<name>.cif` 를 읽어 `UseChargesFromCIFFile yes` 로 넘깁니다. `18_PoreNarrowing/structures/` 의 CIF 에는 빌더가 써 넣은 **EQeq** 전하가 있고, `narrow_results.json` 의 Q_st·선택도는 **PACMAN DDEC6**(`charged/*_DDEC6.cif`)로 계산됐습니다. `structures/` 를 쓰면 **밀도맵이 설명하려는 수치와 다른 전하 모형**을 그리게 됩니다.

하필 EQeq 는 공명에 의한 전하 분리를 못 다뤄 폐기한 방법이고(니트로 N 이 +0.025, 정상 +0.6), **−SO₃H 는 S=O 공명을 갖습니다.** "왜 술폰산이 강한가"를 보려는 계산에서 가장 쓰면 안 되는 전하입니다.

---

## 5-1. ZIF-69(gme) 계열 밀도맵

`21_ZIF69_MTV/run_density_map.py` 가 같은 절차를 gme 계열에 적용합니다.

```bash
conda activate czeromof
export RASPA_DIR=${HOME}/RASPA/simulations
cd ~/mof_project/21_ZIF69_MTV
python run_density_map.py                              # 전하 ON/OFF 쌍 GCMC + 격자
python ../10_DensityMap/export_diff_vtk.py density     # 차분맵 -> density/diff_vtk/
```

`export_diff_vtk.py` 는 인자로 실행 디렉터리 경로를 받습니다(생략하면 종전대로
`10_DensityMap/` 자신을 봅니다). **스크립트를 복제하지 마세요** — 한쪽만 고쳐지는
사고가 납니다.

### ZIF-8 계열과 다른 점

| | 07_Bracketed_MTV (ZIF-8) | 21_ZIF69_MTV (gme) |
|---|---|---|
| 축 | 조성 × **닫힌상/열린상** × 전하 ON/OFF | 조성 × 전하 ON/OFF |
| 이유 | ZIF-8 은 게이트 오프닝이 있어 1.47 GPa 열린상을 따로 씀 | gme 는 강체 골격이라 상이 하나 |

**전하 ON/OFF 축은 여기서 더 중요합니다.** ZIF-69 는 치환율을 올리면 공동 축소
(분산력↑)와 술폰산 도입(정전기↑)이 **동시에** 일어나서, 로딩만 봐서는 Q_st 31.07
이 어느 쪽에서 왔는지 못 가립니다. 차분맵이 그걸 가르는 유일한 수단입니다.

## 6. 주의 — 다른 실행 스크립트는 VTK 를 지웁니다

`07 / 13 / 14 / 17 / 18 / 19 / 21` 의 RASPA 실행 스크립트는 전부 끝에서 다음을 합니다.

```python
for sub in ('VTK', 'Movies', 'Restart'):
    shutil.rmtree(os.path.join(d, sub), ignore_errors=True)
```

게다가 `ComputeDensityProfile3DVTKGrid` 플래그는 **`run_density_map.py` 에만** 있습니다. 즉 다른 스크립트로 돌린 계산에서는 애초에 밀도 분포가 생기지 않고, 남는 VTK 는 골격 형상(`Frame.vtk`, `FrameworkAtoms.vtk`)뿐입니다.

**밀도맵이 필요하면 반드시 `run_density_map.py` 를 쓰세요.** 다른 계산에 플래그만 얹는 것으로는 안 되고, 전하 ON/OFF 쌍을 돌려야 차분맵이 나옵니다(2절 단계 1).
