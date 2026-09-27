#!/usr/bin/env bash
# 入口ごとに守りのばらつく API の repository を作る。
set -euo pipefail
CASE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
exec bash "$CASE_DIR/../../scaffold.sh" "$CASE_DIR/fixture"
