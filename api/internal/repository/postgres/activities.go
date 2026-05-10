package postgres

import (
	"context"

	"github.com/jackc/pgx/v5/pgxpool"
)

type ActivitiesRepository struct {
	connPool *pgxpool.Pool
}

func NewActivitiesRepo(connPool *pgxpool.Pool) *ActivitiesRepository {
	return &ActivitiesRepository{
		connPool: connPool,
	}
}

func (r *ActivitiesRepository) CreateUserActivity(ctx context.Context, userId int64, action string, action_data map[string]any) (id int64, err error) {
	query := `
		INSERT INTO user_activities (
			user_id,
			action,
			action_data
		)
		VALUES ($1, $2, $3)
		ON CONFLICT DO NOTHING
		RETURNING id
	`
	row := r.connPool.QueryRow(ctx, query, userId, action, action_data)
	err = row.Scan(&id)
	return id, err
}
