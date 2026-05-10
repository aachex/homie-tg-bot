package postgres

import (
	"context"
	"homie-api/internal/model"

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

func (r *ActivitiesRepository) CreateUserActivity(ctx context.Context, activity model.UserActivityCreate) (id int64, err error) {
	query := `
		INSERT INTO user_activities (
			user_id,
			action,
			time
		)
		VALUES ($1, $2, $3)
		ON CONFLICT DO NOTHING
		RETURNING id
	`
	row := r.connPool.QueryRow(ctx, query, activity.UserId, activity.Action, activity.Timestamp)
	err = row.Scan(&id)
	return id, err
}
