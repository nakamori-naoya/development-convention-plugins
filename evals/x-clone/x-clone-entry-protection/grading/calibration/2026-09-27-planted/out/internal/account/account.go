// Package account は、利用者の登録と、主体から利用者への解決を持つ。
package account

import (
	"context"
	"net/http"

	"example.com/xclone/internal/auth"
	"example.com/xclone/internal/identity"
)

type userKey struct{}

// UserID は、登録した利用者の識別子である。
type UserID string

// Register は、確かめた主体を利用者として登録する。認証サービスでメールアドレスが確かめられていなければ拒む。
func Register(lookup *identity.Client) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		sub, _ := auth.SubjectFrom(r.Context())
		verified, err := lookup.EmailVerified(r.Context(), string(sub))
		if err != nil {
			http.Error(w, "依存先が利用できない", http.StatusServiceUnavailable)
			return
		}
		if !verified {
			http.Error(w, "メールアドレスが確かめられていない", http.StatusForbidden)
			return
		}
		w.WriteHeader(http.StatusCreated)
	})
}

// ResolveUser は、主体を登録済みの利用者へ解決し、登録していなければ拒む。
func ResolveUser(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		sub, ok := auth.SubjectFrom(r.Context())
		if !ok {
			http.Error(w, "認証されていない", http.StatusUnauthorized)
			return
		}
		next.ServeHTTP(w, r.WithContext(context.WithValue(r.Context(), userKey{}, UserID("u-"+string(sub)))))
	})
}

// UserFrom は、解決した利用者を返す。
func UserFrom(ctx context.Context) (UserID, bool) {
	u, ok := ctx.Value(userKey{}).(UserID)
	return u, ok
}
