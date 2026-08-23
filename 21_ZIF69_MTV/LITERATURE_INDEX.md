# 문헌 색인 (EndNote 라이브러리 전수) — 2026-08-24

ZIF-69 MTV(saIm) 프로젝트 기준으로 EndNote 라이브러리 **live 69건**을 전수
색인한 표입니다. 각 행의 마지막 칸은 **이 프로젝트에 대한** 한 줄 관련성
태그이고, 📖 표시는 [LITERATURE_NOTES_20260824.md](LITERATURE_NOTES_20260824.md)
에서 전문 정독한 논문입니다.

## 0. 원본 위치와 읽는 법

**PDF 저장소 (절대경로, 리포지토리 바깥)**

    /mnt/c/Users/skyjun/Downloads/종합설계_References/EndNote_References.Data/PDF/<file_path>

**PDF 는 리포지토리에 커밋하지 않습니다.** 이유는 두 가지입니다: (i) 용량 —
73개 첨부 합계가 수백 MB 이고 그중 단일 파일 16.7 MB(id 7)도 있습니다,
(ii) 저작권 — 대부분 구독 저널의 출판사판(publisher PDF)이라 재배포 불가입니다.
이 표의 `file_path` 는 위 저장소 기준 **상대경로**이며, 저장소를 가진 기기에서만
열립니다.

**메타데이터 원본 (SQLite)**

    /home/skyjun/.claude/uploads/7c8e1e27-4d09-485b-8efd-19633a3abec1/929ada74-EndNote_References.enl
    테이블 refs (live 필터: trash_state is null or trash_state=0) / file_res(refs_id, file_path)

**한 편 읽는 recipe (python + pypdf 6.14.2)**

```python
# /home/skyjun/miniconda3/envs/czeromof/bin/python
import sqlite3, os
from pypdf import PdfReader

ENL  = '/home/skyjun/.claude/uploads/7c8e1e27-4d09-485b-8efd-19633a3abec1/929ada74-EndNote_References.enl'
BASE = '/mnt/c/Users/skyjun/Downloads/종합설계_References/EndNote_References.Data/PDF'

con = sqlite3.connect(ENL)
rid = 57                                   # 이 표의 EndNote id
(fp,) = con.execute(
    'select file_path from file_res where refs_id=? limit 1', (rid,)).fetchone()

rd = PdfReader(os.path.join(BASE, fp))
print(len(rd.pages), '쪽')
for i, pg in enumerate(rd.pages[:3]):      # 필요한 쪽만
    print(f'--- p{i+1} ---')
    print(pg.extract_text())
```

**본문 검색**(수치 뽑을 때 실제로 쓴 방식)은 `extract_text()` 결과를 줄 단위로
정규식 필터하면 됩니다 — 예: `re.search(r'kJ.?mol|kJ/mol', line, re.I)`.

> 환경 제약: poppler 가 없어 **이미지 렌더링은 불가**합니다. 그림·표 이미지 안의
> 숫자는 못 읽고, 본문 텍스트 레이어에 있는 값만 인용했습니다. 노트에서 그림에서만
> 읽히는 값은 인용하지 않았습니다.

## 1. ⚠ 인용 전 반드시 알아야 할 두 가지

**(1) 에세이(이전 리뷰)의 인용 번호가 [35]-[63] 구간에서 깨져 있습니다.**
본문 번호는 인용 순서(citation order)를 가정하는데 참고문헌 목록이 알파벳순으로
정렬돼 버려서, **[35] 이상은 본문 번호와 목록 항목이 일치하지 않습니다.**
[1]-[34] 는 일치합니다. 에세이에서 [35]+ 번호로 무언가를 인용하려면 번호가 아니라
**저자·연도·DOI 로 다시 확인**하고, 이 색인의 EndNote id 로 갈아타십시오.
이 색인의 id 는 EndNote 내부 id 이고 에세이 번호와 **무관**합니다.

**(2) id 59 는 메타데이터가 잘못돼 있습니다.** 제목 필드는 "Insights into Ionic
Liquids: From Z-Bonds to Quasi-Liquids"(Wang 2022)인데 실제 첨부 PDF 는 JACS Au
2023 사설 "Recent Developments in CO2 Capture and Conversion"(3쪽)입니다.
**둘 중 어느 쪽으로도 인용하지 말고** EndNote 레코드를 먼저 고쳐야 합니다.

## 2. 라이브러리 구성 (한눈에)

