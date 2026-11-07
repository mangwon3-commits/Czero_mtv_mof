import json, os
O = json.load(open(os.path.expanduser('~/.mof_magi/caspar_work/baseline_recompute.json')))
print('HEAD', O['repo_head'], 'dirty tracked:', repr(O['repo_status_tracked_dirty']))
for ver in ('smix_verdict_version_3seed', 'smix_ranking_version_6seed_cn_br', 'smix_new_s456_only'):
    print('\n==', ver)
    for t, v in O[ver].items():
        print(f"  {t:7s} k={v['k']} mean={v['mean']:.3f} pmbar={v['mean_err_bar']:.3f} pm={v['pm']:.3f} SD={v['seed_SD']:.3f} SEM={v['seed_SEM']:.3f} NCO2={v['N_CO2_mean']:.4f} uniq={v['seeds_unique']} seeds={v['seeds']} each={[round(x,2) for x in v['each']]}")
print('\nold3 vs new3', O['old3_vs_new3_consistency'])
print('\n== rows')
for k, rows in O['mix_rows'].items():
    for r in rows:
        ra = r.get('raspa')
        print(f"  {k:11s} {r['name']:18s} st={r['status']} rc={r.get('returncode')} ff={r['ff_md5_ok']} match={r['stored_match']} S={r['S']:.3f}±{r['S_err']:.3f} "
              f"min={r.get('minutes')} run={'Y' if r.get('rundir') else '-'} "
              + (f"fin={ra['finished_count']} warn={ra['warnings']} cyc={ra['cycles']}/{ra['init']} uc={ra['unit_cells']} q={ra['net_charge']} rmatch={r['raspa_match']} cif_same={r.get('rundir_cif_same_as_charged_v3')} "
                 f"CI={ {c: round(v['ratio'],4) for c, v in ra['ci_check'].items()} } inp={r['sim_input']['molfrac']},{r['sim_input']['P']},{r['sim_input']['T']},{r['sim_input']['block']}" if ra else '')
              + (f" blockeq={r.get('blocking_eq_ok')} judge={r.get('judge')} final={r.get('final')} nf={r.get('stderr_not_found')}" if r.get('blocked') else ''))
print('\nseed collisions', O['seed_collisions_all_mix_rows'])
print('glob', O['ranking_glob_matches'])
print('other mix files', O['other_e24i_mix_files'])
for f, v in O['mix_file_row_inventory'].items(): print('  inv', f, v['n_rows'], v['names'], v['statuses'], v['cifs'])
print('\n== pairwise')
for ver in ('verdict_3seed', 'ranking_6seed'):
    print(' ', ver)
    for k, v in O['pairwise'][ver].items():
        print(f"    {k:12s} d={v['diff']:+7.2f} reg={v['reg_units']:+6.2f} SEM={v['seed_SEM_ruler']:+6.2f} SD={v['seed_SD_ruler_batch_unit']:+6.2f} SEM95={v['seed_SEM95_ruler']:+6.2f}")
print('  vs mslm050', {k: {kk: round(vv, 2) for kk, vv in v.items() if isinstance(vv, float)} for k, v in O['pairwise']['vs_mslm050_ranking'].items()})
print('  ratio vs mslm050', O['ratio_vs_mslm050'])
print('\n== mslm050', {k: v for k, v in O['mslm050'].items() if k not in ('runs', 'realizations')})
print('\n== widom')
for k, v in O['widom'].items():
    print(f"  {k:13s} S_ON={v['S_ON']:.3f}±{v['S_ON_err']:.3f} S_OFF={v['S_OFF']:.2f} G={v['G']:.3f} match={v.get('stored_match')} fin={v.get('finished')} ff={v.get('ff_md5_ok')} cif={v.get('cif')} nf={v.get('n_files_matching')}")
print('  bp gate', O['widom']['c2h5_blocked']['rows_gate'], O['widom']['c2h5_blocked']['rundirs'], O['widom']['c2h5_blocked']['coords_vs_charged'])
print('\n== retention')
for ver in ('verdict_3seed', 'ranking_6seed'):
    print(' ', ver, {k: (round(v['ratio'], 3), round(v['err'], 3)) for k, v in O['retention'][ver].items()})
print('  mslm050', O['retention']['mslm050_v3_selectivity'])
print('\n== gate5', O['gate5']['LCD_ref'], O['gate5']['LCD_ref_in_file'])
for k, v in O['gate5']['rows'].items():
    print(f"  {k:15s} pass={v['pass_stored']} drop_ref={v['drop_vs_ref_pct']:.2f} stored={v['drop_stored']} own={v['drop_vs_own_before_pct']:.2f} PLD {v['PLD_before']:.3f}->{v['PLD_after']:.3f} AV/cell {v['AV_per_cell_before']}->{v['AV_per_cell_after']} EDiff={v['final_EDiff']:.3g} loops={v['outer_loops']} conv={v['converged_1e4']}")
print('\n== joins')
for k, v in O['structure_joins'].items(): print(' ', k, v)
print('\n== water index')
for k, v in O['water_index'].items():
    print(' ', k, v if not isinstance(v, dict) or 'idx' not in v else {kk: (round(vv, 6) if isinstance(vv, float) else vv) for kk, vv in v.items()})
print('\n== humid')
for k, v in O['humid_wc'].items():
    if isinstance(v, dict) and 'tsa_mean' in v:
        print(f"  {k:13s} k={v['k']} TSA={v['tsa_mean']:.4f}±{v['tsa_pm']:.4f} SD={v['tsa_SD']:.4f} each={[round(x,4) for x in v['tsa_each']]} VSA={v['vsa_mean']:.4f} adsCO2={v['ads_CO2_mean']:.4f} adsW={v['ads_water_mean']:.4f} {[round(x,4) for x in v['ads_water_each']]} tsaCO2={v['tsa_CO2_mean']:.3f} match={[r['tsa_match'] for r in v['rows']]} vsP={ {kk: round(vv,2) for kk,vv in v.get('vs_parent',{}).items()} }")
        if v['audit']: print('      audit', {kk: vv for kk, vv in v['audit'].items() if kk != 'n_blocked'}, v['audit']['n_blocked'])
    else:
        print(' ', k, v)
