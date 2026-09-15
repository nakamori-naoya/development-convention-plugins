#!/usr/bin/env python3
"""一場面の開始条件と検証ゲートを決定的に評価する。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


ALLOWED = {
    "journey_scene", "mode", "persistence", "rdb_explicitly_excludes",
    "lower_gate_green",
}


def evaluate(value: dict) -> dict:
    unknown = sorted(set(value) - ALLOWED)
    if unknown:
        raise ValueError(f"未定義の入力: {unknown}")
    for key in ALLOWED - {"mode"}:
        if key in value and value[key] is not None and not isinstance(value[key], bool):
            raise ValueError(f"{key}はbooleanまたはnullでなければならない")
    if "journey_scene" not in value or value["journey_scene"] is None:
        return {"action": "stop", "reason": "journey_scene_unknown", "gates": []}
    if value["journey_scene"] is not True:
        return {"action": "stop", "reason": "journey_scene_missing", "gates": []}
    if "persistence" not in value or value["persistence"] is None:
        return {"action": "stop", "reason": "persistence_requirement_unknown", "gates": []}
    if value["persistence"] is True:
        if "rdb_explicitly_excludes" not in value or value["rdb_explicitly_excludes"] is None:
            return {"action": "stop", "reason": "persistence_scope_unknown", "gates": []}
        if value["rdb_explicitly_excludes"] is True:
            return {"action": "stop", "reason": "persistence_input_missing", "gates": []}
    if "mode" not in value or value["mode"] is None:
        return {"action": "stop", "reason": "operation_mode_unknown", "gates": []}
    if not isinstance(value["mode"], str):
        raise ValueError("modeはstringでなければならない")
    if value["mode"] not in {"command", "query"}:
        return {"action": "stop", "reason": "operation_mode_unknown", "gates": []}
    if "lower_gate_green" not in value or value["lower_gate_green"] is None:
        return {"action": "stop", "reason": "lower_gate_unknown", "gates": []}
    if value["lower_gate_green"] is not True:
        return {"action": "stop", "reason": "lower_gate_red", "gates": ["acceptance_red"]}
    gates = ["acceptance_red"]
    if value["mode"] == "query":
        gates.append("query_real_db")
    else:
        gates.append("domain")
        if value.get("persistence") is True:
            gates.append("repository_real_db")
    gates.extend(["usecase", "handler_acceptance_green"])
    return {"action": "proceed", "gates": gates}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    args = parser.parse_args()
    value = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit("入力はJSON objectでなければならない")
    try:
        result = evaluate(value)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