| 구분 | 건수 | 비고 |
|---|---|---|
| live 레코드 | 69 | `trash_state` 필터 적용 (전체 73건 중 4건 휴지통) |
| PDF 첨부가 있는 레코드 | 61 | 첨부 총 73건 — 결측 0 (전수 확인) |
| 첨부 없는 레코드 | 8 | id 19/20/40/41/42/44/48/63 — 전부 **다른 id 와 같은 DOI 의 중복 레코드** |
| 중복 첨부(같은 논문 파일 반복) | 8 레코드 | id 1(5개) 2(3개) 3·4·5·6·7·10(각 2개) — 아래 표는 대표 1개만 적고 `(+중복 N건)` 로 표기 |
| 범위 밖(촉매/광촉매/막) | 9 | id 2/26/28/29/30/31/32/38 + 부분 35·50 — 아래에서 명시적으로 제외 |
| 📖 전문 확인(PDF 정독) | 16 | 그중 **14편은 상세 노트**, 2편(id 51·55)은 보조로 짧게 — 노트 파일 참조 |

**범위 밖 처리 원칙.** CO2 **전환(conversion)·광촉매(photoreduction)·촉매 고정
(cycloaddition)** 논문은 우리 과제(습윤 flue gas 물리흡착 포집)와 축이 달라
성능 비교·설계 근거로 쓰지 않습니다. 표에서 "범위 밖" 으로 태그했습니다.
포집+전환 혼합 총설(id 7/35/50)은 **포집 절만** 인용합니다.

## 3. 전수 색인

