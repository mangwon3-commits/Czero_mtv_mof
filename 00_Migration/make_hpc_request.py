"""기관 계산자원 신청용 요청서 PDF.

[방침]
    * 심사자가 5분 안에 판단할 수 있게 — 무엇을, 왜, 얼마나가 앞 한 장에 들어갑니다.
    * 규모는 세 안(최소/표준/확장)으로 나눕니다. **최소안만으로도 목적을 달성**하므로
      소규모 할당으로도 승인될 수 있게 합니다.
    * 색을 쓰지 않습니다. 인쇄와 흑백 복사를 고려합니다.
    * U+2212(빼기표)는 맑은 고딕에 없습니다. ASCII 하이픈이나 &#8211; 를 쓰세요.
"""
import os
import shutil

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (PageBreak, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

pdfmetrics.registerFont(TTFont('Malgun', '/mnt/c/Windows/Fonts/malgun.ttf'))
pdfmetrics.registerFont(TTFont('MalgunBd', '/mnt/c/Windows/Fonts/malgunbd.ttf'))
pdfmetrics.registerFontFamily('Malgun', normal='Malgun', bold='MalgunBd',
                              italic='Malgun', boldItalic='MalgunBd')

OUT = '/mnt/c/Users/mangw/Downloads/계산자원_요청서_MTV-ZIF.pdf'
BLACK = colors.black
ss = getSampleStyleSheet()
BODY = ParagraphStyle('b', parent=ss['Normal'], fontName='Malgun', fontSize=9.5,
                      leading=15, alignment=TA_JUSTIFY, textColor=BLACK, spaceAfter=5)
H1 = ParagraphStyle('h1', parent=ss['Heading1'], fontName='MalgunBd', fontSize=13.5,
                    leading=18, spaceBefore=12, spaceAfter=6, textColor=BLACK)
H2 = ParagraphStyle('h2', parent=ss['Heading2'], fontName='MalgunBd', fontSize=10.5,
                    leading=14, spaceBefore=8, spaceAfter=4, textColor=BLACK)
TITLE = ParagraphStyle('t', parent=ss['Title'], fontName='MalgunBd', fontSize=17,
                       leading=23, spaceAfter=3, textColor=BLACK)
SUB = ParagraphStyle('s', parent=BODY, fontSize=9.5, alignment=1, textColor=BLACK,
                     spaceAfter=12)
CELL = ParagraphStyle('c', parent=BODY, fontSize=8.3, leading=11, alignment=0,
                      textColor=BLACK, spaceAfter=0)
NOTE = ParagraphStyle('n', parent=BODY, fontSize=8.5, leading=12.5, leftIndent=8,
                      textColor=BLACK)

S = []


def P(t, st=BODY):
    S.append(Paragraph(t, st))


def box(t):
    tb = Table([[Paragraph(t, ParagraphStyle('bx', parent=BODY, fontSize=9.2,
                                             leading=14))]], colWidths=[166 * mm])
    tb.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 0.8, BLACK),
                            ('LEFTPADDING', (0, 0), (-1, -1), 9),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 9),
                            ('TOPPADDING', (0, 0), (-1, -1), 7),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 7)]))
    S.append(tb)
    S.append(Spacer(1, 7))


def table(rows, widths):
    data = [[Paragraph(f'<b>{c}</b>' if i == 0 else c, CELL) for c in r]
            for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
    t.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.5, BLACK),
                           ('LINEBELOW', (0, 0), (-1, 0), 1.1, BLACK),
                           ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                           ('LEFTPADDING', (0, 0), (-1, -1), 4.5),
                           ('RIGHTPADDING', (0, 0), (-1, -1), 4.5),
                           ('TOPPADDING', (0, 0), (-1, -1), 3.5),
                           ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5)]))
    S.append(t)
    S.append(Spacer(1, 8))


A = '&#197;'
CO2 = 'CO<sub>2</sub>'

