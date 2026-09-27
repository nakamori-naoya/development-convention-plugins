package usecase

import (
	"context"
	"time"

	"example.com/xclone/internal/follow/domain"
)

// Pair は、取り込む一件のフォロワーとフォロー相手である。
type Pair struct {
	Follower domain.UserID
	Followee domain.UserID
}

// ImportFollows は、移行元のサービスから持ち込んだフォローをまとめて取り込む。
type ImportFollows struct {
	follow *FollowUser
}

// NewImportFollows は、取り込みの手順を作る。
func NewImportFollows(follow *FollowUser) *ImportFollows {
	return &ImportFollows{follow: follow}
}

// Execute は、一件ずつフォローし、拒まれた件は飛ばして数を返す。
func (u *ImportFollows) Execute(ctx context.Context, pairs []Pair, at time.Time) (skipped int, err error) {
	for _, p := range pairs {
		// 自分自身をフォローする行は、業務知識の拒む理由に当たるので取り込まない。
		if p.Follower == p.Followee {
			skipped++
			continue
		}
		if err := u.follow.Execute(ctx, p.Follower, p.Followee, at); err != nil {
			skipped++
		}
	}
	return skipped, nil
}