| id | 제1저자·연도 | 저널 | 제목 | DOI | PDF 상대경로 | 이 프로젝트와의 관련성 |
|---|---|---|---|---|---|---|
| 1 | Shi, Xiaoyang 2023 | Materials Today | Water-stable MOFs and hydrophobically encapsulated MOFs for CO2 capture from ambient air and wet flue gas | 10.1016/j.mattod.2023.03.004 | `0363423299/Water-stable MOFs and hydrophobically encapsul.pdf` <br>(+중복 4건) | 📖 **소수성 차폐 물리흡착 선례** — 습윤 flue gas/DAC 용 water-stable·hydrophobic encapsulation 총설. 우리 saIm 소수성 co-linker 설계의 1차 근거 |
| 2 | Li, Yaling 2021 | Catalysts | Covalent Organic Frameworks for Simultaneous CO2 Capture and Selective Catalytic Transformation | 10.3390/catal11091133 | `1640069542/catalysts-11-011331.pdf` <br>(+중복 2건) | 범위 밖 — COF 촉매 전환(catalysis). 포집 성능 비교에 쓰지 않음 |
| 3 | Zhao, Guobin 2025 | Matter | CoRE MOF DB: A curated experimental metal-organic framework database with machine-learned properties for integrated material-process screening | 10.1016/j.matt.2025.102140 | `1782217579/Core MOF DB1.pdf` <br>(+중복 1건) | 스크리닝 인프라 — CoRE MOF DB(ML 물성 포함). 우리 조성이 실험 MOF 분포 어디인지 대조용 |
| 4 | Jin, X. 2025 | Digit Discov | MOFChecker: a package for validating and correcting metal-organic framework (MOF) structures | 10.1039/d5dd00109a | `0930627587/d5dd00109a.pdf` <br>(+중복 1건) | 구조 검증 도구 — MOFChecker. 치환 구조 sanity check 절차의 외부 표준 |
| 5 | Chen, Yongwei 2017 | Chemical Engineering Journal | A new MOF-505@GO composite with high selectivity for CO2/CH4 and CO2/N2 separation | 10.1016/j.cej.2016.09.138 | `2707551843/1-s2.0-S1385894716313833-main1.pdf` <br>(+중복 1건) | 주변 — MOF-505@GO 복합체 CO2/CH4·CO2/N2 선택도. 복합화 경로(우리 축 아님) |
| 6 | Yang, Chuanruo 2021 | Chemical Engineering Journal | Amine-functionalized micron-porous polymer foams with high CO2 adsorption efficiency and exceptional stability in PSA process | 10.1016/j.cej.2021.129555 | `2767925670/Amine-functionalized micron-porous polymer foa.pdf` <br>(+중복 1건) | 아민 경로 대조군 — 비-MOF 폴리머 폼, PSA 안정성. 아민 route 의 공정 내구성 비교점 |
| 7 | Kong, F. 2024 | Nanomaterials (Basel) | Carbon Dioxide Capture and Conversion Using Metal-Organic Framework (MOF) Materials: A Comprehensive Review | 10.3390/nano14161340 | `0529608049/nanomaterials-14-01340-v2.pdf` <br>(+중복 1건) | 부분 범위 밖 — 포집+전환 종설. 전환(conversion) 절은 제외하고 인용 |
| 10 | Qazvini, O. T. 2021 | Nat Commun | Selective capture of carbon dioxide from hydrocarbons using a metal-organic framework | 10.1038/s41467-020-20489-2 | `1486499654/s41467-020-20489-2.pdf` <br>(+중복 1건) | 📖 **선택적 CO2 포집 MOF(MUF-16)** — 비-OMS·물리흡착 선택도 선례. 우리 no-OMS ZIF-69 와 같은 계열 |
| 11 | Chung, Yongchul G. 2019 | Journal of Chemical & Engineering Data | Advances, Updates, and Analytics for the Computation-Ready, Experimental Metal–Organic Framework Database: CoRE MOF 2019 | 10.1021/acs.jced.9b00835 | `3389556342/advances-updates-and-analytics-for-the-computa.pdf` | 스크리닝 인프라 — CoRE MOF 2019 DB |
| 12 | Li, L. 2024 | Environ Res | The utility of MOF-based materials in direct air capture (DAC) application to ppm-level CO(2) | 10.1016/j.envres.2024.119985 | `0837016144/1-s2.0-S0013935124018905-main.pdf` | DAC 총설(ppm) — id 19 와 중복 레코드 |
| 13 | Ben-Mansour, Rached 2018 | Energy Conversion and Management | An efficient temperature swing adsorption (TSA) process for separating CO2 from CO2/N2 mixture using Mg-MOF-74 | 10.1016/j.enconman.2017.11.010 | `2473912581/1-s2.0-S019689041731049X-main.pdf` | **TSA 공정 근거** — Mg-MOF-74 CO2/N2 TSA. 우리 성능 지표가 humid TSA WC 인 근거 계열 |
| 14 | Liu, W. 2022 | Applied Thermal Engineering | Thermodynamic study on two adsorption working cycles for direct air capture | 10.1016/j.applthermaleng.2022.118920 | `1661531575/1-s2.0-S1359431122008596-main.pdf` | 공정 열역학 — DAC 두 흡착 사이클 비교. 재생 에너지 관점 |
| 15 | Pal, Shyam Chand 2025 | Chemical Engineering Journal | A 2D microporous ‘flexible-robust’ MOF for efficient natural gas purification with C2s/CH4 and CO2/CH4 separations | 10.1016/j.cej.2025.162121 | `1190331626/1-s2.0-S138589472502947X-main.pdf` | 유연성 캠프 — 2D 'flexible-robust' MOF. 게이트 개폐로 재생 유리 |
| 16 | Veldhuizen, H. 2023 | ACS Appl Mater Interfaces | Competitive and Cooperative CO(2)-H(2)O Adsorption through Humidity Control in a Polyimide Covalent Organic Framework | 10.1021/acsami.3c04561 | `2230064282/competitive-and-cooperative-co2-h2o-adsorption.pdf` | 📖 **경쟁 AND 협력 CO2-H2O(습도 제어)** — 우리 RH 축과 정면으로 같은 주제 |
| 17 | Ahlen, M. 2023 | Dalton Trans | Low-concentration CO(2) capture using metal-organic frameworks - current status and future perspectives | 10.1039/d2dt04088c | `3673432692/d2dt04088c.pdf` | 📖 **저농도 CO2 포집 총설** — 고치환 상거동/조성-성능 비단조 언급 확인 대상 |
| 18 | Deeg, K. S. 2020 | ACS Appl Mater Interfaces | In Silico Discovery of Covalent Organic Frameworks for Carbon Capture | 10.1021/acsami.0c01659 | `2577280197/in-silico-discovery-of-covalent-organic-framew.pdf` | 스크리닝 방법론 — COF in silico 발굴 |
| 19 | Li, Lirong 2024 | Environmental Research | The utility of MOF-based materials in direct air capture (DAC) application to ppm-level CO2 | 10.1016/j.envres.2024.119985 | — (첨부 없음) | 중복 레코드(id 12 와 동일 DOI, 첨부 없음) |
| 20 | Veldhuizen, Hugo 2023 | ACS Applied Materials & Interfaces | Competitive and Cooperative CO2–H2O Adsorption through Humidity Control in a Polyimide Covalent Organic Framework | 10.1021/acsami.3c04561 | — (첨부 없음) | 중복 레코드(id 16 와 동일 DOI, 첨부 없음) |
| 22 | Yan, Tongan 2024 | Journal of Chemical & Engineering Data | Machine Learning Assisted Discovery of Efficient MOFs for One-Step C2H4 Purification from Ternary C2H2/C2H4/C2H6 Mixtures | 10.1021/acs.jced.4c00244 | `1412239053/machine-learning-assisted-discovery-of-efficie.pdf` | 범위 밖 — C2H2/C2H4/C2H6 삼성분 분리 ML. CO2 포집 아님 |
| 23 | Sanz-Perez, E. S. 2016 | Chem Rev | Direct Capture of CO(2) from Ambient Air | 10.1021/acs.chemrev.6b00173 | `3072260609/direct-capture-of-co2-from-ambient-air.pdf` | DAC 기초 총설(Chem Rev) — 아민/물리흡착 경로 지형 |
| 24 | Chen, O. I. 2024 | Journal of the American Chemical Society | Water-Enhanced Direct Air Capture of Carbon Dioxide in Metal-Organic Frameworks | 10.1021/jacs.3c14125 | `1450940886/water-enhanced-direct-air-capture-of-carbon-di.pdf` | 📖 **물이 CO2 를 '돕는' 반대 방향 기전** — water-enhanced DAC. 우리 RH90 손실 서사의 반례 |
| 25 | Abdolalian, Payam 2019 | Polyhedron | Flexible and breathing metal–organic framework with high and selective carbon dioxide storage versus nitrogen | 10.1016/j.poly.2019.01.001 | `0515586733/1-s2.0-S0277538719300166-main.pdf` | 유연성 캠프 — breathing MOF CO2 vs N2 (id 41 중복) |
| 26 | Khan, Mazhar 2024 | Carbon Capture Science & Technology | MOFs materials as photocatalysts for CO2 reduction: Progress, challenges and perspectives | 10.1016/j.ccst.2024.100191 | `3378820027/1-s2.0-S2772656824000034-main.pdf` | 범위 밖 — 광촉매 CO2 환원(photocatalysis) |
| 27 | Alezi, D. 2015 | J Am Chem Soc | MOF Crystal Chemistry Paving the Way to Gas Storage Needs: Aluminum-Based soc-MOF for CH4, O2, and CO2 Storage | 10.1021/jacs.5b07053 | `2194060119/mof-crystal-chemistry-paving-the-way-to-gas-st.pdf` | 주변 — Al soc-MOF 고압 가스 저장. 0.15 bar 조건과 무관 |
| 28 | Fu, J. 2016 | J Am Chem Soc | Fabrication of COF-MOF Composite Membranes and Their Highly Selective Separation of H2/CO2 | 10.1021/jacs.6b03348 | `0145920208/fabrication-of-cof-mof-composite-membranes-and.pdf` | 범위 밖 — COF-MOF 복합막 H2/CO2 분리(막 공정) |
| 29 | Eskemech, A. 2024 | Inorg Chem | Zn-MOF as a Single Catalyst with Dual Lewis Acidic and Basic Reaction Sites for CO(2) Fixation | 10.1021/acs.inorgchem.3c03901 | `3173034527/zn-mof-as-a-single-catalyst-with-dual-lewis-ac.pdf` | 범위 밖 — Zn-MOF CO2 고정 촉매(catalysis) |
| 30 | Liu, Nana 2025 | ACS Applied Nano Materials | Thiophene-Functionalized Zn-Based Metal–Organic Frameworks with Nanosheets/Nanopores as Heterogeneous Catalysts for CO2 Conversion | 10.1021/acsanm.5c01238 | `2240279677/thiophene-functionalized-zn-based-metal-organi.pdf` | 범위 밖 — 티오펜 Zn-MOF CO2 전환 촉매(catalysis) |
| 31 | Das, Rajesh 2021 | Crystal Growth & Design | Design of Bifunctional Zinc(II)–Organic Framework for Efficient Coupling of CO2 with Terminal/Internal Epoxides under Mild Conditions | 10.1021/acs.cgd.1c01148 | `2292218965/design-of-bifunctional-zinc(ii)-organic-framew.pdf` | 범위 밖 — Zn 골격 CO2-에폭사이드 커플링 촉매(catalysis) |
| 32 | Qin, X. 2025 | Inorg Chem | Construction of Lanthanide Metal-Organic Frameworks for Cyclic Carbonates Synthesis by CO(2) Chemical Fixation with Epoxides or Olefins | 10.1021/acs.inorgchem.5c02137 | `3654676491/construction-of-lanthanide-metal-organic-frame.pdf` | 범위 밖 — 란타나이드 MOF 고리형 카보네이트 합성 촉매(catalysis) |
| 33 | Zhao, Y. L. 2024 | Adv Sci (Weinh) | Enabling C(2)H(2)/CO(2) Separation Under Humid Conditions with a Methylated Copper MOF | 10.1002/advs.202310025 | `1459046589/Advanced Science - 2024 - Zhao - Enabling C2H2.pdf` | 📖 **메틸화 소수성 선례(습윤 조건)** — 우리 ternary MTV 의 -CH3 co-linker 직접 선례 |
| 34 | Su, X. 2017 | ACS Appl Mater Interfaces | Postsynthetic Functionalization of Mg-MOF-74 with Tetraethylenepentamine: Structural Characterization and Enhanced CO(2) Adsorption | 10.1021/acsami.7b02471 | `3475993317/postsynthetic-functionalization-of-mg-mof-74-w.pdf` | 아민 그래프팅 — Mg-MOF-74 + TEPA 후처리 기능화 |
| 35 | Sher, Farooq 2024 | Journal of Materials Chemistry A | Advanced metal–organic frameworks for superior carbon capture, high-performance energy storage and environmental photocatalysis – a critical review | 10.1039/d4ta03877k | `1782029853/d4ta03877k.pdf` | 부분 범위 밖 — 포집/에너지저장/광촉매 통합 총설. 광촉매 절 제외 |
| 36 | Wu, P. 2019 | Nat Commun | Carbon dioxide capture and efficient fixation in a dynamic porous coordination polymer | 10.1038/s41467-019-12414-z | `1170821967/s41467-019-12414-z.pdf` | 유연성/동적 골격 — dynamic PCP 포집+고정. 게이트 개폐 재생 논거 |
| 37 | Xiao, C. 2024 | Chem Sci | Water-stable metal-organic frameworks (MOFs): rational construction and carbon dioxide capture | 10.1039/d3sc06076d | `1582835622/d3sc06076d.pdf` | **물 안정성 설계 규칙** — water-stable MOF 합리적 설계 + CO2 포집. 안정성 관문 다지표화 참고 |
| 38 | Zhao, Zhiyong 2026 | Fundamental Research | Asymmetric sites engineering in metal oxide catalysts for enhanced environmental remediation and energy conversion | 10.1016/j.fmre.2026.01.014 | `4093323564/1-s2.0-S2667325826000294-main.pdf` | 범위 밖 — 금속 산화물 비대칭 자리 촉매(MOF 아님, catalysis) |
| 39 | Zhang, Xiaoyu 2023 | Carbon Capture Science & Technology | Direct air capture of CO2 in designed metal-organic frameworks at lab and pilot scale | 10.1016/j.ccst.2023.100145 | `0446614824/1-s2.0-S2772656823000490-main.pdf` | 공정 스케일업 — 설계 MOF DAC lab/pilot (id 40 중복) |
| 40 | Zhang, Xiaoyu 2023 | Carbon Capture Science & Technology | Direct air capture of CO2 in designed metal-organic frameworks at lab and pilot scale | 10.1016/j.ccst.2023.100145 | — (첨부 없음) | 중복 레코드(id 39 와 동일 DOI, 첨부 없음) |
| 41 | Abdolalian, Payam 2019 | Polyhedron | Flexible and breathing metal–organic framework with high and selective carbon dioxide storage versus nitrogen | 10.1016/j.poly.2019.01.001 | — (첨부 없음) | 중복 레코드(id 25 와 동일 DOI, 첨부 없음) |
| 42 | Ben-Mansour, Rached 2018 | Energy Conversion and Management | An efficient temperature swing adsorption (TSA) process for separating CO2 from CO2/N2 mixture using Mg-MOF-74 | 10.1016/j.enconman.2017.11.010 | — (첨부 없음) | 중복 레코드(id 13 와 동일 DOI, 첨부 없음) |
| 43 | Ji, Y. 2024 | Carbon Capture Science & Technology | Techno-economic analysis on temperature vacuum swing adsorption system integrated with pre-dehumidification for direct air capture | 10.1016/j.ccst.2024.100199 | `0406144014/1-s2.0-S2772656824000113-main.pdf` | **전처리 제습 대안** — TVSA + pre-dehumidification TEA. '물 견디는 흡착제' 대신 '물을 먼저 뺀다' 노선의 비용 |
| 44 | Ji, Y. 2024 | Carbon Capture Science & Technology | Techno-economic analysis on temperature vacuum swing adsorption system integrated with pre-dehumidification for direct air capture | 10.1016/j.ccst.2024.100199 | — (첨부 없음) | 중복 레코드(id 43 와 동일 DOI, 첨부 없음) |
| 45 | Min, Youn Ji 2024 | ACS Sustainable Chemistry & Engineering | Model-Based Energy and Cost Analysis of Direct Air Capture Using ePTFE-Based Laminate-Structured Gas–Solid Contactors | 10.1021/acssuschemeng.4c05769 | `4126130459/model-based-energy-and-cost-analysis-of-direct.pdf` | 공정 비용 — ePTFE 라미네이트 접촉기 DAC 에너지·비용 모델 |
| 46 | Zhang, Xiangyu 2021 | ACS Sustainable Chemistry & Engineering | Machine Learning-Driven Discovery of Metal–Organic Frameworks for Efficient CO2 Capture in Humid Condition | 10.1021/acssuschemeng.0c08806 | `3846090606/machine-learning-driven-discovery-of-metal-org.pdf` | **습윤 조건 ML 스크리닝** — humid CO2 포집 MOF 발굴. 우리 습윤 관문의 문헌 대응물 |
| 47 | Mudhulu, Sudeep 2026 | Chemical Engineering Journal: Green and Sustainable | High-throughput computational screening of metal organic frameworks (MOFs) for CO2 selective separations: trends, challenges, and future perspectives | 10.1016/j.cejgas.2026.100025 | `2049178450/1-s2.0-S3051003126000017-main.pdf` | 스크리닝 총설 — 고처리량 CO2 선택 분리 동향/한계 (id 48 중복) |
| 48 | Mudhulu, Sudeep 2026 | Chemical Engineering Journal: Green and Sustainable | High-throughput computational screening of metal organic frameworks (MOFs) for CO2 selective separations: trends, challenges, and future perspectives | 10.1016/j.cejgas.2026.100025 | — (첨부 없음) | 중복 레코드(id 47 와 동일 DOI, 첨부 없음) |
| 49 | Xiong, S. 2025 | J Am Chem Soc | Mechanistic Studies of Oxidative Degradation in Diamine-Appended Metal-Organic Frameworks Exhibiting Cooperative CO(2) Capture | 10.1021/jacs.5c07551 | `0430656813/mechanistic-studies-of-oxidative-degradation-i.pdf` | 📖 **아민 경로의 반증** — diamine MOF 산화 열화 기전. 화학흡착 노선의 수명 리스크 |
| 50 | Zanatta, M. 2023 | ACS Mater Au | Materials for Direct Air Capture and Integrated CO(2) Conversion: Advancement, Challenges, and Prospects | 10.1021/acsmaterialsau.3c00061 | `2881117473/materials-for-direct-air-capture-and-integrate.pdf` | 부분 범위 밖 — DAC + 통합 CO2 전환. 전환 절 제외 |
| 51 | Gladysiak, A. 2024 | JACS Au | Enhanced Carbon Dioxide Capture from Diluted Streams with Functionalized Metal-Organic Frameworks | 10.1021/jacsau.4c00923 | `2483497516/enhanced-carbon-dioxide-capture-from-diluted-s.pdf` | 📖 **희박 스트림 기능화** — functionalized MOF 로 묽은 CO2 포집 강화. 작용기 도입 효과 정량 비교군 |
| 52 | Yadav, A. K. 2024 | JACS Au | Sequential Pore Functionalization in MOFs for Enhanced Carbon Dioxide Capture | 10.1021/jacsau.4c00808 | `3915958644/sequential-pore-functionalization-in-mofs-for-.pdf` | 📖 **순차 세공 기능화** — MTV 인접 전략(두 작용기 순차 도입). 우리 혼합 링커 설계와 직접 비교 |
| 53 | Allen, A. J. 2015 | Journal of Alloys and Compounds | Flexible metal-organic framework compounds: In situ studies for selective CO2 capture | 10.1016/j.jallcom.2015.05.148 | `3713047418/1-s2.0-S0925838815014589-main.pdf` | 유연성 캠프 — flexible MOF in situ 선택적 CO2 포집 |
| 54 | Dzil Razman, N. K. 2026 | ACS Omega | Engineering Superparamagnetic Fe(3)O(4)@Mg-MOF-74 for Advanced CO(2) Capture Application | 10.1021/acsomega.5c08395 | `2106938167/engineering-superparamagnetic-fe3o4-mg-mof-74-.pdf` | 주변 — 자성 Fe3O4@Mg-MOF-74. 유도가열 재생(우리 축 아님) |
| 55 | Noorani, N. 2024 | ACS Omega | Improving the Separation of CO(2)/N(2) Using Impregnation of a Deep Eutectic Solvent on a Porous MOF | 10.1021/acsomega.3c09243 | `2658646460/improving-the-separation-of-co2-n2-using-impre.pdf` | 📖 **세공 충전 대안(DES 함침)** — 링커 치환 대신 용매 함침으로 CO2/N2 선택도. 경쟁 전략 |
| 56 | Sriram, A. 2024 | ACS Cent Sci | The Open DAC 2023 Dataset and Challenges for Sorbent Discovery in Direct Air Capture | 10.1021/acscentsci.3c01629 | `0333420400/the-open-dac-2023-dataset-and-challenges-for-s.pdf` | **Open DAC 2023 데이터셋** — 습윤 포함 대규모 DFT/ML 데이터. 외부 검증 축 |
| 57 | Kwon, O. 2025 | ACS Cent Sci | Identification of Metal-Organic Frameworks for near Practical Energy Limit CO(2) Capture from Wet Flue Gases: An Integrated Atomistic and Process Simulation Screening of Experimental MOFs | 10.1021/acscentsci.5c00777 | `0602147125/identification-of-metal-organic-frameworks-for.pdf` | 📖 **공정지표 우선 스크리닝의 표준** — 습윤 flue gas 통합 원자·공정 시뮬. 30-40 kJ/mol 밴드와 '지표 29종 예측력 부족' 근거 |
| 58 | Cai, Zhongzheng 2020 | Chemistry of Materials | Insights into CO2 Adsorption in M–OH Functionalized MOFs | 10.1021/acs.chemmater.0c00746 | `0982756813/insights-into-co2-adsorption-in-m-oh-functiona.pdf` | 📖 **작용기-CO2 결합 기전** — M-OH 기능화 MOF 의 CO2 흡착 통찰. 우리 SO3H 정전기 기전과 대조 |
| 59 | Wang, Y. 2022 | JACS Au | Insights into Ionic Liquids: From Z-Bonds to Quasi-Liquids | 10.1021/jacsau.1c00538 | `3740317685/recent-developments-in-co2-capture-and-convers.pdf` | ⚠ 메타데이터 오류 — 제목은 'Insights into Ionic Liquids' 이나 첨부 PDF 는 JACS Au 2023 사설 'Recent Developments in CO2 Capture and Conversion'(3쪽). 인용 금지, 레코드 수정 필요 |
| 60 | Deng, Zijun 2024 | Chemistry of Materials | Multi-Scale Computational Design of Metal–Organic Frameworks for Carbon Capture Using Machine Learning and Multi-Objective Optimization | 10.1021/acs.chemmater.4c01969 | `3845685059/multi-scale-computational-design-of-metal-orga.pdf` | 📖 **다목적 최적화** — ML + multi-objective MOF 설계. 우리 '성능-안정성 두 관문 비중첩' 문제의 방법론적 대응 |
| 61 | Zhu, Z. 2024 | J Am Chem Soc | High-Capacity, Cooperative CO(2) Capture in a Diamine-Appended Metal-Organic Framework through a Combined Chemisorptive and Physisorptive Mechanism | 10.1021/jacs.3c13381 | `3848907073/high-capacity-cooperative-co2-capture-in-a-dia.pdf` | 📖 **협력적 화학흡착(chemi+physi 결합)** — 우리 물리흡착 상한을 넘는 대안 노선 |
| 62 | Jiang, Yao 2020 | Industrial & Engineering Chemistry Research | Controllable CO2 Capture in Metal–Organic Frameworks: Making Targeted Active Sites Respond to Light | 10.1021/acs.iecr.0c04126 | `3976492241/controllable-co2-capture-in-metal-organic-fram.pdf` | 자극 응답 캠프 — 광 응답 활성자리로 CO2 포집 제어 (id 63 중복) |
| 63 | Jiang, Yao 2020 | Industrial & Engineering Chemistry Research | Controllable CO2 Capture in Metal–Organic Frameworks: Making Targeted Active Sites Respond to Light | 10.1021/acs.iecr.0c04126 | — (첨부 없음) | 중복 레코드(id 62 와 동일 DOI, 첨부 없음) |
| 64 | Mahdavi, H. 2024 | Langmuir | Engineering Insights into Tailored Metal-Organic Frameworks for CO(2) Capture in Industrial Processes | 10.1021/acs.langmuir.4c01500 | `1913796011/engineering-insights-into-tailored-metal-organ.pdf` | 공학 총설 — 산업 공정용 MOF 맞춤 설계 통찰 |
| 66 | Jo, D. 2022 | ACS Appl Mater Interfaces | An Amine-Functionalized Ultramicroporous Metal-Organic Framework for Postcombustion CO(2) Capture | 10.1021/acsami.2c15476 | `1663067600/an-amine-functionalized-ultramicroporous-metal.pdf` | 초미세공 + 아민 — 후연소 CO2 포집 ultramicroporous MOF |
| 67 | Jiang, Mingyuan 2025 | ACS Materials Letters | Reconfiguration of Electrostatic Interactions within an Ultramicroporous Metal–Organic Framework Enables CO2 Separation | 10.1021/acsmaterialslett.4c02551 | `3816431980/reconfiguration-of-electrostatic-interactions-.pdf` | 📖 **정전기 재배치로 CO2 분리** — 우리 'SO3H 이득은 dispersive 아니라 electrostatic' 결론의 독립 선례 |
| 68 | Agrawal, A. 2020 | ACS Omega | Augmenting the Carbon Dioxide Uptake and Selectivity of Metal-Organic Frameworks by Metal Substitution: Molecular Simulations of LMOF-202 | 10.1021/acsomega.0c01267 | `3099474354/augmenting-the-carbon-dioxide-uptake-and-selec.pdf` | **치환 축 시뮬레이션** — LMOF-202 금속 치환으로 CO2 흡착·선택도 증강. 치환율-성능 관계의 방법 선례 |
| 69 | Jeong, Se-Min 2024 | ACS Sustainable Chemistry & Engineering | Carbon Dioxide Capture in a Carbonate-Pillared Ultramicroporous Metal–Organic Framework | 10.1021/acssuschemeng.4c01172 | `1989599419/carbon-dioxide-capture-in-a-carbonate-pillared.pdf` | 초미세공 — 카보네이트 기둥 ultramicroporous MOF CO2 포집 |
| 70 | Klokic, S. 2025 | Nat Commun | Flexible metal-organic framework films for reversible low-pressure carbon capture and release | 10.1038/s41467-025-60027-6 | `0394933413/s41467-025-60027-6.pdf` | 📖 **유연성 재생 노선** — flexible MOF 필름 저압 가역 포집/방출. TSA 대신 구조 전이로 재생 |
| 71 | Orhan, I. B. 2023 | Commun Chem | Accelerating the prediction of CO(2) capture at low partial pressures in metal-organic frameworks using new machine learning descriptors | 10.1038/s42004-023-01009-x | `2881788935/42004_2023_Article_1009.pdf` | **저분압 ML 기술자** — 낮은 CO2 분압(우리 0.15 bar 대역) 예측 descriptor |
| 72 | Avci, G. 2020 | ACS Appl Mater Interfaces | Do New MOFs Perform Better for CO(2) Capture and H(2) Purification? Computational Screening of the Updated MOF Database | 10.1021/acsami.0c12330 | `1259770414/do-new-mofs-perform-better-for-co2-capture-and.pdf` | 스크리닝 — 갱신 MOF DB 계산 스크리닝(CO2 포집·H2 정제) |
| 73 | Kazemi, A. 2023 | Sci Rep | Enhanced CO(2) capture potential of UiO-66-NH(2) synthesized by sonochemical method: experimental findings and performance evaluation | 10.1038/s41598-023-47221-6 | `1329525859/41598_2023_Article_47221.pdf` | 주변 — UiO-66-NH2 초음파 합성 실험. 합성법 축 |

