# v3 앞단 네 러너를 비-ZIF-69 골격에 쓸 수 있나 — 읽고 재 본 결과 (2026-09-10, 데스크탑)

대상: `relax_series_v3.py` · `judge_relax_v3.py` · `charge_v3.py` · `risk_screen_v3_sub.py`
맥락: `TNF_REGISTRATION_20260910.md` (T-NF-1 MUF-16 · T-NF-0 ZIF-71/90 · T-NF-2 ZIF-94)
구조: `21_ZIF69_MTV/external_cif/` (`PROVENANCE.md`)

> **이 문서는 소견입니다. 네 파일은 한 줄도 고치지 않았습니다.**
> 살아 있는 v3 계열이 그 위에서 돌기 때문입니다(CLAUDE.md §6).

## 0. 한 줄 답

**"`structures_v2/ZIF69_<tag>.cif` 로 이름만 바꿔 넣으면 된다" 는 성립하지 않습니다.**
기계적으로는 돌지만 **네 곳에서 조용히 틀리고, 두 곳에서는 v3 계열 전체를 같이 죽입니다.**
`charge_anchor_zif93.py`(08-21)가 이미 답을 보여 줍니다 — 계열에 섞지 않고
**폴더가 분리된 얇은 래퍼**를 새로 씁니다.

## 1. `relax_series_v3.py` — GFN-FF 셀 고정 이완

무엇을 가정하나:

    SRC        structures_v2/ 의 *.cif 전부 (glob)           <- 이름 규약 없음. 파일만 놓으면 잡힙니다
    OUT        relax_v3/<name>_relaxed.cif                   <- 이어받기: 있으면 건너뜁니다
    판정       relax_criteria.evaluate() 넷 + 셀 고정
    원소       relax_criteria.COV 에 있는 원소만 (H C N O Cl Zn S F Br **Co**)

**좋은 소식 (실측)**: `structures_v2/` 104종이 **전부** `relax_v3/` 에 이완본이 있습니다.
새 CIF 하나를 넣어도 **그 하나만** 돌고 104종은 `skipped` 로 넘어갑니다.

### ⚠ 1-1. 판정 ③ `3_ZnN` 이 Zn 없는 골격에서 **배치를 통째로 죽입니다**

`evaluate()` 는 `('N','Zn')` 쌍이 없으면 `ZnN_min = None` 을 돌려주는데,
`relax_series_v3.py:120` 이 그것을 `f"{num['ZnN_min']:.3f}"` 로 찍습니다.

    실측: TypeError: unsupported format string passed to NoneType.__format__

이 예외는 워커 `one()` 안에서 나고 아무도 잡지 않습니다 → `imap_unordered` 가
`main()` 으로 올려 보냄 → **결과 JSON 을 한 줄도 안 쓰고 배치가 죽습니다.**
(같은 유형이 2026-08-12 risk_screen 에서 일어났습니다. 그때는 이완 2시간 30분을 날렸습니다.)

MUF-16(Co)에는 Zn 이 아예 없으므로 **반드시** 걸립니다. 이완 자체는 그 전에 끝나고
`_relaxed.cif` 도 쓰인 뒤라(쓰기 조건은 `err is None and ncalls > 0` 이지 `pass` 가 아닙니다)
**파일은 남고 판정만 사라집니다** — "실패가 결과처럼 보이는 것" 의 정확한 변형입니다.

### ⚠ 1-2. 판정 ② `방향족CC폭` 이 **–CHO ZIF 를 전부 거짓 실패**로 찍습니다

`relax_criteria.bonds()` 는 탄소의 이웃 수 3 을 방향족으로 봅니다. 그런데
**알데하이드 탄소(–CHO)도 이웃이 셋**입니다(고리C, O, H). 그래서 고리 C–C 와
아릴–CHO 결합이 한 통에 들어갑니다. 실측(as-built, 이완 전):

    ZIF-93   ('C','C') n=192  1.372~1.471  폭 **0.0984**   <- 문턱 0.08 초과
             내역: 고리 C–C ≈ 1.37~1.42 · 아릴–CHO ≈ 1.47  (화학적으로 다른 결합)

**이완해도 안 합쳐집니다.** 두 결합의 평형 길이가 서로 다르기 때문입니다.
ZIF-90 · ZIF-93 · ZIF-94 · ZIF-96 · ZIF-97 이 전부 해당합니다.

