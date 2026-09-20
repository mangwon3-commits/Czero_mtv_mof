# 이 폴더는 **남의 저장소 파일**입니다 — 우리 것이 아닙니다

여기 있는 다섯 파일은 **CoRE-MOF-Tools** 업스트림 저장소의 것입니다.
2026-09-20 에 사용자가 `D:\CoRE-MOF-Tools-main.zip` 에서 꺼내 GitHub 웹으로 올렸고(커밋 `5f4a58a`),
그때 **우리 저장소 루트**에 놓였습니다. 2026-09-20 20:5x 에 이 폴더로 옮겼습니다.

    LICENSE      CC-BY-4.0 (Creative Commons Attribution 4.0 International)
    README.md    CoRE MOF Tools 의 README (배지·설치법·인용)
    setup.py     패키지 `CoREMOF_tools` 0.3.1, author Guobin Zhao
    env.yaml     conda 환경 `coremof_tools`
    logo.png     CoRE MOF Tools 로고

## 왜 루트에 두면 안 되었나

    LICENSE   루트에 있으면 **우리 저장소 전체가 CC-BY-4.0 으로 배포된다는 뜻**이 됩니다.
              우리가 줄 수 있는 라이선스가 아니고, 우리 작업의 조건을 남의 문서가 정하게 됩니다.
    setup.py  `pip install .` 이 우리 저장소를 `CoREMOF_tools 0.3.1`(author Guobin Zhao)로 설치합니다.
    README.md GitHub 첫 화면이 남의 소프트웨어 소개가 됩니다.

우리 저장소의 파일을 덮어쓰지는 않았습니다 — 루트에 `README.md`·`LICENSE` 가 원래 없었습니다(`git log` 로 확인).

## 지우지 않고 남기는 이유

CC-BY-4.0 은 **출처 표시**를 요구합니다. 우리가 이 자료(`CR.json`·CR CIF·`MOF_Project_Master_Data.pkl` 등)를
쓰는 한, 원저작자와 라이선스 전문을 저장소 안에 두는 것이 맞습니다.
**단, 그 사실이 보이는 자리에** — 루트가 아니라 여기입니다.

## 출처와 인용

    저장소   https://github.com/Chung-Research-Group/CoRE-MOF-Tools
             (미러 https://github.com/mtap-research/CoRE-MOF-Tools · PyPI `CoREMOF-tools` 0.3.1)
    개발     Guobin Zhao (sxm13)
    Zenodo   doi 10.5281/zenodo.15055758
    논문     Zhao G, Brabson L, Chheda S, Huang J, Kim H, Liu K, et al.
             "CoRE MOF DB: a curated experimental metal-organic framework database with
              machine-learned properties for integrated material-process screening."
             *Matter* **8** (2025) 102140.  doi 10.1016/j.matt.2025.102140
    zip md5  79213f201dec0cbefd19000d7a93d701  (627,873,526 B, `D:\CoRE-MOF-Tools-main.zip`)

## 아직 정해지지 않은 것

**우리 저장소 자체의 라이선스는 정해져 있지 않습니다.** 루트에 있던 CC-BY-4.0 은 우리 것이 아니었으므로
치웠고, 대신 무엇을 둘지는 사용자 결정입니다. 정하기 전까지 이 저장소는 **라이선스 없음**(= 기본 저작권,
명시적 허락 없이 재사용 불가)입니다. 발표·공개 전에 한 번 결정하십시오.
