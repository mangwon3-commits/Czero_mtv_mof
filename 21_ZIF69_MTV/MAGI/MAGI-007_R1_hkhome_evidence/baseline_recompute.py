#!/usr/bin/env python3
"""Caspar (HKHOME critic) — MAGI-007 baseline recompute. READ-ONLY on ~/mof_project.
Recomputes S_mix / S_Henry / gate 5 / humid TSA WC / water index for the five E-24i open-site
designs + e22_parent (+ mslm050 dry S_mix) from raw result JSON (+ RASPA .data where present).
Never uses rounded doc numbers as inputs; doc numbers appear only in CLAIMS for comparison.
Writes only ~/.mof_magi/caspar_work/baseline_recompute.json
"""
import glob, hashlib, json, math, os, re, statistics as st, subprocess, datetime

P = os.path.expanduser('~/mof_project')
Z = os.path.join(P, '21_ZIF69_MTV')
OUTD = os.path.expanduser('~/.mof_magi/caspar_work')
FF = '8e8ec933f9013c7e932da04dc256efd3'
X = 0.15 / 0.85
T95_4 = 2.776
TAGS = ['cn', 'br', 'c2h5', 'cl', 'ch3']
KEY = {t: f'e24i_{t}_open' for t in TAGS}
FILES = {}          # rel path -> md5


def md5(path):
    h = hashlib.md5(open(path, 'rb').read()).hexdigest()
    FILES[os.path.relpath(path, P)] = h
    return h


def J(rel):
    p = os.path.join(Z, rel)
    md5(p)
    return json.load(open(p, encoding='utf-8'))


def git(*a):
    return subprocess.run(['git', *a], cwd=P, capture_output=True, text=True).stdout.strip()


def smix_of(nc, ec, nn, en):
    s = (nc / nn) / X
    return s, s * math.hypot(ec / nc, en / nn)


# ---------------------------------------------------------------- RASPA .data parsing
def parse_data(path):
    md5(path)
    finished = 0; seed = None; comp = None; blocks = []; res = {}; warn = []; cyc = init = None; uc = []
    for ln in open(path, encoding='utf-8', errors='ignore'):
        if 'Simulation finished' in ln:
            finished += 1
            m = re.search(r'Simulation finished,\s+(\d+) warnings', ln)
            if m: warn.append(int(m.group(1)))
        m = re.match(r'\s*Random number seed:\s*(\d+)', ln)
        if m and seed is None: seed = int(m.group(1))
        m = re.match(r'Number of cycles:\s*(\d+)', ln)
        if m: cyc = int(m.group(1))
        m = re.match(r'Number of initializing cycles:\s*(\d+)', ln)
        if m: init = int(m.group(1))
        m = re.match(r'Number of unitcells \[[abc]\]:\s*(\d+)', ln)
        if m: uc.append(int(m.group(1)))
        m = re.search(r'Component\s+\d+\s+\[(\w+)\]', ln)
        if m: comp = m.group(1); blocks = []
        m = re.search(r'Block\[\s*\d+\]\s+([0-9.eE+-]+)', ln)
        if m: blocks.append(float(m.group(1)))
        m = re.match(r'\s*Average loading absolute\s+([0-9.eE+-]+)\s+\+/-\s+([0-9.eE+-]+)', ln)
        if m and comp:
            res.setdefault(comp, {})['abs_box'] = (float(m.group(1)), float(m.group(2)), blocks[-5:])
        m = re.search(r'Average loading absolute \[mol/kg framework\]\s+([0-9.eE+-]+)\s+\+/-\s+([0-9.eE+-]+)', ln)
        if m and comp:
            res.setdefault(comp, {}).setdefault('molkg', []).append((float(m.group(1)), float(m.group(2))))
        m = re.search(r'Framework has net charge:\s*([0-9.eE+-]+)', ln)
        if m: res['_net_charge'] = float(m.group(1))
    ci = {}
    for c, v in res.items():
        if c.startswith('_') or 'abs_box' not in v: continue
        mean, err, b = v['abs_box']
        if len(b) == 5:
            sem = st.stdev(b) / math.sqrt(5)
            ci[c] = dict(printed=err, t2776_sem=T95_4 * sem, ratio=err / (T95_4 * sem) if sem else None,
                         block_mean=st.mean(b), printed_mean=mean)
    return dict(finished_count=finished, warnings=warn, seed=seed, cycles=cyc, init=init, unit_cells=uc[-3:],
                molkg={c: v.get('molkg') for c, v in res.items() if not c.startswith('_')},
                net_charge=res.get('_net_charge'), ci_check=ci)


def sim_input(path):
    md5(path)
    t = open(path).read()
    g = lambda k: (re.search(rf'^[ \t]*{k}[ \t]+(\S+(?:[ \t]+\S+){{0,2}})', t, re.M) or [None, None])[1]
    return dict(cycles=g('NumberOfCycles'), init=g('NumberOfInitializationCycles'), T=g('ExternalTemperature'),
                P=g('ExternalPressure'), uc=g('UnitCells'), cutoff=g('CutOff'), ewald=g('EwaldPrecision'),
                molfrac=re.findall(r'MolFraction\s+(\S+)', t), block='BlockPockets' in t, ff=g('Forcefield'))


# ---------------------------------------------------------------- CIF (stdlib)
def cif_atoms(path):
    md5(path)
    L = open(path, encoding='utf-8', errors='ignore').read().splitlines()
    cell = {}
    for ln in L:
        m = re.match(r'_cell_(length_[abc]|angle_\w+)\s+([0-9.]+)', ln.strip())
        if m: cell[m.group(1)] = float(m.group(2))
    i = 0; atoms = []
    while i < len(L):
        if L[i].strip() == 'loop_':
            hdr = []; j = i + 1
            while j < len(L) and L[j].strip().startswith('_'):
                hdr.append(L[j].strip()); j += 1
            if '_atom_site_fract_x' in hdr:
                ix = {h: k for k, h in enumerate(hdr)}
                while j < len(L) and L[j].strip() and not L[j].strip().startswith(('loop_', '_', '#')):
                    f = L[j].split()
                    if len(f) >= len(hdr):
                        q = float(f[ix['_atom_site_charge']]) if '_atom_site_charge' in ix else None
                        atoms.append((f[ix.get('_atom_site_type_symbol', 0)], float(f[ix['_atom_site_fract_x']].split('(')[0]),
                                      float(f[ix['_atom_site_fract_y']].split('(')[0]), float(f[ix['_atom_site_fract_z']].split('(')[0]), q))
                    j += 1
            i = j
        else:
            i += 1
    return cell, atoms


def cif_compare(a, b):
    ca, A = cif_atoms(a); cb, B = cif_atoms(b)
    if len(A) != len(B): return dict(n=(len(A), len(B)), same_n=False)
    d = 0.0
    for x, y in zip(A, B):
        for k in (1, 2, 3):
            dd = abs(x[k] - y[k]); dd = min(dd, 1 - dd); d = max(d, dd)
    return dict(n=len(A), same_n=True, symbols_same=all(x[0] == y[0] for x, y in zip(A, B)), frac_max_diff=d,
                cell_max_diff=max(abs(ca.get(k, 0) - cb.get(k, 0)) for k in set(ca) | set(cb)) if ca and cb else None,
                qsum_a=sum(x[4] for x in A) if A and A[0][4] is not None else None,
                qsum_b=sum(x[4] for x in B) if B and B[0][4] is not None else None)


