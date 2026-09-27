#!/usr/bin/env bash
# 取り込みの経路にだけ自分自身のフォローの防ぎが無い repository を作る。
set -euo pipefail
CASE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
exec bash "$CASE_DIR/../../scaffold.sh" "$CASE_DIR/fixture"
