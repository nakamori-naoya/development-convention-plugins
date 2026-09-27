---
description: 入口ごとに守りのばらつく小さな API の repository を渡し、protect-entry-points で入口の保護の宣言を資料にさせる。
tags: [x-clone, protect-entry-points]
plugins: ["../../../plugins/development-convention"]
max_turns: 120
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite, Write, Edit, Bash]
---

X のクローン（X に似た SNS）の API について、外から呼べる入口ごとの保護を宣言した資料を作ってください。

## 作業場所と保存先

対象の repository は、この作業場所の `out/` です。品質要求の資料は `out/docs/品質要求.md` にあります。資料は `out/docs/入口の保護.md` に新しく保存してください。コードは変えないでください。

この skill は write-doc の書くときの規範に従うよう求めますが、この環境には write-doc が入っていません。代わりに、その最新のファイルを `harness/write-doc/` の下へ写してあります。規範は `harness/write-doc/references/writing-norms.md` です。

## 問いと止まるとき

この実行には、問いに答える利用者がいません。skill が止まるよう定めた場面に当たったら、止まって、何が足りないかを報告してください。

## 報告

最後に、日本語で、保存した資料のパス、入口の数と列挙した方法、無防備な入口、受け入れの決定の無い適用除外、仮説として置いた宣言と未決を短く書いてください。
