# -*- coding: utf-8 -*-
"""A4 / 11pt / 단일 줄간격 7페이지 보고서(.docx) 생성.

시행착오는 쓰지 않는다. 계산 방법은 "무엇을 썼는가 + 설정 표" 까지만 두고,
나머지는 물리화학적 내용으로 채운다. 아직 나오지 않은 결과는 자리를 잡아
두고 [진행 중] 으로 표시한다 -- 분량이 흔들리지 않게.
"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

OUT = os.path.expanduser("~/mof_project/04_Analysis/MTV_ZIF69_보고서.docx")
FONT = "맑은 고딕"
FONT_EN = "Times New Roman"


def setfont(run, size=11, bold=False, italic=False, color=None):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.name = FONT_EN
    run._element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    if color:
        run.font.color.rgb = color


def para(doc, text, size=11, bold=False, align=None, space_after=6,
         space_before=0, indent=None, italic=False, color=None):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
    pf.space_after = Pt(space_after)
    pf.space_before = Pt(space_before)
    if indent is not None:
        pf.left_indent = Cm(indent)
    if align:
        p.alignment = align
    if text:
        setfont(p.add_run(text), size, bold, italic, color)
    return p


def rich(doc, chunks, size=11, space_after=6, indent=None):
    """chunks = [(text, bold), ...] 한 문단 안에서 굵기를 섞는다."""
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
    pf.space_after = Pt(space_after)
    if indent is not None:
        pf.left_indent = Cm(indent)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for t, b in chunks:
        setfont(p.add_run(t), size, b)
    return p


def h1(doc, text):
    para(doc, text, size=13, bold=True, space_before=10, space_after=5)


def h2(doc, text):
    para(doc, text, size=11.5, bold=True, space_before=7, space_after=4)


def table(doc, rows, widths=None, size=9.5, header=True, caption=None):
    if caption:
        para(doc, caption, size=9.5, bold=True, space_before=4, space_after=2)
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(rows):
        for j, cell in enumerate(row):
            c = t.cell(i, j)
            c.text = ""
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
            if j > 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            setfont(p.add_run(str(cell)), size, bold=(header and i == 0))
    if widths:
        for j, w in enumerate(widths):
            for r in t.rows:
                r.cells[j].width = Cm(w)
    para(doc, "", size=4, space_after=2)
    return t


def note(doc, text):
    p = para(doc, text, size=9.5, indent=0.4, space_after=6)
    return p


doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.top_margin = sec.bottom_margin = Cm(2.3)
sec.left_margin = sec.right_margin = Cm(2.3)

st = doc.styles["Normal"]
st.font.name = FONT_EN
st.font.size = Pt(11)
st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
st.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
st.paragraph_format.space_after = Pt(6)

print("build_report: 골격 준비 완료")

# ─────────────────────────────────────────── 표제
para(doc, "배가스 CO₂ 포집을 위한 MTV-ZIF-69의 전산 설계",
     size=16, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
para(doc, "흡착 · 수분 경쟁 · 재생 · 구조 안정성의 통합 평가",
     size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)

# ─────────────────────────────────────────── 초록
para(doc, "초록", size=11.5, bold=True, space_after=3)
rich(doc, [
    ("gme 위상 ZIF-69의 벤조이미다졸레이트 링커에 술폰산기를 부분 치환한 "
     "다변량 골격 계열을 설계하고, 배가스 조건(0.15 bar CO₂, 298 K)에서 "
     "건조 흡착·수분 경쟁·재생 작업 용량·구조 안정성의 네 축을 동일한 "
     "프로토콜로 평가했다. 치환율 상승에 따라 등량 흡착열은 22.4에서 "
     "34.0 kJ/mol까지 단조 증가해 목표대(30~40)에 진입하지만, 술폰산의 "
     "수소결합 공여 자리가 CO₂와 물을 같은 기전으로 붙잡기 때문에 상대습도 "
     "90%에서의 작업 용량은 치환율 75%에서 최대가 되고 100%에서 오히려 "
     "떨어진다. 동시에 공동 축소로 인해 구조 안정성 관문은 치환율 50%까지만 "
     "통과한다. 세 축의 경계가 모두 치환율 50~75% 구간에 모여 있어, 이 "
     "구간을 정수 격자로 세분한 조성이 결론을 정한다.", False)], space_after=10)

# ─────────────────────────────────────────── 1. 서론
h1(doc, "1. 서론 — 포집 물질에 요구되는 것")
rich(doc, [
    ("석탄화력 배가스는 CO₂ 분압이 약 ", False), ("0.15 bar", True),
    ("이고 나머지 대부분이 N₂이며, 298 K에서 상대습도가 90%에 이르는 수증기를 "
     "동반한다. 이 조건에서 흡착제가 만족해야 하는 것은 흡착량 하나가 아니다. "
     "실제 공정은 붙였다 떼는 순환이므로, 성능의 최종 척도는 한 사이클에 "
     "실어 나르는 양 — ", False),
    ("작업 용량(working capacity) = 흡착 로딩 − 탈착 로딩", True),
    (" — 이다.", False)])
rich(doc, [
    ("여기서 흡착 세기와 재생 용이성이 서로 맞선다. 등량 흡착열 ", False),
    ("Q_st", True),
    ("가 클수록 낮은 분압에서도 잘 붙지만, 흡착은 기체가 자유도를 잃는 과정이라 "
     "ΔS < 0이고 ΔG = ΔH − TΔS에서 결합이 강할수록 떼어내는 데 더 큰 온도나 "
     "더 낮은 압력이 필요하다. 두 요구를 함께 만족하는 창이 ", False),
    ("Q_st 30~40 kJ/mol", True),
    ("이며, 본 연구는 이를 사전 목표대로 등록하고 출발했다.", False)])
rich(doc, [
    ("물은 별도의 제약이 아니라 같은 자리를 두고 다투는 경쟁자다. 물의 물리흡착 "
     "엔탈피 최대치는 약 ", False), ("−59 kJ/mol", True),
    ("로, 본 연구에서 얻은 어떤 조성의 CO₂ Q_st(22~34)보다도 크다. 따라서 "
     "CO₂를 더 세게 잡기 위해 극성 자리를 늘리면 그 자리는 물을 더 세게 잡는다. "
     "이 긴장이 본 보고서를 관통하는 주제이며, 건조 조건의 우수성이 습윤 조건에서 "
     "유지되는지를 별도로 검증해야 하는 이유다.", False)])
rich(doc, [
    ("본 연구는 gme 위상의 ZIF-69를 모체로 삼아 링커의 염소 자리를 술폰산으로 "
     "부분 치환한 다변량(MTV) 계열을 설계하고, ", False),
    ("건조 흡착 → 수분 경쟁 → 작업 용량 → 구조 안정성", True),
    ("의 네 축에서 평가했다. 각 축의 판정 기준은 계산 이전에 등록했고 결과를 "
     "본 뒤 수정하지 않았다.", False)])

# ─────────────────────────────────────────── 2. 흡착의 물리
h1(doc, "2. 흡착을 지배하는 두 힘")
rich(doc, [
    ("골격과 CO₂ 사이에 작용하는 힘은 분산력과 정전기 상호작용 둘이다. "
     "분산력은 순간 쌍극자의 상관에서 나오며 거리에 대해 ", False),
    ("r⁻⁶", True),
    ("로 감쇠한다. 감쇠가 가파르기 때문에 분자가 벽에 가까울수록, 즉 기공이 "
     "좁을수록 유리하다. 반면 정전기 상호작용은 감쇠가 완만해 기공이 넓어도 "
     "작동하지만, 상대 분자가 영구 전하 분포를 가져야 한다.", False)])
rich(doc, [
    ("CO₂는 쌍극자가 없고 ", False), ("사중극자(quadrupole)", True),
    ("를 갖는다. 본 연구가 사용한 모델에서 CO₂의 사중극자는 −0.876 e·Å², N₂는 "
     "−0.245 e·Å²로 CO₂가 3.6배 크다. 골격에 국소적으로 강한 전기장을 만들면 "
     "CO₂만 선택적으로 더 붙잡을 수 있고, 이것이 극성 작용기를 도입하는 논리다. "
     "선택도가 흡착량보다 작용기에 민감한 이유도 여기에 있다.", False)])
rich(doc, [
    ("두 힘의 기여는 골격 전하를 켜고 끈 두 번의 계산을 차분해 분리할 수 있다. "
     "Lennard-Jones 항은 전하와 무관하므로 상쇄되고 정전기 항만 남는다. "
     "본 계열에서 정전기가 전체 흡착에 기여하는 비율은 무치환 모체의 "
     "41.2 ± 2.3%에서 술폰산 100%의 69.1 ± 1.1%까지 증가한다", False),
    ("(v2 세대 밀도맵)", False),
    (". 즉 치환의 이득은 주로 정전기에서 오며, 이는 사중극자 논리와 정합한다.",
     False)])

# ─────────────────────────────────────────── 3. 모체와 치환 설계
h1(doc, "3. 모체 선택과 치환 설계")
h2(doc, "3.1 위상이 치환의 방향을 정한다")
rich(doc, [
    ("같은 작용기를 같은 밀도로 도입해도 골격 위상에 따라 결과가 반대로 나온다. "
     "ZIF-8이 속한 sod 위상에서는 링커의 C2 치환기가 6원환 창구를 향하므로, "
     "치환하면 창구(PLD)만 좁아지고 공동(LCD)은 줄지 않는다. 분산력을 키우려면 "
     "공동이 좁아져야 하는데 정작 좁아지는 것은 통로여서, 치환율을 올릴수록 "
     "Q_st가 감소하는 역전이 일어난다.", False)])
rich(doc, [
    ("gme 위상의 ZIF-69에서는 벤조 고리의 치환 자리가 ", False),
    ("공동 쪽", True),
    ("을 향한다. 치환하면 공동이 줄고 창구는 남으므로 분산력과 정전기가 함께 "
     "증가한다. 모체를 sod에서 gme로 옮긴 것은 이 기하학적 사실에 근거한다.",
     False)])
h2(doc, "3.2 ZIF-69의 구조와 치환 자리")
table(doc, [
    ["항목", "값"],
    ["화학식", "Zn(nIm)(cbIm) × 24 (단위셀당 아연 24개)"],
    ["링커", "nIm = 2-니트로이미다졸레이트 / cbIm = 5-클로로벤조이미다졸레이트"],
    ["단위셀 원자", "600개 — Zn 24 · C 240 · N 120 · O 48 · Cl 24 · H 144"],
    ["셀 파라미터", "a = b = 26.084 Å, c = 19.408 Å, γ = 120° (육방정)"],
    ["기공 지표", "PLD 5.157 Å · LCD 8.90 Å · 접근가능부피 1232 Å³"],
], widths=[3.6, 12.4], caption="표 1. 무치환 ZIF-69 모체의 구조 지표")
rich(doc, [
    ("ZIF-69는 서로 다른 링커 두 종을 이미 갖는 다변량 골격이며, 본 연구의 치환은 "
     "그중 벤조이미다졸레이트의 염소 자리를 술폰산으로 바꾸는 것이다. "
     "치환 가능한 자리는 염소 원자 수와 같은 ", False), ("24개", True),
    ("이므로, 치환율은 24의 약수 관계를 따르는 값만 정확히 구현된다. "
     "한 자리가 4.167%p에 해당하며, 50%와 75% 사이에는 격자점이 다섯 개뿐이다.",
     False)])
rich(doc, [
    ("염소 하나가 술폰산으로 치환되면 원자 수는 넷 증가한다(−Cl 1개 제거, "
     "S·O₃·H 5개 추가). 따라서 ", False),
    ("원자 수 = 600 + 4 × (치환 자리 수)", True),
    ("가 성립하며, 이는 의도한 조성이 실제로 구현되었는지를 구조 파일만으로 "
     "확인하는 독립 검산으로 사용된다. 염소 수와 황 수의 합이 항상 24가 되어야 "
     "한다는 조건도 함께 검사한다.", False)])

# ─────────────────────────────────────────── 4. 계산 방법
h1(doc, "4. 계산 방법")
rich(doc, [
    ("흡착 등온 물성은 강정준(grand canonical, μVT) 앙상블 몬테카를로 "
     "시뮬레이션(GCMC)으로 계산했다. 기체 저장고와 화학퍼텐셜이 평형을 이룬 채 "
     "분자의 삽입·삭제·이동을 시도하므로, 일정 압력에 노출된 실험 상황과 "
     "대응한다. 무한 희석 극한의 헨리 상수와 흡착열은 Widom 삽입으로 구했다. "
     "골격 기하는 셀을 고정한 채 GFN-FF로 이완했고, 부분전하는 이완된 기하에서 "
     "다시 산출했다. 기공 지표는 Zeo++로, 골격 안정성 판정용 이완은 UFF4MOF로 "
     "수행했다. 설정은 아래 표와 같으며 전 계산에서 동일하다.", False)])
table(doc, [
    ["항목", "설정"],
    ["앙상블 / 사이클", "μVT GCMC, 초기화 5,000 + 생산 15,000"],
    ["골격 힘장", "UFF_MOF"],
    ["CO₂ 모델", "García-Sánchez 2009 — ε/k_B 29.933 K, σ 2.745 Å, q_C +0.6512"],
    ["N₂ 모델", "ε/k_B 38.298 K, σ 3.306 Å, q_N −0.405"],
    ["물 모델", "TIP5P-Ew (5-site) — ε/k_B 89.633 K, σ 3.097 Å"],
    ["골격 전하", "PACMAN (DDEC6 재현), 전하합 |Σq| ≤ 1×10⁻⁴"],
    ["혼합 규칙 / 정전기", "Lorentz-Berthelot / Ewald, 상대정밀도 1×10⁻⁶"],
    ["컷오프 / 셀", "12 Å / 2×2×2 확장 (수직폭 45.2·45.2·38.8 Å)"],
    ["기하 이완", "GFN-FF, 셀 고정, FIRE (fmax 0.05 eV/Å)"],
    ["기공 지표", "Zeo++ (PLD, LCD, 접근가능부피)"],
], widths=[3.8, 12.2], caption="표 2. 계산 설정")
note(doc, "CO₂·N₂의 분자 기하는 TraPPE 정의에서 오지만 Lennard-Jones 계수와 "
          "부분전하는 위 표의 값을 사용했다. 따라서 손님 분자 힘장을 TraPPE로 "
          "표기하는 것은 정확하지 않다.")

# ─────────────────────────────────────────── 5. 건조 흡착
h1(doc, "5. 건조 조건 흡착")
rich(doc, [
    ("0.15 bar CO₂, 298 K에서 술폰산 치환율에 따른 흡착 물성은 표 3과 같다. "
     "치환율이 오르면 Q_st와 로딩이 함께 단조 증가하며, 인접 조성 간 차이는 "
     "모두 통계 오차의 여러 배다. 목표대 30~40 kJ/mol에 진입한 것은 "
     "치환율 75%와 100% 두 조성이다.", False)])
table(doc, [
    ["조성", "치환율", "Q_st (kJ/mol)", "0.15 bar 로딩 (mol/kg)", "PLD (Å)", "LCD (Å)", "AV (Å³)"],
    ["base", "0%", "22.42 ± 0.11", "0.5889 ± 0.0059", "5.157", "8.90", "1232"],
    ["saIm025", "25%", "27.97 ± 0.10", "0.9645 ± 0.0104", "4.479", "9.36", "1290"],
    ["saIm050", "50%", "29.51 ± 0.19", "1.2390 ± 0.0205", "4.495", "10.15", "1085"],
    ["saIm075", "75%", "31.42 ± 0.22", "1.3602 ± 0.0210", "3.747", "9.41", "923"],
    ["saIm100", "100%", "34.01 ± 0.55", "1.5429 ± 0.0357", "4.229", "8.91", "723"],
    ["nbIm100", "−NO₂ 100%", "28.87 ± 0.35", "0.8792 ± 0.0163", "5.554", "10.25", "1415"],
    ["mslm075", "−SO₂CH₃ 75%", "29.01 ± 0.25", "1.0030 ± 0.0200", "3.635", "9.21", "855"],
], widths=[2.0, 2.0, 2.7, 3.5, 1.9, 1.9, 2.0],
   caption="표 3. 건조 조건 흡착 물성 (298 K, 0.15 bar, 1σ 병기)")
rich(doc, [
    ("대체 작용기와의 비교가 술폰산 선택의 근거를 준다. 니트로 100%는 28.87, "
     "메틸설포닐 75%는 29.01로 모두 목표대에 미치지 못한다. 특히 메틸설포닐은 "
     "술폰산과 같은 설폰 골격을 가지면서도 성능이 낮은데, 이는 ", False),
    ("술폰산의 이점이 설폰기 자체가 아니라 수산기(−OH)의 수소결합 공여 능력에 "
     "있음", True),
    ("을 시사한다. 이 해석은 6절의 수분 거동에서 다시 확인된다.", False)])
rich(doc, [
    ("접근가능부피와 흡착량이 같은 방향으로 움직이지 않는다는 점도 기록해 둘 "
     "만하다. saIm100은 부피가 가장 작은데 로딩이 가장 크다. 부피는 담을 수 있는 "
     "공간의 상한일 뿐이고 실제 로딩은 그 공간의 에너지 지형이 정하기 때문이다. "
     "따라서 기하 지표만으로 성능을 예측할 수 없다.", False)])

# ─────────────────────────────────────────── 6. 수분 경쟁
h1(doc, "6. 수분 경쟁 — 같은 자리를 두고 다투는 두 분자")
rich(doc, [
    ("상대습도(RH)는 물의 절대량이 아니라 그 온도의 포화증기압에 대한 비율이다. "
     "298 K에서 포화증기압은 약 3,169 Pa이므로 RH 90%는 물 분압 2,852 Pa에 "
     "해당한다. 배가스 조건에서 물의 분압은 CO₂ 분압의 약 1/5에 불과하지만, "
     "결합 세기가 두 배 이상이므로 경쟁은 대등하지 않다.", False)])
rich(doc, [
    ("술폰산이 CO₂를 붙잡는 기전은 수산기의 수소결합 공여다. 그런데 수소결합 "
     "공여자는 물이 가장 잘 이용하는 자리이기도 하다. ", False),
    ("즉 CO₂를 잡는 기전과 물을 잡는 기전이 동일하며", True),
    (", 이것이 이 노선의 근본 딜레마다. 5절에서 메틸설포닐이 술폰산보다 "
     "성능이 낮았던 것과 같은 원인이 여기서는 불리하게 작용한다.", False)])
rich(doc, [
    ("실제로 흡착 조건(298 K, RH 90%)에서 골격에 붙은 물과 CO₂의 몰비는 "
     "치환율에 따라 0.85 → 1.01 → 1.24 → 2.31로 증가한다. 앞의 세 계단은 "
     "완만하지만 ", False), ("75%에서 100%로 가는 마지막 계단만 두 배 가까이 "
     "뛴다", True),
    (". 물 흡수가 치환율에 선형으로 늘지 않고 특정 밀도 이상에서 급증한다는 "
     "뜻이며, 흡착된 물이 다음 물의 수소결합 자리를 제공해 군집이 자라는 "
     "협동 효과로 해석된다. 이 비선형성 때문에 두 점을 이어 외삽하는 추정은 "
     "성립하지 않는다.", False)])
note(doc, "[진행 중] RH 0/25/50/90 전 구간의 v3 수분 경쟁 스캔(5조성 × 4조건)이 "
          "별도 장비에서 수행 중이다. 완료 시 조성별 RH90 유지율과 물 헨리 상수를 "
          "이 절에 추가하고, 물 친화도와 습윤 CO₂ 손실의 상관을 문헌 축 위에서 "
          "검증한다.")

# ─────────────────────────────────────────── 7. 재생과 작업 용량
h1(doc, "7. 재생과 작업 용량")
h2(doc, "7.1 온도 스윙과 진공 스윙의 열역학적 차이")
rich(doc, [
    ("재생 방식은 둘이다. 온도 스윙(TSA)은 373 K로 승온해 ΔG = ΔH − TΔS에서 "
     "−TΔS 항이 ΔH를 이기게 만들고, 진공 스윙(VSA)은 CO₂ 분압을 0.05 bar로 "
     "낮춰 기상의 화학퍼텐셜을 내린다. 두 방식은 물에 대해 정반대로 행동한다.",
     False)])
rich(doc, [
    ("공정에서 기체 흐름의 수분 함량은 베드를 데운다고 변하지 않으므로, 물 "
     "분압을 2,852 Pa로 고정한 채 온도만 올리면 분모인 포화증기압이 "
     "101,325 Pa로 32배가 되어 ", False),
    ("상대습도가 90%에서 2.8%로 떨어진다", True),
    (". 물 분자의 수는 그대로인데 응축하려는 경향만 사라지는 것이다. 그 결과 "
     "TSA는 별도의 전처리 건조 없이 재생 과정이 건조를 겸한다. 반면 VSA는 "
     "온도가 유지되어 RH 90%가 그대로이고, CO₂가 비운 자리를 물이 채운다.",
     False)])
table(doc, [
    ["조건", "CO₂ 분압", "온도", "물 분압", "상대습도"],
    ["흡착", "0.15 bar", "298 K", "2,852 Pa", "90.0%"],
    ["TSA 재생", "0.15 bar", "373 K", "2,852 Pa", "2.8%"],
    ["VSA 재생", "0.05 bar", "298 K", "2,852 Pa", "90.0%"],
], widths=[2.6, 2.6, 2.2, 2.6, 2.6],
   caption="표 4. 습윤 작업 용량 계산 조건 (물 분압 고정)")
h2(doc, "7.2 습윤 조건의 작업 용량")
table(doc, [
    ["조성", "습윤 TSA WC", "습윤 VSA WC", "건조 TSA WC", "습윤/건조", "H₂O/CO₂", "물 제거율"],
    ["base", "0.469 ± 0.012", "0.352 ± 0.013", "0.4845", "96.8%", "0.85", "85.7%"],
    ["saIm050", "0.768 ± 0.018", "0.557 ± 0.021", "1.0625", "72.3%", "1.01", "88.7%"],
    ["saIm075", "0.833 ± 0.022", "0.580 ± 0.027", "1.1468", "72.6%", "1.24", "89.5%"],
    ["saIm100", "0.688 ± 0.024", "0.498 ± 0.042", "1.2976", "53.0%", "2.31", "77.6%"],
], widths=[2.0, 2.7, 2.7, 2.3, 2.0, 1.7, 2.1],
   caption="표 5. 습윤 작업 용량 (mol/kg, 1σ 병기). 작업 용량의 오차는 "
           "두 로딩 오차의 제곱합근이다.")
rich(doc, [
    ("건조 조건에서 세 축(Q_st·로딩·건조 작업 용량) 모두 1위였던 saIm100이 "
     "습윤 조건에서는 최하위가 된다. 세 조성 간 간격은 모두 2.3σ 이상이므로 "
     "순위를 말할 수 있으며, 습윤 순위는 ", False),
    ("saIm075 > saIm050 > saIm100", True),
    ("이다. 건조 대비 유지 비율에서 saIm100만 53.0%로 떨어지는데, 이는 6절의 "
     "물/CO₂ 몰비 계단과 같은 조성에서 나타난다.", False)])
rich(doc, [
    ("재생 쪽에서도 saIm100만 다르다. 승온으로 제거되는 물의 비율이 다른 "
     "조성에서는 86~90%인데 saIm100은 77.6%에 그친다. 373 K, RH 2.8%에서도 "
     "떨어지지 않는 물이 남는다는 뜻이고, 사이클을 반복하면 베드에 축적된다. "
     "진공 재생에서는 네 조성 모두 물이 오히려 증가한다(+5~13%). 압력은 물의 "
     "화학퍼텐셜을 거의 건드리지 못하기 때문이며, 이 계열에서 TSA를 기준 "
     "공정으로 보는 근거다.", False)])
note(doc, "[진행 중] 재생 에너지 수지(현열 + 건조 잠열 + 흡착열)는 v3 작업 용량이 "
          "확정된 값으로 재계산한다. 지배항은 흡착열이 아니라 작업 용량에 반비례하는 "
          "현열이므로, 치환의 이득은 결합을 강화하는 데 있는 것이 아니라 같은 "
          "가열량을 더 많은 CO₂에 분산시키는 데 있다.")

# ─────────────────────────────────────────── 8. 구조 안정성
h1(doc, "8. 구조 안정성 관문")
rich(doc, [
    ("흡착 성능이 아무리 좋아도 골격이 기공을 유지하지 못하면 후보가 될 수 없다. "
     "이 관문은 순위를 만들지 않고 탈락만 시킨다. 판정 기준은 계산 이전에 "
     "등록했다: 창구 지름(PLD) 3.3 Å 이하, 접근가능부피 20 Å³ 미만, 최소 "
     "원자간 거리 0.7 Å 미만, 그리고 최대 공동 지름(LCD) 감소 20% 초과.", False)])
rich(doc, [
    ("여기서 LCD 감소는 이완 전후의 변화가 아니라 ", False),
    ("이완된 무치환 모체의 공동 대비 해당 조성의 공동이 얼마나 좁은가", True),
    ("를 뜻한다. 모체 자신도 이완 과정에서 LCD가 8.898 Å에서 7.631 Å로 줄기 "
     "때문에 기준선은 고정된 값이 아니라 같은 프로토콜에서 함께 산출된다.",
     False)])
table(doc, [
    ["조성", "LCD 감소 (모체 대비)", "판정", "탈락 기준"],
    ["saIm025", "6.69%", "통과", "—"],
    ["saIm050", "13.75%", "통과", "—"],
    ["saIm075", "20.26%", "탈락", "LCD 감소 20% 초과"],
    ["mslm075", "21.67%", "탈락", "LCD 감소 20% 초과"],
    ["saIm100", "22.50%", "탈락", "LCD 감소 20% 초과"],
], widths=[3.0, 4.6, 2.4, 6.0],
   caption="표 6. 구조 안정성 관문 결과 (전체 31종 중 28종 통과)")
rich(doc, [
    ("탈락한 세 종은 모두 LCD 단일 기준에서 걸렸고 창구·부피·최소거리는 통과했다. "
     "즉 골격이 파탄난 것이 아니라 치환기가 공동을 과도하게 채운 것이다. 문제는 "
     "5절에서 목표대에 진입한 두 조성이 그대로 탈락 목록이라는 점이다. 관문을 "
     "통과한 조성 중 최고 Q_st는 saIm050의 29.51 kJ/mol로 목표대 문턱 바로 "
     "아래에 있다.", False)])
rich(doc, [
    ("이 관문의 이완은 수렴에 이르지 않는다. 본 계열에서 UFF4MOF 최소화는 "
     "수렴하지 않고 진동하므로 반복 상한을 두고 그 시점의 기하를 사용하되 "
     "도달한 에너지 변화량을 함께 기록한다. 따라서 결과는 정밀한 기하 값이 "
     "아니라 심한 불안정성의 선별로 읽어야 하며, 특히 saIm075는 문턱을 "
     "0.26%p 초과해 탈락했으므로 그 마진이 프로토콜 불확실성보다 작은 경계 "
     "사례다.", False)])
note(doc, "[진행 중] 반복 상한을 2배·3배로 늘린 민감도 시험이 수행 중이며, "
          "기준선이 함께 움직이므로 무치환 모체를 같은 조건에서 동시에 계산한다. "
          "이 시험은 판정을 바꾸기 위한 것이 아니라 경계값의 프로토콜 민감도를 "
          "정량화하기 위한 것이다.")

# ─────────────────────────────────────────── 9. 조성 격자
h1(doc, "9. 조성 격자 — 두 경계가 겹치는 구간")
rich(doc, [
    ("세 축의 경계가 모두 치환율 50%와 75% 사이에 놓인다. 흡착이 목표대 문턱을 "
     "넘는 지점(29.51과 31.42 사이), 구조가 안정성 관문을 넘지 못하는 지점"
     "(13.75%와 20.26% 사이), 습윤 성능이 꺾이기 시작하는 지점이 모두 같은 "
     "구간이다. 25% 간격의 조성 축으로는 이 구간 안에서 아무것도 말할 수 없다.",
     False)])
rich(doc, [
    ("치환 자리가 24개이므로 이 구간의 격자점은 다섯 개(12/24~18/24)뿐이다. "
     "그중 58.3%(14자리), 62.5%(15자리), 66.7%(16자리)와 대조를 위한 "
     "87.5%(21자리)를 선정해 구조를 생성하고 조성 개수·충돌·고아 원자 검사를 "
     "통과시켰다. 62.5%가 흡착 목표대와 안정성 관문을 동시에 넘는지가 현재 "
     "남은 물음이다.", False)])
note(doc, "[진행 중] 격자 4종의 기하 이완이 완료 단계이며, 이어서 전하 산출 → "
          "GCMC → 안정성 관문 → 습윤 작업 용량 순으로 동일 프로토콜에서 평가한다. "
          "결과는 표 3·5·6과 같은 형식으로 이 절에 추가한다. 두 문턱을 동시에 "
          "넘는 조성이 없을 경우 그것 또한 결론이며, 술폰산 단독 치환으로는 이 "
          "목표대에서 안정한 구조를 얻을 수 없다는 진술이 된다.")

# ─────────────────────────────────────────── 10. 종합
h1(doc, "10. 종합 논의")
rich(doc, [
    ("네 축의 결과를 겹쳐 놓으면 최적 조성이 축마다 이동한다. 건조 흡착에서는 "
     "치환율이 높을수록 좋고, 습윤 작업 용량에서는 75%가 최적이며, 구조 "
     "안정성에서는 50%까지만 통과한다. ", False),
    ("현재까지 세 축을 동시에 만족하는 조성은 없다.", True),
    (" 이는 실패가 아니라 이 물질군의 설계 공간이 좁다는 정량적 진술이며, "
     "각 축의 판정 기준을 계산 전에 등록했기 때문에 그렇게 말할 수 있다.",
     False)])
table(doc, [
    ["조성", "Q_st 목표대", "습윤 WC 순위", "안정성 관문"],
    ["saIm025", "미달 (27.97)", "—", "통과"],
    ["saIm050", "미달 (29.51)", "3위 (0.768)", "통과"],
    ["saIm075", "충족 (31.42)", "1위 (0.833)", "탈락 (20.26%)"],
    ["saIm100", "충족 (34.01)", "4위 (0.688)", "탈락 (22.50%)"],
    ["saIm0625", "[진행 중]", "[진행 중]", "[진행 중]"],
], widths=[3.0, 3.6, 3.4, 3.6], caption="표 7. 세 축의 교차 판정")
rich(doc, [
    ("이 패턴은 본 계열에 국한되지 않는다. 혼합 링커 MOF에서 친수성 작용기의 "
     "물 경쟁이 CO₂ 친화도 이득을 상쇄해 건조 조건의 순위가 습윤에서 뒤집히는 "
     "사례가 보고되어 있고, 대규모 스크리닝에서도 성능 상위 후보 상당수가 "
     "안정성 지표에서 탈락한다. 또한 원자 수준의 흡착 지표들이 공정 수준 "
     "성능을 잘 예측하지 못한다는 결과가 보고되어 있으며, 본 연구가 Q_st가 "
     "아니라 습윤 작업 용량으로 순위를 판단한 것은 그 지적과 같은 방향이다.",
     False)])
rich(doc, [
    ("saIm100에서 나타난 세 가지 이상 징후 — 공동 축소, 물/CO₂ 몰비의 급증, "
     "승온 재생에서의 물 잔류 — 는 서로 독립적으로 나타난 것이 아니라 같은 "
     "조성에서 동시에 나타난다. 혼합 링커 골격이 고치환 영역에서 다른 상으로 "
     "전이한다는 보고를 고려하면, 이는 점진적 악화가 아니라 완전 치환 근처의 "
     "질적 전이로 읽는 편이 정합적이다.", False)])

# ─────────────────────────────────────────── 11. 결론
h1(doc, "11. 결론과 향후 과제")
rich(doc, [
    ("gme 위상 ZIF-69에 술폰산을 부분 치환하면 흡착열이 22.4에서 34.0 kJ/mol "
     "까지 증가하며 목표대에 진입한다. 그러나 같은 작용기가 물을 함께 끌어들여 "
     "습윤 조건의 최적 조성은 75%로 이동하고, 공동 축소로 인해 구조 안정성 "
     "관문은 50%까지만 통과한다. 세 경계가 모두 50~75% 구간에 모여 있어 그 "
     "구간의 조성 격자가 결론을 정한다.", False)])
para(doc, "향후 과제", size=11, bold=True, space_before=4, space_after=3)
for t in [
    "조성 격자 4종의 전 축 평가 완료 — 62.5%가 두 문턱을 동시에 넘는지 확인",
    "v3 세대 수분 경쟁 전 구간 스캔과 물 헨리 상수 산출, 문헌 상관축 위에서의 검증",
    "안정성 관문의 단일 지표 의존 해소 — 기계적 안정성 등 직교 지표 추가",
    "술폰산과 소수성 공-링커를 함께 도입하는 삼원 다변량 설계 검토",
    "합성 시료의 분광 검증 — 투입 조성이 결정 내 조성으로 그대로 옮겨지는지",
]:
    p = para(doc, "· " + t, size=10.5, indent=0.5, space_after=2)

# ─────────────────────────────────────────── 참고문헌
h1(doc, "참고문헌")
refs = [
    "Banerjee, R.; Yaghi, O. M. et al. Control of Pore Size and Functionality in "
    "Isoreticular Zeolitic Imidazolate Frameworks and their CO₂ Selective Capture "
    "Properties. J. Am. Chem. Soc. 2009, 131, 3875–3877.",
    "García-Sánchez, A. et al. Transferable Force Field for Carbon Dioxide "
    "Adsorption in Zeolites. J. Phys. Chem. C 2009, 113, 8814–8820.",
    "Rick, S. W. A reoptimization of the five-site water potential (TIP5P) for use "
    "with Ewald sums. J. Chem. Phys. 2004, 120, 6085–6093.",
    "Nazarian, D.; Camp, J. S.; Chung, Y. G.; Snurr, R. Q.; Sholl, D. S. "
    "Large-Scale Refinement of Metal–Organic Framework Structures Using Density "
    "Functional Theory. Chem. Mater. 2017, 29, 2521–2528.",
    "Chanut, N.; Llewellyn, P. L. et al. Screening the Effect of Water Vapour on "
    "Gas Adsorption Performance. ChemSusChem 2017, 10, 1543–1553.",
    "Åhlén, M.; Cheung, O. et al. Selective adsorption of CO₂ and SF₆ on "
    "mixed-linker ZIF-7–8s. Chem. Eng. J. 2021, 422, 130117.",
    "Mohamed, S. A.; Jiang, J. Integrating stability metrics with high-throughput "
    "computational screening of MOFs for CO₂ capture. Commun. Mater. 2023, 4, 79.",
    "Huang, C.; van der Veen, M. A. Capturing CO₂ under Dry and Humid Conditions: "
    "When Does the Parent MOF Outperform the MTV MOF? Inorg. Chem. 2025.",
    "Kwon, O.; Rajendran, A.; Woo, T. K. Identification of MOFs for near Practical "
    "Energy Limit CO₂ Capture from Wet Flue Gases. ACS Cent. Sci. 2025.",
]
for i, r in enumerate(refs, 1):
    para(doc, f"[{i}] {r}", size=9.5, indent=0.6, space_after=2)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
doc.save(OUT)

nch = sum(len(p.text) for p in doc.paragraphs)
ntab = len(doc.tables)
ntabrow = sum(len(t.rows) for t in doc.tables)
lines = nch / 41.0 + len(doc.paragraphs) * 0.45 + ntabrow * 1.0 + ntab * 2.0
print(f"저장: {OUT}")
print(f"  문단 {len(doc.paragraphs)} · 표 {ntab}({ntabrow}행) · 본문 {nch:,}자")
print(f"  추정 줄수 {lines:.0f} → 약 {lines/47:.1f} 페이지 (47줄/쪽 기준)")