# ---------------------------------------------------------------- S_mix raw rows
def mix_rows_tj1(rel, prefix, versions_label):
    d = J(rel)
    out = []
    for r in d['rows']:
        if not r.get('name', '').startswith(prefix): continue
        s, e = smix_of(r['N_CO2'], r['N_CO2_err'], r['N_N2'], r['N_N2_err'])
        out.append(dict(file=rel, name=r['name'], seed=r['seed'], status=r['status'], returncode=r.get('returncode'),
                        ff_md5_ok=r.get('ff_md5') == FF, finished_field=r.get('finished'), cif=r.get('cif'),
                        unit_cells=r.get('unit_cells'), N_CO2=r['N_CO2'], N_CO2_err=r['N_CO2_err'], N_N2=r['N_N2'], N_N2_err=r['N_N2_err'],
                        S=s, S_err=e, stored_S=r.get('S_mix'), stored_err=r.get('S_mix_err'),
                        stored_match=abs(s - r['S_mix']) < 1e-6 * s and abs(e - r['S_mix_err']) < 1e-6 * e,
                        minutes=r.get('minutes'), version=versions_label, blocked=False))
    return d, out


def mix_rows_blocked(rel, tag, acc):
    d = J(rel)
    out = []
    for r in d['rows']:
        s, e = smix_of(r['N_CO2'], r['N_CO2_err'], r['N_N2'], r['N_N2_err'])
        ncell = math.prod(r['unit_cells'])
        eq = dict(CO2=(r['n_expected']['CO2'], acc['spheres_1.65'], ncell, r['block']['CO2']['n_blocked'], r['block']['CO2']['blocked_line']),
                  N2=(r['n_expected']['N2'], acc['spheres_1.82'], ncell, r['block']['N2']['n_blocked'], r['block']['N2']['blocked_line']))
        eq_ok = all(v[0] == v[1] * v[2] == v[3] and v[4] for v in eq.values())
        out.append(dict(file=rel, name=f'{tag}_s{r["seed_idx"]}', seed=r['seed'], status=r['status'], judge=r.get('judge'),
                        returncode=r.get('returncode'), ff_md5_ok=d.get('ff_md5') == FF, final=d.get('final'),
                        stderr_not_found=r.get('stderr_not_found'), data=r.get('data'), unit_cells=r['unit_cells'],
                        N_CO2=r['N_CO2'], N_CO2_err=r['N_CO2_err'], N_N2=r['N_N2'], N_N2_err=r['N_N2_err'],
                        S=s, S_err=e, stored_S=r['S_mix'], stored_err=r['S_mix_err'],
                        stored_match=abs(s - r['S_mix']) < 1e-6 * s and abs(e - r['S_mix_err']) < 1e-6 * e,
                        blocking_eq={k: dict(n_expected=v[0], spheres=v[1], cells=v[2], n_blocked=v[3], blocked_line=v[4]) for k, v in eq.items()},
                        blocking_eq_ok=eq_ok, minutes=r.get('minutes'), version='v3 charged_v3 (blocked mix, Junseok)', blocked=True))
    return d, out


def attach_rundir(rows, rundir_glob):
    for r in rows:
        dd = sorted(glob.glob(os.path.join(Z, rundir_glob.format(name=r['name']))))
        if not dd:
            r['rundir'] = None; continue
        d = dd[0]; r['rundir'] = os.path.relpath(d, P)
        datas = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
        r['n_data'] = len(datas)
        if len(datas) == 1:
            pd = parse_data(datas[0])
            r['raspa'] = pd
            mk = pd['molkg']
            r['raspa_match'] = dict(seed=pd['seed'] == r['seed'],
                                    CO2=mk.get('CO2') is not None and len(mk['CO2']) == 1 and abs(mk['CO2'][0][0] - r['N_CO2']) < 1e-9 and abs(mk['CO2'][0][1] - r['N_CO2_err']) < 1e-9,
                                    N2=mk.get('N2') is not None and len(mk['N2']) == 1 and abs(mk['N2'][0][0] - r['N_N2']) < 1e-9 and abs(mk['N2'][0][1] - r['N_N2_err']) < 1e-9)
        si = os.path.join(d, 'simulation.input')
        if os.path.exists(si): r['sim_input'] = sim_input(si)
        cifs = glob.glob(os.path.join(d, '*.cif'))
        if cifs:
            r['rundir_cif_md5'] = md5(cifs[0])
            ref = os.path.join(Z, 'charged_v3', os.path.basename(cifs[0]))
            r['charged_v3_cif_md5'] = md5(ref) if os.path.exists(ref) else None
            r['rundir_cif_same_as_charged_v3'] = r['rundir_cif_md5'] == r['charged_v3_cif_md5']


def agg(rows):
    v = [r['S'] for r in rows]; e = [r['S_err'] for r in rows]; k = len(v)
    m = st.mean(v); eb = st.mean(e)
    sd = st.stdev(v) if k > 1 else None
    seeds = [r['seed'] for r in rows]
    return dict(k=k, mean=m, mean_err_bar=eb, pm=eb / math.sqrt(k), seed_SD=sd, seed_SEM=sd / math.sqrt(k) if sd else None,
                each=v, each_err=e, seeds=seeds, seeds_unique=len(set(seeds)) == k, N_CO2_mean=st.mean(r['N_CO2'] for r in rows),
                N_N2_mean=st.mean(r['N_N2'] for r in rows))


def units(a, b):
    d = a['mean'] - b['mean']
    def q(x, y): return d / math.sqrt(x * x + y * y) if (x or y) else float('inf')
    r_reg = q(a['pm'], b['pm'])
    r_sem = q(a['seed_SD'] / math.sqrt(a['k']), b['seed_SD'] / math.sqrt(b['k']))
    r_sd = q(a['seed_SD'], b['seed_SD'])
    return dict(diff=d, reg_units=r_reg, seed_SEM_ruler=r_sem, seed_SD_ruler_batch_unit=r_sd, seed_SEM95_ruler=r_sem / T95_4,
                reg_ranked=abs(r_reg) >= 1.5, SEM_ranked=abs(r_sem) >= 1.5, SD_ranked=abs(r_sd) >= 1.5)


# ================================================================ main
OUT = dict(made=datetime.datetime.now().isoformat(timespec='seconds'), repo_head=git('rev-parse', 'HEAD'),
           repo_status_tracked_dirty=git('status', '--porcelain', '--untracked-files=no', '--', '21_ZIF69_MTV', '23_SCREENING'),
           conventions=dict(per_run_pm='RASPA 95% CI (2.776*SEM of 5 blocks) - checked from .data where present',
                            S_mix='(N_CO2/N_N2)/(0.15/0.85), rel errors in quadrature',
                            mean_pm='mean(per-run pm)/sqrt(k)  [registered "units" ruler]',
                            rulers=dict(reg_units='d/sqrt(pm1^2+pm2^2), pm = pm_bar/sqrt(k)',
                                        seed_SEM_ruler='d/sqrt(SD1^2/k1+SD2^2/k2)  [verdict 26-2 corrected name "씨앗 SEM 자"; FOLLOWUP d\' and E24I_SEEDS_REG d\' call this "씨앗 SD 자"]',
                                        seed_SD_ruler_batch_unit='d/sqrt(SD1^2+SD2^2)  [verdict 26-2 corrected "씨앗 SD 자" = CLAUDE.md batch unit, E-23 배치 단위]',
                                        seed_SEM95_ruler='seed_SEM_ruler/2.776  [E24I_SEEDS_REGISTRATION "95 % 척도 씨앗 산포" 1.21~1.25]')))

