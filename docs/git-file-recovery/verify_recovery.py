#!/usr/bin/env python3
"""Run article examples in disposable repositories, never in the blog repository.

Usage: python3 docs/git-file-recovery/verify_recovery.py > verification-output.txt
Requires Git 2.23+ and Python 3.11+. Remote examples use a local bare repository.
"""
from pathlib import Path
import os
import platform
import shlex
import subprocess
import sys
import tempfile


def require(condition, message):
    if not condition:
        raise AssertionError(message)


with tempfile.TemporaryDirectory(prefix="git-file-recovery-") as scratch:
    root = Path(scratch)
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update({"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
                "GIT_TERMINAL_PROMPT": "0", "LC_ALL": "C.UTF-8"})

    def run(repo, *args, expected=0, quiet=False):
        proc = subprocess.run(["git", *args], cwd=repo, env=env,
                              text=True, capture_output=True)
        if not quiet:
            print("$ git " + shlex.join(args))
            print(f"exit={proc.returncode}")
            print(proc.stdout.rstrip("\n") or "(stdout empty)")
            if proc.stderr:
                print("stderr: " + proc.stderr.rstrip("\n").replace(str(root), "<temporary-root>"))
        require(proc.returncode == expected, f"{args}: unexpected exit {proc.returncode}: {proc.stderr}")
        return proc.stdout

    def put(repo, name, content):
        (repo / name).write_text(content, encoding="utf-8")

    def content(repo, name):
        p = repo / name
        value = p.read_text(encoding="utf-8") if p.exists() else "<missing>"
        print(f"{name} content: {value!r}")
        return value

    def new_repo(name):
        repo = root / name
        repo.mkdir()
        run(repo, "init", "-b", "main", quiet=True)
        for key, value in (("user.name", "Recovery Example"),
                           ("user.email", "example@example.invalid"),
                           ("commit.gpgsign", "false"), ("core.autocrlf", "false")):
            run(repo, "config", "--local", key, value, quiet=True)
        put(repo, "memo.txt", "saved version\n")
        put(repo, "other.txt", "other original\n")
        put(repo, "later.txt", "later original\n")
        run(repo, "add", "--", "memo.txt", "other.txt", "later.txt", quiet=True)
        run(repo, "commit", "-m", "Add initial files", quiet=True)
        return repo

    def heading(text):
        print("\n## " + text)

    print("Git file recovery: actual execution transcript")
    print("OS: " + platform.platform())
    print("Python: " + sys.version.split()[0])
    print("Git: " + subprocess.check_output(["git", "--version"], text=True).strip())
    print("Shell: Git commands invoked by Python subprocess on Linux; no Windows/PowerShell execution")
    print("Isolation: new disposable repository per case; local bare remote only; global Git config disabled")

    heading("1. Unstaged deletion: index -> worktree, other changes preserved")
    repo = new_repo("unstaged")
    before = run(repo, "rev-parse", "HEAD")
    put(repo, "other.txt", "uncommitted other edit\n")
    (repo / "memo.txt").unlink()
    require(content(repo, "memo.txt") == "<missing>", "file must be deleted")
    require(run(repo, "status", "--short", "--", "memo.txt") == " D memo.txt\n", "unstaged marker")
    run(repo, "restore", "--", "memo.txt")
    require(content(repo, "memo.txt") == "saved version\n", "restore content")
    require(run(repo, "status", "--short") == " M other.txt\n", "other change retained")
    require(run(repo, "rev-parse", "HEAD") == before, "history unchanged")
    print("PASS")

    heading("2. Staged deletion: --staged alone does not recover the worktree")
    repo = new_repo("staged")
    run(repo, "rm", "--", "memo.txt")
    require(run(repo, "status", "--short") == "D  memo.txt\n", "staged marker")
    run(repo, "restore", "--staged", "--", "memo.txt")
    require(content(repo, "memo.txt") == "<missing>", "--staged must leave file deleted")
    require(run(repo, "status", "--short") == " D memo.txt\n", "now unstaged deletion")
    run(repo, "add", "--", "memo.txt")
    run(repo, "restore", "--source=HEAD", "--staged", "--worktree", "--", "memo.txt")
    require(content(repo, "memo.txt") == "saved version\n", "restore both")
    require(run(repo, "status", "--short") == "", "clean")
    print("PASS")

    heading("3. Staged edit followed by deletion: restore uses the index, not HEAD")
    repo = new_repo("index-edit")
    put(repo, "memo.txt", "staged edited version\n")
    run(repo, "add", "--", "memo.txt")
    (repo / "memo.txt").unlink()
    require(run(repo, "status", "--short") == "MD memo.txt\n", "MD marker")
    run(repo, "restore", "--", "memo.txt")
    require(content(repo, "memo.txt") == "staged edited version\n", "index version")
    require(run(repo, "status", "--short") == "M  memo.txt\n", "staged edit preserved")
    run(repo, "show", "HEAD:memo.txt")
    print("PASS")

    heading("4. Committed mixed deletion: restore only the target; preserve staged and unstaged edits")
    repo = new_repo("committed")
    run(repo, "rm", "--", "memo.txt")
    put(repo, "other.txt", "intentional committed edit\n")
    run(repo, "add", "--", "other.txt")
    run(repo, "commit", "-m", "Delete memo and update other")
    deletion = run(repo, "rev-parse", "HEAD").strip()
    require(run(repo, "status", "--short") == "", "clean does not mean file exists")
    run(repo, "log", "--oneline", "--diff-filter=D", "--", "memo.txt")
    run(repo, "show", "--stat", deletion)
    run(repo, "show", f"{deletion}^:memo.txt")
    put(repo, "other.txt", "unrelated staged edit\n")
    run(repo, "add", "--", "other.txt")
    put(repo, "later.txt", "unrelated unstaged edit\n")
    staged_before = run(repo, "diff", "--staged", "--", "other.txt")
    run(repo, "restore", f"--source={deletion}^", "--", "memo.txt")
    require(content(repo, "memo.txt") == "saved version\n", "historical content")
    require(run(repo, "rev-parse", "HEAD").strip() == deletion, "restore does not commit")
    require(run(repo, "diff", "--staged", "--", "other.txt") == staged_before, "index elsewhere unchanged")
    require(content(repo, "later.txt") == "unrelated unstaged edit\n", "worktree elsewhere unchanged")
    require("?? memo.txt\n" in run(repo, "status", "--short"), "restored file untracked until add")
    run(repo, "add", "--", "memo.txt")
    run(repo, "diff", "--staged", "--", "memo.txt")
    require("A  memo.txt\n" in run(repo, "status", "--short"), "staged new file")
    print("PASS")

    heading("5. Pushed deletion: restore + a new commit + ordinary push")
    repo = new_repo("pushed-restore")
    remote = root / "restore-remote.git"
    remote.mkdir()
    run(remote, "init", "--bare", "--initial-branch=main", quiet=True)
    run(repo, "remote", "add", "origin", str(remote), quiet=True)
    run(repo, "push", "-u", "origin", "main")
    run(repo, "rm", "--", "memo.txt")
    run(repo, "commit", "-m", "Delete memo")
    deletion = run(repo, "rev-parse", "HEAD").strip()
    run(repo, "push")
    run(repo, "fetch", "origin")
    require("origin/main" in run(repo, "branch", "-r", "--contains", deletion), "deletion shared")
    run(repo, "restore", f"--source={deletion}^", "--", "memo.txt")
    require(content(repo, "memo.txt") == "saved version\n", "restored")
    run(repo, "add", "--", "memo.txt")
    run(repo, "diff", "--staged")
    run(repo, "commit", "-m", "Restore memo")
    run(repo, "push")
    require(run(remote, "show", "main:memo.txt") == "saved version\n", "remote contains recovered file")
    run(repo, "merge-base", "--is-ancestor", deletion, "HEAD")
    require(run(repo, "status", "--short") == "", "clean")
    run(repo, "log", "--oneline", "-3")
    print("PASS")

    heading("6. Pushed mixed commit: revert reverses all its changes and preserves a later unrelated commit")
    repo = new_repo("pushed-revert")
    remote = root / "revert-remote.git"
    remote.mkdir()
    run(remote, "init", "--bare", "--initial-branch=main", quiet=True)
    run(repo, "remote", "add", "origin", str(remote), quiet=True)
    run(repo, "push", "-u", "origin", "main")
    run(repo, "rm", "--", "memo.txt")
    put(repo, "other.txt", "mixed committed edit\n")
    run(repo, "add", "--", "other.txt")
    run(repo, "commit", "-m", "Delete memo and update other")
    deletion = run(repo, "rev-parse", "HEAD").strip()
    put(repo, "later.txt", "later committed edit\n")
    run(repo, "add", "--", "later.txt")
    run(repo, "commit", "-m", "Update later")
    run(repo, "push")
    run(repo, "show", "--stat", deletion)
    run(repo, "revert", "--no-edit", deletion)
    require(content(repo, "memo.txt") == "saved version\n", "file recovered")
    require(content(repo, "other.txt") == "other original\n", "mixed change reversed too")
    require(content(repo, "later.txt") == "later committed edit\n", "later unrelated change retained")
    run(repo, "push")
    run(repo, "merge-base", "--is-ancestor", deletion, "HEAD")
    require(run(repo, "status", "--short") == "", "clean")
    run(repo, "log", "--oneline", "-4")
    print("PASS")

    heading("7. Revert conflict: abort returns to the state before revert")
    repo = new_repo("conflict")
    run(repo, "rm", "--", "memo.txt")
    run(repo, "commit", "-m", "Delete memo")
    deletion = run(repo, "rev-parse", "HEAD").strip()
    put(repo, "memo.txt", "new independently added version\n")
    run(repo, "add", "--", "memo.txt")
    run(repo, "commit", "-m", "Re-add different memo")
    before = run(repo, "rev-parse", "HEAD")
    run(repo, "revert", "--no-edit", deletion, expected=1)
    require("AA memo.txt\n" in run(repo, "status", "--short"), "add/add conflict")
    run(repo, "revert", "--abort")
    require(content(repo, "memo.txt") == "new independently added version\n", "content returned")
    require(run(repo, "rev-parse", "HEAD") == before, "history returned")
    require(run(repo, "status", "--short") == "", "clean again")
    print("PASS")

    heading("8. Git never recorded a new file: restore cannot recover it")
    repo = new_repo("unrecorded")
    put(repo, "never-added.txt", "only in worktree\n")
    (repo / "never-added.txt").unlink()
    run(repo, "restore", "--", "never-added.txt", expected=1)
    require(content(repo, "never-added.txt") == "<missing>", "cannot recover unrecorded bytes")
    run(repo, "log", "--oneline", "--", "never-added.txt")
    print("PASS")

    heading("9. Unstaged edits before deletion: restore cannot recover those newer bytes")
    repo = new_repo("lost-edit")
    put(repo, "memo.txt", "new version never staged\n")
    (repo / "memo.txt").unlink()
    run(repo, "restore", "--", "memo.txt")
    require(content(repo, "memo.txt") == "saved version\n", "only recorded version restored")
    print("PASS")

    print("\nALL 9 CASES PASSED")
