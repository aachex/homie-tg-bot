package postgres

import (
	"context"
	"fmt"
	"homie-api/internal/model"

	"github.com/jackc/pgx/v5/pgxpool"
)

type ReportsRepo struct {
	connPool *pgxpool.Pool
}

func NewReportsRepo(connPool *pgxpool.Pool) *ReportsRepo {
	return &ReportsRepo{
		connPool: connPool,
	}
}

func (r *ReportsRepo) Count(ctx context.Context) (int, error) {
	query := `SELECT COUNT(*) FROM report`

	var count int
	err := r.connPool.QueryRow(ctx, query).Scan(&count)
	if err != nil {
		return 0, fmt.Errorf("failed to count reports: %w", err)
	}

	return count, nil
}
func (r *ReportsRepo) Create(ctx context.Context, data model.ReportCreate) (id int64, err error) {
	query := `
		INSERT INTO report (
			offer_id,
			reporter_id,
			reason
		)
		VALUES ($1, $2, $3)
		ON CONFLICT DO NOTHING
		RETURNING id
	`
	row := r.connPool.QueryRow(ctx, query, data.OfferId, data.ReporterId, data.Reason)
	err = row.Scan(&id)
	return id, err
}
