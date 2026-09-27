# X のクローンの API

利用者は、外部の認証サービスが発行した署名付きトークンを `Authorization: Bearer` で送る。ブラウザの画面は別の配備単位で、この API をトークン付きの fetch で呼ぶ。Cookie は使わない。

入口の組み立ては `cmd/api/main.go` の `newMux` にある。品質要求は `docs/品質要求.md` にある。
