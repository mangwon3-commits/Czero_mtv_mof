# 랩탑 원격 조작 (iPad, 2026-08-19 ~ 08-21)

사용자가 자리를 비우는 동안 iPad 에서 이 랩탑을 조작하기 위한 문서입니다.
**경로는 이미 다 뚫려 있고, 남은 것은 공개키 한 줄뿐입니다.**

## 1. 이미 확인된 것

| 항목 | 상태 |
|---|---|
| Tailscale 노드 | 랩탑 `100.107.56.81`, iPad `100.125.137.15` (같은 테일넷) |
| WSL sshd | `ssh.socket` **active + enabled** (소켓 활성화라 WSL 재시작에도 살아남음) |
| 포트 공개 | `wslrelay.exe` 가 WSL:22 를 Windows `0.0.0.0:22` 로 중계 |
| 방화벽 | `WSL-SSH` Inbound Allow / TCP 22 / **profile=Any** |
| 도달 시험 | `Test-NetConnection 100.107.56.81 -Port 22` → **TcpTestSucceeded: True** |
| 절전 | AC/DC 모두 대기 시간 **0(안 함)**. 전원 연결, 배터리 100% |
| WSL 유지 | `keepalive_wsl` 프로세스가 VM 종료를 막음 (계산이 끝나도 sshd 유지) |
| claude CLI | WSL 안 `/home/skyjun/.local/bin/claude` |
| tmux | 세션 `claude-remote` 대기 중 (창 2개: 작업/상태) |

## 2. 딱 하나 남은 준비 — 공개키

iPad 의 SSH 앱(Blink / Termius / iSH)에서 키를 만들고 **공개키**를 붙여 넣으면 됩니다.
개인키는 iPad 밖으로 내보내지 마세요.

```bash
# 랩탑에서 (사용자 또는 세션이 실행)
echo 'ssh-ed25519 AAAA... ipad' >> ~/.ssh/authorized_keys
```

`~/.ssh`(700)와 `~/.ssh/authorized_keys`(600)는 **이미 만들어 두었습니다.** 줄만 넣으면 됩니다.

> 비밀번호 로그인은 권하지 않습니다. WSL 계정 비밀번호를 새로 정해야 하고,
> 그 값을 대화에 남기면 안 됩니다.

## 3. 접속

```bash
ssh skyjun@100.107.56.81
tmux attach -t claude-remote      # 없으면: tmux new -s claude-remote
claude
```

tmux 를 쓰는 이유: 연결이 끊겨도 세션이 살아 있습니다. iPad 는 화면이 꺼지거나
앱을 전환하면 SSH 가 끊기므로 tmux 없이는 작업이 통째로 날아갑니다.
분리는 `Ctrl-b` 다음 `d`.

## 4. 접속하면 먼저 볼 것

```bash
cd ~/mof_project/21_ZIF69_MTV
tail -20 supervise.log                      # 무인 감독 기록
ls lmp_v3 | wc -l                           # 안정성 진행 (목표 30)
pgrep -x lmp_serial | wc -l ; pgrep -x network | wc -l
pgrep -x simulate | wc -l                   # RASPA 는 0 이어야 정상
ls -lh ~/mof_export/                        # 인계 꾸러미와 해시
```

## 5. 무인으로 도는 것

`supervise_risk_v3.sh` 가 감독합니다. 안정성 러너가 끝나면 **사람 없이**
판정 집계 → `tar.gz` 포장 → sha256 → `SESSION_LOG.md` 항목 커밋·푸시까지 합니다.
따라서 접속하지 못하더라도 결과는 확정되고 기록이 남습니다.

로그: `21_ZIF69_MTV/supervise.log`

## 6. 접속이 안 될 때 — GitHub 가 대체 경로입니다

iPad 브라우저나 GitHub 앱에서 `mangwon3-commits/Czero_mtv_mof` 의
`SESSION_LOG.md` 를 열면 현황이 보입니다. 감독 스크립트가 완료 시점에 항목을
올리므로, SSH 없이도 **끝났는지 / 몇 종이 통과했는지 / 아카이브 해시**를 확인할 수 있습니다.

## 7. 하지 말아야 할 것 (48H_COMPUTE_PLAN 4절)

- `wsl --shutdown`, VHDX 압축, 빠른 시작 변경 — 계산과 sshd 가 동시에 죽습니다
- RASPA 가 도는 중 Zeo++(`network`) 기동 — 08-12 에 OOM 으로 WSL 이 통째로 멈췄습니다
- `git pull` / `rebase` / `clean` — 랩탑 계보가 데스크탑 생산 커밋 이전에 갈라져 있고,
  작업 트리에 추적되지 않은 `21_ZIF69_MTV/` 171 파일이 충돌 대상입니다
- 돌고 있는 셸 스크립트 편집 — 바이트 오프셋으로 읽어 엉뚱한 줄을 실행합니다

## 8. 남은 일감이 필요하면

랩탑은 안정성 관문을 끝내면 유휴입니다. `48H_COMPUTE_PLAN.md` 8~10번(증거표 작성,
재생 에너지 재계산, 후보 2종 밀도맵)은 RASPA 가 비어 있어야 하므로 랩탑이 받을 수
있습니다. 다만 **선택 이후에만** 도는 단계라 데스크탑의 순위 결정이 먼저입니다.
