#!/usr/bin/env python3
"""development-convention packageの公開境界と内部文書契約を検査する。"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


IDS = ("apply-layer-convention", "develop-inside-out", "apply-yagni", "fix-root-cause", "protect-entry-points")
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


class ValidationError(ValueError):
    pass


def fail(message: str) -> None:
    raise ValidationError(message)


def load_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        fail(f"JSONがregular fileではありません: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        fail(f"JSONを読めません: {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"JSON objectではありません: {path}")
    return value


def shared_manifest(value: dict) -> dict:
    result = dict(value)
    result.pop("interface", None)
    return result


def assert_regular(path: Path, label: str) -> None:
    if path.is_symlink() or not path.is_file():
        fail(f"{label}がありません: {path}")


def skill_name(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        fail(f"SKILL.mdのYAML frontmatter開始がありません: {path}")
    try:
        end = lines.index("---", 1)
    except ValueError:
        fail(f"SKILL.mdのYAML frontmatter終端がありません: {path}")
    result = subprocess.run(
        ["yq", "-o=json", "-I=0", "."],
        input="\n".join(lines[1:end]) + "\n",
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        fail(f"SKILL.mdのYAML frontmatterを解析できません: {path}: {result.stderr.strip()}")
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        fail(f"SKILL.mdのYAML parser出力が不正です: {path}: {exc}")
    name = value.get("name") if isinstance(value, dict) else None
    if not isinstance(name, str) or not name:
        fail(f"SKILL.mdのfrontmatter nameが文字列ではありません: {path}")
    return name


def bracket_values(text: str, key: str) -> list[str]:
    matches = re.findall(rf"^\s+{re.escape(key)}:\s*\[([^\]]*)\]\s*$", text, re.MULTILINE)
    if len(matches) != 1:
        fail(f"{key}は一つの明示的な配列でなければなりません")
    return [item.strip() for item in matches[0].split(",") if item.strip()]


def catalog_entry(repository: Path, runtime: str) -> tuple[str, str, str]:
    path = repository / (".agents/plugins/marketplace.json" if runtime == "codex" else ".claude-plugin/marketplace.json")
    value = load_json(path)
    entries = value.get("plugins")
    if not isinstance(entries, list) or len(entries) != 1 or not isinstance(entries[0], dict):
        fail(f"{runtime} marketplaceは公開package一件だけでなければなりません")
    entry = entries[0]
    source = entry.get("source")
    if runtime == "codex":
        if not isinstance(source, dict) or source.get("source") != "local":
            fail("Codex marketplace sourceがlocalではありません")
        source = source.get("path")
    values = (entry.get("name"), entry.get("version"), source)
    if not all(isinstance(item, str) and item for item in values):
        fail(f"{runtime} marketplace identityが不正です")
    return values  # type: ignore[return-value]


def sibling_path_reference(text: str, sibling: str) -> str | None:
    """兄弟の入口の中身（directory、参照資料、scripts）を指す path を返す。名前を挙げるだけの参照は返さない。"""
    name = re.escape(sibling)
    patterns = (
        rf"skills/{name}/",
        rf"\.\./{name}/",
        rf"(?<![A-Za-z0-9_-]){name}/references/",
        rf"(?<![A-Za-z0-9_-]){name}/scripts/",
        rf"(?<![A-Za-z0-9_-]){name}/playbook\.yml",
        rf"(?<![A-Za-z0-9_-]){name}/SKILL\.md",
    )
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None


def check_names(path: Path, text: str, identity: str | None) -> None:
    for sibling in IDS:
        if sibling == identity:
            continue
        found = sibling_path_reference(text, sibling)
        if found:
            fail(f"兄弟の入口の中身をpathで参照しています: {path}: {found}")


def validate_internal(package: Path) -> None:
    roots = {identifier: package / "skills" / identifier for identifier in IDS}
    for identifier, root in roots.items():
        entry = root / "SKILL.md"
        reference_dir = root / "references"
        assert_regular(entry, "内部入口")
        text = entry.read_text(encoding="utf-8")
        check_names(entry, text, identifier)
        links = []
        for raw in MARKDOWN_LINK.findall(text):
            if raw.startswith("references/"):
                links.append(raw)
                assert_regular(root / raw, "直接参照資料")
        references = sorted(reference_dir.glob("*.md"))
        if len(links) != 1 or {root / raw for raw in links} != set(references):
            fail(f"内部入口から参照資料へ一段で到達できません: {entry}")
        for reference in references:
            check_names(reference, reference.read_text(encoding="utf-8"), identifier)
        if any(root.glob(".*-plugin/plugin.json")):
            fail(f"直接公開skillに入口別runtime manifestは不要です: {root}")


def validate_public(package: Path, manifest: dict) -> None:
    harness = manifest.get("metadata", {}).get("harness", {})
    if "playbooks" in harness or "internalPlugins" in harness or harness.get("installationSurface") == "playbook-package":
        fail("自己完結skillへplaybook包装を強制してはいけません")
    expected = [f"./skills/{identifier}" for identifier in IDS]
    if manifest.get("skills") != expected:
        fail("manifestのskillsが直接公開するskillと一致しません")
    for identifier in IDS:
        entry = package / "skills" / identifier / "SKILL.md"
        assert_regular(entry, "直接公開skill")
        if skill_name(entry) != identifier:
            fail(f"直接公開skillのnameが不一致です: {entry}")


def validate_repository(repository: Path) -> None:
    if not repository.is_absolute() or repository.is_symlink() or not repository.is_dir():
        fail(f"repositoryは実在する絶対directoryでなければなりません: {repository}")
    codex, claude = catalog_entry(repository, "codex"), catalog_entry(repository, "claude")
    package = repository / "plugins/development-convention"
    manifests = [load_json(package / f".{runtime}-plugin/plugin.json") for runtime in ("codex", "claude")]
    # 期待versionはruntime manifestから導き、両marketplaceと一致することを確かめる。
    if codex != claude or codex != ("development-convention", manifests[0].get("version"), "./plugins/development-convention"):
        fail("runtime間の公開package identityが一致しません")
    if shared_manifest(manifests[0]) != shared_manifest(manifests[1]):
        fail("runtime間の公開契約が一致しません")
    validate_public(package, manifests[0])
    validate_internal(package)
    print(f"Repository contract: passed ({repository})")


def expect_rejected(repository: Path, label: str, expected: str, mutate) -> None:
    with tempfile.TemporaryDirectory(prefix="development-convention-negative-") as value:
        candidate = Path(value) / "repository"
        shutil.copytree(repository, candidate, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        mutate(candidate)
        try:
            validate_repository(candidate)
        except (ValidationError, OSError, UnicodeError, json.JSONDecodeError) as exc:
            if expected not in str(exc):
                fail(f"負例「{label}」が期待した理由で失敗しません: {exc}")
            print(f"Repository negative: passed ({label})")
        else:
            fail(f"負例「{label}」を拒否できません")


def self_test(repository: Path) -> None:
    package = Path("plugins/development-convention")

    with tempfile.TemporaryDirectory(prefix="development-convention-positive-") as value:
        candidate = Path(value) / "repository"
        shutil.copytree(repository, candidate, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        entry = candidate / package / "skills/apply-yagni/SKILL.md"
        entry.write_text(
            """---
