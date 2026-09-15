#!/usr/bin/env python3
"""一つの責務または整合性判断を決定的に評価する。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


ALLOWED = {
    "operation", "mode", "requested_role", "restores_aggregate",
    "reads_other_aggregate", "writes_aggregates", "expected_time_gap",
    "collective_constraint", "db_declarative_constraint",
}
ROLES = {
    "domain", "aggregate_repository", "external_boundary",
    "query_implementation", "aggregate_command_coordination",
    "cross_aggregate_command_coordination",
}


def evaluate(value: dict) -> dict:
    unknown = sorted(set(value) - ALLOWED)
    if unknown:
        raise ValueError(f"未定義の入力: {unknown}")
    for key in ("restores_aggregate", "reads_other_aggregate", "expected_time_gap", "collective_constraint", "db_declarative_constraint"):
        if key in value and value[key] is not None and not isinstance(value[key], bool):
            raise ValueError(f"{key}はbooleanまたはnullでなければならない")
    if "requested_role" not in value or value["requested_role"] is None:
        return {"action": "stop", "reason": "responsibility_unknown"}
    if not isinstance(value["requested_role"], str):
        return {"action": "stop", "reason": "responsibility_invalid"}
    role = value["requested_role"]
    if role not in ROLES:
        return {"action": "stop", "reason": "responsibility_invalid"}
    if "mode" in value and value["mode"] is not None and not isinstance(value["mode"], str):
        return {"action": "stop", "reason": "operation_mode_invalid"}
    if "operation" in value and value["operation"] is not None and not isinstance(value["operation"], str):
        raise ValueError("operationはstringまたはnullでなければならない")
    is_query = value.get("mode") == "query" or value.get("operation") in {"list", "count", "search", "exists"}
    if is_query and (role in {"domain", "aggregate_repository"} or value.get("restores_aggregate") is True):
        return {"action": "stop", "reason": "query_role_conflict"}
    if value.get("collective_constraint") is True:
        if "db_declarative_constraint" not in value or value["db_declarative_constraint"] is None:
            return {"action": "stop", "reason": "db_constraint_unknown"}
        if value["db_declarative_constraint"] is False:
            return {"action": "stop", "reason": "db_constraint_unavailable"}
    if role in {"domain", "aggregate_repository", "external_boundary"}:
        return {"logical_role": role, "action": "proceed"}
    if role == "query_implementation":
        if value.get("mode") not in {None, "query"}:
            return {"action": "stop", "reason": "responsibility_mode_conflict"}
        if value.get("restores_aggregate") is True:
            return {"action": "stop", "reason": "query_restores_aggregate"}
        return {"logical_role": role, "action": "proceed"}
    if value.get("mode") not in {None, "command"}:
        return {"action": "stop", "reason": "responsibility_mode_conflict"}
    if "writes_aggregates" not in value or value["writes_aggregates"] is None:
        return {"action": "stop", "reason": "aggregate_write_count_unknown"}
    writes = value["writes_aggregates"]
    if not isinstance(writes, int) or isinstance(writes, bool) or writes < 0:
        raise ValueError("writes_aggregatesは0以上の整数でなければならない")
    if role == "cross_aggregate_command_coordination":
        if writes < 2:
            return {"action": "stop", "reason": "responsibility_write_count_conflict"}
        if "expected_time_gap" not in value or value["expected_time_gap"] is None:
            return {"action": "stop", "reason": "consistency_timing_unknown"}
        return {
            "logical_role": "cross_aggregate_command_coordination",
            "consistency": "outbox" if value.get("expected_time_gap") is True else "single_transaction",
            "action": "proceed",
        }
    if writes >= 2:
        return {"action": "stop", "reason": "responsibility_write_count_conflict"}
    return {"logical_role": "aggregate_command_coordination", "action": "proceed"}


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
