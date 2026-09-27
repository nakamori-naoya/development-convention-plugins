// Package domain は、一人のフォロワーから一人のフォロー相手へのフォローを表す。
package domain

import "time"

// followLimit は、一人がフォロー中にできる人数の上限である。
const followLimit = 5000

// UserID は、登録した利用者を一人に決める識別子である。
type UserID struct{ v string }

// NewUserID は、利用者IDを読む。
func NewUserID(s string) UserID { return UserID{v: s} }

// FollowingCount は、フォロワーがいまフォロー中の人数である。
type FollowingCount struct{ n int }

// NewFollowingCount は、フォロー中の人数を作る。
func NewFollowingCount(n int) FollowingCount { return FollowingCount{n: n} }

// Candidate は、まだフォローしていないフォロワーと相手の組と、フォロワーのいまのフォロー中の人数である。
type Candidate struct {
	follower  UserID
	followee  UserID
	following FollowingCount
}

// NewCandidate は、フォローする前の状態を作る。
func NewCandidate(follower, followee UserID, following FollowingCount) Candidate {
	return Candidate{follower: follower, followee: followee, following: following}
}

// Following は、フォロー中のフォローである。
type Following struct {
	follower   UserID
	followee   UserID
	followedAt time.Time
}

// Followed は、フォローしたという出来事である。
type Followed struct {
	Follower   UserID
	Followee   UserID
	FollowedAt time.Time
}

// FollowResult は、フォローした結果である。
type FollowResult struct {
	Next  Following
	Event Followed
}

// Follow は、相手をフォローする。相手が自分自身か、フォロー上限に達していれば拒む。
func (c Candidate) Follow(at time.Time) (FollowResult, error) {
	if c.follower == c.followee {
		return FollowResult{}, ErrSelfFollow
	}
	if c.following.n >= followLimit {
		return FollowResult{}, ErrFollowLimitReached
	}
	next := Following{follower: c.follower, followee: c.followee, followedAt: at}
	return FollowResult{Next: next, Event: Followed{Follower: c.follower, Followee: c.followee, FollowedAt: at}}, nil
}
