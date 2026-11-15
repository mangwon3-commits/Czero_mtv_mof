#!/bin/bash
# COREPOP-H323 새 기기 착수 전 점검 — HANDOVER_COREPOP_NEWMACHINE_20261115.md §4.
# 읽기만 합니다: RASPA · Zeo++ 를 띄우지 않고, 저장소 파일을 고치지 않습니다(CIF 를 저장소 밖 ~/.mof_chain/corepop_1114/cifs/ 에 푸는 것만 함).
# 쓰는 법:  bash 21_ZIF69_MTV/corepop_preflight.sh <기기> <묶음>        예) bash 21_ZIF69_MTV/corepop_preflight.sh pc3 b06
#   REPO(기본 ~/mof_project) · PY(기본 ~/miniconda3/envs/czeromof/bin/python) · RASPA_DIR(기본 ~/RASPA/simulations) 은 env 로 덮을 수 있음.
# 끝에 "점검 통과" 가 나오면 권고 명령을 그대로 씁니다. "점검 실패 N" 이면 띄우지 말고 !! 줄을 고칩니다. 반환코드 = 실패 수.
set -u
M=${1:-}; B=${2:-}
[ -n "$M" ] && [ -n "$B" ] || { echo "쓰는 법: corepop_preflight.sh <기기> <묶음>"; exit 99; }
REPO=${REPO:-$HOME/mof_project}
D=$REPO/21_ZIF69_MTV
PY=${PY:-$HOME/miniconda3/envs/czeromof/bin/python}
RD=${RASPA_DIR:-$HOME/RASPA/simulations}
NF=0
ok()  { echo "  ok  $*"; }
bad() { echo "  !!  $*"; NF=$((NF+1)); }
m8()  { md5sum < "$1" 2>/dev/null | cut -c1-8; }

