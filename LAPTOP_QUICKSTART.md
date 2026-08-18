# 다른 기기에서 계산 돌리기 — 10분 셋업

랩탑이든 지인의 서버든 절차는 같습니다. **RASPA 를 빌드하지 않습니다.**
conda 패키지가 있습니다 — 이것을 몰라서 "빌드 절차를 보내겠다"고 적었는데,
확인해 보니 우리 본 기계도 conda 로 깔려 있었습니다.

```
/home/mangwon1/miniconda3/pkgs/raspa2-2.0.50-h678ec8c_0/bin/simulate
$ simulate -v  ->  RASPA 2.0.41 (2021)
```

## 1. 환경 (약 10분)

```bash
# miniconda 가 없으면 먼저
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3
source $HOME/miniconda3/etc/profile.d/conda.sh

conda create -y -n mof python=3.10
conda activate mof
conda install -y -c conda-forge raspa2 ase numpy
simulate -v          # RASPA 2.0.4x 가 찍히면 성공
```

윈도우라면 WSL2(Ubuntu) 안에서 위를 그대로 합니다.

## 2. 꾸러미 풀기

`D:\MTV-ZIF_계산지원` 을 통째로 복사해 옵니다(1.5 MB).

```bash
mkdir -p ~/mof_run && cd ~/mof_run
# 꾸러미 내용을 여기에 풀어 놓습니다
```

**힘장 자리를 잡아 줍니다.** RASPA 는 `$RASPA_DIR/share/raspa/` 를 봅니다.

```bash
export RASPA_DIR=$HOME/RASPA/simulations
mkdir -p $RASPA_DIR/share/raspa
cp -r raspa_share/* $RASPA_DIR/share/raspa/
```

> **이 단계를 건너뛰거나 배포본 기본 힘장을 쓰면 계산은 정상으로 끝나는데
> 숫자가 우리 것과 안 맞습니다.** 우리가 쓰는 CO2 파라미터는 경로가 TraPPE 지만
> 내용은 Garc&#237;a-S&#225;nchez 2009 입니다(eps 29.933 / sigma 2.745 / q +0.6512).
> 확인:
> ```bash
> grep C_co2 $RASPA_DIR/share/raspa/forcefield/UFF_MOF/force_field_mixing_rules.def
> #   C_co2   lennard-jones   29.933   2.745    <- 이 값이어야 합니다
> ```

## 3. 구조 배치

```bash
mkdir -p 21_ZIF69_MTV/charged_v3
cp cif/*.cif 21_ZIF69_MTV/charged_v3/
```

## 4. 돌리기

**코어 수만큼 워커를 주십시오.** 물리 코어 수를 넘기지 마세요 — RASPA 는
작업당 단일 스레드라 논리 코어까지 채우면 오히려 느려집니다.

```bash
cd 21_ZIF69_MTV

# (A) 작업 용량 v3 — 건조. 24작업, 4코어에서 약 12시간
WC_V3_WORKERS=4 python run_wc_v3.py

# (B) 습윤 작업 용량 / 수분 경쟁 — 물. 한 작업이 9~20시간이라 코어가 많을 때만
WATER_V3_WORKERS=16 python run_water_v3.py
```

노트북이라면 **(A) 만** 하십시오. (B) 는 코어가 적으면 마감 안에 안 끝납니다.

## 5. 중단되어도 괜찮습니다

**작업 단위 이어받기**가 있습니다. 완주한 작업은 출력을 읽어 `cached` 로
건너뜁니다. 절전으로 죽든 정전이 나든 **그냥 다시 같은 명령을 치면** 됩니다.
실제로 2026-08-17 정전에서 19작업을 이 방식으로 전부 회수했습니다.

노트북이면 절전을 꺼 두는 편이 낫습니다.

```bash
# 화면만 끄고 계속 돌게
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

## 6. 진행이 안 보이는 것은 정상입니다

`PrintEvery` 가 생산 사이클 수와 같아서 출력 파일이 **처음과 끝에만** 갱신됩니다.
몇 시간 그대로여도 멈춘 것이 아닙니다. 살아 있는지 보려면:

```bash
ps -o pid,etime,pcpu,comm -C simulate
```

CPU 가 100% 근처면 정상입니다.

## 7. 돌려줄 것

```
v3_wc/working_capacity.json        (A)
v3_water/water_results.json        (B)
```

각 100 KB 안팎입니다. 실행 폴더(`wc_runs_v3/`, `water_runs_v3/`)는 한 작업이
30 MB 라 보내지 마세요.

**실패한 작업은 목록만 주십시오.** 중간에 죽은 RASPA 출력도 30 MB 를 남겨서
크기로는 구별되지 않습니다. 무리해서 채우지 않으셔도 됩니다.
