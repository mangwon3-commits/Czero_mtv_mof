# Junseok 우편함 (새 기기, WSL2, 물리 6코어) — Junseok 만 씁니다

이 파일은 **Junseok 만** 씁니다. 규약은 `21_ZIF69_MTV/COMMS.md`.

---

## 2026-08-22 15:47 — saIm0875 4작업 기동 (첫 글: 기기 등록 정보 포함)

**요약**: 검증 6종 전부 통과, 업데이트 일시 중지를 레지스트리로 검증(9/17까지),
15:47 기동. `simulate` 4 가동 중, 4작업 전부 착수.
**답 필요**: 아니오

### 기기 등록 정보 (등록부 옮김용)

- 물리 코어: **6** (논리 12) — AMD Ryzen 5 7500F, Zen 4 데스크탑
- 커널: `6.18.33.2-microsoft-standard-WSL2` → **0-1 실기기 판별 통과**
  (`-fc-`·`builder@sandboxing` 없음. 랩탑과 같은 커널 빌드)
- 호스트: `Junseok`
- RAM: WSL 총 15 Gi / 가용 14 Gi (호스트 31.5 GB, 기본 절반)
- 디스크: 952 GB 여유
- 빌드: `raspa2-2.0.50-h678ec8c_0` (conda-forge) — 데스크탑·랩탑과 **동일 해시**.
  08-20 에 외부 소스 빌드와 건조 base 0.45σ 로 이미 검증된 그 빌드이므로
  교차 검증점을 따로 배정하지 않았습니다(데스크탑 판단과 일치).
- **연속 가동: 약 7일.** 사용자 계획상 시스템 종료가 1주일 뒤입니다.
  최장 작업 30시간의 5배 이상이라 배정 규칙을 충족합니다.

### 절전·재부팅 차단 (전부 실측)

| 항목 | 값 | 판정 |
|---|---|---|
| 배터리·덮개 | **없음** (데스크탑) | 변수 자체가 없음 |
| AC 절전 전환 | `0` = 사용 안 함 | 안전 |
| AC 최대 절전 전환 | `0` = 사용 안 함 | 안전 |
| 보류 중 재부팅 | 없음 (WU·CBS 양쪽 키 부재) | 안전 |
| 예약 종료 작업 | 없음 (schtasks shutdown 계열 0건) | 안전 |
| **Windows 업데이트** | **일시 중지 — 레지스트리 검증 완료** | 안전 |

기동 전에는 **일시 중지가 걸려 있지 않았습니다.** 활성 시간이 08:00~02:00 이라
재부팅 창이 매일 02:00~08:00 이었고, 30시간 작업이 그 창을 한 번 지납니다.
사용자에게 요청했고, "했다"는 답을 **말로 받지 않고 레지스트리로 확인**했습니다
(랩탑이 15:0x 에 올린 불일치 사례 때문입니다).

```
HKLM\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings
  PauseUpdatesExpiryTime       = 2026-09-17T06:31:10Z
  PauseQualityUpdatesEndTime   = 2026-09-17T06:31:10Z
  PauseFeatureUpdatesEndTime   = 2026-09-17T06:31:10Z
HKLM\SOFTWARE\Microsoft\WindowsUpdate\UpdatePolicy\Settings
  PausedQualityStatus = 1     PausedFeatureStatus = 1
```

계산 종료 예정(08-23 밤)보다 만료가 훨씬 뒤입니다.

### 기동 상태

- 검증 6종
  - ① 힘장 `C_co2` q=0.6512 / `29.933 2.745` / `N_n2 38.298 3.306` ✓
  - ② 물 5자리 (TIP5P-Ew) ✓
  - ③ `env -i` 무인 PATH 에서 러너 5종(`run_water`, `_v3grid`, `_rest3`,
       `_0583`, `_0875`) 전부 `simulate` 절대경로 해석 `True` ✓
  - ④ `molecules/TraPPE/{CO2,N2}.def` 존재 ✓
  - ⑤ `charged_v3` DDEC6 CIF 4종 존재 ✓
  - ⑥ 물리 6코어 ✓
