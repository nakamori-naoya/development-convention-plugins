package domain

import "errors"

// フォローするときの拒む理由。文言は業務知識の拒む理由の語である。
var (
	ErrSelfFollow         = errors.New("自分自身をフォローする")
	ErrFollowLimitReached = errors.New("フォロー上限に達している利用者がフォローする")
	ErrNotFollowing       = errors.New("フォローしていない相手のフォローを外す")
)
