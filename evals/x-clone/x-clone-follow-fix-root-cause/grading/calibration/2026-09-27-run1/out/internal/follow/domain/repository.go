package domain

import "context"

// Repository は、フォローを見つけ、起きたことを記録する。
type Repository interface {
	FindCandidate(ctx context.Context, follower, followee UserID) (Candidate, error)
	ApplyFollowed(ctx context.Context, e Followed) error
}
