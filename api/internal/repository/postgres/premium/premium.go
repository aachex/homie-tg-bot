package premium

import (
	"context"
	"homie-api/internal/model"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

type Repository struct {
	connPool *pgxpool.Pool
}

func NewRepository(connPool *pgxpool.Pool) *Repository {
	return &Repository{
		connPool: connPool,
	}
}

func (r Repository) UserLimits(ctx context.Context, userId int64) (limits model.UserLimits, err error) {
	return r.UserLimitsTx(ctx, r.connPool, userId)
}

func (r Repository) UserLimitsTx(ctx context.Context, q rowQueryer, userId int64) (limits model.UserLimits, err error) {
	if userId == 1 {
		return model.UserLimits{
			IsPremium:      false,
			MaxOffersCount: 2000,
			MaxLikesPerDay: 2000,
		}, nil
	}

	hasPrem, err := r.CheckPremiumTx(ctx, q, userId)
	if err != nil {
		return model.UserLimits{}, err
	}

	limits.IsPremium = hasPrem

	// Максимальное количество объявлений
	limits.MaxOffersCount = 1
	if hasPrem {
		limits.MaxOffersCount = 10
	}

	// Максимальное количество лайков в день
	limits.MaxLikesPerDay = 10
	if hasPrem {
		limits.MaxLikesPerDay = 100
	}

	return limits, nil
}

type rowQueryer interface {
	QueryRow(ctx context.Context, sql string, args ...any) pgx.Row
}

func (r Repository) CheckPremiumTx(ctx context.Context, tx rowQueryer, userId int64) (hasPremium bool, err error) {
	if tx == nil {
		tx = r.connPool
	}

	query := `
		SELECT EXISTS (
			SELECT until
			FROM premium
			WHERE user_id = $1 AND NOW() < until
		)
	`
	row := tx.QueryRow(ctx, query, userId)
	err = row.Scan(&hasPremium)
	return hasPremium, err
}
