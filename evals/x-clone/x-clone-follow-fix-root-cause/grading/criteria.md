<!-- common: root-cause-fix -->
<!-- document: out/go.mod -->

# X のクローンの自分自身のフォローに固有の条件

作業の前の repository では、フォローするコマンドは自分自身のフォローを拒まず、画面の入口（`handler/follow_rpc.go`）だけが同じ利用者かを比べて拒んでいた。夜間の取り込み（`handler/import_job.go` から `usecase/import_follows.go`）は同じコマンドを通るが、防ぎが無かった。業務知識は「自分自身をフォローする」を拒む理由に持つ。

### fixed-in-aggregate-command

重み: 3

PASS：自分自身のフォローを拒む判断を、画面と取り込みの両方が通るフォローのコマンド（`domain` の集約）の中に置き、拒む理由を業務知識の「自分自身をフォローする」に当たる具体エラーで返している。

FAIL：判断を取り込みの経路（`import_job.go` か `import_follows.go`）か usecase の手順に足している。または、集約以外の一つの経路にだけ置いている。

### duplicate-guard-consolidated

重み: 2

PASS：直した後の repository で、自分自身のフォローを拒む判断は一か所にだけある。画面の入口にあった同じ判断（同じ利用者かを比べて拒む分岐）は、集約へ寄せて取り除かれている。

FAIL：同じ判断が、入口、手順、集約のうち二か所以上に残っている。報告が残した理由を述べていても、二か所以上にあれば FAIL とする。
