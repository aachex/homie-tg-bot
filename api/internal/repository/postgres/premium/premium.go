package premium

import (
	"context"

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

func (r Repository) CheckPremiumTx(ctx context.Context, tx pgx.Tx, userId int64) (hasPremium bool, err error) {
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