# ---------- access (pockets) for blocking equations
acc_all = J('results_e24i_access_junseok.json')['summary']
OUT['access'] = {t: acc_all[KEY[t]] for t in TAGS}

# ---------- S_mix raw rows per structure
MIX = {}
_, MIX['cn_s123'] = mix_rows_tj1('results_e24i_e24i_cn_open_mix_hkhome.json', 'e24i_cn_open_s', 'v3 charged_v3 (open site)')
_, MIX['cn_s456'] = mix_rows_tj1('results_e24i_e24i_cn_open_mix_s456_hkhome.json', 'e24i_cn_open_s', 'v3 charged_v3 (open site)')
_, MIX['br_s123'] = mix_rows_tj1('results_e24i_e24i_br_open_mix_laptop2.json', 'e24i_br_open_s', 'v3 charged_v3 (open site)')
_, MIX['br_s456'] = mix_rows_tj1('results_e24i_e24i_br_open_mix_s456_hkhome.json', 'e24i_br_open_s', 'v3 charged_v3 (open site)')
_, MIX['cl_s123'] = mix_rows_tj1('results_e24i_e24i_cl_open_mix_junseok.json', 'e24i_cl_open_s', 'v3 charged_v3 (open site)')
_, MIX['ch3_s123'] = mix_rows_tj1('results_e24i_e24i_ch3_open_mix_laptop2.json', 'e24i_ch3_open_s', 'v3 charged_v3 (open site)')
c2d, MIX['c2h5_s123'] = mix_rows_blocked('results_e24i_e24i_c2h5_open_mix_junseok.json', 'e24i_c2h5_open', acc_all['e24i_c2h5_open'])
OUT['c2h5_mix_file_summary_block'] = c2d.get('summary')
_, MIX['parent_s123'] = mix_rows_tj1('results_e23_mix_desktop.json', 'e22_parent_s', 'v3 charged_v3 (parent, E-23 desktop)')
# all rows in each file (check nothing else hides in the files the ranking glob reads)
for rel in ['results_e24i_e24i_cn_open_mix_hkhome.json', 'results_e24i_e24i_cn_open_mix_s456_hkhome.json',
            'results_e24i_e24i_br_open_mix_laptop2.json', 'results_e24i_e24i_br_open_mix_s456_hkhome.json',
            'results_e24i_e24i_cl_open_mix_junseok.json', 'results_e24i_e24i_ch3_open_mix_laptop2.json',
            'results_e24i_e24i_c2h5_open_mix_junseok.json']:
    d = J(rel)
    OUT.setdefault('mix_file_row_inventory', {})[rel] = dict(n_rows=len(d['rows']), names=[r.get('name') for r in d['rows']],
                                                            statuses=[r.get('status') for r in d['rows']], cifs=sorted({str(r.get('cif')) for r in d['rows']}),
                                                            note=d.get('note') if isinstance(d.get('note'), str) else None)
OUT['ranking_glob_matches'] = {t: sorted(os.path.basename(f) for f in glob.glob(os.path.join(Z, f'results_e24i_e24i_{t}_open_mix_*.json'))) for t in TAGS}
OUT['other_e24i_mix_files'] = sorted(os.path.basename(f) for f in glob.glob(os.path.join(Z, 'results_e24i_*mix*.json')))

# run directories (only on HKHOME for CN s1-6, Br s4-6, parent s1-3)
attach_rundir(MIX['cn_s123'], 'e24i_mix_runs_e24i_cn_open/mix_{name}')
attach_rundir(MIX['cn_s456'], 'e24i_mix_runs_e24i_cn_open_s456/mix_{name}')
attach_rundir(MIX['br_s456'], 'e24i_mix_runs_e24i_br_open_s456/mix_{name}')
attach_rundir(MIX['parent_s123'], 'e23_mix_runs/mix_{name}')
for k in ('br_s123', 'cl_s123', 'ch3_s123', 'c2h5_s123'):
    for r in MIX[k]: r['rundir'] = None
OUT['mix_rows'] = MIX

# seeds across everything
allseeds = [(k, r['name'], r['seed']) for k, v in MIX.items() for r in v]
cnt = {}
for k, n, s in allseeds: cnt.setdefault(s, []).append(f'{k}:{n}')
OUT['seed_collisions_all_mix_rows'] = {str(s): v for s, v in cnt.items() if len(v) > 1}

# ---------- aggregates in two versions
V3 = dict(cn=agg(MIX['cn_s123']), br=agg(MIX['br_s123']), c2h5=agg(MIX['c2h5_s123']), cl=agg(MIX['cl_s123']), ch3=agg(MIX['ch3_s123']),
          parent=agg(MIX['parent_s123']))
V6 = dict(V3); V6['cn'] = agg(MIX['cn_s123'] + MIX['cn_s456']); V6['br'] = agg(MIX['br_s123'] + MIX['br_s456'])
NEW3 = dict(cn=agg(MIX['cn_s456']), br=agg(MIX['br_s456']))
OUT['smix_verdict_version_3seed'] = V3
OUT['smix_ranking_version_6seed_cn_br'] = V6
OUT['smix_new_s456_only'] = NEW3
OUT['old3_vs_new3_consistency'] = {t: dict(diff=NEW3[t]['mean'] - V3[t]['mean'],
                                           in_pm3_units=(NEW3[t]['mean'] - V3[t]['mean']) / math.hypot(NEW3[t]['pm'], V3[t]['pm']),
                                           in_seedSEM_units=(NEW3[t]['mean'] - V3[t]['mean']) / math.hypot(NEW3[t]['seed_SEM'], V3[t]['seed_SEM'])) for t in ('cn', 'br')}

# ---------- mslm050 (6 realizations: e0 = mean of 3 seeds of one CIF, e1..e5 one seed each on different CIFs)
tj = J('results_tj1_mix_laptop.json'); e21 = J('results_e21b_mix_junseok.json'); e23 = J('results_e23_mix_junseok.json')
def rr(r, src):
    s, e = smix_of(r['N_CO2'], r['N_CO2_err'], r['N_N2'], r['N_N2_err'])
    cif = os.path.join(Z, r['cif'])
    return dict(file=src, name=r['name'], seed=r['seed'], cif=r['cif'], cif_md5=md5(cif) if os.path.exists(cif) else None,
                status=r['status'], returncode=r.get('returncode'), ff_md5_ok=r.get('ff_md5') == FF, S=s, S_err=e,
                stored_match=abs(s - r['S_mix']) < 1e-6 * s)
e0 = [rr(r, 'results_tj1_mix_laptop.json') for r in tj['rows'] if r.get('name') == 'mslm050'] + \
     [rr(r, 'results_e21b_mix_junseok.json') for r in e21['rows'] if r['name'].startswith('mslm050_s')]
