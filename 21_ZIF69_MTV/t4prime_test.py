"""T-4' 판정 — `T4_PRIME_20260907.md` §1·§2 그대로. 문턱·부호·표본 안 바꿈."""
import numpy as np, gzip, json, sys, os

N, REP, RC, NDRAW = 90, 2, 3.0, 200

def cif(p):
    el, fr, cell = [], [], []
    for ln in open(p):
        if ln.startswith('_cell_length'): cell.append(float(ln.split()[1]))
        q = ln.split()
        if len(q) >= 8 and q[0].isalpha():
            try: fr.append([float(q[3]), float(q[4]), float(q[5])]); el.append(q[0])
            except ValueError: pass
    a, b, c = cell
    A = np.array([[a,0,0],[b*np.cos(np.radians(120)), b*np.sin(np.radians(120)),0],[0,0,c]])
    return np.array(el), np.array(fr), A

def near(f0, F, A, rc):
    d = F - f0; d -= np.round(d); return np.linalg.norm(d @ A, axis=1) <= rc

def sub_set(name, el, fr, A):
    """§2 — **첨가** 치환기 집합들을 이름표와 함께 돌려줍니다.

    ⚠️ 초판은 조성 이름으로 분기했고 **모르는 이름은 조용히 `Cl` 로 떨어졌습니다.**
    확장 덱(09-07)에서 실측: `saIm100`·`sa50nb50` 은 Cl 이 0 개라 **빈 집합**,
    `nbIm075` 는 **남은 미치환 Cl 6 개**를 집어 **그럴듯한 수를 내고 끝났습니다.**
    이름이 아니라 **화학으로** 고릅니다. 빈 집합은 조용히 넘기지 않고 막습니다.
    """
    sets = {}
    S = np.where(el == 'S')[0]; O = np.where(el == 'O')[0]; N = np.where(el == 'N')[0]
    if len(S):
        so = sorted({o for s in S for o in O[near(fr[s], fr[O], A, 1.7)]})
        sets['술폰산'] = np.array(sorted(set(list(S) + so)))
    # --- 첨가 나이트로 식별 -------------------------------------------------
    # 등록문 §2 는 "base 의 Cl 자리와 위치를 맞춰" 라고 적었습니다. 그 절차는
    # **nbIm025 에서만 검증**됐고(6개, 0.98 Å 대 4.84 Å 로 깨끗) **치환율이 높으면
    # 무너집니다** — 09-07 실측: 허용 1.0 Å 에서 nbIm075 는 18개 중 **3개**,
    # sa50nb50 은 12개 중 **1개**만 잡혔습니다(골격이 더 뒤틀려 자리가 밀림).
    #
    # 그래서 **화학으로** 가릅니다. 모체 나이트로는 이미다졸(5고리) C2 에,
    # 첨가 나이트로는 벤즈이미다졸의 **벤조 고리** 탄소에 붙습니다. 부착 탄소의
    # 고리 N 이웃 수가 **3 대 0** 으로 갈립니다(세 구조에서 확인).
    # 정의(=첨가 나이트로)는 그대로이고 **식별 절차만** 바꿉니다. 두 방법이
    # 겹치는 nbIm025 에서 **6 = 6 으로 일치**합니다.
    C = np.where(el == 'C')[0]
    add = []
    for i in N:
        if near(fr[i], fr[O], A, 1.4).sum() < 2:      # 나이트로 N 은 O 2개
            continue
        cc = C[near(fr[i], fr[C], A, 1.6)]
        if len(cc) and near(fr[cc[0]], fr[N], A, 1.45).sum() == 0:
            add.append(i)
    if add:
        ao = sorted({o for n in add for o in O[near(fr[n], fr[O], A, 1.4)]})
        sets['첨가나이트로'] = np.array(sorted(set(add + ao)))
    Cl = np.where(el == 'Cl')[0]
    if not sets:                       # 첨가분이 없으면(base) Cl 이 음성 대조
        sets['Cl(음성대조)'] = Cl
    return sets

