#!/usr/bin/env python3
"""MAGI-007 사고과정 금고를 사용자의 Obsidian 금고에 넣는다 — mcpvault(MCP 서버) 경유.

어디서 도는가
  Obsidian 금고가 있는 기기(데스크탑 D:\\Obsidian 등)에서 돈다. 클라우드 세션은 그 디스크에
  닿지 않으므로 거기서는 모의 금고로 시험만 했다(2026-11-05, 51 노트 바이트 일치).

무엇을 하는가
  1) https://github.com/bitbonsai/mcpvault 를 `npx -y @bitbonsai/mcpvault@latest <금고>` 로 띄워
     JSON-RPC(stdio) 로 말을 건다 — initialize → tools/list → write_note ×N → get_vault_stats.
  2) 노트(.md 등)는 mcpvault 의 `write_note` 로 쓴다. 노트가 아닌 파일(edges.json · assets/*)은
     mcpvault 가 "note-only" 라 파일 복사로 넣는다(--with-assets).
  3) 저장소 상대 경로를 그대로 비춰 넣는다: <금고>/<dest>/21_ZIF69_MTV/MAGI/MAGI-007_obsidian/…
     그래서 금고 안의 상대 링크(graph/FLOW.md, ../questions/A-1.md)가 그대로 살고,
     --with-refs 를 주면 밖을 가리키는 링크(../../ASSIGN_*.md 등 13건)도 같은 자리에 놓여 산다.
  4) 쓴 뒤 디스크에서 다시 읽어 원본과 글자 단위로 대조해 보고한다.

쓰는 법 (금고가 있는 기기에서)
  python 21_ZIF69_MTV/MAGI/MAGI-007_obsidian_mcp_put.py --vault "D:/Obsidian/<금고이름>" --with-refs --with-assets
  python ... --dry-run                    # 넣을 목록만
  python ... --via copy                   # Node 가 없으면 MCP 대신 파일 복사
  python ... --dest .                     # 금고 뿌리에 바로(기본 dest 는 Czero_mtv_mof)

필요한 것: Python 3.8+, (MCP 경로일 때) Node.js ≥ 22.12 와 npx. Obsidian 은 꺼져 있어도 된다.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[2]
VAULT_REL = Path("21_ZIF69_MTV/MAGI/MAGI-007_obsidian")
NOTE_EXT = {".md", ".markdown", ".txt", ".canvas", ".base"}
REFS = [
    "21_ZIF69_MTV/MAGI/MAGI-007_ligand-modification.md",
    "21_ZIF69_MTV/MAGI/MAGI-007_brief.md",
    "21_ZIF69_MTV/ASSIGN_ZNBDT_C1_20261105.md",
    "21_ZIF69_MTV/ASSIGN_ZNBDT_C2_20261105.md",
    "21_ZIF69_MTV/ASSIGN_ZNBDT_C2_FOLLOWUP_20261105.md",
    "21_ZIF69_MTV/ASSIGN_MAGI7_AMEND_20261105.md",
    "21_ZIF69_MTV/ASSIGN_ZNBDT_SUPP_20261103.md",
    "21_ZIF69_MTV/MAGI_20260905.md",
    "21_ZIF69_MTV/COMMS/cloud.md",
    "SESSION_LOG.md",
    "23_SCREENING/FINAL_RANKING_SMIX_20260930.md",
    "23_SCREENING/FINAL_RANKING_20260930.md",
    "24_DISCUSSION_WORKFLOW/RUN_20260929-1521_FOLLOWUP.md",
]


class McpVault:
    """mcpvault 를 자식 프로세스로 띄우고 JSON-RPC(줄 단위, stdio)로 부른다."""

    def __init__(self, vault: Path, npx: str = None, pkg: str = "@bitbonsai/mcpvault@latest", log: Path = None):
        cmd = npx or shutil.which("npx") or shutil.which("npx.cmd")
        if not cmd:
            sys.exit("npx 를 찾지 못했습니다 — Node.js(>= 22.12) 를 설치하거나 --via copy 로 도세요.")
        self._id = 0
        self.log = open(log or (Path(tempfile.gettempdir()) / "mcpvault_stderr.log"), "wb")
        self.p = subprocess.Popen(
            [cmd, "-y", pkg, str(vault)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.log,
            bufsize=0, shell=(os.name == "nt"),
        )

    def _send(self, obj):
        self.p.stdin.write((json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8"))
        self.p.stdin.flush()

    def _recv(self, want_id):
        while True:
            line = self.p.stdout.readline()
            if not line:
                raise RuntimeError(f"mcpvault 가 응답 없이 끝났습니다 — {self.log.name} 를 보세요.")
            line = line.strip()
            if not line.startswith(b"{"):
                continue
            msg = json.loads(line.decode("utf-8"))
            if msg.get("id") == want_id:
                return msg

    def call(self, method, params=None):
        self._id += 1
        self._send({"jsonrpc": "2.0", "id": self._id, "method": method, "params": params or {}})
        r = self._recv(self._id)
        if "error" in r:
            raise RuntimeError(f"{method}: {r['error']}")
        return r["result"]

    def start(self):
        info = self.call("initialize", {
            "protocolVersion": "2024-11-05", "capabilities": {},
            "clientInfo": {"name": "magi007-put", "version": "1"}})
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        tools = {t["name"] for t in self.call("tools/list")["tools"]}
        return info.get("serverInfo", {}), tools

    def tool(self, name, **args):
        r = self.call("tools/call", {"name": name, "arguments": args})
        if r.get("isError"):
            txt = r.get("content", [{}])[0].get("text", "")
            raise RuntimeError(f"{name}: {txt[:300]}")
        return r

    def text(self, name, **args):
        r = self.tool(name, **args)
        return "".join(c.get("text", "") for c in r.get("content", []) if c.get("type") == "text")

    def close(self):
        try:
            self.p.stdin.close()
        except Exception:
            pass
        self.p.terminate()
        try:
            self.p.wait(timeout=10)
        except Exception:
            self.p.kill()
        self.log.close()


def collect(src: Path):
    notes, others = [], []
    for p in sorted(src.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(src)
        if any(part.startswith(".") for part in rel.parts):
            continue
        if p.name.endswith(".tar.gz"):
            continue  # 봉인 묶음은 금고에 안 넣는다(해시 대조용 원본)
        (notes if p.suffix.lower() in NOTE_EXT else others).append(rel)
    return notes, others


def git_sha(repo: Path):
    try:
        return subprocess.check_output(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def start_note(dest_prefix: str, sha: str, via: str, n_notes: int, n_refs: int):
    v = f"{VAULT_REL.as_posix()}"
    return (
        "# MAGI-007 — 사고과정 금고 입구\n\n"
        "E · A · B 조건에서 Zn(bib)(bdtdc) 의 어떤 유기 리간드 개질이 좋은가 — 토론 MAGI-007 의 질문 · 합의 · 결정 · 라운드 노트.\n\n"
        f"- [INDEX — 금고 지도]({v}/INDEX.md)\n"
        f"- [FLOW — 사고과정 흐름(절차 · 논리 흐름도 2)]({v}/graph/FLOW.md)\n"
        f"- [TIMELINE — 시간순]({v}/graph/TIMELINE.md)\n"
        f"- [decisions — 결정 목록]({v}/graph/decisions.md)\n"
        f"- [R4 판정문](21_ZIF69_MTV/MAGI/MAGI-007_ligand-modification.md)\n\n"
        f"넣은 날 {time.strftime('%Y-%m-%d %H:%M')} · 저장소 커밋 `{sha}` · 방식 `{via}`"
        f"(노트 {n_notes} · 참조 문서 {n_refs}) · 스크립트 `21_ZIF69_MTV/MAGI/MAGI-007_obsidian_mcp_put.py`\n"
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vault", required=True, help="Obsidian 금고 뿌리 (예: D:/Obsidian/<금고이름>)")
    ap.add_argument("--dest", default="Czero_mtv_mof", help="금고 안에 만들 폴더 (기본 Czero_mtv_mof, '.' 이면 뿌리)")
    ap.add_argument("--src", default=str(REPO), help="저장소 뿌리 (기본: 이 스크립트 위치에서 계산)")
    ap.add_argument("--via", choices=["mcp", "copy"], default="mcp", help="노트를 넣는 길 (기본 mcp = mcpvault write_note)")
    ap.add_argument("--with-refs", action="store_true", help="밖을 가리키는 링크의 대상 13 문서도 같은 상대 자리에 넣는다")
    ap.add_argument("--with-assets", action="store_true", help="노트가 아닌 파일(edges.json · assets/*)도 파일 복사로 넣는다")
    ap.add_argument("--no-start", action="store_true", help="입구 노트 MAGI-007_START.md 를 만들지 않는다")
    ap.add_argument("--dry-run", action="store_true", help="넣을 목록만 보여 준다")
    ap.add_argument("--npx", default=None, help="npx 실행 파일 경로 (자동 탐지 실패 때)")
    args = ap.parse_args()

    repo = Path(args.src).resolve()
    src = repo / VAULT_REL
    if not src.is_dir():
        sys.exit(f"금고 원본이 없습니다: {src}")
    vault = Path(args.vault).expanduser().resolve()
    if not vault.is_dir():
        sys.exit(f"Obsidian 금고 폴더가 없습니다: {vault}  (먼저 Obsidian 에서 만든 금고 경로를 주세요)")
    dest = Path(args.dest)
    if str(dest) in (".", ""):
        dest = Path()

    notes, others = collect(src)
    refs = [Path(r) for r in REFS if (repo / r).is_file()] if args.with_refs else []
    missing_refs = [r for r in REFS if args.with_refs and not (repo / r).is_file()]
    sha = git_sha(repo)

    plan = []  # (vault 상대 경로(posix), 원본 Path, 종류)
    for rel in notes:
        plan.append(((dest / VAULT_REL / rel).as_posix(), src / rel, "note"))
    for rel in refs:
        plan.append(((dest / rel).as_posix(), repo / rel, "ref"))
    assets = [((dest / VAULT_REL / rel).as_posix(), src / rel, "asset") for rel in others] if args.with_assets else []

    print(f"원본 {src}\n금고 {vault}\n넣는 자리 <금고>/{dest.as_posix() or '.'}/…  커밋 {sha}  방식 {args.via}")
    print(f"노트 {len(notes)} · 참조 문서 {len(refs)} · 비노트 파일 {len(assets)}" + (f" · 없는 참조 {missing_refs}" if missing_refs else ""))
    if args.dry_run:
        for p, s, k in plan + assets:
            print(f"  [{k}] {p}")
        return

    written, same, differ, failed = 0, 0, 0, []
    mv = None
    if args.via == "mcp":
        mv = McpVault(vault, npx=args.npx)  # stderr 는 임시 폴더의 mcpvault_stderr.log (금고 안에 안 남김)
        info, tools = mv.start()
        print(f"mcpvault {info.get('version', '?')} 연결 · 도구 {len(tools)}개" + ("" if "write_note" in tools else " · write_note 없음!"))
        if "write_note" not in tools:
            mv.close()
            sys.exit("이 mcpvault 판에는 write_note 가 없습니다.")

    t0 = time.time()
    for vpath, spath, kind in plan:
        text = spath.read_text(encoding="utf-8")
        try:
            if mv:
                mv.tool("write_note", path=vpath, content=text, mode="overwrite")
            else:
                out = vault / vpath
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(text, encoding="utf-8")
            written += 1
            back = (vault / vpath).read_text(encoding="utf-8")
            if back == text:
                same += 1
            elif back.rstrip("\n") == text.rstrip("\n"):
                same += 1  # 끝 줄바꿈만 다름
            else:
                differ += 1
                print(f"  다름: {vpath} (원본 {len(text)} 자 · 금고 {len(back)} 자)")
        except Exception as e:
            failed.append((vpath, str(e)[:200]))
            print(f"  실패: {vpath}: {str(e)[:200]}")

    for vpath, spath, kind in assets:
        out = vault / vpath
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(spath, out)

    if not args.no_start:
        start_path = (dest / "MAGI-007_START.md").as_posix()
        content = start_note(dest.as_posix(), sha, args.via, len(notes), len(refs))
        if mv:
            mv.tool("write_note", path=start_path, content=content, mode="overwrite")
        else:
            (vault / start_path).parent.mkdir(parents=True, exist_ok=True)
            (vault / start_path).write_text(content, encoding="utf-8")

    stats = ""
    if mv:
        try:
            stats = mv.text("get_vault_stats")
            link = mv.text("wiki_link", document="FLOW")
            stats += "\n  wiki_link FLOW → " + link[:200]
        except Exception as e:
            stats = f"(통계 실패: {e})"
        mv.close()

    print(f"\n썼음 {written} · 원본과 같음 {same} · 다름 {differ} · 실패 {len(failed)} · 비노트 복사 {len(assets)} · {time.time() - t0:.1f} s")
    if stats:
        print("금고 통계(mcpvault):", stats[:400])
    if failed or differ:
        sys.exit(1)
    print("끝. Obsidian 에서 금고를 열면 <금고>/" + (dest / "MAGI-007_START.md").as_posix() + " 부터 보세요.")


if __name__ == "__main__":
    main()
