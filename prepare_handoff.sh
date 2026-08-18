#!/bin/bash
# 다른 기기(지인 서버 / 랩탑)에 넘길 계산 꾸러미를 D 드라이브에 만든다.
#
# [설계 원칙 1: 상대가 우리 값을 재현할 수 있어야 한다]
#   힘장 파라미터를 손으로 골라 담지 않습니다. **폴더째** 넘깁니다.
#   우리가 쓰는 CO2 정의는 경로가 molecules/TraPPE/CO2.def 인데 **내용은
#   TraPPE 가 아닙니다.** 기하만 거기서 오고 LJ 와 전하는 UFF_MOF 의 두 파일에서
#   옵니다 -- eps 29.933 / sigma 2.745 / q +0.6512, 즉 Garcia-Sanchez 2009 입니다.
#   상대가 폴더 이름만 보고 배포본 표준 파일을 쓰면 다른 숫자가 나오고 우리 값과
#   합칠 수 없습니다. 실행 스크립트도 우리가 쓰는 것을 그대로 넘깁니다 --
#   견본 simulation.input 을 손으로 만들면 그 순간 규약이 갈라집니다.
#
# [설계 원칙 2: 넣을 파일을 사람이 고르지 않는다]
#   같은 결함이 세 번 났습니다.
#       1차  run_working_capacity.py, run_gcmc_v2.py  -> 랩탑에서 ModuleNotFound
#       2차  run_density_v3.py 계열                   -> 랩탑 지시가 부를 수 없음
#       3차  risk_screen_v3.py, risk_screen.py        -> 안정성 배정이 실행 불가
#   tools/pack_scripts.py 가 import 폐포를 **형제 폴더까지** 계산하고, 꾸러미에
#   넣은 **문서가 부르는 .py 가 실제로 들어갔는지** 대조합니다. 대조에 걸리면
#   꾸러미를 만들지 않고 실패합니다.
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
PACK=$P/tools/pack_scripts.py
PY=/home/mangwon1/miniconda3/envs/czeromof/bin/python

SEEDS="run_wc_v3.py run_gcmc_v3.py run_water_v3.py run_density_v3.py run_humid_wc_v3.py risk_screen_v3.py"

GO=0
for a in "$@"; do [ "$a" = "--go" ] && GO=1; done

say() { echo "  $*"; }
echo "=== 전달 꾸러미 준비 ==="

