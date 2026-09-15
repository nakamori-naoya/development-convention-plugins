---
name: apply-layer-convention
description: 論理責務・依存方向・CommandとQueryの分離・複数集約の整合性の置き場を、言語を問わず決める。「これはどの責務に置く？」「集約をまたぐ整合はどこで守る？」と言われたときに使う独立プレイブック。内部skill `apply-layer-convention` へルーティングする。
---

# apply-layer-convention

同梱の`playbook.yml`を公開入口とし、内部skill`apply-layer-convention`（`skills/apply-layer-convention/SKILL.md`）へ明示的にルーティングする。

## 実行

1. package root を決める。Claude Code では`${CLAUDE_PLUGIN_ROOT}`が package root である。Codex ではこの`SKILL.md`があるdirectoryの3つ上（`playbooks/development-convention/apply-layer-convention` の親の親の親）が package root である。
2. `bash "<package root>/playbooks/development-convention/apply-layer-convention/scripts/prepare.sh"`で、この入口と対応する内部skillが同じ配布パッケージ内にあることを検査する。
3. `<package root>/skills/apply-layer-convention/SKILL.md`を読み、その手順に従って実行する。手順、入力、出力、停止条件は内部skillの`SKILL.md`を正本とし、この入口は何も足さない。
4. `scripts/resolve.sh`は公開入口と内部skillの対応を機械可読なJSONとして返す。

外部packageへの依存は無い。