name: apply-yagni
description: 構造契約だけを満たす境界fixture
---
# 境界fixture

[根拠](references/evidence-rule.md)

証拠を実読して判断する。
""",
            encoding="utf-8",
        )
        validate_repository(candidate)
        print("Repository positive: passed (判断語や節名を意味品質の代理にしない)")

    with tempfile.TemporaryDirectory(prefix="development-convention-sibling-name-") as value:
        candidate = Path(value) / "repository"
        shutil.copytree(repository, candidate, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        entry = candidate / package / "skills/apply-yagni/SKILL.md"
        entry.write_text(entry.read_text(encoding="utf-8") + "\n層の置き場の判断は `apply-layer-convention` が持つ。Go の単位は go-convention の `develop-go-unit` が仕上げる。\n", encoding="utf-8")
        validate_repository(candidate)
        print("Repository positive: passed (兄弟と外部packageの公開入口をbacktickの名前で挙げる境界の宣言)")

    for label, replacement in (
        ("frontmatter nameのYAML comment", "name: apply-yagni # 公開identity"),
        ("frontmatter nameのquoted scalar", 'name: "apply-yagni"'),
    ):
        with tempfile.TemporaryDirectory(prefix="development-convention-frontmatter-") as value:
            candidate = Path(value) / "repository"
            shutil.copytree(repository, candidate, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            entry = candidate / package / "skills/apply-yagni/SKILL.md"
            entry.write_text(entry.read_text(encoding="utf-8").replace("name: apply-yagni", replacement, 1), encoding="utf-8")
            validate_repository(candidate)
            print(f"Repository positive: passed ({label})")

    def add_missing_skill(root: Path) -> None:
        for runtime in ("codex", "claude"):
            path = root / package / f".{runtime}-plugin/plugin.json"
            value = load_json(path)
            value["skills"].append("./skills/does-not-exist")
            path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def remove_reference(root: Path) -> None:
        (root / package / "skills/develop-inside-out/references/delivery-gates.md").unlink()

    def add_sibling_path(root: Path) -> None:
        path = root / package / "skills/apply-yagni/SKILL.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n[手順](../develop-inside-out/references/delivery-gates.md)を読む。\n", encoding="utf-8")

    def add_sibling_reference_path(root: Path) -> None:
        path = root / package / "skills/apply-yagni/references/evidence-rule.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n詳しくは skills/fix-root-cause/ を読む。\n", encoding="utf-8")

    def body_only_name(root: Path) -> None:
        path = root / package / "skills/apply-yagni/SKILL.md"
        text = path.read_text(encoding="utf-8").replace("name: apply-yagni\n", "", 1)
        path.write_text(text + "\nname: apply-yagni\n", encoding="utf-8")

    def missing_name(root: Path) -> None:
        path = root / package / "skills/apply-yagni/SKILL.md"
        path.write_text(path.read_text(encoding="utf-8").replace("name: apply-yagni\n", "", 1), encoding="utf-8")

    expect_rejected(repository, "存在しないskillの公開", "skillと一致", add_missing_skill)
    expect_rejected(repository, "直接参照資料の欠落", "直接参照資料", remove_reference)
    expect_rejected(repository, "兄弟の参照資料へのpath", "兄弟の入口の中身", add_sibling_path)
    expect_rejected(repository, "参照資料から兄弟のdirectoryへのpath", "兄弟の入口の中身", add_sibling_reference_path)
    expect_rejected(repository, "本文だけの偽name", "frontmatter name", body_only_name)
    expect_rejected(repository, "frontmatter name欠落", "frontmatter name", missing_name)
    print("Repository self-test: passed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    repository = args.repository.resolve()
    validate_repository(repository)
    if args.self_test:
        self_test(repository)


if __name__ == "__main__":
    try:
        main()
    except (ValidationError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"FAIL: {exc}")
