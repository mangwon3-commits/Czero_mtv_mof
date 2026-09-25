# -*- coding: utf-8 -*-
"""관문 ⑤ 외부 골격 판정 — 사용자 결정 (다) 2026-09-25 (`MAGI5_USER_DECISIONS_20260925.md` §4).

`risk_screen.py` 는 고치지 않는다(ZIF-69 계열 판정은 그대로). 결과 JSON 의 before/after LCD 를 읽어
두 갈래 값을 계산해 붙일 뿐이다.

  치환 조성      drop_family = (LCD_ref_family − LCD_after) / LCD_ref_family
                 LCD_ref_family = 같은 골격 **무치환 모체**를 같은 처리(UFF4MOF box/relax)로 이완한 뒤의 LCD.
                 ZIF-69 계열은 7.63144(= 기존 규칙, 과거 판정 불변).
  무치환 외부 골격  drop_corrected = 1 − (LCD_after/LCD_before)_골격 ÷ (LCD_after/LCD_before)_ZIF-69 모체
                 = "같은 처리에서 모체보다 몇 % 더 줄었나". 모체 자신은 정의상 0.
  문턱은 둘 다 20 % (불변).
"""
import json, sys

BASE_BEFORE, BASE_AFTER = 8.89809, 7.63144      # risk_results_v3.json base (GFN-FF 이완본 → UFF4MOF box/relax)
LIMIT = 20.0


def corrected_drop(before, after):
    return 100.0 * (1.0 - (after / before) / (BASE_AFTER / BASE_BEFORE))


if __name__ == '__main__':
    f = sys.argv[1] if len(sys.argv) > 1 else 'risk_results_magi5_gate5.json'
    d = json.load(open(f, encoding='utf-8'))
    for r in d['rows']:
        if r['name'] == 'base' or not r.get('before') or not r.get('after'):
            continue
        b, a = r['before']['LCD'], r['after']['LCD']
        c = corrected_drop(b, a)
        print(f"{r['name']:10s} LCD {b:.3f} → {a:.3f} | 기존(ZIF-69 모체 대비) {r.get('LCD_drop_pct')}% | "
              f"자기 대비 {100*(b-a)/b:.1f}% | 처리 보정 {c:.1f}% → {'통과' if c < LIMIT else '탈락'}")
