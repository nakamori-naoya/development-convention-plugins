// Package auth は、署名付きトークンから要求の主体を確かめる。
package auth

import (
	"context"
	"net/http"
	"strings"
)

type subjectKey struct{}

// Subject は、認証サービスが発行したトークンの主体である。例: "user_2abcXYZ"。
type Subject string

// Require は、主体を確かめられた要求だけを next へ渡す。
func Require(v *Verifier, next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		token, ok := strings.CutPrefix(r.Header.Get("Authorization"), "Bearer ")
		if !ok {
			http.Error(w, "認証されていない", http.StatusUnauthorized)
			return
		}
		sub, err := v.Verify(r.Context(), token)
		if err != nil {
			http.Error(w, "認証されていない", http.StatusUnauthorized)
			return
		}
		next.ServeHTTP(w, r.WithContext(context.WithValue(r.Context(), subjectKey{}, sub)))
	})
}

// SubjectFrom は、確かめた主体を返す。
func SubjectFrom(ctx context.Context) (Subject, bool) {
	s, ok := ctx.Value(subjectKey{}).(Subject)
	return s, ok
}
