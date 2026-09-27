// Command api は、X のクローンの API を起動する。
package main

import (
	"context"
	"log/slog"
	"net/http"
	"os"
	"os/signal"

	"example.com/xclone/internal/account"
	"example.com/xclone/internal/auth"
	"example.com/xclone/internal/follow"
	"example.com/xclone/internal/identity"
	"example.com/xclone/internal/ratelimit"
	"example.com/xclone/internal/timeline"
)

func main() {
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)
	defer stop()
	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
	srv := &http.Server{Addr: ":8080", Handler: newMux(logger)}
	go func() { <-ctx.Done(); _ = srv.Shutdown(context.Background()) }()
	if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		logger.Error("起動できなかった", slog.Any("err", err))
	}
}

func newMux(logger *slog.Logger) http.Handler {
	verifier := auth.NewVerifier("https://auth.example.com", "https://auth.example.com/.well-known/jwks.json")
	lookup := identity.NewClient("https://api.auth.example.com/v1")
	limiter := ratelimit.New()

	mux := http.NewServeMux()
	mux.Handle("POST /accounts", auth.Require(verifier, account.Register(lookup)))
	mux.Handle("POST /follows", auth.Require(verifier, limiter.PerUser("follow", 20, account.ResolveUser(follow.Follow()))))
	mux.Handle("DELETE /follows/{followee}", auth.Require(verifier, limiter.PerUser("follow", 20, account.ResolveUser(follow.Unfollow()))))
	mux.Handle("GET /timeline", auth.Require(verifier, limiter.PerUser("timeline", 60, account.ResolveUser(timeline.Home()))))
	mux.Handle("POST /webhooks/identity", identity.Webhook(logger))
	mux.Handle("POST /internal/timelines/rebuild", timeline.Rebuild(logger))
	mux.HandleFunc("GET /healthz", func(w http.ResponseWriter, _ *http.Request) { w.WriteHeader(http.StatusNoContent) })
	return mux
}
