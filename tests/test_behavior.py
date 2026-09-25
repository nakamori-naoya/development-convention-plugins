#!/usr/bin/env python3
"""Direct publication and distribution."""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / "plugins/development-convention"
IDS = ("apply-layer-convention", "develop-inside-out", "apply-yagni", "fix-root-cause", "protect-entry-points", "write-readable-code")


def run(*args: str, ok: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, text=True, capture_output=True, check=False)
    if ok and result.returncode:
        raise AssertionError(f"失敗: {args}\n{result.stdout}\n{result.stderr}")
    if not ok and result.returncode == 0:
        raise AssertionError(f"拒否されなかった: {args}")
    return result


def exercise_direct_skills(package: Path) -> None:
    manifests = [json.loads((package / f".{runtime}-plugin/plugin.json").read_text(encoding="utf-8")) for runtime in ("codex", "claude")]
    assert manifests[0]["skills"] == [f"./skills/{identifier}" for identifier in IDS]
    assert manifests[0]["skills"] == manifests[1]["skills"]
    for identifier in IDS:
        entry = package / "skills" / identifier / "SKILL.md"
        assert entry.is_file()
        assert f"name: {identifier}\n" in entry.read_text(encoding="utf-8")
        assert not any((package / "skills" / identifier).glob(".*-plugin/plugin.json"))


def main() -> None:
    exercise_direct_skills(PACKAGE)
    with tempfile.TemporaryDirectory(prefix="development-convention-copy-") as value:
        copied_repo = Path(value) / "repository"
        shutil.copytree(ROOT, copied_repo)
        exercise_direct_skills(copied_repo / "plugins/development-convention")
        (copied_repo / "plugins/development-convention/skills/apply-yagni/SKILL.md").unlink()
        result = run("python3", str(copied_repo / "scripts/validate_repository.py"), str(copied_repo.resolve()), ok=False)
        assert "直接公開skill" in result.stderr or "直接参照資料" in result.stderr
    print("Behavior: passed (direct skills, copied package, missing skill)")


if __name__ == "__main__":
    main()
