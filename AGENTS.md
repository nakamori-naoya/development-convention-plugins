# AGENTS.md

このrepositoryは、言語に依存しない開発規約を公開入口から配布するsourceである。

- marketplaceへ公開するインストール対象は`development-convention` package 1件だけにする。
- 公開入口は`apply-layer-convention`、`develop-inside-out`、`apply-yagni`の3件だけにする。
- 内部skillは一つの仕事を単独で完了し、兄弟skill、構成順序、公開入口を認識しない。
- 内部skillとその参照資料では、英語が通例の技術用語を除き日本語を使う。
- 検証では典型例、負例、境界例を実行し、期待した判断と停止を確かめる。
- 変更後は`bash scripts/validate.sh`とworkspace rootの検査を実行する。
