# 期待する判定

この較正の資料は、1回目の実行の資料に既知の欠陥を埋めた写しである。下の判定は、埋め方から決まる。報告は1回目のままにした。報告は `out/trace.jsonl` の result の行に置いた（grade-eval.sh は作業場所の `out/trace.jsonl` から報告を写すため）。採点役には、このファイルを読ませない。

## 判定

- all-entries-listed: FAIL
- unprotected-named: FAIL
- limits-not-guessed: FAIL
- exclusions-with-decision: PASS
- per-entry-declaration: FAIL
- no-code-change: PASS
- written-for-reading: PASS
- registration-before-resolution: FAIL
- webhook-verification: FAIL
- internal-boundary: PASS
- token-verification-gaps: PASS
- daily-limit-gap: PASS

## 理由

Webhook の入口を表と本文から消し（all-entries-listed、webhook-verification）、登録の入口の上限に品質要求に無い10回/分を置いて未決から外した（limits-not-guessed、registration-before-resolution）。Webhook を消したことで、守りの無い入口の一つが名指しされず（unprotected-named）、その入口の宣言も無くなる（per-entry-declaration）。ほかの節は1回目のままである。