def load(p):
    o = gzip.open(p, 'rt', errors='replace') if p.endswith('.gz') else open(p, errors='replace')
    L = o.read().splitlines(); i = L.index('LOOKUP_TABLE default') + 1
    return np.array([float(x) for x in L[i:] if x.strip()]).reshape(N, N, N)

def run(name):
    el, fr, A = cif(f'charged_v3/{name}_DDEC6.cif')
    sets = sub_set(name, el, fr, A)
    As = A * REP
    F = np.vstack([(fr + [i,j,k]) / REP for i in range(REP) for j in range(REP) for k in range(REP)])
    tag = np.tile(np.arange(len(fr)), REP**3)
    heavy = np.where(el != 'H')[0]
    pad = np.ceil(RC / (np.linalg.norm(As, axis=1) / N)).astype(int) + 1
    def shell(sel):
        m = np.zeros((N,N,N), bool)
        for f in F[np.isin(tag, sel)]:
            c = (f * N).astype(int)
            sl = [np.mod(np.arange(c[d]-pad[d], c[d]+pad[d]+1), N) for d in range(3)]
            ii, jj, kk = np.meshgrid(*sl, indexing='ij')
            df = np.stack([ii/N-f[0], jj/N-f[1], kk/N-f[2]], -1); df -= np.round(df)
            m[ii,jj,kk] |= (np.linalg.norm(df @ As, axis=-1) <= RC)
        return m
    grids = {}
    for sp in ('water', 'CO2'):
        p = f'water_runs_density_v3w/rh90_{name}/VTK/System_0/COMDensityProfile_{sp}.vtk.gz'
        if os.path.exists(p): grids[sp] = load(p)
    rows = []
    for label, idx in sets.items():
        if len(idx) == 0:
            print(f'  !! {name}/{label}: **집합이 비었습니다. 건너뜁니다** '
                  f'(조용히 0 을 내면 안 됩니다)'); continue
        ms = shell(idx)
        rng = np.random.default_rng(20260907)
        draws = [shell(rng.choice(heavy, size=len(idx), replace=False)) for _ in range(NDRAW)]
        r = {'name': name, 'set': label, 'n_atoms': int(len(idx)),
             'shell_voxels': int(ms.sum()), 'shell_pct': round(100*ms.sum()/N**3, 2)}
        for sp, rho in grids.items():
            T = float(rho[ms].mean())
            nul = np.array([float(rho[d].mean()) for d in draws])
            k = int((nul >= T).sum())
            r[sp] = {'T': T, 'null_med': float(np.median(nul)),
                     'null_p95': float(np.percentile(nul,95)), 'null_max': float(nul.max()),
                     'k_ge_T': k, 'p_onesided': (k+1)/(NDRAW+1),
                     'p_depletion_descriptive': (NDRAW-k+1)/(NDRAW+1),
                     'ratio_to_null_med': T/float(np.median(nul))}
        rows.append(r)
    return rows

if __name__ == '__main__':
    names = sys.argv[1:] or ['base', 'nbIm025', 'saIm050']
    res = [r for n in names for r in run(n)]
    json.dump(res, open('t4prime_result.json','w'), indent=2, ensure_ascii=False)
    for r in res:
        print(f"\n  === {r['name']} / {r['set']}  원자 {r['n_atoms']} · 껍질 {r['shell_voxels']:,} ({r['shell_pct']} %)")
        for sp in ('water','CO2'):
            if sp not in r: continue
            d = r[sp]
            print(f"    {sp:<6} T {d['T']:.6g}   위약 중앙 {d['null_med']:.6g} · 95% {d['null_p95']:.6g} · 최대 {d['null_max']:.6g}"
                  f"   **{d['k_ge_T']}/200**  p={d['p_onesided']:.4f}   T/중앙 **{d['ratio_to_null_med']:.2f}**"
                  f"   [고갈 p {d['p_depletion_descriptive']:.4f} — 서술]")