eN = [rr(r, 'results_e23_mix_junseok.json') for r in e23['rows'] if r['name'].startswith('mslm050e')]
real = [dict(realization='e0', cif=e0[0]['cif'], S=st.mean(x['S'] for x in e0), S_err=st.mean(x['S_err'] for x in e0) / math.sqrt(3),
             n_seeds=3, seed_SD=st.stdev(x['S'] for x in e0))] + [dict(realization=x['name'], cif=x['cif'], S=x['S'], S_err=x['S_err'], n_seeds=1) for x in eN]
ms = dict(k_realizations=6, n_runs=len(e0) + len(eN), mean=st.mean(x['S'] for x in real), pm=st.mean(x['S_err'] for x in real) / math.sqrt(6),
          pm_if_e0_err_not_div_sqrt3=(st.mean(x['S_err'] for x in e0) + sum(x['S_err'] for x in eN)) / 6 / math.sqrt(6),
          realization_SD=st.stdev(x['S'] for x in real), runs=e0 + eN, realizations=real,
          seeds_unique=len({x['seed'] for x in e0 + eN}) == len(e0 + eN))
OUT['mslm050'] = ms

# ---------- Widom S_Henry
def widom(rel):
    d = J(rel)
    R = {r['charges']: r for r in d['rows']}
    on, off = R['on'], R['off']
    S = on['KH_CO2'] / on['KH_N2']; Se = S * math.hypot(on['KH_CO2_err'] / on['KH_CO2'], on['KH_N2_err'] / on['KH_N2'])
    So = off['KH_CO2'] / off['KH_N2']
    return dict(file=rel, finished=d.get('finished'), ff_md5_ok=d.get('ff_md5') == FF, cif=d.get('cif'), host=d.get('host'),
                S_ON=S, S_ON_err=Se, stored_match=abs(S - on['selectivity']) < 1e-6 * S and abs(Se - on['selectivity_err']) < 1e-3 * Se,
                KH_CO2=on['KH_CO2'], KH_CO2_err=on['KH_CO2_err'], KH_N2=on['KH_N2'], KH_N2_err=on['KH_N2_err'],
                S_OFF=So, G=S / So, status=[(r['charges'], r['status_CO2'], r['status_N2']) for r in d['rows']])
WID = {}
for t in TAGS:
    f = sorted(glob.glob(os.path.join(Z, f'results_magi5_e3_e24i_{t}_open_widom_*.json')))
    WID[t] = widom(os.path.basename(f[0])); WID[t]['n_files_matching'] = len(f)
WID['parent'] = widom('results_magi5_e3_e22_parent_widom_desktop-js1ib6u.json')
bp = J('results_e24i_blockpockets_hkhome.json')
e = bp['per_structure']['e24i_c2h5_open']; R = e['rows']
Sb = R['on_CO2@1.65']['KH'] / R['on_N2@1.82']['KH']
Sbe = Sb * math.hypot(R['on_CO2@1.65']['KH_err'] / R['on_CO2@1.65']['KH'], R['on_N2@1.82']['KH_err'] / R['on_N2@1.82']['KH'])
Sbo = R['off_CO2@1.65']['KH'] / R['off_N2@1.82']['KH']
WID['c2h5_blocked'] = dict(file='results_e24i_blockpockets_hkhome.json', S_ON=Sb, S_ON_err=Sbe, S_OFF=Sbo, G=Sb / Sbo,
                           KH_CO2=R['on_CO2@1.65']['KH'], KH_CO2_err=R['on_CO2@1.65']['KH_err'],
                           stored_match=abs(Sb - e['S_ON_blocked']) < 1e-6 * Sb, all_ok=bp.get('all_ok'), seeds_distinct=bp.get('seeds_distinct'),
                           finished=bp.get('finished'), coords_vs_charged=e.get('coords'),
                           rows_gate={k: dict(status=v['status'], marker_finished=v['marker_finished'], blocked_line=v['pockets_blocked_line'],
                                              not_found=v['stderr_not_found'], n_blocked=v['n_blocked_reported'], n_expected=v['n_expected'],
                                              eq=v['n_blocked_reported'] == v['n_expected'] == v['n_spheres_per_uc'] * math.prod(v['unit_cells'])) for k, v in R.items()})
# bp run dir markers + block files
bpm = {}
for sub in sorted(glob.glob(os.path.join(Z, 'e24i_bp_runs', 'e24i_c2h5_open', '*'))):
    ds = glob.glob(os.path.join(sub, 'Output', 'System_0', '*.data'))
    blk = glob.glob(os.path.join(sub, '*.block'))
    bpm[os.path.basename(sub)] = dict(finished_count=sum(open(x, errors='ignore').read().count('Simulation finished') for x in ds),
                                      block_file_md5=md5(blk[0]) if blk else None, block_first_line=open(blk[0]).readline().strip() if blk else None)
WID['c2h5_blocked']['rundirs'] = bpm
OUT['widom'] = WID

# ---------- retention S_mix/S_Henry, both versions, and both C2H5 S_Henry choices
def ret(m, e, S, Se): return dict(ratio=m / S, err=m / S * math.hypot(e / m, Se / S))
OUT['retention'] = {}
for ver, V in (('verdict_3seed', V3), ('ranking_6seed', V6)):
    OUT['retention'][ver] = {t: ret(V[t]['mean'], V[t]['pm'], WID[t]['S_ON'], WID[t]['S_ON_err']) for t in TAGS}
    OUT['retention'][ver]['parent'] = ret(V['parent']['mean'], V['parent']['pm'], WID['parent']['S_ON'], WID['parent']['S_ON_err'])
    OUT['retention'][ver]['c2h5_with_blocked_SHenry'] = ret(V['c2h5']['mean'], V['c2h5']['pm'], Sb, Sbe)
OUT['retention']['mslm050_v3_selectivity'] = None
v3 = {r['name']: r for r in J('results_v3.json')['rows']}
OUT['retention']['mslm050_v3_selectivity'] = dict(S_Henry=v3['mslm050']['selectivity'], S_Henry_err=v3['mslm050']['selectivity_err'],
                                                  **ret(ms['mean'], ms['pm'], v3['mslm050']['selectivity'], v3['mslm050']['selectivity_err']))

# ---------- pairwise units
PAIRS = [('cn', 'br'), ('br', 'c2h5'), ('c2h5', 'cl'), ('cl', 'ch3'), ('br', 'cl'), ('br', 'ch3'), ('cl', 'c2h5'), ('ch3', 'c2h5'),
         ('cn', 'parent'), ('br', 'parent'), ('c2h5', 'parent'), ('cl', 'parent'), ('ch3', 'parent')]
OUT['pairwise'] = {ver: {f'{a}-{b}': units(V[a], V[b]) for a, b in PAIRS} for ver, V in (('verdict_3seed', V3), ('ranking_6seed', V6))}
msA = dict(mean=ms['mean'], pm=ms['pm'], seed_SD=ms['realization_SD'], k=6)
OUT['pairwise']['vs_mslm050_ranking'] = {t: units(V6[t], msA) for t in ('cn', 'br', 'parent')}
OUT['ratio_vs_mslm050'] = {ver: {t: V[t]['mean'] / ms['mean'] for t in ('cn', 'br', 'parent')} for ver, V in (('verdict_3seed', V3), ('ranking_6seed', V6))}

