#!/usr/bin/env python3
"""一つの公開シンボルの保持・拒否を決定的に評価する。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


ALLOWED = {
    "public", "canonical_doc_calls", "derived_test_calls", "future_only",
    "compatibility", "auxiliary_test_case_id_generated",
    "randomized_input_values", "random_new_behavior", "existing",
}


def reject_action(value: dict) -> str:
    return "remove" if value.get("existing") is True else "do_not_create"


def evaluate(value: dict) -> dict:
    unknown = sorted(set(value) - ALLOWED)
    if unknown:
        raise ValueError(f"未定義の入力: {unknown}")
    for key in ALLOWED:
        if key in value and value[key] is not None and not isinstance(value[key], bool):
            raise ValueError(f"{key}はbooleanまたはnullでなければならない")
    required = ("public", "existing", "canonical_doc_calls", "derived_test_calls")
    missing = [key for key in required if key not in value or value[key] is None]
    if missing:
        return {"classification": "unresolved", "action": "stop", "reason": "required_evidence_unknown", "unknown": missing}
    if value["public"] is not True:
        return {"classification": "out_of_scope", "action": "proceed"}
    if value.get("compatibility") is True:
        return {"classification": "reject", "action": reject_action(value)}
    if value.get("random_new_behavior") is True:
        return {"classification": "reject", "action": reject_action(value)}
    documents = value.get("canonical_doc_calls") is True
    tests = value.get("derived_test_calls") is True
    if documents and tests:
        return {"classification": "keep", "action": "proceed"}
    if documents and not tests:
        return {"classification": "reject", "action": "stop", "reason": "test_trace_missing"}
    return {"classification": "reject", "action": reject_action(value)}


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
