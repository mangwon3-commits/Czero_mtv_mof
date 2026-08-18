"""구조 안정성 v3 — spawn 안전 실행기 (랩탑에서 추가).

[왜 필요한가]
    risk_screen.py 는 워커를 ProcessPoolExecutor(max_tasks_per_child=1) 로 만든다.
    Zeo++ 가 한 건에 3.2 GB 라 작업마다 프로세스를 버려 메모리를 돌려받으려는
    의도이고 그 자체는 옳다. 그런데 **max_tasks_per_child 는 spawn 기동을
    강제한다**(fork 와는 ValueError 로 배타적).

    spawn 자식은 부모 메모리를 물려받지 않고 __main__ 을 __mp_main__ 으로 다시
    실행한다. risk_screen_v3.py 는 rs.STRUCT 를 **main() 안에서** 바꾸는데,
    자식에서는 __name__ 이 "__main__" 이 아니라 main() 이 돌지 않는다. 따라서

        부모: STRUCT = structures_v3_stage   (출력에 그렇게 찍힌다)
        자식: STRUCT = structures            (기본값으로 되돌아간다)

    가 되어 run_one 이 v1 폴더를 읽는다. 랩탑에는 structures/ 가 없어서
    FileNotFoundError 로 죽었지만, **그 폴더가 있는 기기에서는 죽지 않고
    v3 라고 이름 붙은 결과가 v1 구조에서 나온다.** risk_screen_v3.py 의
    docstring 이 경계한 바로 그 사고가 다른 경로로 재현된 것이다.

[고치는 방법]
    패치를 **모듈 최상위**에 둔다. spawn 자식이 이 파일을 __mp_main__ 으로 다시
    실행할 때도 같은 대입이 일어나므로 부모와 자식이 같은 STRUCT 를 본다.
    검증된 risk_screen.py / risk_screen_v3.py 는 건드리지 않는다.

    sys.argv 는 risk_screen 이 import 시점에 INDEX/SUFFIX/WORK/RESULT 를
    계산하므로 import 보다 먼저 세운다(risk_screen_v3.py 와 같은 값).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STAGE = os.path.join(HERE, "structures_v3_stage")

sys.argv = ["risk_screen.py", "risk_v3_index.json", "v3"]
sys.path.insert(0, HERE)

import risk_screen as rs  # noqa: E402

rs.STRUCT = STAGE
rs.BASE_SRC = os.path.join(STAGE, "ZIF69_base.cif")
rs.MAX_WORKERS = int(os.environ.get("RISK_WORKERS", "4"))

if __name__ == "__main__":
    import risk_screen_v3 as v3
    print(f"  [spawn 안전 실행기] 최상위에서 STRUCT 고정: {rs.STRUCT}", flush=True)
    assert rs.STRUCT.endswith("structures_v3_stage")
    sys.exit(v3.main())