# ---------- gate 5
g5 = J('results_e24i_gate5_desktop-nvsrr9m.json'); g22 = J('results_e22b_gate5_hkhome.json')
REF = g22['rows']['e22_parent']['after']['LCD']
G5 = dict(LCD_ref=REF, LCD_ref_in_file=g5.get('LCD_ref_family'), rule='drop=(LCD_ref_parent_after - LCD_after)/LCD_ref*100 < 20 (risk_screen.py:414-423; PLD & AV checks use BEFORE structure m0)', rows={})
for k, r in list(g5['rows'].items()) + [('e22_parent', g22['rows']['e22_parent'])]:
    a, b = r['after'], r['before']
    drop = (REF - a['LCD']) / REF * 100
    G5['rows'][k] = dict(status=r['status'], pass_stored=r.get('pass'), checks=r.get('checks'), LCD_before=b['LCD'], LCD_after=a['LCD'],
                         drop_vs_ref_pct=drop, drop_stored=r.get('LCD_drop_pct'), drop_match=abs(round(drop, 2) - r.get('LCD_drop_pct')) < 0.006,
                         drop_vs_own_before_pct=(b['LCD'] - a['LCD']) / b['LCD'] * 100, gate5_LCD_ok=drop < 20,
                         PLD_before=b['PLD'], PLD_after=a['PLD'], AV_per_cell_before=b.get('AV_per_cell'), AV_per_cell_after=a.get('AV_per_cell'),
                         final_EDiff=r.get('final_EDiff'), outer_loops=r.get('outer_loops'), converged_1e4=(r.get('final_EDiff') or 9) < 1e-4,
                         PLD_after_below_3p3=a['PLD'] < 3.3)
OUT['gate5'] = G5

# ---------- structure/version joins: every input CIF path, charged_v3 vs relax_tnf coords
joins = {}
for t in TAGS + ['parent']:
    tag = 'e22_parent' if t == 'parent' else KEY[t]
    cv = os.path.join(Z, 'charged_v3', f'{tag}_DDEC6.cif'); rx = os.path.join(Z, 'relax_tnf', f'{tag}_relaxed.cif')
    rows = MIX[f'{t}_s123'] + (MIX.get(f'{t}_s456') or [])
    joins[t] = dict(mix_cifs=sorted({str(r.get('cif') or r.get('data')) for r in rows}),
                    widom_cif=WID[t]['cif'], charged_v3_md5=md5(cv), charged_v3_git_log=git('log', '--format=%h %ad', '--date=iso', '--', os.path.relpath(cv, P)).splitlines(),
                    charged_v3_vs_relax_tnf=cif_compare(cv, rx) if os.path.exists(rx) else None,
                    any_e24_100_or_non_open=any(('_100' in str(r.get('cif'))) or ('open' not in str(r.get('cif') or r.get('data')) and t != 'parent') for r in rows))
OUT['structure_joins'] = joins

# ---------- water index (dry Widom water / CO2)
wtr = J('results_e24i_water_hkhome.json'); wb = J('results_e24i_c2h5_open_water_blk_junseok.json'); wp = J('results_e22c_water_hkhome.json')
WI = {}
def windex(ok, KH, KHe):
    k = [r['KH_water'] for r in ok]; m = st.mean(k); me = st.mean(r['KH_water_err'] for r in ok) / 2
    i = m / KH
    return dict(n=len(ok), seeds=[r['seed'] for r in ok], seeds_unique=len({r['seed'] for r in ok}) == len(ok), idx=i, err=i * math.hypot(me / m, KHe / KH))
for t in TAGS:
    ok = [r for r in wtr['rows'] if r['name'] == KEY[t] and r['status'] == 'ok' and r.get('marker_finished') and r.get('header_gate_ok') and r.get('water_sites_in_rundir') == 5]
    WI[t + '_unblocked'] = windex(ok, WID[t]['KH_CO2'], WID[t]['KH_CO2_err'])
okb = [r for r in wb['rows'] if abs(r.get('block_radius', 0) - 1.3) < 1e-6 and r['status'] == 'ok' and r.get('marker_finished') and r.get('block', {}).get('blocked_line')
       and r['block']['n_blocked'] == r['n_expected']]
WI['c2h5_blocked'] = windex(okb, R['on_CO2@1.65']['KH'], R['on_CO2@1.65']['KH_err'])
WI['c2h5_blocked']['n_expected'] = sorted({r['n_expected'] for r in okb}); WI['c2h5_blocked']['spheres_1.30'] = acc_all['e24i_c2h5_open']['spheres_1.30']
WI['c2h5_blocked']['eq_ok'] = all(r['n_expected'] == acc_all['e24i_c2h5_open']['spheres_1.30'] * math.prod(r['unit_cells']) for r in okb)
okp = [r for r in wp['rows'] if r['name'] == 'e22_parent' and r['status'] == 'ok']
WI['parent'] = windex(okp, WID['parent']['KH_CO2'], WID['parent']['KH_CO2_err'])
ws = [(r['name'], r['seed']) for r in wtr['rows']]
WI['e24i_water_file_seed_dups'] = [[n for n, s in ws if s == x] for x in {s for _, s in ws} if sum(1 for _, s in ws if s == x) > 1]
wrd = {}
for d_ in sorted(glob.glob(os.path.join(Z, 'e24i_water_runs', 'widom_water_*'))):
    ds = glob.glob(os.path.join(d_, 'Output', 'System_0', '*.data'))
    wrd[os.path.basename(d_)] = sum(open(x, errors='ignore').read().count('Simulation finished') for x in ds)
WI['hkhome_water_rundir_finished_counts'] = wrd
OUT['water_index'] = WI

# ---------- humid TSA working capacity
HW = {}
def humid(rel, stem, summ_rel):
    d = J(rel)
    rows = [r for r in d['rows'] if r['name'].startswith(stem + '_h')]
    each = []
    for r in rows:
        L = r['loadings']; wc = r['working_capacity']
        t = L['ads']['CO2']['mol_per_kg'] - L['tsa']['CO2']['mol_per_kg']
        te = math.hypot(L['ads']['CO2']['err'], L['tsa']['CO2']['err'])
        v = L['ads']['CO2']['mol_per_kg'] - L['vsa']['CO2']['mol_per_kg']
        each.append(dict(name=r['name'], tsa=t, tsa_err=te, tsa_stored=wc['tsa']['value'], tsa_err_stored=wc['tsa']['err'],
                         tsa_match=abs(t - wc['tsa']['value']) < 6e-5 and abs(te - wc['tsa']['err']) < 6e-5, vsa=v, vsa_stored=wc['vsa']['value'],
                         ads_CO2=L['ads']['CO2']['mol_per_kg'], ads_water=L['ads']['water']['mol_per_kg'], ads_water_err=L['ads']['water']['err'],
                         tsa_CO2=L['tsa']['CO2']['mol_per_kg']))
    k = len(each)
    out = dict(file=rel, k=k, tsa_mean=st.mean(x['tsa'] for x in each), tsa_pm=st.mean(x['tsa_err'] for x in each) / math.sqrt(k),
               tsa_SD=st.stdev(x['tsa'] for x in each), tsa_each=[x['tsa'] for x in each], vsa_mean=st.mean(x['vsa'] for x in each),
               ads_CO2_mean=st.mean(x['ads_CO2'] for x in each), ads_water_mean=st.mean(x['ads_water'] for x in each),
               ads_water_each=[x['ads_water'] for x in each], tsa_CO2_mean=st.mean(x['tsa_CO2'] for x in each), rows=each)
    if summ_rel:
        a = J(summ_rel)
        seeds = [x['seed'] for x in a.get('audit', [])]
        out['audit'] = dict(file=summ_rel, audit_summary=a.get('audit_summary'), blocking=a.get('blocking'),
                            all_finished=all(x.get('finished') for x in a.get('audit', [])), all_rc0=all(x.get('returncode') == 0 for x in a.get('audit', [])),
                            not_found_any=any(x.get('stderr_not_found') for x in a.get('audit', [])), seeds=seeds, seeds_unique=len(set(seeds)) == len(seeds),
                            n_blocked=[(x['condition'], x['block']['CO2']['n_blocked'], x['block']['water']['n_blocked']) for x in a.get('audit', [])])
    else:
        out['audit'] = None
    return out
