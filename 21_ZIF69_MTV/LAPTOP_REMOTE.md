# 랩탑 원격 조작 (iPad, 2026-08-19 ~ 08-21)

**검증 완료.** iPad Termius 에서 실제 접속을 확인했습니다(2026-08-19 00:02).

## 접속

```
Host      100.107.56.81      (랩탑의 Tailscale 주소)
Port      2222               ← 22 아님
Username  skyjun
Auth      공개키 전용 (ED25519 SHA256:3udQZPNLX5zAw+I8+DsVmHHUSt06S69jG42yLUZ0fXM)
```

```bash
bash                          # 방향키가 ^[[A 로 찍히면 이것부터
tmux attach -t claude-remote
```

## 왜 2222 이고 왜 이렇게 복잡한가

```
iPad ──Tailscale──> 100.107.56.81:2222 ──> ssh_forward.py ──> 127.0.0.1:22 ──> sshd
                    (Tailscale 주소에만 바인딩)                 (루프백에만 바인딩)
```

한 겹씩 이유가 있습니다.

**mirrored 네트워킹** — 기본 NAT 모드에서는 WSL 포트가 호스트의 localhost 로만
전달되어 Tailscale 로 들어온 연결이 WSL 의 sshd 에 닿지 못합니다.
`.wslconfig` 의 `networkingMode=mirrored` 로 WSL 이 호스트 인터페이스를 공유하게
했습니다.

**2222 포워더** — 22 번에는 `netsh portproxy` 규칙 `0.0.0.0:22 -> 127.0.0.1:22` 가
남아 있었습니다. `0.0.0.0` 이 `127.0.0.1` 을 포함하므로 `iphlpsvc` 가 연결을 받아
자기에게 넘기고 끊는 **자기 참조 고리**였습니다. iPad 에서 본
*"end of file"* 이 이것입니다. 규칙을 지우자 이번에는 mirrored 때문에 그 22 번을
WSL 의 sshd 가 쓰려다 `Address already in use` 로 죽어 있었습니다.
1024 초과 포트를 쓰면 이 다툼을 통째로 피할 수 있습니다.

**루프백 전용 sshd** — 아래 사고 기록 참조.

## ⚠️ 2026-08-18 밤: SSH 가 인터넷에 노출됐던 일

portproxy 를 지운 뒤 mirrored 모드의 sshd 가 `0.0.0.0:22` 에 붙었고, 이 기기의
eth1 은 **공인 IP** 입니다. 약 30 분 만에 세 곳에서 무차별 대입이 들어왔습니다.

```
91.224.92.17     root  비밀번호 5회
62.60.130.253    root  비밀번호 5회
2.57.122.209     연결 시도
```

`PasswordAuthentication` 이 미지정(=기본값 yes)이었고 `skyjun` 은 sudo 권한이
있으므로 실제 위험이었습니다.

**두 가지가 이 사고의 교훈입니다.**

1. **방화벽 규칙으로 못 막았습니다.** 22 번을 여는 인바운드 허용 규칙은 처음부터
   존재하지 않았는데도 외부 연결이 들어왔습니다. mirrored 모드에서 Hyper-V
   방화벽이 기대만큼 걸러 주지 않습니다. **노출을 막으려면 방화벽이 아니라
   소켓이 어디에 바인딩되는가를 봐야 합니다.**

2. **`sshd_config` 의 `ListenAddress` 는 무시됩니다.** 우분투는 `ssh.socket` 으로
   소켓 활성화를 쓰므로 주소는 소켓 유닛이 정합니다. 고칠 곳은 여기입니다.

```bash
sudo mkdir -p /etc/systemd/system/ssh.socket.d
printf '[Socket]\nListenStream=\nListenStream=127.0.0.1:22\n' \
  | sudo tee /etc/systemd/system/ssh.socket.d/listen.conf
sudo systemctl daemon-reload && sudo systemctl restart ssh.socket
```

빈 `ListenStream=` 이 기존 `0.0.0.0:22` 를 지우고 다음 줄이 루프백만 지정합니다.

함께 적용한 것:

```bash
printf 'PasswordAuthentication no\nPermitRootLogin no\n' \
  | sudo tee /etc/ssh/sshd_config.d/99-hardening.conf
```

현재 상태 — 공인 IP 로는 22 도 2222 도 보이지 않고, 키 없이는 들어올 수 없습니다.

## 무인 유지

`cron` 이 15 분마다 `~/watchdog.sh` 를 돌립니다. 소유자는 이 스크립트 하나뿐이고
생존 판정은 **PID 파일이 아니라 프로세스 이름**으로 합니다 — PID 파일로 판정하다
러너가 두 개 떠서 메모리가 0 이 된 적이 있습니다(tmux 로 띄우면 PID 파일이
갱신되지 않습니다).

감시 대상: 러너 · SSH 포워더 · `claude-remote` tmux · keepalive.
31 종이 끝나면 포장 · sha256 · SESSION_LOG 커밋까지 무인으로 마칩니다.

재부팅 대비로 시작 프로그램에 `mtv-zif-wsl-start.vbs` 를 넣었습니다. WSL 은
Windows 부팅만으로는 뜨지 않으므로, 로그온 시 이것이 배포판을 깨우면
`ssh.socket`(enabled)과 `cron`(enabled)이 자동 복귀합니다.
**한계: 로그온 시점에 돕니다.** 잠금 화면에 머무르면 로그인 전까지 뜨지 않습니다.

## 접속이 안 될 때

```bash
pgrep -fc ssh_forward.py                 # 1 이어야 함
ss -tln | grep -E ':22 |:2222'           # 127.0.0.1:22 와 100.107.56.81:2222
systemctl is-active ssh.socket           # active
tail -20 ~/mof_project/21_ZIF69_MTV/watchdog.log
```

SSH 가 아예 안 되면 GitHub 가 대체 경로입니다. 감시자가 완료 시점에
`SESSION_LOG.md` 에 결과와 아카이브 해시를 올리므로, iPad 브라우저로 진행 상황을
확인할 수 있습니다.

## 하지 말 것 (`48H_COMPUTE_PLAN.md` 4절)

- `wsl --shutdown`, VHDX 압축, 빠른 시작 변경 — 계산과 sshd 가 함께 죽습니다
- RASPA 가 도는 중 Zeo++(`network`) 기동 — OOM 으로 WSL 이 통째로 멈춘 전례
- `git pull` / `rebase` / `clean` — 랩탑 계보가 갈라져 있고 작업 트리에
  추적되지 않은 `21_ZIF69_MTV/` 파일이 충돌 대상입니다
- 돌고 있는 셸 스크립트 제자리 편집 — 원자 교체(`mv`)를 쓰세요