## 4. 📖 전문 정독 대상 (상세 14편) — 노트 파일로

읽은 순서가 아니라 **논점 묶음** 순입니다. 상세는
[LITERATURE_NOTES_20260824.md](LITERATURE_NOTES_20260824.md).

| 묶음 | id | 논문 | 왜 이 편인가 |
|---|---|---|---|
| 공정지표 우선 | 57 | Kwon 2025 ACS Cent Sci | 30-40 kJ/mol 밴드와 "흡착 지표는 공정 성능의 나쁜 예측자" 주장의 원출처 |
| 공정지표 우선 | 60 | Deng 2024 Chem Mater | 성능-안정성 두 관문이 겹치지 않는 문제를 다목적 최적화로 다루는 법 |
| 소수성 차폐 | 1 | Shi 2023 Materials Today | 습윤 포집에서 소수성 캡슐화가 표준 처방이 된 근거 |
| 소수성 차폐 | 33 | Zhao 2024 Adv Sci | 메틸화 = 우리 ternary MTV -CH3 co-linker 의 직접 선례 |
| 물이 아군 | 24 | Chen 2024 JACS | 물이 CO2 흡착을 **증가**시키는 반대 방향 기전 |
| 물이 아군/양면 | 16 | Veldhuizen 2023 ACS AMI | 같은 물질에서 습도에 따라 경쟁↔협력이 뒤집힘 |
| 화학흡착 | 61 | Zhu 2024 JACS | 협력적 화학흡착 + 물리흡착 결합으로 물리흡착 상한 돌파 |
| 화학흡착의 반증 | 49 | Xiong 2025 JACS | 그 아민 경로가 산화로 죽는 기전 |
| 정전기 기전 | 67 | Jiang 2025 ACS Mater Lett | "이득이 dispersive 아니라 electrostatic" 의 독립 선례 |
| 정전기 기전 | 58 | Cai 2020 Chem Mater | 작용기(-OH)의 CO2 결합 기여 분해 |
| 물리흡착 선택도 | 10 | Qazvini 2021 Nat Commun | 비-OMS 물리흡착만으로 선택도를 얻은 선례 |
| 조성 축 | 17 | Åhlén 2023 Dalton Trans | 저농도 CO2 총설 — 고치환 상거동/조성 비단조 확인 |
| 기능화 축 | 52 | Yadav 2024 JACS Au | 순차 세공 기능화 = MTV 인접 전략 |
| 유연성 재생 | 70 | Klokic 2025 Nat Commun | TSA 대신 구조 전이로 재생하는 노선 |

표 안에서 📖 가 붙었지만 위 14편에 없는 두 건 — **id 51**(희박 스트림 기능화),
**id 55**(DES 함침) — 은 PDF 를 열어 수치까지 뽑았고 노트의 "보조 3편" 절에
짧게 실었습니다. **id 56**(Open DAC 2023)도 같은 절에 있습니다.
초록·표제 수준으로만 참고한 것: id 43(전처리 제습 TEA), id 37(물 안정성 설계).

---

*생성: 2026-08-24, EndNote live 69건 전수. 표의 관련성 태그는 이 프로젝트
(ZIF-69 gme / saIm / 습윤 0.15 bar / RH90) 기준이며 논문 자체의 중요도 평가가
아닙니다.*
