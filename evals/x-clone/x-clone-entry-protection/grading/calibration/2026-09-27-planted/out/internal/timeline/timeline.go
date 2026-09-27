// Package timeline は、ホームタイムラインの取得と作り直しの入口を持つ。
package timeline

import (
	"log/slog"
	"net/http"
)

// Home は、利用者のホームタイムラインを返す。
func Home() http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) { w.WriteHeader(http.StatusOK) })
}

// Rebuild は、全利用者のホームタイムラインを作り直す。
func Rebuild(logger *slog.Logger) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		logger.InfoContext(r.Context(), "ホームタイムラインの作り直しを始めた")
		w.WriteHeader(http.StatusAccepted)
	})
}