이것은 **2026-08-16 의 `cf3Im075` 오탐과 같은 계열**입니다(`relax_criteria.py` 머리말).
그때 sp3 탄소는 이웃 4 라서 갈라낼 수 있었지만, –CHO 는 이웃 3 이라 **같은 수법으로는
못 갈라냅니다.** 이웃의 **원소 구성**까지 봐야 합니다(O 를 이웃으로 갖는 탄소는 제외 등).
등록된 문구는 "벤조 C-C 폭" 이므로, 이 분리는 기준을 무르게 하는 것이 아니라
**등록된 기준을 제대로 재는 것**입니다 — 08-16 과 같은 논리입니다.

### 1-3. 그 밖에

    · ZIF-90 배포본은 알데하이드 C–H 가 **0.686 Å** 입니다(24개). 이완이 이것부터 고치므로
      앞단을 반드시 거쳐야 합니다(`external_cif/PROVENANCE.md` §3-1).
    · ZIF-71 as-built C–C 폭 0.1085 · C–N 폭 0.1497 — 4종의 결정학적 링커가 서로 다른
      정밀도로 정련된 탓입니다. 이완 뒤 다시 재야 판단할 수 있습니다.
    · GFN-FF 가 Co(II) 카복실레이트를 어떻게 다루는지 **이 저장소에 전례가 없습니다.**
      MUF-16 이완은 "된다" 가 아니라 "재 봐야 안다" 입니다.
    · `COV` 에 Co 는 있습니다. Mn·Ni 로 가면 **없습니다**(Mn·Ni 를 쓰려면 추가 필요).

## 2. `judge_relax_v3.py` — 다시 재는 도구

같은 `evaluate()` 를 쓰고 **같은 None 서식 폭탄**이 47행에 있습니다.

    print(f"... {num['ZnN_min']:6.3f}~{num['ZnN_max']:.3f}({num['ZnN_pairs']:3d}) ...")

`relax_v3/` 에 Zn 없는 `_relaxed.cif` 가 **하나라도** 있으면 이 도구가 죽고,
`relax_v3_judged.json` 이 **안 써집니다.** 그 파일은 `charge_v3.py` 의 관문이므로
**v3 전체의 전하 단계가 멈춥니다.** 비-ZIF-69 를 `relax_v3/` 에 섞으면 안 되는
가장 강한 이유입니다.

또 `judge_relax_v3.py` 는 `structures_v2/<n>.cif` 를 **이완 전** 구조로 읽습니다.
`relax_v3/` 에만 있고 `structures_v2/` 에 없는 이름이면 `FileNotFoundError` 입니다.

## 3. `charge_v3.py` — PACMAN DDEC6

    관문   relax_v3_judged.json 의 pass 만                  <- 1-1·1-2 로 비-ZIF-69 는 항상 탈락
    태그   name.replace('ZIF69_','')  ->  charged_v3/<tag>_DDEC6.cif
    대조군 relax_fixcell/base_relaxed_gfnff_fixcell.cif (ZIF-69 모체)를 **항상** 넣습니다

문제는 둘입니다.

    (가) 판정 관문 때문에 **어차피 못 지나갑니다**(②③). 관문을 고치지 않으면 무의미.
    (나) 지나가면 더 나쁩니다 — MUF-16 이 `charged_v3/muf16_DDEC6.cif` 로 앉습니다.
         `charged_v3/` 는 ZIF-69 v3 계열의 전하 CIF 자리이고, 여러 러너가 거기를
         glob 합니다. **다른 계열을 같은 서랍에 넣지 마십시오**(CLAUDE.md §3·§8).

PACMAN 자체는 구조에 무관합니다(`charge_anchor_zif93.py` 가 ZIF-93 에 그대로 썼습니다).
`fix_tags()`(RASPA 2.0.41 구 태그) · `net_charge()` 5e-5 관문도 그대로 유효합니다.

## 4. `risk_screen_v3_sub.py` — 안정성 관문(Zeo++ + LAMMPS/UFF4MOF)

    대상   RISK_SUB_TAGS 환경변수로 임의 태그 지정 가능 (첫 항목은 반드시 'base')
    입력   relax_v3/ZIF69_<tag>_relaxed.cif  ->  structures_v3sub_stage/
    base   relax_fixcell/base_relaxed_gfnff_fixcell.cif (ZIF-69 모체) — 강제

### ⚠ 4-1. `LCD_drop` 판정의 분모가 **ZIF-69 모체 LCD** 입니다

`risk_screen.py:361-414`:

    lcd_ref = res['base'] 의 이완 후 LCD          <- ZIF-69 무치환 모체
    drop    = (lcd_ref - LCD_이 구조) / lcd_ref * 100
    통과     drop < 20 %

