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
    """§2 — **첨가** 치환기만. base 는 첨가분이 없어 Cl(음성 대조)."""
    if name == 'saIm050':
        S = np.where(el == 'S')[0]; O = np.where(el == 'O')[0]
        so = sorted({o for s in S for o in O[near(fr[s], fr[O], A, 1.7)]})
        return np.array(sorted(set(list(S) + so))), 'S 12 + 술폰산 O 36'
    if name == 'nbIm025':
        eb, fb, _ = cif('charged_v3/base_DDEC6.cif')
        Clb = fb[eb == 'Cl']; Nn = np.where(el == 'N')[0]
        add = [n for n in Nn if near(fr[n], Clb, A, 1.0).any()]
        O = np.where(el == 'O')[0]
        ao = sorted({o for n in add for o in O[near(fr[n], fr[O], A, 1.4)]})
        return np.array(sorted(set(add + ao))), f'첨가 나이트로 N {len(add)} + O {len(ao)}'
    return np.where(el == 'Cl')[0], 'Cl 24 (음성 대조 — 첨가 치환기 없음)'

def load(p):
    o = gzip.open(p, 'rt', errors='replace') if p.endswith('.gz') else open(p, errors='replace')
    L = o.read().splitlines(); i = L.index('LOOKUP_TABLE default') + 1
    return np.array([float(x) for x in L[i:] if x.strip()]).reshape(N, N, N)

def run(name):
    el, fr, A = cif(f'charged_v3/{name}_DDEC6.cif')
    idx, desc = sub_set(name, el, fr, A)
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
    ms = shell(idx)
    rng = np.random.default_rng(20260907)
    draws = [shell(rng.choice(heavy, size=len(idx), replace=False)) for _ in range(NDRAW)]
    out = {'name': name, 'set': desc, 'n_atoms': int(len(idx)),
           'shell_voxels': int(ms.sum()), 'shell_pct': round(100*ms.sum()/N**3, 2)}
    for sp, path in (('water', f'water_runs_density_v3w/rh90_{name}/VTK/System_0/COMDensityProfile_water.vtk.gz'),
                     ('CO2',   f'water_runs_density_v3w/rh90_{name}/VTK/System_0/COMDensityProfile_CO2.vtk.gz')):
        if not os.path.exists(path): continue
        rho = load(path)
        T = float(rho[ms].mean())
        nul = np.array([float(rho[d].mean()) for d in draws])
        k = int((nul >= T).sum())
        out[sp] = {'T': T, 'null_med': float(np.median(nul)), 'null_p95': float(np.percentile(nul,95)),
                   'null_max': float(nul.max()), 'k_ge_T': k, 'p_onesided': (k+1)/(NDRAW+1),
                   'ratio_to_null_med': T/float(np.median(nul))}
    return out

if __name__ == '__main__':
    res = [run(n) for n in ('base', 'nbIm025', 'saIm050')]
    json.dump(res, open('t4prime_result.json','w'), indent=2, ensure_ascii=False)
    for r in res:
        print(f"\n  === {r['name']}  [{r['set']}]  원자 {r['n_atoms']} · 껍질 {r['shell_voxels']:,} ({r['shell_pct']} %)")
        for sp in ('water','CO2'):
            if sp not in r: continue
            d = r[sp]
            print(f"    {sp:<6} T {d['T']:.6g}   위약 중앙 {d['null_med']:.6g} · 95% {d['null_p95']:.6g} · 최대 {d['null_max']:.6g}"
                  f"   **{d['k_ge_T']}/200**  p={d['p_onesided']:.4f}   T/중앙 **{d['ratio_to_null_med']:.2f}**")