HW['parent'] = humid('v3w_humid_wc/humid_working_capacity_w2_e22parent_laptop.json', 'e22_parent', None)
for t, m in (('cn', 'junseok'), ('br', 'hkhome'), ('cl', 'junseok'), ('cl', 'laptop2'), ('ch3', 'laptop'), ('c2h5', 'junseok')):
    HW[f'{t}_{m}'] = humid(f'v3w_humid_wc/humid_working_capacity_w2_{KEY[t]}_{m}.json', KEY[t], f'results_e24i_{KEY[t]}_humid_summary_{m}.json')
par = HW['parent']
for k, v in HW.items():
    if k == 'parent': continue
    d = v['tsa_mean'] - par['tsa_mean']
    v['vs_parent'] = dict(diff=d, reg_units=d / math.hypot(v['tsa_pm'], par['tsa_pm']), seed_SEM_ruler=d / math.hypot(v['tsa_SD'] / math.sqrt(3), par['tsa_SD'] / math.sqrt(3)),
                          seed_SD_ruler=d / math.hypot(v['tsa_SD'], par['tsa_SD']))
HW['cl_junseok_vs_laptop2_units'] = (HW['cl_junseok']['tsa_mean'] - HW['cl_laptop2']['tsa_mean']) / math.hypot(HW['cl_junseok']['tsa_pm'], HW['cl_laptop2']['tsa_pm'])
hrd = {}
for d_ in sorted(glob.glob(os.path.join(Z, 'humid_wc_runs_v3w', '*_e24i_br_open_h*'))):
    ds = glob.glob(os.path.join(d_, 'Output', 'System_0', '*.data'))
    pdd = parse_data(ds[0]) if len(ds) == 1 else None
    hrd[os.path.basename(d_)] = dict(n_data=len(ds), finished_count=pdd['finished_count'] if pdd else None, seed=pdd['seed'] if pdd else None,
                                     molkg=pdd['molkg'] if pdd else None)
    cond, hname = os.path.basename(d_).split('_', 1)
    row = next((x for x in json.load(open(os.path.join(Z, HW['br_hkhome']['file'])))['rows'] if x['name'] == hname), None)
    if row and pdd:
        hrd[os.path.basename(d_)]['json_match'] = all(abs(pdd['molkg'][c][0][0] - row['loadings'][cond][c]['mol_per_kg']) < 1e-9 for c in ('CO2', 'water'))
    hrd[os.path.basename(d_)]['seed_in_audit'] = pdd['seed'] in HW['br_hkhome']['audit']['seeds'] if pdd else None
HW['br_hkhome_rundirs'] = hrd
OUT['humid_wc'] = HW

# ---------- doc claims (for comparison only; never inputs)
CLAIMS = {
 'SMIX_G': dict(src='23_SCREENING/FINAL_RANKING_SMIX_20260930.md §G', rows={
   'cn': (6, 139.8, 4.0, 4.4, 116.6, 2.6, 1.20, 0.04), 'br': (6, 127.9, 2.9, 2.8, 127.6, 3.1, 1.00, 0.03),
   'c2h5': (3, 114.6, 6.9, 8.0, 154.3, 3.8, 0.74, 0.05), 'cl': (3, 111.2, 2.9, 4.7, 110.2, 1.5, 1.01, 0.03),
   'ch3': (3, 108.7, 3.9, 0.9, 128.2, 2.7, 0.85, 0.04), 'parent': (3, 75.4, 2.1, 0.4, 87.8, 1.2, 0.86, 0.03),
   'mslm050': (6, 39.7, 0.4, 3.4, 58.1, 1.7, 0.68, 0.02)}),
 'VERDICT_26_2': dict(src='21_ZIF69_MTV/MAGI5_E22_VERDICT_20260925.md §26-2', rows={
   'cn': (3, 141.53, 5.47, 5.25, 11.25, 1.21, 3.26), 'br': (3, 128.02, 5.05, 4.43, 9.59, 1.00, 2.84), 'cl': (3, 111.15, 2.95, 4.70, 9.80, 1.01, 2.98),
   'ch3': (3, 108.67, 3.87, 0.92, 7.51, 0.85, 2.84), 'c2h5': (3, 114.62, 6.92, 8.01, 5.41, 0.90, 1.48), 'parent': (3, 75.43, 2.14, 0.42, None, 0.86, 2.83)},
   pairs_reg={'br-cn': -1.82, 'br-c2h5': 1.56, 'br-cl': 2.89, 'br-ch3': 3.04, 'c2h5-parent': 5.41},
   pairs_SEM={'br-cn': -3.41, 'br-c2h5': 2.53, 'c2h5-parent': 8.47},
   pairs_SD={'cn-br': 1.97, 'br-c2h5': 1.46, 'br-cl': 2.61, 'br-ch3': 4.28, 'cl-ch3': 0.52, 'cl-c2h5': -0.37, 'ch3-c2h5': -0.74, 'cn-parent': 12.55, 'br-parent': 11.82}),
 'FOLLOWUP_6seed': dict(src='24_DISCUSSION_WORKFLOW/RUN_20260929-1521_FOLLOWUP.md 결정 2', cn=(139.77, 9.76, 3.99, 4.40), br=(127.92, 7.19, 2.94, 2.83), d=2.39, d_prime_called_seedSD=5.55,
                        old_new=dict(cn=-0.44, br=-0.03)),
 'FR_B_extra': dict(src='23_SCREENING/FINAL_RANKING_20260930.md §B (= ours_extra_20260930.json, hand-typed)',
                    rows={'cn': ('141.5 ± 5.5', 0.0276, 3.26, 2.40), 'br': ('128.0 ± 5.1', 0.0095, 2.84, 2.16), 'cl': ('111.2', 0.0113, 2.98, 2.31),
                          'ch3': ('108.7', 0.0121, 2.84, 2.17), 'c2h5': ('114.6', 0.0153, 1.48, 1.11), 'parent': ('75.4 ± 2.1', 0.0147, 2.83, 2.29), 'mslm050': ('39.7', 0.718, None, '0.74~0.81')}),
 'VERDICT_26_4_humid': dict(src='MAGI5_E22_VERDICT §26-4', rows={'cn_junseok': (2.401, 0.031, 0.048, 2.64, 3.89, 0.783, 3.31, 0.161), 'br_hkhome': (2.160, 0.027, 0.007, -3.52, None, 0.766, 2.94, 0.015),
                    'cl_junseok': (2.310, 0.018, 0.014, 0.51, None, 0.854, 3.11, 0.022), 'ch3_laptop': (2.171, 0.026, 0.020, -3.26, None, 0.856, 2.96, 0.026),
                    'c2h5_junseok': (1.107, 0.035, 0.012, -27.1, None, 0.396, 1.54, 0.027), 'cl_laptop2': (2.297, 0.019, 0.018, None, None, 0.840, None, None)}, parent=2.293,
                    cl_rep_units=0.49),
 'WATER_INDEX_26_2': dict(cn=(0.0276, 0.0019), br=(0.0095, 0.0003), cl=(0.0113, 0.0002), ch3=(0.0121, 0.0002), c2h5=(0.0153, 0.0005), parent=(0.0147, 0.0003)),
 'WIDOM_26': dict(ch3=(128.21, 2.70, 63.2, 2.03), br=(127.60, 3.10, 55.9, 2.28), cn=(116.59, 2.63, 53.6, 2.18), cl=(110.20, 1.54, 52.8, 2.09), c2h5_unblocked=154.34,
                  c2h5_blocked=(127.05, 3.99, 66.5, 1.91), parent=(87.80, 1.22)),
}
OUT['doc_claims'] = CLAIMS