# ------------------------------------------------------------------ 표지
P('계산자원 사용 요청서', TITLE)
P('MTV-ZIF 기반 CO<sub>2</sub> 포집 소재 전산 스크리닝 &#183; 2026년 8월', SUB)

box('<b>한 줄 요약</b> &#8212; 다공성 골격 <b>ZIF-69</b>의 결정 구조를 <b>주기 DFT로 '
    '기하 최적화</b>하려 합니다. 현재 쓰는 침착 구조가 <b>기하 최적화되지 않은 상태</b>'
    '(파일에 <font face="Courier">not optimized</font>로 명시)이고, 그로 인해 흡착량이 '
    '<b>5~7% 계통 오차</b>를 갖는다는 것을 자체 검증으로 확인했습니다.<br/><br/>'
    '<b>최소 요청은 구조 1종</b>이며 <b>약 5,000 core&#183;hour</b>입니다. '
    '이것만으로도 목적을 달성할 수 있습니다 &#8212; 나머지 구조는 최적화된 모체 위에 '
    '고전 힘장으로 얹으면 되기 때문입니다.')

# ------------------------------------------------------------------ 1
P('1. 무엇을 계산하려 하는가', H1)
table([
    ['항목', '내용'],
    ['계산 종류', '<b>주기 경계 조건 하의 기하 최적화</b> (geometry optimization)'],
    ['이론 수준', 'DFT / GGA-PBE + 분산력 보정(D3 또는 TS)'],
    ['최적화 범위', '<b>원자 위치만</b>. 격자상수는 실험값에 고정 &#8212; 5절 참조'],
    ['대상 물질', 'ZIF-69 = Zn(nIm)(cbIm), 육방정 <i>a</i>=<i>b</i>=26.084 ' + A
     + ', <i>c</i>=19.408 ' + A + ', &#947;=120&#176;'],
    ['단위셀 크기', '<b>600 원자</b> (Zn 24 &#183; C 240 &#183; N 120 &#183; O 48 '
     '&#183; Cl 24 &#183; H 144)'],
    ['셀 부피', '11,436 ' + A + '<sup>3</sup>'],
    ['원자가 전자', '약 <b>2,450개</b> (Zn 12e 기준) &#8594; 점유 밴드 약 1,225'],
    ['k점', '<b>&#915;점 단독으로 충분</b> &#8212; 셀이 커서 역격자가 조밀'],
    ['스핀', '비자성 (Zn<sup>2+</sup>는 d<sup>10</sup> 閉殼)'],
], [26, 139])

# ------------------------------------------------------------------ 2
P('2. 왜 필요한가', H1)
P('저희가 쓰는 결정 구조 파일에 다음이 명시되어 있습니다.')
S.append(Paragraph("<font face='Courier' size='8.5'>"
                   "_citation_special_details 'ZIF-69 removed random disorder, "
                   "<b>not optimized</b>'</font>", NOTE))
P('무질서만 제거하고 <b>기하 최적화는 하지 않은 구조</b>입니다. 실측이 그것을 '
  '뒷받침합니다.')
table([
    ['결합', '개수', '실측 범위 (' + A + ')', '폭', '이상값', '판정'],
    ['<b>C&#8211;H</b>', '<b>144</b>', '<b>0.949 ~ 0.951</b>', '0.003', '<b>1.083</b>',
     'X선 riding model 계통 오차'],
    ['C&#8211;C (방향족)', '168', '1.273 ~ 1.465', '<b>0.192</b>', '1.39',
     '공명하면 균일해야 함'],
    ['C&#8211;Cl', '24', '1.673 ~ 1.982', '<b>0.309</b>', '1.74', '과도한 분산'],
    ['Zn&#8211;N', '96', '1.970 ~ 2.002', '0.032', '1.99', '정상'],
], [24, 14, 34, 16, 18, 59])
P('C&#8211;H가 144개 <b>전부</b> 0.949이고 폭이 0.003인 것은 잡음이 아니라 계통 '
  '오차입니다. X선은 수소의 <b>전자밀도</b>를 보는데 그것이 결합 상대 쪽으로 끌려 '
  '있어 핵간거리보다 10~20% 짧게 나옵니다. 중성자 회절 기준값은 1.083 ' + A + '입니다.',
  NOTE)

