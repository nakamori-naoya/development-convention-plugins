# apply-yagni — 2026-09-16 実行記録の所見

記録: [apply-yagni.json](apply-yagni.json)（case `apply-yagni-judgment-only`、stage `after-required-reference-read`、resource `references/evidence-rule.md`、生成 `claude-opus-5` effort high、独立judge `claude-sonnet-5`、SKILL sha256 `d2edc3f1cfed…` ＝ 確定版）。試行の履歴: [attempt-1](apply-yagni.attempt-1.json) 確定前SKILL・judge出力がJSONでなく `error`、[attempt-2](apply-yagni.attempt-2.json) 確定前SKILL（`dda7271a…`）に対する有効な記録、[attempt-3](apply-yagni.attempt-3.json) / [attempt-4](apply-yagni.attempt-4.json) 確定版に対する生成は有効・judgeのJSONが不正（表を跨ぐquoteのエスケープ不正、末尾の `}` 欠落）で `error`。本記録は5回目。

## 実行

```bash
cd development-convention-plugins && python3 ../product-planning-plugins/shared/runtime-source/evaluate-skills.py --fixtures evals/scenarios.json \
  --model-command '["python3","../product-planning-plugins/shared/runtime-source/claude-eval-adapter.py"]' \
  --judge-command '["python3","../product-planning-plugins/shared/runtime-source/claude-eval-adapter.py"]' \
  --model claude-opus-5 --judge-model claude-sonnet-5 --settings '{"effort":"high"}' --output evals/runs/2026-09-16/apply-yagni.json
```

このrepositoryは評価runtimeの複製を持たないので、正式な定義を直接使った。

## agentの所見（「」は応答の逐語。『』はSKILL等の出典付き引用）

| criterion | 所見 | 根拠 |
|---|---|---|
| reject-unsourced | 満たす。RescheduleとExportCSVをrejectにし、保持依頼には従えないと明言。保持したいなら正式な定義へ操作を追加するのが先と示す | 「`Reschedule`を`keep`にしてほしいという依頼には従えません。「あると便利」「将来必要」で保持しない、が手順3の失敗時条項そのものです。」 |
| keep-sourced | 満たす。ConfirmとCancelをkeepにし、資料の絶対path・観測時点・業務操作・テストの追跡を根拠に挙げる | 「domain-rule「予約を確定する」（`/tmp/fixture-repo/docs/domain-rule.md`, 2026-09-01）と、それを写した確定テストが呼ぶ」 |
| judgment-only | 満たす。コードを変えず、未確認5点と正式な定義へ戻す問いを示す | 「判定だけの依頼のため、コードは変更していません。」「正式な定義へ戻す問い: 「日程を変更する」を業務操作として domain-rule / domain-model に追加するか。」 |

judge（3件pass）と一致。attempt-2（確定前）と判定は同じ。

## 気づき

- ExportCSVが集約packageに置かれている点を「層配置は非責務」として判定対象外にしており、SKILL.md冒頭の『層の配置、実装工程の進行、一般的なコード品質の改善は行わない』と整合する。
- judgeが5回中3回JSONを正しく返せなかった唯一のcase。応答が表（`|` 区切り）を多用し、judgeが表の行をquoteに選ぶとエスケープを誤る傾向がある。runner側の検査は変えていない。

## 未確認

- 実コード・実資料は無く、利用者提示の事実だけで判定させた合成fixture。
