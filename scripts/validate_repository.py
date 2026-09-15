#!/usr/bin/env python3
"""development-convention packageの公開境界と内部文書契約を検査する。"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
from pathlib import Path


IDS = ("apply-layer-convention", "develop-inside-out", "apply-yagni")
FORBIDDEN_COMPOSITION = re.compile(r"playbook|プレイブック", re.IGNORECASE)
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


def validate_internal(package: Path) -> None:
    roots = {identifier: package / "skills" / identifier for identifier in IDS}
    for identifier, root in roots.items():
        entry = root / "SKILL.md"
        reference_dir = root / "references"
        assert_regular(entry, "内部入口")
        assert_regular(root / "scripts/evaluate.py", "決定的評価器")
        text = entry.read_text(encoding="utf-8")
        if FORBIDDEN_COMPOSITION.search(text):
            fail(f"内部入口が構成単位を認識しています: {entry}")
        for sibling in set(IDS) - {identifier}:
            if re.search(rf"(?<![A-Za-z0-9_-]){re.escape(sibling)}(?![A-Za-z0-9_-])", text):
                fail(f"内部入口が兄弟identityを参照しています: {entry}: {sibling}")
        if "scripts/evaluate.py" not in text or "--input" not in text:
            fail(f"内部入口が所有する評価器を実行手順にしていません: {entry}")
        links = []
        for raw in MARKDOWN_LINK.findall(text):
            if raw.startswith("references/"):
                links.append(raw)
                assert_regular(root / raw, "直接参照資料")
        references = sorted(reference_dir.glob("*.md"))
        if len(links) != 1 or {root / raw for raw in links} != set(references):
            fail(f"内部入口から参照資料へ一段で到達できません: {entry}")
        for reference in references:
            body = reference.read_text(encoding="utf-8")
            if FORBIDDEN_COMPOSITION.search(body) or re.search(r"(?:skill|スキル)\s*(?:名|ID|入口|工程|実行|参照)", body, re.IGNORECASE):
                fail(f"参照資料が構成単位を認識しています: {reference}")
            for identity in IDS:
                if re.search(rf"(?<![A-Za-z0-9_-]){re.escape(identity)}(?![A-Za-z0-9_-])", body):
                    fail(f"参照資料が構成identityを参照しています: {reference}: {identity}")
        for runtime in ("codex", "claude"):
            manifest = load_json(root / f".{runtime}-plugin/plugin.json")
            if manifest.get("name") != identifier or manifest.get("skills") != "./":
                fail(f"内部{runtime} manifestが自己入口を指していません: {root}")


def validate_public(package: Path, manifest: dict) -> None:
    harness = manifest.get("metadata", {}).get("harness", {})
    if harness.get("installationSurface") != "playbook-package":
        fail("公開・インストール面がplaybook-packageではありません")
    expected_public = {identifier: f"./playbooks/development-convention/{identifier}" for identifier in IDS}
    expected_internal = {identifier: f"./skills/{identifier}" for identifier in IDS}
    if harness.get("playbooks") != expected_public:
        fail("公開入口宣言が三件の規定値と一致しません")
    if harness.get("internalPlugins") != expected_internal:
        fail("内部実装宣言が三件の規定値と一致しません")
    if manifest.get("skills") != list(expected_public.values()):
        fail("manifestのskillsに公開入口以外が混入しています")

    for identifier, relative in expected_public.items():
        root = package / relative.removeprefix("./")
        for name in ("SKILL.md", "playbook.yml", "scripts/prepare.sh", "scripts/resolve.sh"):
            assert_regular(root / name, "公開入口の必須file")
        contract = (root / "playbook.yml").read_text(encoding="utf-8")
        if not re.search(rf"^name:\s*{re.escape(identifier)}\s*$", contract, re.MULTILINE):
            fail(f"公開契約のnameが不一致です: {root}")
        if not re.search(rf"skill:\s*{re.escape(identifier)}(?:\s|[, }}]|$)", contract):
            fail(f"公開契約が対応する内部実装へroutingしていません: {root}")
        if re.search(r"^\s*-\s*\{[^\n]*(?:playbook|plugin):", contract, re.MULTILINE):
            fail(f"公開契約に外部または追加の構成工程があります: {root}")
        inputs = bracket_values(contract, "inputs")
        needs = bracket_values(contract, "needs")
        if inputs != needs:
            fail(f"公開契約のinputsと工程needsが一致しません: {root}: inputs={inputs}, needs={needs}")
        for runtime in ("codex", "claude"):
            child = load_json(root / f".{runtime}-plugin/plugin.json")
            if child.get("name") != identifier or child.get("skills") != "./":
                fail(f"公開{runtime} manifestが自己入口を指していません: {root}")


def validate_content(repository: Path) -> None:
    package = repository / "plugins/development-convention"
    layer = (package / "skills/apply-layer-convention/SKILL.md").read_text(encoding="utf-8")
    delivery = (package / "skills/develop-inside-out/SKILL.md").read_text(encoding="utf-8")
    yagni = (package / "skills/apply-yagni/SKILL.md").read_text(encoding="utf-8")
    required_layer = ("ドメイン", "集約リポジトリ", "ユースケース", "外部境界", "Query実装", "logical_role", "outbox", "宣言的制約", "言語固有の物理配置を出力していない")
    required_delivery = ("user-journey-bdd", "受け入れテスト", "実DB", "Before/After", "ロールバック", "Query実装", "下層のゲート")
    required_yagni = ("domain-rule", "domain-model", "rdb-logical-data-modeling", "user-journey-bdd", "公開シンボル", "shim", "deprecated", "ランダム")
    for label, text, required in (("層", layer, required_layer), ("実装", delivery, required_delivery), ("YAGNI", yagni, required_yagni)):
        missing = [item for item in required if item not in text]
        if missing:
            fail(f"{label}の必須判断が不足しています: {missing}")
        for heading in ("## 入力", "## 開始条件", "## 作業手順", "## 出力", "## 非責務", "## 停止条件", "## 完了条件", "## 使用例"):
            if heading not in text:
                fail(f"{label}にsectionがありません: {heading}")
        for example in ("典型例:", "似て非なる例:", "反例:", "境界例:"):
            if example not in text:
                fail(f"{label}に判断例がありません: {example}")


def validate_decisions(repository: Path) -> None:
    path = repository / "decisions/development-convention-plugins.jsonl"
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not any(item.get("aspect") == "root validate.sh の self-test" and item.get("status") == "superseded" for item in records):
        fail("古いroot self-test未決を上書きする追記がありません")


def validate_repository(repository: Path) -> None:
    if not repository.is_absolute() or repository.is_symlink() or not repository.is_dir():
        fail(f"repositoryは実在する絶対directoryでなければなりません: {repository}")
    codex, claude = catalog_entry(repository, "codex"), catalog_entry(repository, "claude")
    if codex != claude or codex != ("development-convention", "0.1.0", "./plugins/development-convention"):
        fail("runtime間の公開package identityが一致しません")
    package = repository / "plugins/development-convention"
    manifests = [load_json(package / f".{runtime}-plugin/plugin.json") for runtime in ("codex", "claude")]
    if shared_manifest(manifests[0]) != shared_manifest(manifests[1]):
        fail("runtime間の公開契約が一致しません")
    validate_public(package, manifests[0])
    validate_internal(package)
    validate_content(repository)
    validate_decisions(repository)
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

    def expose_internal(root: Path) -> None:
        for runtime in ("codex", "claude"):
            path = root / package / f".{runtime}-plugin/plugin.json"
            value = load_json(path)
            value["skills"].append("./skills/apply-yagni")
            path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def remove_reference(root: Path) -> None:
        (root / package / "skills/develop-inside-out/references/delivery-gates.md").unlink()

    def add_composition(root: Path) -> None:
        path = root / package / "skills/apply-yagni/references/evidence-rule.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n外部playbookを呼ぶ。\n", encoding="utf-8")

    def add_sibling(root: Path) -> None:
        path = root / package / "skills/apply-yagni/SKILL.md"
        path.write_text(path.read_text(encoding="utf-8") + "\ndevelop-inside-outを先に実行する。\n", encoding="utf-8")

    def add_undeclared_need(root: Path) -> None:
        path = root / package / "playbooks/development-convention/apply-yagni/playbook.yml"
        text = path.read_text(encoding="utf-8")
        text = text.replace(
            "needs: [request, target_repository, target_scope, canonical_artifacts, derived_tests, public_symbols]",
            "needs: [request, target_repository, target_scope, canonical_artifacts, derived_tests, public_symbols, undeclared_input]",
        )
        path.write_text(text, encoding="utf-8")

    expect_rejected(repository, "内部実装の公開", "公開入口以外", expose_internal)
    expect_rejected(repository, "直接参照資料の欠落", "直接参照資料", remove_reference)
    expect_rejected(repository, "参照資料の構成認識", "構成単位", add_composition)
    expect_rejected(repository, "内部入口の兄弟認識", "兄弟identity", add_sibling)
    expect_rejected(repository, "未宣言の工程入力", "inputsと工程needs", add_undeclared_need)
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
