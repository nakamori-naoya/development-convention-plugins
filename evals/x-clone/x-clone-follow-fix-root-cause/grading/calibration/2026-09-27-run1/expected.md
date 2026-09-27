# 期待する判定

この較正の資料は、2026-09-27 の1回目の実行（claude plugin eval、`--runs 1 --ablation none`）で作られた repository と報告である。下の判定は、eval を組んだ担当がコードと報告と資料を読んで出した。報告は `out/trace.jsonl` の result の行に置いた（grade-eval.sh は作業場所の `out/trace.jsonl` から報告を写すため）。採点役には、このファイルを読ませない。

## 判定

- expected-from-docs: PASS
- repro-at-innermost-layer: PASS
- paths-traced: PASS
- minimal-change: PASS
- names-and-comments: PASS
- fixed-in-aggregate-command: PASS
- duplicate-guard-consolidated: PASS

## 理由

実行の成果は、判断を集約のコマンド（`Candidate.Follow`）へ置き、入口の同じ判断を取り除き、BDD-004 を写した再現のテストをドメインに足し、二つの経路を報告に挙げている。入口の応答の Code が変わることは、症状を直す一か所の変更に伴うもので、報告で確かめを求めているので minimal-change を PASS とした。
