#!/bin/bash
# 지인에게 넘길 계산 꾸러미를 D 드라이브에 만든다.
#
# **승인 전에는 돌리지 마세요.** 사용자가 말로 승인하면 그때 실행합니다.
#
# [설계 원칙: 상대가 우리 값을 재현할 수 있어야 한다]
#   힘장 파라미터를 손으로 골라 담지 않습니다. **폴더째** 넘깁니다.
#   이유가 있습니다 -- 우리가 쓰는 CO2 정의는 경로가 `molecules/TraPPE/CO2.def`
#   인데 **내용은 TraPPE 가 아닙니다.** 기하만 거기서 오고 LJ 와 전하는
#   `forcefield/UFF_MOF/` 의 두 파일에서 옵니다:
#
#       force_field_mixing_rules.def   C_co2  eps 29.933  sigma 2.745
#       pseudo_atoms.def               C_co2  q   +0.6512
#
#   이것은 Garcia-Sanchez 2009 값입니다(TraPPE 라면 27.0 / 2.80). 2026-08-15
#   감사에서 "입력 파일은 TraPPE 라고 적혀 있는데 숫자는 Garcia-Sanchez" 로
#   걸린 바로 그 지점입니다. 상대가 폴더 이름만 보고 배포본 표준 파일을 쓰면
#   **다른 숫자가 나오고, 우리 값과 합칠 수 없습니다.**
#
#   그래서 실행 스크립트도 우리가 쓰는 것을 그대로 넘깁니다. 견본
#   simulation.input 을 손으로 만들면 그 순간 규약이 갈라집니다.
#
# 사용:
#   bash prepare_handoff.sh --dry-run   무엇이 담길지만 본다 (기본)
#   bash prepare_handoff.sh --go        실제로 만든다

set -u
P=/home/mangwon1/mof_project
Z=$P/21_ZIF69_MTV
R=/home/mangwon1/RASPA/simulations/share/raspa
DEST=/mnt/d/MTV-ZIF_계산지원
PDFGEN=$P/tools/make_peer_request.py
PY=/home/mangwon1/miniconda3/envs/czeromof/bin/python
GO=0
for a in "$@"; do [ "$a" = "--go" ] && GO=1; done

say() { echo "  $*"; }
echo "=== 전달 꾸러미 준비 ==="