box('<b>영향을 자체 검증으로 정량했습니다.</b><br/>'
    'C&#8211;H만 1.083으로 정규화해 동일 조건 A/B 계산을 돌린 결과, 헨리 상수가 '
    + CO2 + ' <b>&#8211;6.81%</b>(5.5&#963;), N<sub>2</sub> <b>&#8211;4.74%</b>'
    '(3.8&#963;) 이동했습니다.<br/><br/>'
    '<b>수소는 기공 벽면을 이루는 원자</b>이므로 ' + CO2 + '가 실제로 닿는 자리가 '
    '0.134 ' + A + ' 안쪽에 박혀 있으면 기공이 그만큼 넓게 보입니다. 즉 '
    '<b>흡착량이 5~7% 과대평가</b>돼 있습니다.<br/><br/>'
    '조성 간 <b>순위는 영향받지 않으나</b>(두 기체가 같은 방향으로 이동해 선택도에서 '
    '상쇄, 1.2&#963;), <b>절대값을 보고하려면 최적화된 구조가 필요합니다.</b>')

S.append(PageBreak())

# ------------------------------------------------------------------ 3
P('3. 자체 자원으로 시도한 것과 그 한계', H1)
P('기관 자원을 요청하기 전에 보유 장비(8코어 데스크탑)에서 가능한 방법을 먼저 '
  '소진했습니다.')
table([
    ['방법', '결과', '판정'],
    ['<b>고전 힘장</b> UFF4MOF (LAMMPS)', '17종 <b>전부 수렴 실패</b>. 최종 에너지 '
     '변화가 수렴 기준(1&#215;10<sup>-4</sup>)보다 4~5자릿수 크고, 계산 시간을 '
     '늘려도 수렴하지 않고 <b>진동</b>', '사용 불가'],
    ['<b>반경험적</b> GFN-FF / GFN0 (xtb)', '주기 계산 가능. 모체 1종 시험 진행 중',
     '검증 중'],
    ['<b>DFT</b>', '미설치. 600원자 주기 최적화는 가정용 장비 범위를 초과',
     '<b>기관 자원 필요</b>'],
], [40, 90, 35])
P('고전 힘장이 실패하는 이유는 원리적입니다. 이완이 고치려는 것 &#8212; 방향족 고리의 '
  '결합 길이가 공명으로 균일해지는 현상 &#8212; 은 <b>파이 전자가 고리 전체에 '
  '비국재화</b>되기 때문인데, 고전 힘장은 그것을 경험식으로 흉내 낼 뿐 '
  '<b>전자를 풀지 않습니다.</b>', NOTE)

# ------------------------------------------------------------------ 4
P('4. 요청 규모 &#8212; 세 안', H1)
P('<b>최소안만으로 목적을 달성할 수 있습니다.</b> 치환 구조는 최적화된 모체 위에 '
  '고전 힘장으로 얹는 것이 이 분야의 표준 절차이므로, 모체 1종이 핵심입니다.')
table([
    ['안', '대상', '추정 core&#183;hour', '벽시계 (128코어 기준)', '비고'],
    ['<b>최소</b>', '모체 1종', '<b>약 5,000</b>', '약 1.5~2일',
     '<b>이것만으로 충분</b>'],
    ['표준', '모체 + 대표 치환 3종', '약 20,000', '약 1주',
     '힘장 근사의 타당성 교차검증'],
    ['확장', '전 조성 30종', '약 150,000', '약 3~4주',
     '전수 확인. 필수 아님'],
], [12, 36, 27, 33, 57])
P('추정 근거: 600원자 &#183; &#915;점 &#183; 평면파 500~600 eV 기준 SCF 1회가 '
  '128코어에서 약 20분(&#8776;42 core&#183;hour), 이온 완화 100~150 스텝을 가정했습니다. '
  '코드와 알고리즘(특히 CP2K의 GPW)에 따라 <b>2~3배 줄어들 수 있습니다.</b>', NOTE)

