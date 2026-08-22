# -*- coding: utf-8 -*-
"""학술제 서류심사용 1매 요약 포스터 (A4 세로, PDF).

규정: 1매 이내 · 모든 텍스트 10pt 이상 · 블라인드(팀·개인 식별 정보 금지).
VESTA / ParaView 그림 자리는 흰 공백으로 비워 둔다.
"""
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

OUT = os.path.expanduser('~/mof_project/04_Analysis/학술제_요약포스터.pdf')
FIG = os.path.expanduser('~/mof_project/04_Analysis/figs/')

pdfmetrics.registerFont(TTFont('KR', '/mnt/c/Windows/Fonts/malgun.ttf'))
pdfmetrics.registerFont(TTFont('KRB', '/mnt/c/Windows/Fonts/malgunbd.ttf'))

NAVY   = (0x1F/255, 0x3B/255, 0x57/255)
ORANGE = (0xE0/255, 0x8A/255, 0x3C/255)
SAGE   = (0x8F/255, 0xA3/255, 0x7E/255)
SAGE_L = (0xE8/255, 0xEE/255, 0xE1/255)
GREY   = (0x6A/255, 0x6A/255, 0x6A/255)
GREY_L = (0xC8/255, 0xC8/255, 0xC8/255)
INK    = (0x22/255, 0x26/255, 0x2A/255)

W, H = A4                      # 595.3 x 841.9 pt
M    = 10*mm                   # 여백
CW   = (W - 2*M - 6*mm) / 2    # 단 폭
LX   = M
RX   = M + CW + 6*mm

c = canvas.Canvas(OUT, pagesize=A4)


def txt(x, y, s, size=10, font='KR', color=INK, align='l'):
    c.setFont(font, size); c.setFillColorRGB(*color)
    if align == 'c':   c.drawCentredString(x, y, s)
    elif align == 'r': c.drawRightString(x, y, s)
    else:              c.drawString(x, y, s)


def wrap(x, y, s, w, size=10, font='KR', lead=None, color=INK, first_bold=None):
    """단순 줄바꿈. y는 첫 줄 baseline, 마지막 baseline 다음 y를 돌려준다."""
    lead = lead or size * 1.32
    c.setFillColorRGB(*color)
    words, line = s.split(' '), ''
    for wd in words:
        t = (line + ' ' + wd).strip()
        c.setFont(font, size)
        if c.stringWidth(t, font, size) <= w:
            line = t
        else:
            c.setFont(font, size); c.drawString(x, y, line)
            y -= lead; line = wd
    if line:
        c.setFont(font, size); c.drawString(x, y, line)
        y -= lead
    return y


def head(x, y, s, w, size=12.5):
    """소제목 — 네이비 바 + 흰 글자."""
    h = size + 5
    c.setFillColorRGB(*NAVY); c.rect(x, y - h + size - 1, w, h, stroke=0, fill=1)
    txt(x + 3.2*mm, y, s, size=size, font='KRB', color=(1, 1, 1))
    return y - h - 3


def figure(x, y, path, w, cap, capsize=10):
    """그림 + 캡션. 다음 y를 돌려준다."""
    from PIL import Image
    iw, ih = Image.open(path).size
    h = w * ih / iw
    c.drawImage(path, x, y - h, width=w, height=h, mask='auto')
    yy = y - h - 3.7*mm
    yy = wrap(x, yy, cap, w, size=capsize, color=GREY, lead=capsize*1.22)
    return yy - 1.4*mm


def blank(x, y, w, h, cap, capsize=10):
    """VESTA/ParaView 그림을 넣을 흰 공백. 옅은 점선 테두리는 위치 표시용."""
    c.setFillColorRGB(1, 1, 1); c.rect(x, y - h, w, h, stroke=0, fill=1)
    c.setStrokeColorRGB(*GREY_L); c.setLineWidth(0.6); c.setDash(2.5, 2.5)
    c.rect(x, y - h, w, h, stroke=1, fill=0); c.setDash()
    yy = y - h - 3.7*mm
    yy = wrap(x, yy, cap, w, size=capsize, color=GREY, lead=capsize*1.25)
    return yy - 2*mm