echo "[1] 기기"
K=$(uname -r)
case "$K" in *-fc-*|*sandbox*) bad "커널 $K — 임시 클라우드 샌드박스로 보임. 긴 계산 금지(NEW_MACHINE_20260822.md 0-1)";; *) ok "커널 $K · $(hostname)";; esac
case "$M" in *[!a-z0-9_]*) bad "기기 이름은 소문자 · 숫자 · _ 만: $M";; desktop|hkhome|laptop|laptop2|cloud|junseok|audit|cloud4c) bad "기기 이름 $M 은 이미 쓰는 이름";; *) ok "기기 이름 $M";; esac
case "$REPO" in /mnt/*) bad "저장소가 $REPO — 윈도우 디스크(NTFS) 아래. WSL ext4 안(~/mof_project)에 클론해야 함";; *) [ -d "$D" ] && ok "저장소 $REPO" || bad "저장소 폴더 없음 $D";; esac
cd "$D" 2>/dev/null || { echo "점검 실패 — 저장소에 들어갈 수 없음"; exit 98; }

echo "[2] 실행 파일"
[ -x "$PY" ] && ok "python $PY ($($PY -c 'import sys;print(sys.version.split()[0])' 2>/dev/null))" || bad "python 없음 $PY"
$PY -c 'import ase, numpy' 2>/dev/null && ok "ase · numpy import" || bad "ase 또는 numpy import 실패"
SIM=$(env -i HOME=$HOME PATH=/usr/bin:/bin "$PY" -c "import shutil,os;print(shutil.which('simulate') or os.path.expanduser('~/miniconda3/envs/czeromof/bin/simulate'))" 2>/dev/null)
[ -n "$SIM" ] && [ -x "$SIM" ] && ok "RASPA simulate $SIM (러너가 보는 자리)" || bad "RASPA simulate 없음 ($SIM) — 러너는 ~/miniconda3/envs/czeromof/bin/simulate 를 봄"
ZEO=$HOME/miniconda3/envs/czeromof/bin/network
[ -x "$ZEO" ] && ok "Zeo++ network $ZEO" || bad "Zeo++ network 없음 $ZEO — corepop_blocks.py 가 이 자리만 봄(conda install -n czeromof -c conda-forge zeopp-lsmo)"

echo "[3] 힘장(파일 관문)"
FF=$RD/share/raspa/forcefield/UFF_MOF/force_field_mixing_rules.def
F8=$(m8 "$FF")
[ "$F8" = "8e8ec933" ] && ok "혼합 규칙 md5 8e8ec933 ($FF)" || bad "혼합 규칙 md5 ${F8:-없음} ≠ 8e8ec933 ($FF) — 저장소의 00_Migration/raspa_share/raspa 를 \$RASPA_DIR/share/raspa 로 복사"
grep -E '^C_co2' "$RD/share/raspa/forcefield/UFF_MOF/pseudo_atoms.def" 2>/dev/null | grep -q '0\.6512' && ok "C_co2 전하 0.6512" || bad "pseudo_atoms.def 의 C_co2 전하가 0.6512 가 아님"
for f in CO2 N2; do [ -f "$RD/share/raspa/molecules/TraPPE/$f.def" ] && ok "molecules/TraPPE/$f.def 있음" || bad "molecules/TraPPE/$f.def 없음"; done
W8=$(m8 "$REPO/19_WaterCompetition/water.def"); [ "$W8" = "6fc8850d" ] && ok "물 정의 5자리 water.def 6fc8850d" || bad "19_WaterCompetition/water.def md5 ${W8:-없음} ≠ 6fc8850d"
[ -n "${RASPA_DIR:-}" ] && ok "RASPA_DIR 가 env 에 있음 ($RASPA_DIR)" || echo "  --  RASPA_DIR 가 env 에 없음 — 아래 권고 명령처럼 띄울 때 같이 줌"

echo "[4] 실행기 md5"
while read -r f want; do
  got=$(m8 "$f"); [ "$got" = "$want" ] && ok "$f $want" || bad "$f md5 ${got:-없음} ≠ $want"
done <<'T'
corepop_humid323_targets.json f0cbc615
corepop_blocks.py c00cd11a
run_corepop_e_humid3.py e05cbc1b
run_corepop_e_humid3_323.py 75307c47
corepop_chain.sh ec27c8b3
run_znbdt_e_humid3.py 97023663
run_znbdt_e_humid3_323.py 7f83dc3c
ff_gate.py 9fee09a4
core_pop_cifs.zip 96a5fbf8
core_pop_annotated.json cbccf2e0
T

echo "[5] 기기 상태"
NS=$(pgrep -xc simulate); NN=$(pgrep -xc network)
[ "$NS" = 0 ] && [ "$NN" = 0 ] && ok "simulate 0 · network 0" || bad "simulate $NS · network $NN — 비어 있지 않음"
NPROC=$(nproc); TOT=$(awk '/^MemTotal:/{print int($2/1048576+0.5)}' /proc/meminfo); AV=$(awk '/^MemAvailable:/{print int($2/1048576)}' /proc/meminfo)
PAR=$(( (TOT - 5) / 9 )); [ $PAR -lt 1 ] && PAR=1; [ $PAR -gt 4 ] && PAR=4
ok "논리 코어 $NPROC · 메모리 전체 ${TOT} GB · 여유 ${AV} GB"
[ "$TOT" -ge 14 ] || bad "메모리 전체 ${TOT} GB — Zeo++ 호출 하나가 6~14 GB 라 대부분 가드에 걸림(WSL 이면 .wslconfig 의 memory 를 올릴 수 있는지 사용자에게 물음)"
if [ -d /mnt/c ]; then FREE=$(df -BG /mnt/c | awk 'NR==2{gsub("G","",$4);print $4}'); [ "${FREE:-0}" -ge 20 ] && ok "C: 여유 ${FREE} GB" || bad "C: 여유 ${FREE:-?} GB < 20 GB (CLAUDE.md §5 — 게스트 df 가 아니라 df /mnt/c)"
else FREE=$(df -BG "$HOME" | awk 'NR==2{gsub("G","",$4);print $4}'); [ "${FREE:-0}" -ge 20 ] && ok "디스크 여유 ${FREE} GB" || bad "디스크 여유 ${FREE:-?} GB < 20 GB"; fi
git -C "$REPO" ls-remote -q origin refs/heads/master >/dev/null 2>&1 && ok "origin master 읽힘" || bad "origin master 를 읽지 못함(인증 · 네트워크)"
[ -n "$(git -C "$REPO" config user.name)" ] && [ -n "$(git -C "$REPO" config user.email)" ] && ok "git user.name · user.email 있음" || bad "git user.name 또는 user.email 없음 — 게시 도구가 커밋을 못 만듦"

echo "[6] 묶음 $B 입력 대조(Zeo++ 드라이)"
[ -e "results_corepop_blocks_${M}_${B}.json" ] && bad "results_corepop_blocks_${M}_${B}.json 이 이미 있음 — 이어받기 금지"
[ -e "results_corepop_e_humid3_323_${M}_${B}.json" ] && bad "results_corepop_e_humid3_323_${M}_${B}.json 이 이미 있음 — 이어받기 금지"
DRY=$(COREPOP_MACHINE=$M COREPOP_BATCHES=$B COREPOP_ZEO_PAR=$PAR COREPOP_ZEO_DRY=1 "$PY" -u corepop_blocks.py 2>&1 | grep -E '입력 대조|!!')
case "$DRY" in *"입력 대조 통과"*) ok "$DRY";; *) bad "드라이 실패: ${DRY:-출력 없음}";; esac

echo
if [ $NF = 0 ]; then
  echo "점검 통과 — 착수 글을 먼저 올린 뒤 아래 두 줄로 띄웁니다(Zeo++ 병렬 $PAR · 워커 $NPROC):"
  echo "  mkdir -p ~/.mof_chain && cp $D/corepop_chain.sh ~/.mof_chain/"
  echo "  RASPA_DIR=$RD REPO=$REPO PY=$PY setsid nohup bash ~/.mof_chain/corepop_chain.sh $M $B $PAR $NPROC < /dev/null > /dev/null 2>&1 &"
else
  echo "점검 실패 $NF — 띄우지 마십시오. 위의 !! 줄을 고친 뒤 다시 돌립니다."
fi
exit $NF
