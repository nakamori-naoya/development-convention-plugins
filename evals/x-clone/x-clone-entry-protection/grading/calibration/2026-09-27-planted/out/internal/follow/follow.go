// Package follow は、フォローとフォロー解除の入口を持つ。
package follow

import "net/http"

// Follow は、利用者が相手をフォローする。
func Follow() http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) { w.WriteHeader(http.StatusNoContent) })
}

// Unfollow は、利用者が相手のフォローを外す。
func Unfollow() http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) { w.WriteHeader(http.StatusNoContent) })
}
