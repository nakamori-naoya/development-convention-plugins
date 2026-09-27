package handler

import (
	"context"
	"encoding/csv"
	"io"
	"log/slog"
	"time"

	"example.com/xclone/internal/follow/domain"
	"example.com/xclone/internal/follow/usecase"
)

// ImportJob は、移行元から受け取った CSV（フォロワーID,フォロー相手ID）を取り込む夜間の入口である。
type ImportJob struct {
	Import *usecase.ImportFollows
	Logger *slog.Logger
}

// Run は、CSV を読み、全件を取り込む。
func (j *ImportJob) Run(ctx context.Context, src io.Reader) error {
	rows, err := csv.NewReader(src).ReadAll()
	if err != nil {
		return err
	}
	pairs := make([]usecase.Pair, 0, len(rows))
	for _, row := range rows {
		pairs = append(pairs, usecase.Pair{Follower: domain.NewUserID(row[0]), Followee: domain.NewUserID(row[1])})
	}
	skipped, err := j.Import.Execute(ctx, pairs, time.Now().UTC())
	if err != nil {
		return err
	}
	j.Logger.InfoContext(ctx, "フォローを取り込んだ", slog.Int("skipped", skipped))
	return nil
}
