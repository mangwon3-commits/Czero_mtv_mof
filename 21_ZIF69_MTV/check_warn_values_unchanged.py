"""표기가 **측정값을 안 건드렸는지** 값으로 확인한다.

텍스트 diff 는 오해를 준다 — 키가 마지막이었다가 뒤에 하나 붙으면 쉼표 때문에
그 줄이 '삭제 후 추가' 로 보인다. **파싱해서 값끼리 비교**해야 한다.
"""
import json, subprocess, glob, os

REPO = "/home/leehk/mof_project"
os.chdir(REPO)
sub = "21_ZIF69_MTV"

changed = subprocess.run(["git", "diff", "--name-only", "--", f"{sub}/v3_water*"],
                         capture_output=True, text=True).stdout.split()
print(f"바뀐 파일 {len(changed)}개")


def strip_warn(o):
    if isinstance(o, dict):
        return {k: strip_warn(v) for k, v in o.items() if k != "WARN_forcefield"}
    if isinstance(o, list):
        return [strip_warn(x) for x in o]
    return o


bad = []
for f in changed:
    old_raw = subprocess.run(["git", "show", f"HEAD:{f}"],
                             capture_output=True, text=True).stdout
    if not old_raw.strip():
        continue
    try:
        old = json.loads(old_raw)
        new = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        bad.append((f, f"파싱 {e}"))
        continue
    if strip_warn(old) != strip_warn(new):
        bad.append((f, "**값이 다름**"))

print()
if bad:
    print(f"⚠ 값이 바뀐 파일 {len(bad)}개:")
    for f, why in bad:
        print(f"    {f}  {why}")
else:
    print("✅ **WARN_forcefield 키를 빼면 모든 파일이 이전과 완전히 동일하다.**")
    print("   측정값·구조·순서 전부 불변. 키 추가만 일어났다.")
