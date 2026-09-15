---
name: develop-inside-out
description: BDD 資料のテストをゲートにして、受け入れテストから始めドメイン → リポジトリ → ユースケース → ハンドラーの順に実装する。「この資料一式から実装して」「次の層へ進んでいい？」 と言われたときに使う独立プレイブック。内部skill `develop-inside-out` へルーティングする。
---

# develop-inside-out

同梱の`playbook.yml`を公開入口とし、内部skill`develop-inside-out`（`skills/develop-inside-out/SKILL.md`）へ明示的にルーティングする。

## 実行

1. package root を決める。Claude Code では`${CLAUDE_PLUGIN_ROOT}`が package root である。Codex ではこの`SKILL.md`があるdirectoryの3つ上（`playbooks/development-convention/develop-inside-out` の親の親の親）が package root である。
2. `bash "<package root>/playbooks/development-convention/develop-inside-out/scripts/prepare.sh"`で、この入口と対応する内部skillが同じ配布パッケージ内にあることを検査する。
3. `<package root>/skills/develop-inside-out/SKILL.md`を読み、その手順に従って実行する。手順、入力、出力、停止条件は内部skillの`SKILL.md`を正本とし、この入口は何も足さない。
4. `scripts/resolve.sh`は公開入口と内部skillの対応を機械可読なJSONとして返す。

外部packageへの依存は無い。