# ---------- discrepancy table (computed - claimed)
disc = []
def chk(where, item, computed, claimed, tol):
    if claimed is None or computed is None: return
    disc.append(dict(where=where, item=item, computed=computed, claimed=claimed, diff=computed - claimed, flag=abs(computed - claimed) > tol))
for t, c in CLAIMS['SMIX_G']['rows'].items():
    if t == 'mslm050':
        chk('SMIX_G', 'mslm050 S_mix', ms['mean'], c[1], 0.05); chk('SMIX_G', 'mslm050 pm', ms['pm'], c[2], 0.05)
        chk('SMIX_G', 'mslm050 "seed SD" (is realization SD)', ms['realization_SD'], c[3], 0.05)
        chk('SMIX_G', 'mslm050 S_Henry', v3['mslm050']['selectivity'], c[4], 0.05)
        chk('SMIX_G', 'mslm050 retention', OUT['retention']['mslm050_v3_selectivity']['ratio'], c[6], 0.005)
        continue
    V = V6[t]
    chk('SMIX_G', f'{t} k', V['k'], c[0], 0); chk('SMIX_G', f'{t} S_mix', V['mean'], c[1], 0.05); chk('SMIX_G', f'{t} pm', V['pm'], c[2], 0.05)
    chk('SMIX_G', f'{t} seed SD', V['seed_SD'], c[3], 0.05); chk('SMIX_G', f'{t} S_Henry', WID[t]['S_ON'], c[4], 0.05)
    chk('SMIX_G', f'{t} S_Henry err', WID[t]['S_ON_err'], c[5], 0.05); chk('SMIX_G', f'{t} retention', OUT['retention']['ranking_6seed'][t]['ratio'], c[6], 0.005)
    chk('SMIX_G', f'{t} retention err', OUT['retention']['ranking_6seed'][t]['err'], c[7], 0.005)
chk('SMIX_G', 'c2h5 retention if blocked S_Henry used', OUT['retention']['ranking_6seed']['c2h5_with_blocked_SHenry']['ratio'], 0.74, 0.005)
for t, c in CLAIMS['VERDICT_26_2']['rows'].items():
    V = V3[t]
    chk('VERDICT_26_2', f'{t} S_mix', V['mean'], c[1], 0.005); chk('VERDICT_26_2', f'{t} pm', V['pm'], c[2], 0.005); chk('VERDICT_26_2', f'{t} seed SD', V['seed_SD'], c[3], 0.005)
    if c[4] is not None: chk('VERDICT_26_2', f'{t} vs parent reg units', OUT['pairwise']['verdict_3seed'][f'{t}-parent']['reg_units'], c[4], 0.005)
    r = OUT['retention']['verdict_3seed']['c2h5_with_blocked_SHenry' if t == 'c2h5' else t]['ratio']
    chk('VERDICT_26_2', f'{t} retention', r, c[5], 0.005); chk('VERDICT_26_2', f'{t} N_CO2', V['N_CO2_mean'], c[6], 0.005)
PW3 = OUT['pairwise']['verdict_3seed']
for k_, v in CLAIMS['VERDICT_26_2']['pairs_reg'].items():
    a, b = k_.split('-'); x = PW3.get(f'{a}-{b}') or {k2: -vv if isinstance(vv, float) else vv for k2, vv in PW3[f'{b}-{a}'].items()}
    chk('VERDICT_26_2 reg', k_, x['reg_units'], v, 0.005)
for k_, v in CLAIMS['VERDICT_26_2']['pairs_SEM'].items():
    a, b = k_.split('-'); x = PW3.get(f'{a}-{b}') or {k2: -vv if isinstance(vv, float) else vv for k2, vv in PW3[f'{b}-{a}'].items()}
    chk('VERDICT_26_2 SEM', k_, x['seed_SEM_ruler'], v, 0.005)
for k_, v in CLAIMS['VERDICT_26_2']['pairs_SD'].items():
    a, b = k_.split('-'); x = PW3.get(f'{a}-{b}') or {k2: -vv if isinstance(vv, float) else vv for k2, vv in PW3[f'{b}-{a}'].items()}
    chk('VERDICT_26_2 SD', k_, x['seed_SD_ruler_batch_unit'], v, 0.005)
F = CLAIMS['FOLLOWUP_6seed']
for t in ('cn', 'br'):
    chk('FOLLOWUP', f'{t} mean6', V6[t]['mean'], F[t][0], 0.005); chk('FOLLOWUP', f'{t} pm_bar', V6[t]['mean_err_bar'], F[t][1], 0.005)
    chk('FOLLOWUP', f'{t} e', V6[t]['pm'], F[t][2], 0.005); chk('FOLLOWUP', f'{t} SD', V6[t]['seed_SD'], F[t][3], 0.005)
    chk('FOLLOWUP', f'{t} old3->new3 (pm3 units)', OUT['old3_vs_new3_consistency'][t]['in_pm3_units'], F['old_new'][t], 0.005)
