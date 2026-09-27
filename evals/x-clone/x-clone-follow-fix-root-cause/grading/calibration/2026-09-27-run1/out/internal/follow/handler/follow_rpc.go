// Package handler は、フォローの入口を持つ。
package handler

import (
	"encoding/json"
	"net/http"
	"time"

	"example.com/xclone/internal/follow/domain"
	"example.com/xclone/internal/follow/usecase"
)

// FollowRPC は、利用者がフォロー相手を指定してフォローする入口である。
type FollowRPC struct {
	Follow *usecase.FollowUser
}

type followRequest struct {
	FolloweeID string `json:"followee_id"`
}

// ServeHTTP は、認証済みの利用者をフォロワーとしてフォローする。
func (h *FollowRPC) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	var req followRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "入力が不正", http.StatusBadRequest)
		return
	}
	me := r.Header.Get("X-User-ID")
	err := h.Follow.Execute(r.Context(), domain.NewUserID(me), domain.NewUserID(req.FolloweeID), time.Now().UTC())
	if err != nil {
		http.Error(w, err.Error(), http.StatusConflict)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
