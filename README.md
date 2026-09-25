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

`scripts/validate.sh`は先に兄弟checkout `../harness-tools/tools/validate-plugin-repository.py`（保守toolの唯一の参照元。無ければ止まる）でroot契約を検査し、CIは`.github/workflows/validate.yml`で`harness-tools`を兄弟checkoutして`harness-tools/ci/validate.sh`で同じcommandを実行する。repository固有検証は、manifest、直接公開境界、各skill文書の自己完結性（兄弟の中身へのpathの参照が無いこと）を検査する。文章や判断の意味品質は対象を実読して評価する。