chk('FOLLOWUP', 'd (reg, 6 seeds)', OUT['pairwise']['ranking_6seed']['cn-br']['reg_units'], F['d'], 0.005)
chk('FOLLOWUP', "d' (named 씨앗 SD 자) vs SEM ruler", OUT['pairwise']['ranking_6seed']['cn-br']['seed_SEM_ruler'], F['d_prime_called_seedSD'], 0.005)
chk('FOLLOWUP', "d' (named 씨앗 SD 자) vs undivided SD ruler", OUT['pairwise']['ranking_6seed']['cn-br']['seed_SD_ruler_batch_unit'], F['d_prime_called_seedSD'], 0.005)
for t, c in CLAIMS['FR_B_extra']['rows'].items():
    if t == 'mslm050': continue
    try: smv = float(c[0].split(' ')[0])
    except ValueError: smv = None
    chk('FR_B_extra', f'{t} S_mix vs 3-seed', V3[t]['mean'], smv, 0.05); chk('FR_B_extra', f'{t} S_mix vs 6-seed (§G)', V6[t]['mean'], smv, 0.05)
    wi = WI['c2h5_blocked' if t == 'c2h5' else ('parent' if t == 'parent' else t + '_unblocked')]['idx']
    chk('FR_B_extra', f'{t} water idx', wi, c[1], 0.00005); chk('FR_B_extra', f'{t} dry N_CO2 vs 3-seed', V3[t]['N_CO2_mean'], c[2], 0.005)
    chk('FR_B_extra', f'{t} dry N_CO2 vs 6-seed', V6[t]['N_CO2_mean'], c[2], 0.005)
    hk = {'cn': 'cn_junseok', 'br': 'br_hkhome', 'cl': 'cl_junseok', 'ch3': 'ch3_laptop', 'c2h5': 'c2h5_junseok', 'parent': 'parent'}[t]
    chk('FR_B_extra', f'{t} humid TSA', HW[hk]['tsa_mean'], float(str(c[3]).split('(')[0]), 0.005)
for k_, c in CLAIMS['VERDICT_26_4_humid']['rows'].items():
    h = HW[k_]
    chk('VERDICT_26_4', f'{k_} WC_TSA', h['tsa_mean'], c[0], 0.0005); chk('VERDICT_26_4', f'{k_} pm', h['tsa_pm'], c[1], 0.0005)
    chk('VERDICT_26_4', f'{k_} SD', h['tsa_SD'], c[2], 0.0005)
    if c[3] is not None: chk('VERDICT_26_4', f'{k_} vs parent reg', h['vs_parent']['reg_units'], c[3], 0.006 if abs(c[3]) < 10 else 0.06)
    if c[4] is not None: chk('VERDICT_26_4', f'{k_} vs parent SEM', h['vs_parent']['seed_SEM_ruler'], c[4], 0.006)
    chk('VERDICT_26_4', f'{k_} VSA', h['vsa_mean'], c[5], 0.0006)
    if c[6] is not None: chk('VERDICT_26_4', f'{k_} ads CO2', h['ads_CO2_mean'], c[6], 0.006)
    if c[7] is not None: chk('VERDICT_26_4', f'{k_} ads water', h['ads_water_mean'], c[7], 0.0006)
chk('VERDICT_26_4', 'parent WC_TSA', HW['parent']['tsa_mean'], 2.293, 0.0005)
chk('VERDICT_26_4', 'Cl replicate units', HW['cl_junseok_vs_laptop2_units'], 0.49, 0.006)
for t, c in CLAIMS['WATER_INDEX_26_2'].items():
    w = WI['c2h5_blocked' if t == 'c2h5' else ('parent' if t == 'parent' else t + '_unblocked')]
    chk('WATER_26_2', f'{t} idx', w['idx'], c[0], 0.00005); chk('WATER_26_2', f'{t} idx err', w['err'], c[1], 0.00005)
for t, c in CLAIMS['WIDOM_26'].items():
    if t == 'c2h5_unblocked': chk('WIDOM_26', 'c2h5 unblocked S_ON', WID['c2h5']['S_ON'], c, 0.005); continue
    if t == 'c2h5_blocked':
        w = WID['c2h5_blocked']; chk('WIDOM_26', 'c2h5 blocked S_ON', w['S_ON'], c[0], 0.005); chk('WIDOM_26', 'c2h5 blocked err', w['S_ON_err'], c[1], 0.005)
        chk('WIDOM_26', 'c2h5 blocked S_OFF', w['S_OFF'], c[2], 0.05); chk('WIDOM_26', 'c2h5 blocked G', w['G'], c[3], 0.005); continue
    w = WID[t]; chk('WIDOM_26', f'{t} S_ON', w['S_ON'], c[0], 0.005); chk('WIDOM_26', f'{t} err', w['S_ON_err'], c[1], 0.005)
    if len(c) > 2: chk('WIDOM_26', f'{t} S_OFF', w['S_OFF'], c[2], 0.05); chk('WIDOM_26', f'{t} G', w['G'], c[3], 0.005)
OUT['discrepancies'] = disc
OUT['n_flagged'] = sum(1 for d in disc if d['flag'])
PW6 = OUT['pairwise']['ranking_6seed']
OUT['findings'] = [
 dict(id='F1', text='3-seed (s1-s3) recompute reproduces verdict 26-2 to 2 dp for all 6 rows; 6-seed (CN,Br s1-s6) reproduces SMIX G and FOLLOWUP. The CN/Br gap between versions comes only from s4-s6.',
      cn=(V3['cn']['mean'], V6['cn']['mean']), br=(V3['br']['mean'], V6['br']['mean'])),
 dict(id='F2', text='FOLLOWUP/E24I_SEEDS_REG d\' ("씨앗 SD 자") = SEM ruler; verdict-corrected "씨앗 SD 자" (undivided SD) gives a different number.',
      d_prime=PW6['cn-br']['seed_SEM_ruler'], undivided_SD_ruler=PW6['cn-br']['seed_SD_ruler_batch_unit'], SEM95=PW6['cn-br']['seed_SEM95_ruler'],
      three_seed=dict(reg=PW3['cn-br']['reg_units'], SEM=PW3['cn-br']['seed_SEM_ruler'], SD=PW3['cn-br']['seed_SD_ruler_batch_unit'], SEM95=PW3['cn-br']['seed_SEM95_ruler'])),
 dict(id='F3', text='C2H5 retention in SMIX G (0.74) and C2H5 S_Henry in FINAL_RANKING A\'/B (154.3, rank 1 of 3D) use the unblocked pocket-inclusive Widom; the gated (blocked) value is 127.05 and retention 0.90.',
      unblocked=WID['c2h5']['S_ON'], blocked=WID['c2h5_blocked']['S_ON'], ret_unblocked=OUT['retention']['ranking_6seed']['c2h5']['ratio'],
      ret_blocked=OUT['retention']['ranking_6seed']['c2h5_with_blocked_SHenry']['ratio']),
 dict(id='F4', text='FINAL_RANKING_20260930 B S_mix column (141.5 / 128.0) and dry N_CO2 3.26 are 3-seed (hand-typed ours_extra_20260930.json) while its own G section and SMIX G use 6-seed 139.8 / 127.9.'),
 dict(id='F5', text='Gate 5 LCD rule passes for all 5 + parent; 5 of 6 rows stopped at outer-loop cap 12 with EDiff>1e-4; CN after-relax AV/cell 0.0 & PLD 3.270<3.3 do not enter the gate (PLD/AV evaluated on BEFORE structure).'),
]
OUT['raw_file_md5'] = dict(sorted(FILES.items()))
json.dump(OUT, open(os.path.join(OUTD, 'baseline_recompute.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
print('written', os.path.join(OUTD, 'baseline_recompute.json'), 'files', len(FILES), 'flagged', OUT['n_flagged'], 'of', len(disc))
for d in disc:
    if d['flag']: print('  FLAG', d['where'], d['item'], 'computed %.4f claimed %.4f diff %+.4f' % (d['computed'], d['claimed'], d['diff']))
