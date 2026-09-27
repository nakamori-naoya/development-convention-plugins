# development-convention-plugins

言語に依存しない開発規約を、独立した六つの公開入口として配布するrepositoryである。

## 公開入口

- `apply-layer-convention`: 四層、CQRSの読み書き分離、複数集約の整合性をコードへ適用する。
- `develop-inside-out`: BDD資料を検証可能なゲートへ写し、内側から外側へ機能を実装する。
- `apply-yagni`: 現在の業務の資料とそこから導いたテストが要求しない公開シンボルを作らず、残さない。
- `fix-root-cause`: 不具合の症状を業務の資料と突き合わせて再現テストを赤にし、全呼び出し経路が経由する最も内側の一か所を最小の変更で直す。
- `protect-entry-points`: 外部から呼べる入口ごとに、認証、認可、利用上限、偽装要求への対策、呼び出す高価な下流の資源を宣言した資料を作る。
- `write-readable-code`: 名前を業務の言葉で付け、コメントを自分の責務だけで書き、テストのために実装を曲げない。

marketplaceが公開・インストールするのは`development-convention` package一件だけである。package manifestは六つの自己完結skillを`skills/`から直接公開する。各skillの判断と手順は、その`SKILL.md`（と参照資料）にある。

## 責務の境界

各入口は単独で利用できる。層の配置判断、機能の実装手順、不要な公開面の削減、不具合の根本原因修正、入口の保護の宣言を暗黙に連鎖させない。対象コードや業務の資料が不足し、判断によって結果が変わる場合は推測せず停止する。

規約の基準資料は`decisions/development-convention-plugins.jsonl`である。過去の決定は書き換えず、変更は新しい記録を追記する。

## このpackageが持つ判断

入口の保護の判断は `protect-entry-points` が持つ。外部から呼べる入口ごとに、認証、認可、利用上限、偽装要求への対策、呼び出す高価な下流の資源を宣言させること、適用除外にする入口には下流を何で守るかと受け入れの決定の所在を書かせること、主体を解決する前に高価な資源を呼ぶ入口の扱い、署名付きトークンの検証の順と鍵の取り直しの間隔がここにある。

その他の入口が持つ判断は、各入口の `SKILL.md` にある。

## 検証

```bash
PYTHONDONTWRITEBYTECODE=1 bash /Users/naoya-nakamoriq/Documents/Github/harness-pluginsv2/development-convention-plugins/scripts/validate.sh
PYTHONDONTWRITEBYTECODE=1 bash /Users/naoya-nakamoriq/Documents/Github/harness-pluginsv2/scripts/validate.sh /Users/naoya-nakamoriq/Documents/Github/harness-pluginsv2/development-convention-plugins
```

`scripts/validate.sh`は先に兄弟checkout `../harness-tools/tools/validate-plugin-repository.py`（保守toolの唯一の参照元。無ければ止まる）でroot契約を検査し、CIは`.github/workflows/validate.yml`で`harness-tools`を兄弟checkoutして`harness-tools/ci/validate.sh`で同じcommandを実行する。repository固有検証は、各入口から自分の参照資料へ直接届くことと、各skill文書の自己完結性（兄弟の中身へのpathの参照が無いこと）を検査する。文章や判断の意味品質は対象を実読して評価する。

## 検証の eval

skill が利用者の原則に沿った成果を出せるかは、root の `evals/` の下のケースで確かめる。実行は `claude plugin eval` が受け持ち、出来の採点は、作業したエージェントとは別の Claude（採点役）が、条件ごとに判定と根拠の引用を書いて受け持つ。今は、X のクローンを題材に、fix-root-cause（入口の一つにだけ防ぎがある repository の不具合を直す）と protect-entry-points（入口ごとに守りのばらつく API の保護を宣言する）の二つのケースを置いている。develop-inside-out は実物の DB を通す受け入れテストを要し、eval のサンドボックスでは Docker にも localhost にも接続できないので、単独のケースを置かず、go-convention と react-convention の実装のケースの条件で、書く前に書かずに済む道を探したか、赤から始めたかを見る。apply-layer-convention、apply-yagni、write-readable-code も同じく、実装のケースの条件で見る。

`evals/criteria/` には採点役への指示 `brief.md` と成果の種類ごとの共通の条件を、`evals/scaffold.sh` には、ケースの `fixture/` を手元だけの git repository（`out/`）に写し、write-doc の skill を兄弟 checkout から `harness/` へ写す共通の準備を置く。ケースには、`prompt.md`、`case.yaml`、`scaffold.sh`、読まずに判定できること（skill を使ったか、資料ができたか、直す前に再現のテストが失敗したか）だけの `graders/`、固有の条件 `grading/criteria.md`、較正の資料 `grading/calibration/`（実際の成果と、既知の欠陥を埋めた写しの二本と、それぞれの `expected.md`）を置く。

```bash
claude plugin eval . --case x-clone-follow-fix-root-cause \
  --runs 1 --ablation none --keep-temp \
  --scaffold --allow-tools Write Edit Bash \
  --max-cost-usd 10 --no-publish
bash /Users/naoya-nakamoriq/Documents/Github/harness-pluginsv2/harness-tools/tools/grade-eval.sh \
  "$(pwd)/evals/x-clone/x-clone-follow-fix-root-cause" /private/tmp/e-XXXXXX
```

採点役は3回回し、条件ごとの多数決に重み（利用者の原則の芯を3、骨組みを2、細部を1）を掛けて100点満点にする。85点以上は「実用に足る」、70点以上は「手直しで使える」、70点未満は「作り直しが要る」である。条件や採点役への指示を変えたら、較正の資料に採点役をかけ、`expected.md` を三つ目の引数に渡して一致を確かめる。結果は `evals/results/` に書かれ、git の管理から外してある。
