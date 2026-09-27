// Package usecase は、フォローの業務の手順を持つ。
package usecase

import (
	"context"
	"time"

	"example.com/xclone/internal/follow/domain"
)

// FollowUser は、利用者がほかの利用者をフォローする。
type FollowUser struct {
	repo domain.Repository
}

// NewFollowUser は、フォローする手順を作る。
func NewFollowUser(repo domain.Repository) *FollowUser {
	return &FollowUser{repo: repo}
}

// Execute は、フォロワーがフォロー相手をフォローする。
func (u *FollowUser) Execute(ctx context.Context, follower, followee domain.UserID, at time.Time) error {
	c, err := u.repo.FindCandidate(ctx, follower, followee)
	if err != nil {
		return err
	}
	res, err := c.Follow(at)
	if err != nil {
		return err
	}
	return u.repo.ApplyFollowed(ctx, res.Event)
}
