# development-convention-plugins

言語に依存しない開発規約を、独立した三つの公開入口として配布するrepositoryである。

## 公開入口

- `apply-layer-convention`: 四層、CQRSの読み書き分離、複数集約の整合性をコードへ適用する。
- `develop-inside-out`: BDD資料を検証可能なゲートへ写し、内側から外側へ機能を実装する。
- `apply-yagni`: 現在の正本資料とそこから導いたテストが要求しない公開シンボルを作らず、残さない。

marketplaceが公開・インストールするのは`development-convention` package一件だけである。package manifestは三つの自己完結skillを`skills/`から直接公開し、存在確認だけのprepare、外側のrouting playbook、入口別manifestを挟まない。各skill直下の`playbook.yml` v2が一つの仕事の工程順序を保持し、公開`SKILL.md`から同じagentが宣言順に辿る。

## 責務の境界

各入口は単独で利用できる。層の配置判断、機能の実装手順、不要な公開面の削減を暗黙に連鎖させない。対象コードや正本資料が不足し、判断によって結果が変わる場合は推測せず停止する。

規約の正本は`decisions/development-convention-plugins.jsonl`である。過去の決定は書き換えず、変更は新しい記録を追記する。

## 検証

```bash
PYTHONDONTWRITEBYTECODE=1 bash /Users/naoya-nakamoriq/Documents/Github/harness-pluginsv2/development-convention-plugins/scripts/validate.sh
PYTHONDONTWRITEBYTECODE=1 bash /Users/naoya-nakamoriq/Documents/Github/harness-pluginsv2/scripts/validate.sh /Users/naoya-nakamoriq/Documents/Github/harness-pluginsv2/development-convention-plugins
```

repository固有検証は、manifest、直接公開境界、各skill文書の自己完結性に加え、隣接`playbook.yml`のidentity、宣言順、`agent_work: invoking_agent`、実値を使う場合のneeds/provides接続を検査する。文章や判断の意味品質は対象を実読して評価する。
