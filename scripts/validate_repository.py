#!/usr/bin/env python3
"""development-convention の各公開入口が、自分の references へ届き、兄弟の入口の中身へ path で依存しないことを検査する。

manifest と配置の一致は harness-tools/tools/validate-plugin-repository.py が見るので、ここでは見ない。

基準資料: plugins/development-convention/skills/ 直下の入口と、その SKILL.md と references/*.md
入力: 引数の repository の絶対path
合格述語: 各入口の SKILL.md が、自分の references/ にある全 .md へ `[..](references/<名前>.md)` の形で直接リンクし、リンク先が実在する。
  SKILL.md と references は、兄弟の入口の中身を指す path（`skills/<兄弟>/`、`../<兄弟>/`、`<兄弟>/references/`、`<兄弟>/scripts/`、`<兄弟>/SKILL.md`）を書かない。
失敗時の診断: `FAIL: <理由>` を1行。終了code 1
正例: この repository そのもの。構造だけを満たす短い SKILL.md。兄弟や外部の入口の名前を backtick で挙げるだけの文
反例: self-test の、reference の欠落、SKILL.md と reference からの兄弟の path への参照
意味評価として残す範囲: 名前を挙げた文が兄弟への依存を作っていないか、文章の良し悪し
"""
from __future__ import annotations

import argparse
import re
import shutil
import tempfile
from pathlib import Path

MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


class ValidationError(ValueError):
    pass


def fail(message: str) -> None:
    raise ValidationError(message)


def sibling_path_reference(text: str, sibling: str) -> str | None:
    """兄弟の入口の中身（directory、参照資料、scripts）を指す path を返す。名前を挙げるだけの参照は返さない。"""
    name = re.escape(sibling)
    patterns = (
        rf"skills/{name}/",
        rf"\.\./{name}/",
        rf"(?<![A-Za-z0-9_-]){name}/references/",
        rf"(?<![A-Za-z0-9_-]){name}/scripts/",
        rf"(?<![A-Za-z0-9_-]){name}/SKILL\.md",
    )
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None


def check_siblings(path: Path, text: str, identity: str, entries: list[str]) -> None:
    for sibling in entries:
        if sibling == identity:
            continue
        found = sibling_path_reference(text, sibling)
        if found:
            fail(f"兄弟の入口の中身をpathで参照しています: {path}: {found}")


def validate_repository(repository: Path) -> None:
    skills = repository / "plugins/development-convention/skills"
    entries = sorted(path.name for path in skills.iterdir() if path.is_dir())
    for identifier in entries:
        root = skills / identifier
        entry = root / "SKILL.md"
        text = entry.read_text(encoding="utf-8")
        check_siblings(entry, text, identifier, entries)
        links = set()
        for raw in MARKDOWN_LINK.findall(text):
            if raw.startswith("references/"):
                if not (root / raw).is_file():
                    fail(f"直接参照資料がありません: {root / raw}")
                links.add(root / raw)
        references = set((root / "references").glob("*.md"))
        if links != references:
            fail(f"内部入口から参照資料へ一段で到達できません: {entry}")
        for reference in references:
            check_siblings(reference, reference.read_text(encoding="utf-8"), identifier, entries)
    print(f"Repository contract: passed ({repository})")


def copy_repository(repository: Path, value: str) -> Path:
    candidate = Path(value) / "repository"
    shutil.copytree(repository, candidate, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    return candidate


def expect_rejected(repository: Path, label: str, expected: str, mutate) -> None:
    with tempfile.TemporaryDirectory(prefix="development-convention-negative-") as value:
        candidate = copy_repository(repository, value)
        mutate(candidate)
        try:
            validate_repository(candidate)
        except (ValidationError, OSError, UnicodeError) as exc:
            if expected not in str(exc):
                fail(f"負例「{label}」が期待した理由で失敗しません: {exc}")
            print(f"Repository negative: passed ({label})")
        else:
            fail(f"負例「{label}」を拒否できません")


def self_test(repository: Path) -> None:
    package = Path("plugins/development-convention")

    with tempfile.TemporaryDirectory(prefix="development-convention-positive-") as value:
        candidate = copy_repository(repository, value)
        (candidate / package / "skills/apply-yagni/SKILL.md").write_text(
            "---\nname: apply-yagni\ndescription: 構造契約だけを満たす境界fixture\n---\n# 境界fixture\n\n証拠を実読して判断する。\n",
            encoding="utf-8",
        )
        validate_repository(candidate)
        print("Repository positive: passed (判断語や節名を意味品質の代理にしない)")

    with tempfile.TemporaryDirectory(prefix="development-convention-sibling-name-") as value:
        candidate = copy_repository(repository, value)
        entry = candidate / package / "skills/apply-yagni/SKILL.md"
        entry.write_text(entry.read_text(encoding="utf-8") + "\n層の置き場の判断は `apply-layer-convention` が持つ。Go の一つの層は go-convention の `develop-usecase` などが仕上げる。\n", encoding="utf-8")
        validate_repository(candidate)
        print("Repository positive: passed (兄弟と外部packageの公開入口をbacktickの名前で挙げる境界の宣言)")

    def remove_reference(root: Path) -> None:
        (root / package / "skills/protect-entry-points/references/token-verification.md").unlink()

    def add_sibling_path(root: Path) -> None:
        path = root / package / "skills/apply-yagni/SKILL.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n[手順](../protect-entry-points/references/token-verification.md)を読む。\n", encoding="utf-8")

    def add_sibling_reference_path(root: Path) -> None:
        path = root / package / "skills/protect-entry-points/references/token-verification.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n詳しくは skills/fix-root-cause/ を読む。\n", encoding="utf-8")

    expect_rejected(repository, "直接参照資料の欠落", "直接参照資料", remove_reference)
    expect_rejected(repository, "兄弟の参照資料へのpath", "兄弟の入口の中身", add_sibling_path)
    expect_rejected(repository, "参照資料から兄弟のdirectoryへのpath", "兄弟の入口の中身", add_sibling_reference_path)
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
    except (ValidationError, OSError, UnicodeError) as exc:
        raise SystemExit(f"FAIL: {exc}")
