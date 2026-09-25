> 作業を始める前に、workspace規約入口 `/Users/naoya-nakamoriq/Documents/Github/harness-pluginsv2/AGENTS.md` を読み、そこから指定される共通規約とこのrepository固有の規則を適用する。

# AGENTS.md

このrepositoryは、言語に依存しない開発規約を公開入口から配布するsourceである。

- marketplaceへ公開するインストール対象は`development-convention` package 1件だけにする。
- 公開入口は`apply-layer-convention`、`develop-inside-out`、`apply-yagni`、`fix-root-cause`、`protect-entry-points`の5件だけにする。
- package manifestは5件の自己完結skillを`skills/`から直接公開する。存在確認だけのprepare、外側の単一routing playbook、入口別runtime manifestを要求しない。
- 各skillは一つの仕事を単独で完了し、兄弟skillの中身（path、参照資料、工程）に依存しない。判断の持ち主として兄弟skillの名前を挙げることは、境界の宣言として許す。
- 内部skillとその参照資料では、英語が通例の技術用語を除き日本語を使う。
- 検証では典型例、負例、境界例を実行し、期待した判断と停止を確かめる。
- 変更後は`bash scripts/validate.sh`とworkspace rootの検査を実行する。

## 検査スクリプトは、意味が一意に決まることだけを判定する

このrepositoryの検査スクリプト（validate、lint、verify、checkなど、名前を問わない）が判定してよいのは、ファイルや見出しの有無、識別子や版の一致、宣言と配置の対応、禁止された書き方の有無のように、入力と基準資料から意味が決定論的に一意に決まることだけである。読んで解釈しないと決まらないことや、件数や語の出現のような品質の代わりの指標は判定せず、エージェントが読んで評価する（意味評価）。判定が一意に決まることを宣言できない検査は作らず、詳しい条件は `/Users/naoya-nakamoriq/Documents/Github/harness-pluginsv2/.agents/rules/deterministic-validation.md` に従う。
