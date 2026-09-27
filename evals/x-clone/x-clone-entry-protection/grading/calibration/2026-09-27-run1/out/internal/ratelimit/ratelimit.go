// Package ratelimit は、利用者一人あたりの要求の回数を数えて上限で止める。
package ratelimit

import (
	"net/http"
	"sync"
	"time"

	"example.com/xclone/internal/account"
)

// Limiter は、操作の種類と利用者ごとに、直近1分の回数を数える。
type Limiter struct {
	mu     sync.Mutex
	counts map[string][]time.Time
}

// New は、空の Limiter を作る。
func New() *Limiter { return &Limiter{counts: map[string][]time.Time{}} }

// PerUser は、解決した利用者ごとに1分あたり perMinute 回までを通す。
func (l *Limiter) PerUser(kind string, perMinute int, next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		user, _ := account.UserFrom(r.Context())
		key := kind + ":" + string(user)
		now := time.Now()
		l.mu.Lock()
		recent := l.counts[key][:0]
		for _, t := range l.counts[key] {
			if now.Sub(t) < time.Minute {
				recent = append(recent, t)
			}
		}
		if len(recent) >= perMinute {
			l.mu.Unlock()
			http.Error(w, "利用上限に達した", http.StatusTooManyRequests)
			return
		}
		l.counts[key] = append(recent, now)
		l.mu.Unlock()
		next.ServeHTTP(w, r)
	})
}