# ---- 관문: 전하가 붙은 v3 구조가 있어야 합니다 ----------------------------
NCIF=$(ls "$Z"/charged_v3/*_DDEC6.cif 2>/dev/null | wc -l)
if [ "$NCIF" -lt 25 ]; then
  echo "!! charged_v3 에 전하 CIF 가 ${NCIF}개뿐입니다."
  echo "   전하 없는 구조를 넘기면 상대가 GCMC 를 돌릴 수 없습니다."
  exit 1
fi
say "전하 CIF ${NCIF}개 확인"

for f in "$PDFGEN" "$PACK"; do
  [ -f "$f" ] || { echo "!! 도구가 없습니다: $f"; exit 1; }
done

echo
echo "  담을 것:"
say "  cif/                     charged_v3 전하 CIF ${NCIF}개"
say "  raspa_share/forcefield/  UFF_MOF 폴더째"
say "  raspa_share/molecules/   CO2.def, N2.def"
say "  19_WaterCompetition/     water.def (TIP5P-Ew 5자리)"
say "  21_ZIF69_MTV/            씨앗의 import 폐포"
say "  문서                     CLAUDE.md, 배정 문서들, 요청명세 PDF"

if [ "$GO" -eq 0 ]; then
  echo
  echo "  --dry-run 입니다. 실제로 만들려면 --go 를 붙이세요."
  exit 0
fi

# ---- 만들기 ---------------------------------------------------------------
echo
rm -rf "$DEST"
mkdir -p "$DEST"/cif "$DEST"/raspa_share/forcefield "$DEST"/raspa_share/molecules
mkdir -p "$DEST"/19_WaterCompetition "$DEST"/21_ZIF69_MTV

cp "$Z"/charged_v3/*_DDEC6.cif "$DEST/cif/"
cp -r "$R/forcefield/UFF_MOF" "$DEST/raspa_share/forcefield/"
cp "$R/molecules/TraPPE/CO2.def" "$R/molecules/TraPPE/N2.def" "$DEST/raspa_share/molecules/"
cp "$P/19_WaterCompetition/water.def" "$DEST/19_WaterCompetition/"

# 문서를 스크립트보다 **먼저** 복사합니다. pack_scripts.py 가 문서를 읽어
# "지시서가 부르는 .py 가 들어갔는지" 를 대조하므로, 순서가 뒤집히면 그 검사가
# 아무것도 못 봅니다.
for d in CLAUDE.md LAPTOP_QUICKSTART.md AUTOMATION_60H.md 48H_COMPUTE_PLAN.md; do
  [ -f "$P/$d" ] && cp "$P/$d" "$DEST/"
done
for d in LAPTOP_10H_SESSION.md LAPTOP_DENSITY_V3.md EXTERNAL_WATER_V3.md; do
  [ -f "$Z/$d" ] && cp "$Z/$d" "$DEST/"
done

say "실행 스크립트 의존성 추적 + 문서 대조..."
"$PY" "$PACK" "$P" "$DEST/21_ZIF69_MTV" $SEEDS || {
  echo "!! 스크립트 꾸리기 실패 — 문서가 부르는 파일이 빠졌습니다"
  exit 1
}

# 요청 명세는 **여기서 새로 뽑습니다.** 다운로드 폴더의 사본을 복사하지 않습니다 --
# 그 파일은 뷰어로 열려 있으면 잠기고, 그러면 생성기가 _2.pdf 로 빠져서 정작
# 꾸러미에는 낡은 판이 들어갑니다. 구조 개수도 이때 실제 폴더를 세므로 문서와
# 내용물이 어긋나지 않습니다.
say "요청 명세 PDF 생성 중..."
PEER_PDF_OUT="$DEST/계산지원_요청명세_MTV-ZIF.pdf" "$PY" "$PDFGEN" \
  || { echo "!! PDF 생성 실패"; exit 1; }

cat > "$DEST/README.md" <<'MD'
# MTV-ZIF CO2 포집 — 계산 꾸러미

`계산지원_요청명세_MTV-ZIF.pdf` 에 무엇을 왜 부탁드리는지 적었습니다.
이 파일은 **그대로 실행하는 방법**만 적습니다.

## 0. 가장 중요한 것 하나

**힘장 파일을 배포본 표준으로 바꾸지 마세요.**

`raspa_share/molecules/CO2.def` 는 경로가 TraPPE 지만 **기하만** 거기서 옵니다.
실제 LJ 와 전하는 `raspa_share/forcefield/UFF_MOF/` 의 두 파일에 있고
그 값은 **Garcia-Sanchez 2009** 입니다.

    force_field_mixing_rules.def   C_co2   eps 29.933 K   sigma 2.745 A
    pseudo_atoms.def               C_co2   q   +0.6512

TraPPE 표준값(27.0 / 2.80)으로 바뀌면 결과가 저희 것과 합쳐지지 않습니다.
물도 같습니다 — 저희 water.def 는 **TIP5P-Ew 5자리**, 배포본은 3자리입니다.

## 1. 환경 (약 10분, 빌드 불필요)

    conda create -y -n mof python=3.10
    conda activate mof
    conda install -y -c conda-forge raspa2 ase numpy

    export RASPA_DIR=$HOME/RASPA/simulations
    mkdir -p $RASPA_DIR/share/raspa
    cp -r raspa_share/* $RASPA_DIR/share/raspa/

**이 복사를 건너뛰면 즉시 실패합니다.** conda 배포본에는 UFF_MOF 가 없습니다.
`.bashrc` 는 비대화형 셸에서 조기 return 하므로 export 를 매번 명시하세요.

확인:

    grep C_co2 $RASPA_DIR/share/raspa/forcefield/UFF_MOF/force_field_mixing_rules.def
    # 29.933  2.745 가 나와야 합니다

## 2. 구조 배치

    mkdir -p 21_ZIF69_MTV/charged_v3
    cp cif/*.cif 21_ZIF69_MTV/charged_v3/

## 3. 무엇을 돌릴지는 배정 문서에

| 문서 | 대상 |
|---|---|
| `EXTERNAL_WATER_V3.md` | 외부 16코어 — 수분 경쟁 v3 (20작업, 약 24시간) |
| `LAPTOP_10H_SESSION.md` | 랩탑 — 밀도맵 + 구조 안정성 |
| `48H_COMPUTE_PLAN.md` | 전체 분담과 순서 |
| `CLAUDE.md` | **규약과 함정. 먼저 읽으세요** |

## 4. 중단되어도 괜찮습니다

모든 배치에 **작업 단위 이어받기**가 있습니다. 코드·설정을 바꾸지 않았다면
같은 명령을 다시 치면 완주분을 `cached` 로 회수합니다. 정전으로 19작업을
이렇게 살렸습니다(08-17).

**설정을 바꿨다면 실행 폴더를 지우고 처음부터.** 이어받기는 출력의 존재만 보고
무슨 설정으로 만든 것인지 검사하지 않습니다.

## 5. 진행이 안 보이는 것은 정상입니다

`PrintEvery` 가 생산 사이클 수와 같아 출력 파일이 **처음과 끝에만** 갱신됩니다.
살아 있는지는 `ps -o pid,etime,pcpu,comm -C simulate` 로 보세요.

## 6. 돌려주실 것

결과 JSON 만 주시면 됩니다(각 100 KB 안팎). 실행 폴더는 한 작업이 30 MB 라
보내지 마세요.

**실패한 작업은 목록만 주십시오.** 중간에 죽은 RASPA 출력도 30 MB 를 남겨
크기로는 구별되지 않습니다. 무리해서 채우지 않으셔도 됩니다.
MD

( cd "$DEST" && find . -type f ! -name CHECKSUMS.txt -exec sha256sum {} + \
    | sort -k2 > CHECKSUMS.txt )

echo "=== 완료 ==="
say "위치 $DEST"
say "크기 $(du -sh "$DEST" | cut -f1)"
say "파일 $(find "$DEST" -type f | wc -l)개"
exit 0