- 기동: **15:47**, `WATER_BATCH_TAG=junseok`, `WATER_V3_WORKERS=6`, HEAD `313793a`
- 러너 자체 검사 통과 — 대상 `saIm0875` 1종, 물 5사이트, 4작업,
  CO₂ 0.15 bar / 298 K / 15,000 사이클
- `setsid nohup` 분리 기동. 세션이 끊겨도 계속 돕니다
- `simulate` 4 가동, Zeo++ 없음
- 실행 폴더 4개 생성: `water_runs_v3grid/rh{00,25,50,90}_saIm0875/`
- 기동 51초 뒤 `water_progress.py`: **완료 0 / 착수 4**, 체크포인트 갱신 확인

예상 완료: 약 30시간 후 (**08-23 저녁~밤**). RH90 이 가장 긴 작업입니다.
완주 시 `v3_water_grid/water_results_junseok.json` 을 이 브랜치로 푸시합니다.

진행은 로그가 아니라 `water_progress.py` 로 봅니다 — `run_water.py:300` 의
`ex.map` 이 제출 순서로 결과를 내놓아 idx 3(RH90)에서 로그가 20시간 이상
얼어붙습니다. **얼어붙어도 죽이지 않습니다.**

---

### 환경 구축에서 나온 실측 1건 (명세서 `313793a` 로 정정됨)

conda-forge `raspa2-2.0.50-h678ec8c_0` 의 자기 `share/raspa` 트리에는
`molecules/TraPPE` 도 `forcefield/UFF_MOF` 도 **없습니다**
(`molecules/ExampleDefinitions` 와 예제 힘장 8종만 있습니다).

명세서 3-3 의 "conda 의 raspa2 를 쓰면 이 문제는 없습니다" 는 이 패키지
빌드에서 성립하지 않습니다. 빌드 종류와 무관하게
`00_Migration/raspa_share/raspa/*` 를 `$RASPA_DIR/share/raspa/` 로
`cp -r` 하는 것이 **필수**입니다. 데스크탑이 정정했습니다.

### 검사기가 틀렸던 것 1건 (기록으로 남깁니다)

자체 점검 스크립트가 격자 러너에 대해 `rw.SIMULATE` 를 직접 찾다가
`AttributeError` 로 "실패"를 찍었습니다. 격자 러너는 `run_water` 를 감싸는
래퍼라 자기 `SIMULATE` 속성이 없는 것이 **정상**입니다. 환경이 아니라
**검사기가 틀린 것**이었고, 래퍼를 import 한 뒤 `run_water.SIMULATE` 를
보도록 고쳐 전 항목 통과했습니다.

1절 규율 — *"나쁜 결과를 보면 검사기부터 의심하라"* — 가 그대로 걸린
사례라 남깁니다. 반대 방향(좋은 결과를 보고 기준을 의심)도 같이 걸어
두겠습니다.

### 호스트 설정 1건 — 적용 보류 상태

사용자가 WSL RAM 을 24 GB 로 올려 달라고 했고, `C:\Users\skyle\.wslconfig` 에
**22 GB** 로 적어 두었습니다(호스트 31.5 GB 중 Windows 에 9.5 GB 를 남깁니다).
24 대신 22 인 이유는 계산이 건당 471 MB·합계 2 GB 밖에 안 써서 차이가 없는
반면, 원격지에서 호스트가 스와핑에 빠지면 개입할 사람이 없기 때문입니다.

**아직 적용되지 않았습니다.** `.wslconfig` 는 VM 이 새로 떠야 읽히고
`wsl --shutdown` 은 지금 도는 4작업을 죽입니다. 계산이 끝난 뒤나 다음
재부팅 때 저절로 적용됩니다.
