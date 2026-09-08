#!/usr/bin/env python
"""단일 실행 -> 연장 사슬의 `chunk0` 로 변환 (09-07, 랩탑).

**왜**: 승인된 연장은 `Restart` 에서 이어 붙이는 것인데, `run_water.py` 로 돈
단일 실행에는 조각 구조가 없습니다. `extend_chain_v3w.py` 는 `chunk<k>/` 를 보므로
그 형태로 옮겨 놓아야 도구가 사슬을 봅니다.

**무엇을 만드는가** (아무것도 지우지 않습니다 — 원본은 그대로 둡니다):

    <CHAIN_ROOT>/rh90_<조성>/chunk0/
        Output/System_0/*.data        원본 완주 출력의 **사본**
        Restart/System_0/restart_*    이어 넘길 배치 (원본 Restart 또는 스냅숏)
        <조성>_DDEC6.cif · water.def · simulation.input   사본

**입력 두 가지 — 열이 다릅니다** (`ASSIGN §D-1`):

    완주 Restart   완주 뒤에도 남은 `Restart/`(고친 러너)  -> **"연장됨(완주 배치)"**
    스냅숏         실행 중에 뜬 사본                        -> **"연장됨(중간 가지)"**

⚠️ **이 변환기는 Δ40 을 계산하지 않습니다.** 아래 이유로 지금 계산하면 틀립니다.
"""
import argparse, glob, json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def blocks_of(data):
    txt = open(data, encoding='utf-8', errors='ignore').read()
    i = txt.rfind('Component 1 [water]')
    return [] if i < 0 else re.findall(r'Block\[\s*\d+\]\s+([\d.eE+-]+)', txt[i:i+1200])[:5]


def cycles_of(inp):
    d = {}
    for ln in open(inp, encoding='utf-8', errors='ignore'):
        p = ln.split()
        if len(p) >= 2 and p[0] in ('NumberOfCycles', 'PrintEvery',
                                    'NumberOfInitializationCycles'):
            d[p[0]] = int(float(p[1]))
    return d


def convert(src, name, chain_root, restart_src=None, dry=True):
    dst = os.path.join(HERE, chain_root, f'rh90_{name}', 'chunk0')
    out = glob.glob(os.path.join(src, 'Output', 'System_0', '*.data'))
    if len(out) != 1:
        return None, f'출력 .data 가 {len(out)}개 — 1개여야 합니다'
    rs = restart_src or os.path.join(src, 'Restart', 'System_0')
    rfiles = sorted(glob.glob(os.path.join(rs, 'restart_*')))
    if len(rfiles) != 1:
        return None, f'restart_* 가 {len(rfiles)}개 — 1개여야 합니다 ({rs})'
    cyc = cycles_of(os.path.join(src, 'simulation.input'))
    nb = len(blocks_of(out[0]))
    info = {'name': name, 'src': src, 'restart': rfiles[0],
            'cycles': cyc.get('NumberOfCycles'), 'print_every': cyc.get('PrintEvery'),
            'blocks': nb,
            'cycles_per_block': (cyc.get('NumberOfCycles') // nb) if nb else None,
            'kind': '완주 배치' if restart_src is None else '중간 가지',
            'restart_bytes': os.path.getsize(rfiles[0])}
    if dry:
        return info, None
    os.makedirs(os.path.join(dst, 'Output', 'System_0'), exist_ok=True)
    os.makedirs(os.path.join(dst, 'Restart', 'System_0'), exist_ok=True)
    shutil.copy2(out[0], os.path.join(dst, 'Output', 'System_0'))
    shutil.copy2(rfiles[0], os.path.join(dst, 'Restart', 'System_0'))
    for f in ('simulation.input', 'water.def', f'{name}_DDEC6.cif'):
        p = os.path.join(src, f)
        if os.path.exists(p):
            shutil.copy2(p, dst)
    json.dump(info, open(os.path.join(dst, 'chunk0_provenance.json'), 'w'),
              indent=2, ensure_ascii=False)
    return info, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--chain-root', required=True)
    ap.add_argument('--src-root', required=True, help='단일 실행들이 있는 폴더')
    ap.add_argument('--snapshot-root', default=None, help='스냅숏 뿌리(있으면 중간 가지)')
    ap.add_argument('--names', nargs='+', required=True)
    ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()
    print(f'{"실행" if a.apply else "**--dry-run** (기본)"} · 사슬 뿌리 {a.chain_root}', flush=True)
    rows = []
    for n in a.names:
        src = os.path.join(HERE, a.src_root, f'rh90_{n}')
        rsrc = None
        if a.snapshot_root:
            cand = os.path.join(HERE, a.snapshot_root,
                                f'{a.src_root.replace("/", "_")}_rh90_{n}', 'Restart', 'System_0')
            if os.path.isdir(cand):
                rsrc = cand
        info, err = convert(src, n, a.chain_root, rsrc, dry=not a.apply)
        if err:
            print(f'  {n:<14} **건너뜀** — {err}'); continue
        rows.append(info)
        print(f"  {n:<14} 사이클 {info['cycles']} · 블록 {info['blocks']}"
              f" · 블록당 {info['cycles_per_block']} · {info['kind']}"
              f" · restart {info['restart_bytes']:,} B")
    if not rows:
        return 1
    cpb = {r['cycles_per_block'] for r in rows}
    print(f"\n  ⚠️ **블록당 사이클 {sorted(cpb)}** — 사슬 조각은 **600** 입니다.")
    print("     `extend_chain_v3w.d40_band` 는 **블록 개수**의 40 % 를 쓰므로,")
    print("     길이가 섞인 열에 그대로 대면 앞/뒤가 **다른 사이클 수**를 덮습니다.")
    print("     -> **창을 사이클 기준으로 바꾸기 전에는 Δ40 을 내지 마십시오.**")
    print("        (이 변환기는 구조만 만들고 Δ40 을 계산하지 않습니다)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