P('4-1. 하드웨어 요구', H2)
table([
    ['항목', '요구'],
    ['코어', '64~128 (MPI). 그 이상은 이 크기에서 확장 효율이 떨어집니다'],
    ['메모리', '<b>노드 합계 200~400 GB</b> (코어당 2~4 GB)'],
    ['저장', '작업당 50~100 GB (파동함수 재시작 파일 포함)'],
    ['실행 시간', '단일 작업 <b>48시간</b> 큐면 충분. 재시작 지원되면 24시간도 가능'],
    ['GPU', '불필요 (있으면 CP2K/QE 가속 가능하나 전제하지 않음)'],
], [22, 143])

P('4-2. 소프트웨어 &#8212; 우선순위 순', H2)
table([
    ['코드', '라이선스', '이 계산에 대한 적합성'],
    ['<b>CP2K</b>', '무료 (GPL)', '<b>1순위.</b> Gaussian&#183;평면파 혼합(GPW)이라 '
     '수백 원자 계에서 순수 평면파보다 훨씬 빠릅니다. MOF 최적화에 널리 쓰입니다'],
    ['<b>Quantum ESPRESSO</b>', '무료 (GPL)', '2순위. 표준적이고 안정적. '
     'PW 방식이라 CP2K보다 비용이 큽니다'],
    ['VASP', '유상', '기관에 라이선스가 있으면 사용 가능. 없으면 위 둘로 충분합니다'],
], [26, 24, 115])
P('<b>무료 코드로 충분하므로 라이선스 문제는 없습니다.</b> 계산에 필요한 입력 파일은 '
  '저희가 준비해 제출하겠습니다.', NOTE)

S.append(PageBreak())

# ------------------------------------------------------------------ 5
P('5. 계산 설정 &#8212; 심사에 필요한 세부', H1)
table([
    ['항목', '값', '근거'],
    ['범함수', 'PBE (GGA)', 'MOF 구조 최적화의 표준'],
    ['분산력 보정', '<b>D3(BJ) 또는 TS</b>', '<b>필수.</b> 기공을 다루므로 반데르발스가 '
     '구조를 좌우합니다. 빼면 격자가 팽창합니다'],
    ['k점 격자', '<b>&#915;점 단독</b>', '셀 최단축이 19.4 ' + A + '로 역격자가 조밀'],
    ['평면파 컷오프', '500~600 eV (또는 CP2K 400~600 Ry)', '수렴 시험 후 확정'],
    ['의사퍼텐셜', 'PAW 또는 GTH', '코드에 따름'],
    ['스핀 편극', '<b>불필요</b>', 'Zn<sup>2+</sup>는 d<sup>10</sup>. Co 유사체를 '
     '넣을 경우에만 필요'],
    ['수렴 기준', '힘 &lt; 0.02 eV/' + A + ', 에너지 1&#215;10<sup>-6</sup> eV',
     '일반적 기준'],
    ['<b>격자 최적화</b>', '<b>하지 않음 (고정)</b>', '아래 참조'],
], [24, 46, 95])

box('<b>격자상수를 고정하는 이유</b> &#8212; 이 요청의 목적은 <b>결합 길이와 수소 '
    '위치를 고치는 것</b>이지 격자를 다시 정하는 것이 아닙니다. 격자상수는 X선 회절이 '
    '가장 정확하게 주는 양이므로, 계산에 맡기면 <b>실측 정보를 계산 오차로 '
    '덮어쓰는 셈</b>이 됩니다. PBE는 격자를 수 % 과대평가하는 경향이 알려져 있고, '
    '그러면 기공 크기가 통째로 이동해 흡착 계산이 오히려 나빠집니다.<br/><br/>'
    '따라서 <b>원자 위치만 이완</b>합니다. 이는 계산 비용도 크게 줄입니다.')

