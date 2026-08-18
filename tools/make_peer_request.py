"""지인 계산 지원 요청 명세서 PDF.

[기관 요청서와 무엇이 다른가]
    앞서 만든 `계산자원_요청서_MTV-ZIF.pdf` 는 **심사자를 설득하는** 문서였습니다.
    이것은 다릅니다. 상대가 그대로 **실행할 수 있어야** 합니다. 그래서

      * 정당화보다 명세를 앞세웁니다 -- 무엇을, 어떤 설정으로, 무엇을 돌려받는지
      * 규약의 고정값을 전부 적습니다. 하나라도 다르면 우리 값과 못 합칩니다
      * 상대가 **하지 않아도 되는 일**을 분명히 적습니다(전하 계산 등)
      * 우리가 실제로 데인 함정을 미리 넘깁니다(Zeo++ 메모리, 최소 이미지 규약)

    그리고 기관 DFT 요청의 전제가 바뀌었습니다. GFN-FF 셀 고정 이완이 사전
    등록 기준을 통과했으므로(08-16) **모체 이완용 DFT 는 더 이상 급하지
    않습니다.** 지금 무거운 것은 DFT 가 아니라 **물이 낀 GCMC** 입니다.

[방침]
    색을 쓰지 않습니다. 박스와 글자 모두 검정 하나입니다.
    U+2212(빼기표)는 맑은 고딕에 없습니다. ASCII 하이픈을 씁니다.
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

# 기본은 다운로드 폴더. 다만 그 파일이 뷰어로 열려 있으면 윈도우가 잠가서
# PermissionError 가 나고 `_2.pdf` 같은 이름으로 빠집니다(실제로 겪었습니다).
# 전달 꾸러미를 만들 때는 PEER_PDF_OUT 으로 꾸러미 안을 직접 가리켜, 잠긴
# 파일과 아예 마주치지 않게 합니다.
OUT = os.environ.get('PEER_PDF_OUT',
                     '/mnt/c/Users/mangw/Downloads/계산지원_요청명세_MTV-ZIF.pdf')
REPO = 'https://github.com/mangwon3-commits/Czero_mtv_mof'
Z = '/home/mangwon1/mof_project/21_ZIF69_MTV'

# 구조 개수를 문서에 손으로 적지 않습니다. 만들 때마다 실제 폴더를 셉니다 --
# 손으로 적은 숫자는 반드시 어느 시점엔가 실제와 어긋납니다.
try:
    N_CIF = len([f for f in os.listdir(os.path.join(Z, 'charged_v3'))
                 if f.endswith('_DDEC6.cif')])
except OSError:
    N_CIF = 0
N_TXT = f'{N_CIF}개' if N_CIF else '31개(예정)'
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
MONO = ParagraphStyle('m', parent=BODY, fontName='Courier', fontSize=8.2,
                      leading=11.5, textColor=BLACK, spaceAfter=0)

S = []
A = '&#197;'          # 옹스트롬


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


def code(lines):
    tb = Table([[Paragraph('<br/>'.join(lines), MONO)]], colWidths=[166 * mm])
    tb.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 0.6, BLACK),
                            ('LEFTPADDING', (0, 0), (-1, -1), 8),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                            ('TOPPADDING', (0, 0), (-1, -1), 6),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 6)]))
    S.append(tb)
    S.append(Spacer(1, 8))


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


# ==================================================================== 1쪽
P('계산 지원 요청 명세', TITLE)
P('MTV-ZIF 이종 링커 CO<sub>2</sub> 포집 스크리닝 &#183; 2026-08-17', SUB)

P('1. 한 장 요약', H1)
box('<b>요청의 핵심은 코어 시간이지 저장 공간이 아닙니다.</b> 보내 드릴 입력 '
    '전체가 <b>1.4 MB</b>(CIF 31개 + 정의 파일 몇 개)이고, 돌려받을 것도 '
    '추출 후 <b>1 MB 미만</b>입니다. 무거운 것은 오직 계산 시간입니다.')

P('저희 쪽 기기는 물리 8코어이고 지금 포화 상태로 돌고 있습니다. 문제는 총량이 '
  '아니라 <b>한 작업의 길이</b>입니다. 물이 낀 이성분 GCMC 는 한 건이 실측으로 '
  '1.5~20.2시간이며(아래 3절), 20건을 8코어로 돌리면 벽시계로 며칠이 걸립니다. '
  '작업끼리 완전히 독립이라 코어만 늘면 그대로 선형으로 줄어듭니다.', BODY)

P('요청 항목은 네 가지이고, <b>A 하나만 받아도 목적을 달성</b>합니다.', BODY)
table([['', '항목', '작업 수', '예상 코어시간', '우선'],
       ['A', '수분 경쟁 v3 &#8211; 이완 구조에서 RH 0/25/50/90% 재계산',
        '20', '약 190', '최우선'],
       ['B', '조성 격자 세분 &#8211; 비단조 구간(50~100%) 해상',
        '24', '약 15', '높음'],
       ['C', '습윤 작업 용량 v3 &#8211; 흡착/탈착 두 조건',
        '24', '약 220', '중간'],
       ['D', 'DFT 단일점 검증 &#8211; 힘장 편향 확인(선택)',
        '3', '약 300~1,500', '낮음']],
      [8, 84, 18, 30, 22])

P('A+B 만 받으면 약 <b>205 코어시간</b>입니다. 32코어 노드 하나에서 <b>약 7시간</b>, '
  '전부(A~C) 받아도 <b>약 14시간</b>입니다. D 는 성격이 달라 별도로 적었습니다.', BODY)

P('2. 배경 &#8211; 왜 이 계산이 필요한가', H1)
P('ZIF-69 골격에 두 종류의 링커를 섞어(MTV) 저농도 CO<sub>2</sub>(0.15 bar, 298 K) '
  '흡착 성능을 올리는 것이 목표입니다. 흡착열 30~40 kJ/mol 구간을 노립니다.', BODY)
P('건조 조건 결과는 이미 나와 있습니다. 그런데 <b>실제 배가스에는 물이 있고, '
  '물은 CO<sub>2</sub>보다 강한 흡착질입니다.</b> 저희 v2 계산에서 상대습도 90%일 때 '
  '물이 CO<sub>2</sub>를 밀어내는 정도가 조성에 따라 크게 달랐습니다. 이 경향이 '
  '구조 이완 뒤에도 유지되는지가 이번 연구의 결론을 좌우합니다.', BODY)
box('<b>지금 다시 계산해야 하는 이유:</b> 자체 감사에서 결정구조 파일의 기하가 '
    '힘장의 최소점이 아니라는 것이 드러났습니다(X선 라이딩 모델 때문에 C-H 가 '
    f'0.949 {A}, 중성자 실측은 1.083 {A}). 이것만으로 헨리 상수가 4.7~6.8% '
    '움직였습니다. 반경험적 힘장(GFN-FF)으로 <b>셀을 고정한 채 원자만 이완</b>해 '
    f'C-H 를 1.077 {A} 로 바로잡았고, 그 위에서 전부 다시 계산하는 중입니다. '
    '건조 조건은 저희가 처리하고 있고, <b>물이 낀 계산만 감당이 안 됩니다.</b>')

S.append(PageBreak())

# ==================================================================== 2쪽
P('3. 왜 물이 낀 계산만 무거운가 &#8211; 실측값', H1)
P('추정이 아니라 저희가 잰 값입니다(RASPA 는 작업당 단일 스레드).', BODY)
table([['계산 종류', '작업당 벽시계', '비고'],
       ['건조 단일성분 GCMC', '약 35분', '작업 용량 v2, 20작업 실측'],
       ['물+CO<sub>2</sub> 이성분 GCMC', '<b>1.5 ~ 20.2시간</b>',
        '수분 경쟁 v2, 20작업 실측. <b>편차 13배</b>'],
       ['Widom 삽입(헨리 상수)', '약 10분', '기체당']],
      [45, 35, 82])
P('물이 4배가 아니라 <b>최대 35배</b> 비싼 이유는 두 가지입니다. 첫째, 물 모델이 '
  'TIP5P-Ew 로 <b>한 분자당 상호작용 자리가 5개</b>입니다(산소 1 + 수소 2 + 가상전하 2). '
  '둘째, 그 자리가 전부 전하를 가져 <b>Ewald 합</b>에 들어갑니다. 습도가 높고 '
  '치환율이 높을수록 상자 안 분자 수가 늘어 비용이 급격히 커집니다.', BODY)
box('<b>일정을 잡으실 때:</b> 작업 길이가 13배 차이 나므로 <b>비싼 것부터 큐에 '
    '넣어 주십시오</b>(RH 90% &#215; 치환율 100% 조합이 가장 비쌉니다). 저희는 '
    '격자 순서로 넣었다가 마지막에 가장 비싼 두 건만 남아 코어 6개가 노는 '
    '상황을 겪었습니다. 표준 makespan 휴리스틱(LPT)이면 피할 수 있습니다.')

P('4. 요청 항목 상세', H1)

P('A. 수분 경쟁 v3 &#8212; 최우선', H2)
P('구조 5종(무치환 모체 + 술폰산 치환 25/50/75/100%) &#215; 상대습도 4단계'
  '(0 / 25 / 50 / 90%) = <b>20작업</b>. CO<sub>2</sub> 분압은 0.15 bar 고정, '
  '298 K. 물의 분압은 298 K 포화증기압 3169 Pa 에 습도를 곱해 넣습니다.', BODY)
P('산출: 조성별 CO<sub>2</sub>/H<sub>2</sub>O 흡착량 [mol/kg]. 저희는 이것으로 '
  '<b>습도에 따른 CO<sub>2</sub> 유지율</b>을 뽑습니다.', BODY)

P('B. 조성 격자 세분 &#8212; 비단조 구간 해상', H2)
box('이 항목이 <b>과학적으로 가장 값집니다.</b> 저희 v2 결과에서 예상 밖의 일이 '
    '있었습니다. 온도 스윙 회수율이 치환율에 대해 <b>단조롭지 않았습니다</b> '
    '(87.1% &#8594; 83.5% &#8594; 77.4%, 75%에서 꺾임). 흡착열 하나로 설명되는 '
    '모델이라면 나올 수 없는 모양이라, 흡착 자리 분포의 꼬리가 관여한다는 뜻입니다. '
    '지금 격자가 25% 간격이라 <b>꺾이는 지점을 짚을 수 없습니다.</b>')
P('50~100% 구간을 12.5% 간격으로 채웁니다 &#8212; 치환율 62.5 / 87.5% 를 2개 계열'
  '(saIm, mslm)에 대해 추가. 구조당 Widom CO<sub>2</sub> + Widom N<sub>2</sub> + '
  'GCMC 3작업이므로 <b>4구조 &#215; 3 = 12작업</b>, 여기에 각 구조의 건조 작업 용량'
  '(흡착/탈착 2조건) 12작업을 더해 <b>24작업</b>입니다. 전부 건조라 값쌉니다.', BODY)

P('C. 습윤 작업 용량 v3', H2)
P('A 와 같은 5구조를, 흡착 조건(298 K)과 탈착 조건(TSA 373 K / VSA 감압) 두 가지에서 '
  '물을 포함해 계산합니다. 실제 공정에서 <b>한 사이클에 실제로 회수되는 양</b>을 '
  '주는 값이라 흡착량보다 현실적입니다. 물이 끼므로 A 와 같은 비용대입니다.', BODY)

P('D. DFT 단일점 검증 &#8212; 선택 항목', H2)
P('저희가 쓴 GFN-FF 가 방향족 C-C 와 Zn-N 은 잘 맞췄지만, <b>아릴-치환기 단일결합을 '
  f'짧게</b> 잡는 편향이 보였습니다(나이트릴 1.393 {A} vs 문헌 1.451 {A}, 약 4%). '
  '판정 기준에 없던 항목이라 결론을 바꾸지는 않았지만, 값을 해석할 때 알고 봐야 '
  '합니다. 구조 3종(모체 + 나이트릴 100% + 술폰산 100%)에 대해 <b>단일점 계산</b>만 '
  '해 주시면 결합 길이 편향의 크기를 확정할 수 있습니다. 구조 최적화까지는 '
  '필요 없습니다.', BODY)

S.append(PageBreak())

# ==================================================================== 3쪽
P('5. 소프트웨어와 규약 &#8212; 하나라도 다르면 합칠 수 없습니다', H1)
box('<b>가장 중요한 부탁입니다.</b> 아래 값은 저희 기존 계산과 <b>같아야만</b> '
    'v2 대비 변화를 "구조 이완 때문" 이라고 말할 수 있습니다. 설정까지 함께 바뀌면 '
    '구조 때문인지 설정 때문인지 영원히 구별할 수 없습니다. 성능을 위해 바꾸고 '
    '싶은 값이 있으면 <b>바꾸지 마시고 알려만 주십시오.</b>')
table([['항목', '고정값'],
       ['엔진', 'RASPA 2.0.50 (2.0.4x 계열이면 동일 결과 확인됨)'],
       ['앙상블', '&#956;VT (GCMC). 헨리 상수는 Widom 삽입'],
       ['사이클', '초기화 5,000 + 생산 15,000'],
       ['골격 힘장', 'UFF_MOF (RASPA 배포본 그대로)'],
       ['CO<sub>2</sub> 모델',
        '<b>Garc&#237;a-S&#225;nchez 2009</b> (q<sub>C</sub> +0.6512, '
        '&#949;/k<sub>B</sub> 29.933 K, &#963; 2.745 {A}). TraPPE 아님'],
       ['물 모델', 'TIP5P-Ew (5자리, &#949;/k<sub>B</sub> 89.633 K, '
        f'&#963; 3.097 {A}, q 0.241)'],
       ['골격 전하', '<b>PACMAN DDEC6 &#8212; CIF 에 이미 들어 있습니다</b>'],
       ['정전기', f'Ewald, 정밀도 1e-6'],
       ['컷오프', f'12 {A}'],
       ['단위셀', '2 &#215; 2 &#215; 2 (아래 6절 참조)'],
       ['온도/압력', '298 K, CO<sub>2</sub> 0.15 bar (D 항목 제외)']],
      [30, 136])
P('<b>상대 쪽에서 하지 않으셔도 되는 일:</b> 전하 계산(이미 CIF 안에 있습니다), '
  '구조 최적화(끝냈습니다), 힘장 파라미터 조정, 물 정의 파일 작성(같이 보냅니다).', BODY)

P('6. 저희가 데인 함정 &#8212; 미리 넘기시라고 적습니다', H1)

P('(1) 단위셀을 2&#215;2&#215;2 로 두는 이유 &#8212; 최소 이미지 규약', H2)
P(f'ZIF-69 단위셀은 a=b=26.084 {A}, c=19.408 {A}, &#947;=120&#176; 입니다. '
  f'컷오프 12 {A} 를 쓰려면 셀의 <b>수직 폭</b>이 24 {A} 를 넘어야 합니다. '
  '2&#215;2&#215;2 로 늘리면 수직 폭이 45.18 / 45.18 / 38.82 가 되어 조건을 '
  '만족합니다. <b>1&#215;1&#215;1 로 돌리면 같은 원자의 복사본 둘과 동시에 '
  '상호작용해 에너지가 이중계산됩니다.</b> 저희가 08-04 에 이 버그로 계산 전량을 '
  '폐기했습니다.', BODY)

P('(2) 기공 분석(Zeo++)을 같이 돌리실 경우', H2)
P('저희 쪽에서는 필요 없습니다만, 혹시 돌리신다면 <b>network 한 건이 약 3.2 GB</b> '
  '를 씁니다. RASPA 와 동시에 병렬로 띄웠다가 OOM 이 나고 dbus 까지 죽어 배포판이 '
  '통째로 멈춘 적이 있습니다. 메모리 여유를 보고 워커 수를 잡아 주십시오.', BODY)

P('(3) 진행 상황이 안 보이는 것은 정상입니다', H2)
P('RASPA 의 <font face="Courier">PrintEvery</font> 를 생산 사이클 수와 같게 두면 '
  '출력 파일이 <b>처음과 끝에만</b> 갱신됩니다. 몇 시간 동안 파일이 그대로여도 '
  '멈춘 것이 아닙니다. 진행을 보고 싶으시면 이 값을 1000 정도로 낮추셔도 '
  '<b>결과에는 영향이 없습니다</b>(출력 빈도만 바뀝니다).', BODY)

S.append(PageBreak())

# ==================================================================== 4쪽
P('7. 주고받을 것', H1)

P('저희가 보내 드리는 것 (약 1.4 MB)', H2)
table([['파일', '내용'],
       ['<font face="Courier">cif/</font> (31개)',
        '이완 완료 + DDEC6 전하가 들어간 골격 구조. 이것이 입력의 전부입니다'],
       ['<font face="Courier">def/water.def</font>',
        'TIP5P-Ew 5자리 물 정의(RASPA 배포본의 3자리 TraPPE 와 다릅니다)'],
       ['<font face="Courier">def/CO2.def, N2.def</font>',
        'Garc&#237;a-S&#225;nchez CO<sub>2</sub> 및 N<sub>2</sub> 정의'],
       ['<font face="Courier">force_field_mixing_rules.def</font>',
        'UFF_MOF + 위 기체들의 혼합 규칙'],
       ['<font face="Courier">templates/*.input</font>',
        '작업별 <font face="Courier">simulation.input</font> 견본(값이 다 채워져 있습니다)'],
       ['<font face="Courier">run_batch.sh</font>',
        '작업 목록을 만들고 병렬로 돌리는 스크립트. 워커 수만 인자로 받습니다'],
       ['<font face="Courier">README.md</font>',
        '실행 한 줄, 규약 표, 돌려주실 파일 목록']],
      [50, 116])

P('돌려받고 싶은 것', H2)
P('둘 중 편하신 쪽이면 됩니다.', BODY)
table([['방식', '무엇을', '크기'],
       ['<b>권장</b>',
        '동봉한 <font face="Courier">extract.py</font> 를 돌려 나온 '
        '<font face="Courier">results.json</font> 하나',
        '약 100 KB'],
       ['대안',
        '각 작업 폴더의 <font face="Courier">Output/System_0/*.data</font> '
        '(압축해서). 저희가 직접 추출하겠습니다',
        '압축 후 약 60 MB']],
      [22, 110, 34])
box('<b>실패한 작업도 알려 주십시오.</b> 저희 쪽에서 가장 자주 겪은 사고 유형이 '
    '<b>"실패가 결과처럼 보이는 것"</b> 이었습니다. 중간에 죽은 RASPA 출력도 '
    '30 MB 를 남기기 때문에 파일 크기로는 구별되지 않습니다. 로그에 '
    '<font face="Courier">Simulation finished</font> 가 없거나 종료 코드가 0 이 '
    '아닌 작업이 있으면 <b>목록만 주시면</b> 저희가 다시 돌리겠습니다. '
    '무리해서 채워 주실 필요 없습니다.')

P('8. 일정과 규모 정리', H1)
table([['시나리오', '작업', '코어시간', '32코어 노드 기준 벽시계'],
       ['최소 (A)', '20', '약 190', '약 6시간'],
       ['권장 (A+B)', '44', '약 205', '약 7시간'],
       ['전체 (A+B+C)', '68', '약 425', '약 14시간'],
       ['+ DFT (D)', '+3', '+300~1,500', '자원에 따라 크게 다름']],
      [28, 18, 30, 90])
P('작업끼리 완전히 독립이므로 코어 수에 대해 선형으로 줄어듭니다. 노드 하나를 '
  '하룻밤 빌려 주시는 정도면 A~C 가 전부 끝납니다. 부분만 받아도 그 부분은 '
  '그대로 씁니다 &#8212; <b>나눠서 주셔도 됩니다.</b>', BODY)

P('9. 회신 시 알려 주시면 좋은 것', H1)
table([['', '항목'],
       ['1', '가용 코어 수와 대략의 기간 (며칠 안에 몇 코어)'],
       ['2', 'RASPA 설치 여부. 없으면 저희가 빌드 절차를 정리해 보내겠습니다'],
       ['3', '작업 스케줄러 종류(SLURM/PBS/직접 실행). 제출 스크립트를 맞춰 드립니다'],
       ['4', '파일 전달 방법(클라우드 링크 / 저장매체 / 저장소 접근)'],
       ['5', '결과 사용에 대해 원하시는 표기 &#8212; 사사 표기, 공저, 또는 표기 없음']],
      [10, 156])
box('결과는 연구 기록(공개 저장소와 문서)에 남고, 어떤 계산이 어디서 돌았는지 '
    '함께 적습니다. 표기 방식은 <b>전적으로 원하시는 대로</b> 하겠습니다.')

S.append(PageBreak())

# ==================================================================== 5쪽
P('10. 연결 방법 &#8212; 결과를 어떻게 주고받나', H1)
P('세 가지 중 <b>편하신 것 하나만</b> 고르시면 됩니다. 아래로 갈수록 간단하고, '
  '위로 갈수록 이력이 잘 남습니다. <b>어느 쪽이든 저희가 맞추겠습니다.</b>', BODY)

P('방식 1. 저장소 협업자 &#8212; 이력이 가장 잘 남습니다', H2)
P(f'저장소: <font face="Courier">{REPO}</font>', BODY)
P('계정만 알려 주시면 협업자로 추가하겠습니다. 결과는 <b>전용 가지(branch)</b>에 '
  '올려 주시면 저희가 확인 후 합칩니다 &#8212; 서로의 작업을 덮어쓸 일이 없습니다.', BODY)
code(['git clone ' + REPO + '.git',
      'cd Czero_mtv_mof',
      'git checkout -b results/&lt;성함이나 기관명&gt;',
      '',
      '# ... 계산 후 ...',
      'git add 21_ZIF69_MTV/v3_water/water_results.json',
      'git add 21_ZIF69_MTV/results_v3.json',
      'git commit -m "water v3 20 jobs on &lt;장비 이름&gt;"',
      'git push origin results/&lt;성함이나 기관명&gt;'])
box('<b>실행 폴더는 올리지 말아 주십시오.</b> RASPA 출력은 한 작업이 약 30 MB 라 '
    '20작업이면 600 MB 입니다. 저장소가 감당하지 못합니다. '
    '<font face="Courier">.gitignore</font> 에 걸어 두었지만, 혹시 '
    '<font face="Courier">water_runs_*/</font> 나 <font face="Courier">runs_*/</font> '
    '가 <font face="Courier">git status</font> 에 보이면 무시하고 넘어가 주십시오. '
    '<b>필요한 것은 JSON 두 개뿐입니다.</b>')

P('방식 2. 포크(fork) &#8212; 저희가 권한을 드리지 않아도 됩니다', H2)
P('저장소를 포크하신 뒤 같은 방식으로 작업하고 pull request 를 보내 주시면 됩니다. '
  '계정 정보를 주고받을 필요가 없고, 상대 쪽 정책상 외부 저장소 접근이 곤란할 때 '
  '편합니다.', BODY)

P('방식 3. 파일만 주고받기 &#8212; git 을 안 쓰셔도 됩니다', H2)
P('사실 이 방식으로 충분합니다. 보내 드릴 것이 1.4 MB, 받을 것이 100 KB 남짓이라 '
  '메일 첨부로도 오갑니다. 클러스터에서 git 을 쓰기 번거로우시면 <b>이쪽을 '
  '권합니다</b> &#8212; 계산에 필요한 것은 git 이 아닙니다.', BODY)
table([['방식', '주고받는 것', '적합한 경우'],
       ['1. 협업자', '가지에 push', '계속 주고받을 예정. 이력이 남아야 할 때'],
       ['2. 포크/PR', 'pull request', '권한을 주고받기 곤란할 때'],
       ['<b>3. 파일</b>', '압축 파일 / 클라우드 링크',
        '<b>한 번에 끝낼 때. 가장 간단합니다</b>']],
      [24, 46, 96])

P('11. 계정 공유는 하지 않습니다', H1)
box('혹시 <b>저희 쪽 도구 계정을 빌려 쓰시는 방식</b>을 생각하셨다면, 그렇게 하지 '
    '않는 편이 서로에게 낫습니다. 저희 작업 계정에는 연구 문서 워크스페이스가 '
    '통째로 연결돼 있어 계정을 넘기면 프로젝트와 무관한 자료까지 열립니다. '
    '<b>무엇보다 이 계산에는 그런 도구가 전혀 필요 없습니다</b> &#8212; '
    'RASPA 와 파이썬만 있으면 됩니다.')

P('12. 받으신 파일이 맞는지 확인하는 법', H1)
P('꾸러미에 <font face="Courier">CHECKSUMS.txt</font> 를 같이 넣었습니다. '
  '특히 <b>힘장 파일 두 개</b>가 저희 것과 같은지 확인해 주시면 좋겠습니다 &#8212; '
  '이 둘이 다르면 계산은 정상으로 끝나지만 <b>숫자가 저희 것과 합쳐지지 '
  '않습니다.</b> 5절에 적은 이유 때문입니다.', BODY)
code(['sha256sum -c CHECKSUMS.txt',
      '',
      '# 최소한 이 둘만이라도:',
      '#   raspa_share/forcefield/UFF_MOF/force_field_mixing_rules.def',
      '#   raspa_share/forcefield/UFF_MOF/pseudo_atoms.def',
      '#',
      '# 값이 맞다면 아래가 보여야 합니다',
      '#   C_co2   lennard-jones   29.933   2.745',
      '#   C_co2   ...   q = 0.6512'])

P('13. 문의', H1)
P(f'꾸러미 안 <font face="Courier">README.md</font> 에 실행 절차가 한 장으로 '
  f'정리돼 있습니다. 구조 파일은 현재 <b>{N_TXT}</b>이며, 막히는 부분이 있으면 '
  '언제든 알려 주십시오 &#8212; 저희 쪽 설정 문제일 가능성이 높습니다. '
  '<b>무리해서 해결하지 마시고 그대로 알려 주시는 편이 저희에게 훨씬 낫습니다.</b>', BODY)

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=22 * mm, rightMargin=22 * mm,
                        topMargin=18 * mm, bottomMargin=16 * mm,
                        title='계산 지원 요청 명세 - MTV-ZIF')


def footer(canv, d):
    canv.saveState()
    canv.setFont('Malgun', 7.5)
    canv.setFillColor(BLACK)
    canv.drawString(22 * mm, 10 * mm, 'MTV-ZIF CO2 포집 스크리닝 · 계산 지원 요청 명세')
    canv.drawRightString(A4[0] - 22 * mm, 10 * mm, f'{d.page}')
    canv.restoreState()


# reportlab 은 넘긴 flowable 을 소비하고 내부 상태를 바꿉니다. 저장 단계에서
# 실패한 뒤 다시 부르면 빈 문서나 LayoutError 가 납니다(둘 다 실제로 겪었습니다).
# 한 번만 만들고, 잠긴 파일은 이름을 바꿔 가며 복사합니다.
TMP = '/tmp/_peer_req.pdf'
doc.filename = TMP
doc.build(S, onFirstPage=footer, onLaterPages=footer)
stem, ext = os.path.splitext(OUT)
written = None
for cand in [OUT] + [f'{stem}_{n}{ext}' for n in range(2, 20)]:
    try:
        shutil.copyfile(TMP, cand)
        written = cand
        break
    except PermissionError:
        continue
print(f'[OK] {written}  ({os.path.getsize(written)/1024:.0f} KB)')