def kv_table(x, y, rows, w, size=10, col=None, headfill=True):
    """간단 표. rows[0]은 머리행."""
    n = len(rows[0])
    col = col or [w/n]*n
    rh = size + 4.6
    for i, row in enumerate(rows):
        yy = y - i*rh
        if i == 0 and headfill:
            c.setFillColorRGB(*SAGE_L); c.rect(x, yy - 3.4, w, rh, stroke=0, fill=1)
        c.setStrokeColorRGB(*GREY_L); c.setLineWidth(0.4)
        c.line(x, yy - 3.4, x + w, yy - 3.4)
        cx = x
        for j, v in enumerate(row):
            f = 'KRB' if i == 0 else 'KR'
            if j == 0: txt(cx + 1.6, yy, str(v), size=size, font=f)
            else:      txt(cx + col[j] - 1.6, yy, str(v), size=size, font=f, align='r')
            cx += col[j]
    c.setStrokeColorRGB(*NAVY); c.setLineWidth(0.8)
    c.line(x, y + size + 1.2, x + w, y + size + 1.2)
    return y - len(rows)*rh - 3*mm

# ══════════════════ 제목 ══════════════════
TB = 20*mm
c.setFillColorRGB(*NAVY); c.rect(0, H - TB, W, TB, stroke=0, fill=1)
c.setFillColorRGB(*ORANGE); c.rect(0, H - TB - 1.5*mm, W, 1.5*mm, stroke=0, fill=1)
txt(W/2, H - 9.2*mm, 'CO₂ 포집을 위한 MTV-ZIF의 전산 설계; ZIF-69를 중심으로',
    size=17, font='KRB', color=(1, 1, 1), align='c')
txt(W/2, H - 16.0*mm,
    '습윤 배가스(CO₂ 0.15 bar · 298 K · RH 90%)에서 최적 치환율을 찾는 6단계 평가 파이프라인',
    size=10.5, color=(0.84, 0.88, 0.92), align='c')

BY = 38*mm                      # 결론 띠 높이
y0 = H - TB - 1.5*mm - 6.5*mm

# ══════════════════ 왼쪽 단 ══════════════════
y = y0
y = head(LX, y, '1.  연구 질문', CW)
y = wrap(LX, y, '실제 배가스에는 수분이 동반되므로 건조 조건의 CO₂ 흡착량만으로는 '
                '포집 소재를 평가할 수 없다. ZIF 유기 링커를 부분 치환한 다변량(MTV) '
                '골격을 설계하고 다음 한 질문에 답한다.', CW, size=10)
y -= 1.2*mm
c.setFillColorRGB(*SAGE_L); c.rect(LX, y - 7.4*mm, CW, 9.0*mm, stroke=0, fill=1)
c.setFillColorRGB(*SAGE); c.rect(LX, y - 7.4*mm, 1.5*mm, 9.0*mm, stroke=0, fill=1)
txt(LX + 4*mm, y - 4.2*mm, '습윤 배가스에서 어느 치환율이 가장 유리한가?',
    size=11, font='KRB', color=NAVY)
y -= 12.6*mm
y = wrap(LX, y, '치환기가 늘면 정전기 자리가 늘어 CO₂ 흡착이 오르지만(가설 1), 같은 '
                '자리가 물도 잡는다(가설 2). 판정 기준을 계산 전에 등록하고 측정으로 '
                '가린다.', CW, size=10)
y -= 1.5*mm

y = blank(LX, y, CW, 38*mm,
          '그림 1. ZIF-69(gme) 단위셀과 치환 가능한 24개 -Cl 자리. '
          '벤조이미다졸레이트 b2 자리가 공동을 향한다.')

y = head(LX, y, '2.  계산 방법', CW)
y = wrap(LX, y, '흡착 RASPA2 대정준 몬테카를로 · 헨리 상수와 흡착열 Widom 삽입 · '
                '이완 GFN-FF(셀 고정) · 전하 PACMAN DDEC6 · 기공 지표 Zeo++. '
                '설정은 전 계산에서 고정했다.', CW, size=10)
y -= 0.8*mm
y = kv_table(LX, y, [
    ['항목', '설정'],
    ['사이클', '초기화 5,000 + 생산 15,000'],
    ['골격 힘장 / 전하', 'UFF_MOF / PACMAN DDEC6'],
    ['CO₂ · 물 모델', 'García-Sánchez 2009 · TIP5P-Ew'],
    ['정전기 / 컷오프', 'Ewald 1e-6 / 12 Å'],
    ['재생', 'TSA 373 K / VSA 0.05 bar'],
], CW, size=10, col=[CW*0.36, CW*0.64])