# ------------------------------------------------------------------ 6
P('6. 산출물과 활용', H1)
table([
    ['산출물', '용도'],
    ['최적화된 원자 좌표 (CIF)', '이후 모든 GCMC 흡착 계산의 입력 구조'],
    ['최종 힘 · 에너지 · 수렴 이력', '최적화가 실제로 수렴했는지의 증거'],
    ['(선택) 부분전하', 'DDEC6 등으로 정전기 항을 개선. 필수는 아님'],
], [45, 120])
P('결과는 <b>공개 저장소에 계산 스크립트와 함께 기록</b>되며, 이 프로젝트의 모든 '
  '중간 결과와 실패 사례도 같은 방식으로 문서화하고 있습니다.', NOTE)

# ------------------------------------------------------------------ 7
P('7. 일정', H1)
table([
    ['시점', '내용'],
    ['현재', '자체 자원으로 GCMC 흡착 계산 진행 중 (v2 재계산 마무리 단계)'],
    ['<b>8월 21일</b>', '<b>결정 필요 시점</b> &#8212; 이후로는 전체 일정이 1:1로 밀립니다'],
    ['승인 후 1~2주', 'DFT 최적화 수행 및 검증'],
    ['그 후 1~2주', '최적화 구조로 전체 흡착 계산 재수행'],
], [26, 139])
P('반경험적 방법(GFN-FF) 시험이 진행 중이며, <b>그것이 성공하면 이 요청은 '
  '철회하겠습니다.</b> 결과는 수일 내 확인됩니다.', NOTE)

# ------------------------------------------------------------------ 8
P('8. 배경 &#8212; 연구의 성격', H1)
P('배가스 조건(' + CO2 + ' 0.15 bar, 298 K)에서 CO<sub>2</sub>를 포집하는 다공성 '
  '소재를 전산으로 탐색하고 있습니다. 골격 ZIF-69의 링커에 작용기를 도입해 흡착 '
  '성능을 조절하는 MTV(multivariate) 전략이며, 흡착 성능 &#183; 수분 경쟁 &#183; '
  '작업 용량 &#183; 재생 에너지의 네 관문으로 판정합니다.')
P('현재까지 등량 흡착 엔탈피 <b>21 &#8594; 34 kJ/mol</b>, ' + CO2 + '/N<sub>2</sub> '
  '선택도 <b>18 &#8594; 231</b>까지 조절했으며, 작업 용량 기준 최적 조성을 확정하는 '
  '단계입니다. 실험 협력(분광 검증)도 별도로 진행 중입니다.')
P('본 요청은 그 계산들이 딛고 선 <b>입력 구조 자체의 품질 문제</b>를 해결하기 '
  '위한 것입니다.', NOTE)


def footer(canv, d):
    canv.saveState()
    canv.setFont('Malgun', 7.5)
    canv.setFillColor(BLACK)
    canv.drawRightString(A4[0] - 22 * mm, 11 * mm, str(canv.getPageNumber()))
    canv.drawString(22 * mm, 11 * mm, '계산자원 사용 요청서 · MTV-ZIF CO2 포집 전산 스크리닝')
    canv.restoreState()


TMP = '/tmp/_hpc_build.pdf'
doc = SimpleDocTemplate(TMP, pagesize=A4, leftMargin=22 * mm, rightMargin=22 * mm,
                        topMargin=20 * mm, bottomMargin=18 * mm,
                        title='계산자원 사용 요청서 — MTV-ZIF CO2 포집 전산 스크리닝',
                        author='')
doc.build(S, onFirstPage=footer, onLaterPages=footer)

written = None
stem, ext = os.path.splitext(OUT)
for cand in [OUT] + [f'{stem}_{n}{ext}' for n in range(2, 20)]:
    try:
        shutil.copyfile(TMP, cand)
        written = cand
        break
    except PermissionError:
        continue
if written is None:
    raise SystemExit(f'모든 후보 경로가 잠겨 있습니다: {OUT}')
print('생성:', written, os.path.getsize(written), 'bytes')
