#!/bin/bash
# 윈도우 쪽에서 wsl.exe 로 이걸 실행해 둔다. 목적은 오직 하나 -- WSL 이 유휴로
# 판정하지 못하게 '붙어 있는 클라이언트'를 하나 유지하는 것이다.
# 안쪽에서 도는 wsl_keepalive.sh 와 다른 점은 이 프로세스의 부모가 윈도우의
# wsl.exe 라는 것이다. 08-10 17:25 에 안쪽 데몬만으로는 VM 종료를 못 막았다.
exec sleep infinity