y = head(LX, y, '3.  작용기 선정', CW)
y = wrap(LX, y, '작용기 7종 중 -SO₃H만 목표대(30~40)에 든다. -OH를 -CH₃로 막은 '
                '-SO₂CH₃와 같은 치환율에서 2.41 kJ/mol 벌어지며, 그 차이가 수소결합 '
                '공여 -OH의 몫이다.', CW, size=10)
y -= 0.8*mm
y = kv_table(LX, y, [
    ['작용기 (최적 조성)', 'Q_st', '무치환 대비'],
    ['-SO₃H (100%)', '34.01', '+11.59'],
    ['-SO₂CH₃ (75%)', '29.01', '+6.59'],
    ['-NO₂ (100%)', '28.87', '+6.45'],
    ['-Br (100%)', '22.73', '+0.31'],
    ['무치환 모체', '22.42', '기준'],
], CW, size=10, col=[CW*0.46, CW*0.27, CW*0.27])

print(f'  왼쪽 단 끝 y = {y/mm:.1f}mm  (결론 띠 상단 {BY/mm:.1f}mm)')
# ══════════════════ 오른쪽 단 ══════════════════
y = y0
y = head(RX, y, '4.  결과', CW)
FW = CW*0.78
FX = RX + (CW-FW)/2
y = figure(FX, y, FIG + 'fig2_ladder.png', FW,
           '그림 2. 치환율에 따른 등량 흡착열과 0.15 bar 로딩. '
           '흡착열 22.4→34.0 kJ/mol, 로딩 2.6배. 오차막대 1σ.')
y = figure(FX, y, FIG + 'fig3_water.png', FW,
           '그림 3. RH90 유지율(좌축)과 H₂O/CO₂ 비(우축). 유지율은 25~75%에서 '
           '고원을 이루고 100%에서 꺾인다 — 점진적 악화가 아닌 문턱 현상.')
y = figure(FX, y, FIG + 'fig4_windows.png', FW,
           '그림 4. 두 관문의 창. 안정성 창은 치환 자리 하나(58.3→62.5%) 사이에서 '
           '닫히고, 흡착 창은 66.7→75%에서 열린다. 회색이 두 창 사이의 간격.')

y = blank(RX, y, CW, 16*mm,
          '그림 5. 전하 ON/OFF 차분 밀도맵 — 정전기가 CO₂를 끌어들인 자리 '
          '(정전기 기여 무치환 41% → 고치환 69%).')
print(f'  오른쪽 단 끝 y = {y/mm:.1f}mm')
# ══════════════════ 결론 띠 ══════════════════
c.setFillColorRGB(*SAGE_L); c.rect(0, 0, W, BY, stroke=0, fill=1)
c.setFillColorRGB(*NAVY); c.rect(0, BY - 1.4*mm, W, 1.4*mm, stroke=0, fill=1)
txt(M, BY - 7.6*mm, '결론', size=12.5, font='KRB', color=NAVY)

bw = 70*mm
c.setFillColorRGB(*NAVY); c.rect(W - M - bw, BY - 30.5*mm, bw, 19.6*mm, stroke=0, fill=1)
txt(W - M - bw/2, BY - 16.0*mm, '-SO₃H  58.3 % (14/24 자리)',
    size=12.5, font='KRB', color=(1, 1, 1), align='c')
txt(W - M - bw/2, BY - 22.4*mm, '습윤 TSA 작업 용량 0.833 ± 0.025 mol/kg',
    size=10, color=(0.86, 0.90, 0.94), align='c')
txt(W - M - bw/2, BY - 28.0*mm, '무치환 대비 +77 % · 차순위와 2.10σ',
    size=10, color=(0.86, 0.90, 0.94), align='c')

tw = W - 2*M - bw - 6*mm
yy = BY - 12.6*mm
for s in [
    '① 건조 성능 1위(100% 치환)가 습윤에서 꼴찌다. CO₂를 잡는 -OH 자리가 물도 잡기 때문이며, '
    '최대 치환은 최적이 아니다.',
    '② 안정성 창(≤58.3%)과 흡착 목표대 창(≥75%)이 겹치지 않아, -SO₃H 단독으로는 두 관문을 동시에 넘는 조성이 없다.',
    '③ 재생의 지배항은 흡착열이 아니라 현열(2~5배)이며, 이득은 작업 용량으로 난방비를 희석한 데서 온다.',
]:
    yy = wrap(M, yy, s, tw, size=10, lead=11.0)
    yy -= 0.4*mm
print(f'  결론 텍스트 끝 y = {yy/mm:.1f}mm  (0 이상이어야 함)')

c.showPage(); c.save()
print('저장:', OUT)