# ---- 관문: 전하가 붙은 v3 구조가 있어야 합니다 ----------------------------
NCIF=$(ls "$Z"/charged_v3/*_DDEC6.cif 2>/dev/null | wc -l)
if [ "$NCIF" -lt 25 ]; then
  echo "!! charged_v3 에 전하 CIF 가 ${NCIF}개뿐입니다."
  echo "   전하 없는 구조를 넘기면 상대가 GCMC 를 돌릴 수 없습니다."
  echo "   overnight.sh 의 E 단계(charge_v3.py)가 끝난 뒤에 다시 부르세요."
  exit 1
fi
say "전하 CIF ${NCIF}개 확인"

[ -f "$PDFGEN" ] || { echo "!! 요청 명세 생성기가 없습니다: $PDFGEN"; exit 1; }

# ---- 담을 목록 ------------------------------------------------------------
echo
echo "  담을 것:"
say "  cif/                     charged_v3 의 전하 CIF ${NCIF}개"
say "  raspa_share/forcefield/  UFF_MOF 폴더째 (혼합규칙 + pseudo_atoms)"
say "  raspa_share/molecules/   CO2.def, N2.def (TraPPE 폴더에서 -- 기하만 사용)"
say "  19_WaterCompetition/     water.def (TIP5P-Ew 5자리)"
say "  21_ZIF69_MTV/            실행 스크립트 (우리가 쓰는 것 그대로)"
say "  README.md, 요청명세.pdf, CHECKSUMS.txt"

if [ "$GO" -eq 0 ]; then
  echo
  echo "  --dry-run 입니다. 실제로 만들려면 --go 를 붙이세요."
  exit 0
fi

# ---- 만들기 ---------------------------------------------------------------
echo
rm -rf "$DEST"
mkdir -p "$DEST"/{cif,raspa_share/forcefield,raspa_share/molecules,19_WaterCompetition,21_ZIF69_MTV,scripts}

cp "$Z"/charged_v3/*_DDEC6.cif "$DEST/cif/"
cp -r "$R/forcefield/UFF_MOF" "$DEST/raspa_share/forcefield/"
cp "$R/molecules/TraPPE/CO2.def" "$R/molecules/TraPPE/N2.def" "$DEST/raspa_share/molecules/"
cp "/home/mangwon1/mof_project/19_WaterCompetition/water.def" "$DEST/19_WaterCompetition/"
# 규약과 함정을 담은 문서. 다른 기기의 세션이 이것을 먼저 읽어야 합니다.
cp "$P/CLAUDE.md" "$DEST/"
cp "$P/LAPTOP_QUICKSTART.md" "$DEST/"
# [2026-08-18] 손으로 고른 목록을 쓰지 않습니다. **의존성 폐포**를 계산합니다.
#
#   앞선 판이 run_aryl_gcmc / run_gcmc_v3 / run_water / run_water_v3 넷만
#   복사했습니다. 그런데
#       run_wc_v3.py   -> import run_working_capacity    (빠짐)
#       run_gcmc_v3.py -> import run_gcmc_v2             (빠짐)
#   이라 상대 기기에서 ModuleNotFoundError 로 즉사했습니다. 랩탑 쪽이 형제
#   러너를 보고 모듈을 **복원해서** 돌렸는데, 규약이 원본과 같다는 보장이 없어
#   더 위험한 상황이 됐습니다.
#
#   목록을 손으로 관리하면 반드시 또 빠집니다. 씨앗에서 import 를 따라가
#   프로젝트 안의 모듈을 전부 끌어옵니다.
say "실행 스크립트 의존성 추적 중..."
"$PY" - "$Z" "$DEST/21_ZIF69_MTV" <<'PYEOF'
import ast, os, shutil, sys
src, dst = sys.argv[1], sys.argv[2]
seeds = ['run_wc_v3.py', 'run_gcmc_v3.py', 'run_water_v3.py',
         'run_density_v3.py', 'run_humid_wc_v3.py']
seen, queue = set(), [s for s in seeds if os.path.exists(os.path.join(src, s))]
while queue:
    f = queue.pop()
    if f in seen:
        continue
    seen.add(f)
    tree = ast.parse(open(os.path.join(src, f), encoding='utf-8').read())
    names = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            names += [a.name for a in n.names]
        elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
            names.append(n.module)
    for m in names:
        cand = m.split('.')[0] + '.py'
        if os.path.exists(os.path.join(src, cand)) and cand not in seen:
            queue.append(cand)
for f in sorted(seen):
    shutil.copy(os.path.join(src, f), os.path.join(dst, f))
print(f'  모듈 {len(seen)}개: {" ".join(sorted(seen))}')
PYEOF

# 요청 명세는 **여기서 새로 뽑습니다.** 다운로드 폴더의 사본을 복사하지 않습니다 --
# 그 파일은 뷰어로 열려 있으면 잠기고, 그러면 생성기가 `_2.pdf` 로 빠져서
# 정작 꾸러미에는 **낡은 판**이 들어갑니다(실제로 그렇게 될 뻔했습니다).
# 꾸러미 안을 직접 가리켜 잠긴 파일과 마주치지 않게 합니다. 구조 개수도
# 이때 실제 폴더를 세므로 문서와 내용물이 어긋나지 않습니다.
say "요청 명세 PDF 생성 중..."
PEER_PDF_OUT="$DEST/계산지원_요청명세_MTV-ZIF.pdf" "$PY" "$PDFGEN" \
  || { echo "!! PDF 생성 실패"; exit 1; }

cat > "$DEST/README.md" <<'MD'
# MTV-ZIF CO2 포집 — 계산 지원 꾸러미

같이 넣은 `계산지원_요청명세_MTV-ZIF.pdf` 에 무엇을 왜 부탁드리는지 적었습니다.
이 파일은 **그대로 실행하는 방법**만 적습니다.

## 0. 가장 중요한 것 하나

**힘장 파일을 배포본 표준으로 바꾸지 말아 주십시오.**

`raspa_share/molecules/CO2.def` 는 경로가 TraPPE 지만 **기하(C=O 1.16 A)만**
거기서 옵니다. 실제 LJ 와 전하는 `raspa_share/forcefield/UFF_MOF/` 의 두 파일에
있고, 그 값은 **Garcia-Sanchez 2009** 입니다.

    force_field_mixing_rules.def   C_co2   eps 29.933 K   sigma 2.745 A
    pseudo_atoms.def               C_co2   q   +0.6512

TraPPE 표준값(27.0 / 2.80)으로 바뀌면 결과가 저희 것과 합쳐지지 않습니다.
물도 마찬가지입니다 — `19_WaterCompetition/water.def` 는 **TIP5P-Ew 5자리**이고
RASPA 배포본의 `TraPPE/water.def` 는 3자리라 다릅니다.

## 1. 환경

    RASPA 2.0.50 (2.0.4x 계열도 동일 결과 확인)
    Python 3.10 + numpy, ase

    export RASPA_DIR=<RASPA 설치 경로>/simulations
    # 위 raspa_share 의 내용을 $RASPA_DIR/share/raspa/ 에 덮어써 주십시오
    # (또는 그 경로를 가리키게 하십시오)

## 2. 실행

작업 목록 생성과 병렬 실행이 파이썬 스크립트 안에 들어 있습니다.
워커 수만 환경변수로 주시면 됩니다.

    cd 21_ZIF69_MTV

    # A. 수분 경쟁 (20작업, 가장 무겁습니다)
    WATER_V3_WORKERS=16 python run_water_v3.py

    # B/C. 건조 GCMC 와 작업 용량
    V3_WORKERS=16 python run_gcmc_v3.py

`cif/` 의 파일을 `21_ZIF69_MTV/charged_v3/` 로 옮겨 두시면 스크립트가 바로 찾습니다.

## 3. 중단되어도 괜찮습니다

두 스크립트 모두 **작업 단위 이어받기**가 있습니다. 완주한 작업은 출력 파일을
읽어 `cached` 로 건너뛰므로, 죽으면 그냥 다시 띄우시면 됩니다. 저희도 정전으로
19작업을 잃을 뻔했다가 이 장치로 전부 회수했습니다.

## 4. 진행이 안 보이는 것은 정상입니다

`PrintEvery` 가 생산 사이클 수와 같아서 출력 파일이 **처음과 끝에만** 갱신됩니다.
몇 시간 그대로여도 멈춘 것이 아닙니다. 보고 싶으시면 스크립트 안의 `PrintEvery`
를 1000 으로 낮추셔도 **결과에는 영향이 없습니다**.

## 5. 돌려주실 것

    v3_water/water_results.json      (A)
    results_v3.json                  (B/C)

이것만 주시면 됩니다(각 100 KB 안팎). 원본 출력이 필요하면 저희가 말씀드리겠습니다.

**실패한 작업은 목록만 주십시오.** 중간에 죽은 RASPA 출력도 30 MB 를 남겨서
크기로는 구별되지 않습니다. 로그에 `Simulation finished` 가 없는 작업이 있으면
이름만 알려 주시면 저희가 다시 돌리겠습니다. 무리해서 채우지 않으셔도 됩니다.

## 6. 일정을 잡으실 때

작업 길이가 **13배까지** 차이 납니다(1.5시간 ~ 20.2시간, 실측).
습도와 치환율이 높을수록 비쌉니다. **비싼 것부터 큐에 넣어 주십시오.**
저희는 격자 순서로 넣었다가 마지막에 가장 비싼 두 건만 남아 코어 6개가
노는 상황을 겪었습니다.
MD

( cd "$DEST" && find . -type f ! -name CHECKSUMS.txt -exec sha256sum {} + \
    | sort -k2 > CHECKSUMS.txt )

echo "=== 완료 ==="
say "위치 $DEST"
say "크기 $(du -sh "$DEST" | cut -f1)"
say "파일 $(find "$DEST" -type f | wc -l)개"
echo
find "$DEST" -maxdepth 2 -type d | sed "s|$DEST|  D:\\\\MTV-ZIF_계산지원|"
exit 0
