"""ZIF-93 앵커용 PACMAN 전하. charge_v3 와 같은 방식, 폴더만 다름."""
import os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from charge_v2 import fix_tags, net_charge  # noqa: E402
W = os.path.join(HERE, "anchor_zif93")
src, work, out = (os.path.join(W, "ZIF93.cif"),
                  os.path.join(W, "ZIF93_work.cif"),
                  os.path.join(W, "ZIF93_DDEC6.cif"))
if os.path.exists(out):
    print("[이미있음]", out); sys.exit(0)
from PACMANCharge import pmcharge  # noqa: E402
shutil.copy(src, work)
pmcharge.predict(cif_file=work, charge_type="DDEC6", digits=6,
                 atom_type=True, neutral=True, keep_connect=False)
gen = work.replace(".cif", "_pacman.cif")
shutil.move(gen, out)
fix_tags(out)
_q = net_charge(out)
q = _q[0] if isinstance(_q, tuple) else _q
print(f"[ok] ZIF93 순전하 {q:+.6f}  -> {out}")
sys.exit(0 if abs(q) < 1e-4 else 1)
