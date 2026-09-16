> 作業を始める前に、workspace正本入口 `/Users/naoya-nakamoriq/Documents/Github/harness-pluginsv2/AGENTS.md` を読み、そこから指定される共通規約とこのrepository固有の規則を適用する。

# AGENTS.md

このrepositoryは、言語に依存しない開発規約を公開入口から配布するsourceである。

- marketplaceへ公開するインストール対象は`development-convention` package 1件だけにする。
- 公開入口は`apply-layer-convention`、`develop-inside-out`、`apply-yagni`、`fix-root-cause`の4件だけにする。
- package manifestは4件の自己完結skillを`skills/`から直接公開する。存在確認だけのprepare、外側の単一routing playbook、入口別runtime manifestを要求しない。
- 各skillは一つの仕事を単独で完了し、兄弟skillを認識しない。各skill直下の`playbook.yml` v2をその仕事の工程順序の正本とし、同じagentが`agent_work: invoking_agent`の工程を宣言順に実行する。
- 内部skillとその参照資料では、英語が通例の技術用語を除き日本語を使う。
- 検証では典型例、負例、境界例を実行し、期待した判断と停止を確かめる。
- 変更後は`bash scripts/validate.sh`とworkspace rootの検査を実行する。
