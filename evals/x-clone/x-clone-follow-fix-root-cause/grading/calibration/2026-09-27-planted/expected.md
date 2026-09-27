# 期待する判定

この較正の資料は、作業の前の repository に既知の欠陥を埋めた写しである。下の判定は、埋め方から決まる。報告は `out/trace.jsonl` の result の行に置いた（grade-eval.sh は作業場所の `out/trace.jsonl` から報告を写すため）。採点役には、このファイルを読ませない。

## 判定

- expected-from-docs: PASS
- repro-at-innermost-layer: FAIL
- paths-traced: FAIL
- minimal-change: FAIL
- names-and-comments: PASS
- fixed-in-aggregate-command: FAIL
- duplicate-guard-consolidated: FAIL

## 理由

埋めた写しは、判断を取り込みの手順にだけ足し（fixed-in-aggregate-command）、入口の判断を残したまま理由を書かず（duplicate-guard-consolidated）、再現のテストを置かず（repro-at-innermost-layer）、画面の経路を辿らずに「取り込みだけを直せば足ります」とし（paths-traced）、症状に関係しない変数名の変更を入れた（minimal-change）。期待の根拠は業務知識の拒む理由を挙げ、足したコメントは業務の語だけなので、expected-from-docs と names-and-comments は PASS である。
