# 期待する判定

この較正の資料は、2026-09-27 の1回目の実行（claude plugin eval、`--runs 1 --ablation none`）で作られた資料と報告である。下の判定は、eval を組んだ担当が資料とコードと品質要求を読んで出した。報告は `out/trace.jsonl` の result の行に置いた（grade-eval.sh は作業場所の `out/trace.jsonl` から報告を写すため）。採点役には、このファイルを読ませない。

## 判定

- all-entries-listed: PASS
- unprotected-named: PASS
- limits-not-guessed: FAIL（境目）
- exclusions-with-decision: PASS
- per-entry-declaration: PASS
- no-code-change: PASS
- written-for-reading: PASS
- registration-before-resolution: PASS
- webhook-verification: PASS
- internal-boundary: PASS
- token-verification-gaps: PASS
- daily-limit-gap: PASS

## 理由

資料は七つの入口を挙げ、登録、Webhook、作り直し、鍵の取り直しを無防備と名指しし、品質要求に無い上限の値を未決に返している。ただし、作り直しの「同時に一つ」は品質要求に無い上限を宣言として置いたもので、同時の数を利用上限の値と読むかで判定が分かれるので、limits-not-guessed を FAIL の境目とした。
