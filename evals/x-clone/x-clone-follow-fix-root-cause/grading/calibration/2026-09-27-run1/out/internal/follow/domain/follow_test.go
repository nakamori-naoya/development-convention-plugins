package domain_test

import (
	"errors"
	"testing"
	"time"

	"example.com/xclone/internal/follow/domain"
)

// BDD の資料: docs/フォロー/business-knowledge.md
func TestCandidate_Follow(t *testing.T) {
	t.Parallel()
	at := time.Date(2026, 9, 1, 12, 0, 0, 0, time.UTC)
	alice := domain.NewUserID("u-alice")
	bob := domain.NewUserID("u-bob")
	tests := []struct {
		id          string
		name        string
		description string
		following   int
		wantErr     error
	}{
		{
			id:   "BDD-002",
			name: "4,999人をフォロー中の利用者は5,000人目をフォローできる",
			description: `
Given: アリスは4,999人をフォロー中である
When: アリスがボブをフォローする
Then: アリスはボブをフォロー中になる`,
			following: 4999,
		},
		{
			id:   "BDD-003",
			name: "5,000人をフォロー中の利用者は次の一人をフォローできない",
			description: `
Given: アリスは5,000人をフォロー中である
When: アリスがボブをフォローする
Then: フォローは拒まれる`,
			following: 5000,
			wantErr:   domain.ErrFollowLimitReached,
		},
	}
	t.Run("BDD-004 自分自身はフォローできない", func(t *testing.T) {
		t.Parallel()
		// Given: アリスのフォロー中の人数は10人である
		// When: アリスがアリスをフォローする
		// Then: フォローは生まれず、「フォローした」は起きない
		c := domain.NewCandidate(alice, alice, domain.NewFollowingCount(10))
		_, err := c.Follow(at)
		if !errors.Is(err, domain.ErrSelfFollow) {
			t.Fatalf("err = %v, want %v", err, domain.ErrSelfFollow)
		}
	})
	for _, tt := range tests {
		t.Run(tt.id+" "+tt.name, func(t *testing.T) {
			t.Parallel()
			c := domain.NewCandidate(alice, bob, domain.NewFollowingCount(tt.following))
			_, err := c.Follow(at)
			if !errors.Is(err, tt.wantErr) {
				t.Fatalf("err = %v, want %v", err, tt.wantErr)
			}
		})
	}
}
