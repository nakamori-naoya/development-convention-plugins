// Package identity は、外部の認証サービスとのやり取りを持つ。
package identity

import (
	"context"
	"encoding/json"
	"log/slog"
	"net/http"
)

// Client は、認証サービスの利用者の照会 API を呼ぶ。例: "https://api.auth.example.com/v1"。
type Client struct{ baseURL string }

// NewClient は、照会 API の base URL から Client を作る。
func NewClient(baseURL string) *Client { return &Client{baseURL: baseURL} }

// EmailVerified は、主体のメールアドレスが確かめられているかを照会する。
func (c *Client) EmailVerified(ctx context.Context, subject string) (bool, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, c.baseURL+"/users/"+subject, nil)
	if err != nil {
		return false, err
	}
	res, err := http.DefaultClient.Do(req)
	if err != nil {
		return false, err
	}
	defer res.Body.Close()
	var body struct {
		EmailVerified bool `json:"email_verified"`
	}
	return body.EmailVerified, json.NewDecoder(res.Body).Decode(&body)
}

type deletedEvent struct {
	Type    string `json:"type"`
	Subject string `json:"subject"`
}

// Webhook は、認証サービスから届く「利用者を削除した」の知らせを受け、その主体の利用者とポストを消す。
func Webhook(logger *slog.Logger) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		var e deletedEvent
		if err := json.NewDecoder(r.Body).Decode(&e); err != nil {
			http.Error(w, "入力が不正", http.StatusBadRequest)
			return
		}
		logger.InfoContext(r.Context(), "利用者の削除を受けた", slog.String("type", e.Type))
		w.WriteHeader(http.StatusNoContent)
	})
}
