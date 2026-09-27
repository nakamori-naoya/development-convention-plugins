#!/usr/bin/env bash
# ケースが共有する準備。空の作業場所に、ケースの fixture を写した手元だけの git repository（out/）を作り、
# skill が読む別 package のファイルを harness/ へ写す。作業場所の agent は外へ接続できないので、
# Go の toolchain は手元のものに固定する。この script は作業場所の外の権限で動く。
#
#   bash scaffold.sh <fixture のディレクトリ>
set -euo pipefail

[ $# -eq 1 ] || { echo "使い方: bash scaffold.sh <fixture のディレクトリ>" >&2; exit 2; }
FIXTURE=$(cd "$1" && pwd)
EVALS_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
WORKSPACE=$(cd "$EVALS_DIR/../.." && pwd)
WRITE_DOC="$WORKSPACE/write-doc-plugins/plugins/write-doc/skills/write-doc"
[ -f "$WRITE_DOC/SKILL.md" ] || { echo "兄弟 checkout の skill が無い: $WRITE_DOC" >&2; exit 2; }

mkdir -p out harness
cp -R "$FIXTURE/." out/
cp -R "$WRITE_DOC" harness/write-doc

GOENV_FILE="$HOME/Library/Application Support/go/env"
mkdir -p "$(dirname "$GOENV_FILE")"
printf 'GOTOOLCHAIN=local\nGOPROXY=off\n' > "$GOENV_FILE"
if [ -f out/go.mod ]; then (cd out && go build ./...); fi

git -C out init -q
git -C out add -A
git -C out -c user.name=eval -c user.email=eval@example.invalid commit -q -m "作業の前の状態"
