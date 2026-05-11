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

// Возвращает только ID (для списка)
func (r *ReportsRepo) PendingReportIDs(ctx context.Context, offset, limit int) ([]int64, error) {
	query := `
		SELECT id
		FROM report
		ORDER BY created_at DESC
		OFFSET $1 LIMIT $2
	`

	rows, err := r.connPool.Query(ctx, query, offset, limit)
	if err != nil {
		return nil, fmt.Errorf("failed to get pending report IDs: %w", err)
	}
	defer rows.Close()

	var ids []int64
	for rows.Next() {
		var id int64
		if err := rows.Scan(&id); err != nil {
			return nil, err
		}
		ids = append(ids, id)
	}

	return ids, rows.Err()
}

// Возвращает полные данные (для детального просмотра)
func (r *ReportsRepo) ByID(ctx context.Context, id int64) (*model.Report, error) {
	query := `
		SELECT 
			id,
			offer_id,
			reporter_id,
			reason,
			created_at
		FROM report
		WHERE id = $1
	`

	var report model.Report
	err := r.connPool.QueryRow(ctx, query, id).Scan(
		&report.Id,
		&report.OfferId,
		&report.ReporterId,
		&report.Reason,
		&report.CreatedAt,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to get report by id: %w", err)
	}

	return &report, nil
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

func (r *ReportsRepo) Delete(ctx context.Context, id int64) error {
	query := `DELETE FROM report WHERE id = $1`
	_, err := r.connPool.Exec(ctx, query, id)
	return err
}
