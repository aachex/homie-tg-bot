package postgres

import (
	"context"
	"homie-api/internal/model"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

type StatsRepo struct {
	connPool *pgxpool.Pool
}

func NewStatsRepo(connPool *pgxpool.Pool) *StatsRepo {
	return &StatsRepo{
		connPool: connPool,
	}
}

func (r *StatsRepo) DAU(ctx context.Context, fromDate time.Time, toDate time.Time) (dau []model.DailyStat, err error) {
	query := `
		SELECT 
        	time,
            COUNT(DISTINCT user_id) as dau
        FROM user_activities
        WHERE time >= $1 AND time <= $2
        GROUP BY time
        ORDER BY time ASC
	`

	rows, err := r.connPool.Query(ctx, query, fromDate, toDate)
	if err != nil {
		return nil, err
	}

	for rows.Next() {
		var s model.DailyStat
		err = rows.Scan(&s.Date, &s.DAU)
		if err != nil {
			return nil, err
		}
	}

	err = rows.Err()
	return dau, err
}

func (r *StatsRepo) CreateUserActivity(ctx context.Context, userId int64, action string, action_data map[string]any) (id int64, err error) {
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