이 식의 뜻은 **"치환이 ZIF-69 공동을 무너뜨렸나"** 입니다. MUF-16(세공부피 0.11 cm³/g)
이나 ZIF-71(RHO)을 여기에 넣으면 "ZIF-69 대비 LCD 가 몇 % 줄었나" 를 재게 되고,
그 수는 **안정성과 아무 관계가 없습니다.** 거의 확실히 큰 값이 나와 자동 탈락하고,
그 탈락은 판정이 아니라 계산 부작용입니다 — 08-12 에 아릴 12종이 정확히 그렇게
전멸했던 그 자리입니다(주석이 그 사고를 적고 있습니다).

**비-ZIF-69 에 쓰려면 분모를 그 골격 자신의 이완 전 LCD 로 바꿔야 합니다**
(= "이완이 이 구조를 무너뜨렸나"). 그것은 **다른 기준**이므로 등록문에 먼저 적어야
합니다(결과를 보고 고치는 것이 아니라, 계산 전에).

등록문 §1 ㉣ 의 **PLD > 3.3 Å 관문은 그대로 유효**합니다 — 분모가 없는 절대 기준이라
골격이 달라져도 뜻이 변하지 않습니다.

### 4-2. 그 밖에

    · `-ff UFF4MOF` lammps-interface 로 이완합니다. **Co(II) 카복실레이트 + 방향족 아민의
      원자 타이핑이 되는지 전례가 없습니다.** 실패하면 rc≠0 이고 LCD(후)가 None 이 됩니다.
    · `run_one` 이 `ZIF69_<tag>.cif` 이름을 박아 씁니다(risk_screen.py:183) — 스테이징이
      그 이름으로 복사하므로 이름 규약을 따라야 합니다.
    · Zeo++ 9.5 GB/건 상한과 "RASPA 가 돌면 안 띄움"(`pgrep -x simulate`) 은 그대로.
      MUF-16 슈퍼셀은 1,872 원자로 v3(≈6,400)보다 작으니 메모리는 더 여유롭습니다.
    · `python` 이 PATH 에 없으면 **rc 0 으로 조용히 아무것도 안 합니다**(NEW_MACHINE §0-1).
      `lammps_mof` 환경(3.11)으로 돌려야 합니다.

## 5. 그래서 최소 개조는 무엇인가 (권고 — 실행하지 않았습니다)

**계열에 섞지 않는 것**이 첫째입니다. `charge_anchor_zif93.py` 가 이미 그 형태입니다.

    ① relax_criteria.py 에 **판정 프로필**을 하나 더 둡니다(기존 함수는 그대로).
         · ③ 금속–N 을 `Zn` 고정이 아니라 **구조에 있는 금속**으로 일반화하고,
           금속이 N 과 결합하지 않는 골격(MUF-16 은 카복실레이트 O 배위)에서는
           **③ 을 '해당 없음'(None)으로 두고 판정에서 뺍니다.** `False` 로 두면 안 됩니다 —
           "검사에 걸렸다" 와 "검사 대상이 아니다" 는 다릅니다(run_tnf.py 머리말과 같은 규율).
         · ② 방향족 통에서 **O 를 이웃으로 갖는 탄소(–CHO, –COOH)를 제외**합니다.
         · 서식 폭탄: `ZnN_min` 이 None 일 때의 출력을 `-` 로. (한 줄짜리 수정이지만
           **돌고 있는 러너를 건드리지 않는다**는 규칙 때문에 지금은 못 합니다.)
    ② `relax_series_tnf.py`(신설): SRC/OUT 만 `external_cif/` · `relax_tnf/` 로 바꾼 사본.
    ③ `charge_tnf.py`(신설): `charge_anchor_zif93.py` 와 같은 형태, 출력 `charged_tnf/`.
    ④ `risk_screen_tnf.py`(신설): LCD 분모를 **자기 이완 전 LCD** 로. 이 기준 변경은
       **등록문에 먼저 적고** 나서.

## 6. 확인하지 못한 것

    · MUF-16 CIF 가 없어 1·2·4 절의 MUF-16 관련 예측은 **셀 파라미터와 코드 독해**에
      근거합니다. 구조를 받으면 다시 재야 합니다.
    · GFN-FF / UFF4MOF 가 Co(Haip)₂ 를 다루는지 — **한 건도 돌리지 않았습니다.**
    · ②③ 를 고친 판정이 ZIF-69 v3 104종의 과거 판정을 바꾸는지 — 대조하지 않았습니다.
      (바꾼다면 그것 자체가 보고 대상입니다.)
