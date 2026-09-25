# -*- coding: utf-8 -*-
"""E-8c 손 검토 적용 — 자동 풀이(MOFid 성분 배수)가 None 으로 남긴 행을 CIF 결합 환경(e8c_conn: COO⁻ · O–H · 물 · 에터 · CH₂/CH)과
조성 산수로 가려 값을 넣는다. 자동 값·근거는 auto_* 로 보존. 산화수: Zn/Cd/Co 2+."""
import json
import time
from collections import Counter

P = '/home/mangwon/mof_project/21_ZIF69_MTV/core_pop_formal_charge_junseok.json'
d = json.load(open(P, encoding='utf-8'))
MANUAL = {
    '2010_Zn__pts_3_ASR_1': (True, 'CIF 결합: COO⁻ 16(O–H 0) · CH₂ 8 · CH 8 = butane-1,2,3,4-tetracarboxylate⁴⁻ × 4 (C₈H₆O₈ × 4 = C₃₂H₂₄O₃₂ 원소 일치) · '
                             'Zn²⁺ × 4 = +8 − 16 = **−8** → 짝양이온 삭제(ASR). CoRE 메타 짝 없음(DOI 미상). E-1 의 Zn pts(G 4.92) 행.', 'high'),
    '2010_Zn__pts_3_FSR_1': (True, 'ASR_1 과 조성·결합 같음(COO⁻ 16 · CH₂ 8 · CH 8) → −8. FSR 에서도 짝양이온 없음.', 'high'),
    '2024_Zn__srs_3_FSR_1': (False, 'Zn₄C₂₈H₂₄N₁₆O₈ = purinate⁻(C₅H₃N₄) × 4 + acetate⁻(CH₃COO, CH₃ 4 · COO⁻ 4) × 4 + Zn²⁺ × 4 → +8 − 4 − 4 = 0. '
                             'H 24 = 12 + 12 로 purine 탈양성자 확인. MOFid 가 아세테이트를 빠뜨려 자동 풀이 실패. 사용자 결정표의 확인값(False)과 같음.', 'high'),
    '2024_Zn__srs_3_FSR_2': (False, 'FSR_1 과 같은 조성 Zn₄(pur)₄(OAc)₄ → 0.', 'high'),
    '2016_Co__sql_2_FSR_17': (False, 'Co + bdc²⁻(C₈H₄O₄) + H₂O + 나머지 C₆H₁₂N₂ = DABCO(중성, 이 계열 다른 행의 MOFid 에 있음) → Co²⁺ − 2 = 0. MOFid(ERROR)가 DABCO 를 빠뜨림.', 'high'),
    '2016_Co__sql_2_ASR_17': (False, 'CIF 결합: COO⁻ 2 · DABCO N(C3, Co 결합) 2 · CH₂ 6 → Co(bdc)(dabco) → 0. anion_removed 표지 행이지만 FSR_17 과의 차는 H₂O(중성).', 'high'),
    '2016_Cd__kgd_2_ASR_1': (False, 'MOFid 실패(no_mof). CIF 결합: COO⁻ 2 · Cd²⁺ → 0 — 단 N 8(Cd 결합 C2-N 4 · 미결합 C2-N 2 · C3-N 2)을 **중성 주개로 가정**한 값(아졸레이트 음이온이면 달라짐).', 'medium'),
    '2018_Zn__sql_2_FSR_4': (False, 'CIF 결합: COO⁻ 4 · 에터 O 2 · CH₂ 6 · CH₃ 2 → 5-butoxyisophthalate²⁻ × 2(남는 C₂₄H₂₄O₁₀ 와 일치) + bpe(중성) × 2 + Zn²⁺ × 2 → 0. MOFid(ERROR)가 카복실레이트를 빠뜨림.', 'high'),
    '2018_Zn__sql_2_ASR_3': (False, 'FSR_4 와 조성·결합 같음 → 0.', 'high'),
    '2021_Zn__srs_3_FSR_1': (False, 'CIF 결합: COO⁻ 8(pyridine-3,5-dicarboxylate²⁻ × 4) · Zn²⁺ × 4 → 0. 남는 C₂₀H₃₆N₄O₄ = N-methylpyrrolidone × 4(CH₂ 12 · CH₃ 4 · N(C3) 4, 결합 용매 — 중성).', 'high'),
    '2024_Zn__sql_2_ASR_3': (False, 'CIF 결합: COO⁻ 8(4,4′-oxybis(benzoate)²⁻ × 4, 에터 O 4) · Zn²⁺ × 4 → 0. 남는 C₅₆H₃₂N₁₆S₈ = C₁₄H₈N₄S₂ × 4(중성 N,S 기둥 — thiazolothiazole-bipyridyl 형). MOFid 가 기둥을 빠뜨림.', 'medium'),
    '2017_Cd__kgd_2_FSR_1': (None, '메타 짝 없음. CIF 결합: COO⁻ 24 · 물 20(H 둘) · 에터 O 8 · **H 없는 금속 결합 O 4** · Cd²⁺ × 12(+24). 그 O 4 가 O²⁻ 면 −8 · OH⁻ 면 −4 · '
                             'H 가 안 잡힌 물이면 0 — X선 구조는 물의 H 를 흔히 못 잡으므로 CIF 만으로는 못 가름.', 'undetermined'),
}
n_applied = 0
for r in d['rows']:
    if r['name'] in MANUAL:
        v, basis, conf = MANUAL[r['name']]
        r['auto_value'], r['auto_basis'] = r.get('value'), r.get('basis')
        r.update(value=v, basis=basis, method='손 검토(CIF 결합 환경 + 조성 산수, e8c_conn)', confidence=conf)
        n_applied += 1
    elif r.get('value') is not None:
        r.setdefault('method', '자동(MOFid 성분 배수 + 흔한 산화수)')
        r.setdefault('confidence', 'high')
    if r['name'] in ('2017_Cd__hcb_2_ASR_1', '2017_Zn__dia_3_ASR_1'):
        r['connectivity_check'] = {'2017_Cd__hcb_2_ASR_1': 'e8c_conn: COO⁻ 6 · Cd²⁺ 2 → −2 (자동과 같음)',
                                   '2017_Zn__dia_3_ASR_1': 'e8c_conn: COO⁻ 8 · Zn²⁺ 4 → 0 (자동과 같음)'}[r['name']]
    if 'known_value' in r:
        r['agrees_with_known'] = (r.get('value') == r['known_value'])
assert n_applied == len(MANUAL), n_applied
c = Counter(str(r.get('value')) for r in d['rows'])
d['summary'] = {'True': c.get('True', 0), 'False': c.get('False', 0), 'None': c.get('None', 0), 'n': len(d['rows']),
                'true_rows': [r['name'] for r in d['rows'] if r.get('value') is True],
                'none_rows': [r['name'] for r in d['rows'] if r.get('value') is None]}
d['known_check'] = [(r['name'], r.get('value'), r['known_value']) for r in d['rows'] if 'known_value' in r]
d['manual_review'] = {'script': 'e8c_manual_junseok.py + e8c_conn_junseok.py', 'time': time.strftime('%F %T'), 'rows': list(MANUAL)}
json.dump(d, open(P, 'w', encoding='utf-8'), indent=1, ensure_ascii=False, default=list)
print('요약', d['summary'])
print('확인 행 대조', d['known_check'])
