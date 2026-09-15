---
name: apply-yagni
description: いまの資料とテストが呼ばない公開シンボルを作らない・残さない。「これ要る？」「資料に無いものが混ざっていないか見て」 と言われたときに使う独立プレイブック。内部skill `apply-yagni` へルーティングする。
---

# apply-yagni

同梱の`playbook.yml`を公開入口とし、内部skill`apply-yagni`（`skills/apply-yagni/SKILL.md`）へ明示的にルーティングする。

## 実行

1. package root を決める。Claude Code では`${CLAUDE_PLUGIN_ROOT}`が package root である。Codex ではこの`SKILL.md`があるdirectoryの3つ上（`playbooks/development-convention/apply-yagni` の親の親の親）が package root である。
2. `bash "<package root>/playbooks/development-convention/apply-yagni/scripts/prepare.sh"`で、この入口と対応する内部skillが同じ配布パッケージ内にあることを検査する。
3. `<package root>/skills/apply-yagni/SKILL.md`を読み、その手順に従って実行する。手順、入力、出力、停止条件は内部skillの`SKILL.md`を正本とし、この入口は何も足さない。
4. `scripts/resolve.sh`は公開入口と内部skillの対応を機械可読なJSONとして返す。

外部packageへの依存は無い。
