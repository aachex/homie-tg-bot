package users

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"homie-api/internal/model"
	"homie-api/internal/repository/postgres"
	"strings"

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

func (r Repository) GetById(ctx context.Context, id int64) (user model.User, err error) {
	query := `
		SELECT
			id,
			name,
			city,
			description,
			media_files,
			flag_processing,
			smoking,
			children,
			pets,
			occupants_count,
			noise_lvl,
			works_from_home,
			alcohol,
			age_min,
			age_max,
			sex
		FROM tg_user WHERE id = $1`
	row := r.connPool.QueryRow(ctx, query, id)
	err = row.Scan(
		&user.Id,
		&user.Name,
		&user.City,
		&user.Description,
		&user.MediaFiles,
		&user.FlagProcessing,
		&user.Flags.Smoking,
		&user.Flags.Children,
		&user.Flags.Pets,
		&user.Flags.OccupantsCount,
		&user.Flags.NoiseLvl,
		&user.Flags.WorksFromHome,
		&user.Flags.Alcohol,
		&user.Flags.AgeMin,
		&user.Flags.AgeMax,
		&user.Flags.Sex,
	)
	return user, err
}

func (r Repository) CreateUser(ctx context.Context, userData model.UserCreate) error {
	query := `
		INSERT INTO tg_user (
			id,
			name,
			city,
			description,
			media_files,
			flag_processing
		)
		VALUES ($1, $2, $3, $4, $5, TRUE)
		ON CONFLICT DO NOTHING
	`
	_, err := r.connPool.Exec(
		ctx,
		query,
		userData.Id,
		userData.Name,
		userData.City,
		userData.Description,
		userData.MediaFiles,
	)

	return err
}

func (r Repository) EditUser(ctx context.Context, userId int64, patch model.UserEdit) error {
	args := pgx.NamedArgs{}

	query := "UPDATE tg_user SET "
	updates := []string{}

	updates = append(updates, "name = @name")
	args["name"] = patch.Name

	updates = append(updates, "city = @city")
	args["city"] = patch.City

	updates = append(updates, "description = @description")
	args["description"] = patch.Description

	updates = append(updates, "media_files = @media_files")
	args["media_files"] = patch.MediaFiles

	updates = append(updates, "flag_processing = TRUE")

	if len(updates) == 0 {
		return nil
	}

	query += strings.Join(updates, ",")

	query += " WHERE id = @id"
	args["id"] = userId

	_, err := r.connPool.Exec(ctx, query, args)
	return err
}

func (r Repository) UpdateFlags(ctx context.Context, userID int64, flags model.UserFlags) error {
	query := `
		UPDATE tg_user SET
            smoking = $1,
            children = $2,
            pets = $3,
            occupants_count = $4,
            noise_lvl = $5,
            works_from_home = $6,
            alcohol = $7,
            age_min = $8,
            age_max = $9,
			sex = $10,
			flag_processing = FALSE
        WHERE id = $11
	`

	_, err := r.connPool.Exec(ctx, query,
		flags.Smoking,
		flags.Children,
		flags.Pets,
		flags.OccupantsCount,
		flags.NoiseLvl,
		flags.WorksFromHome,
		flags.Alcohol,
		flags.AgeMin,
		flags.AgeMax,
		flags.Sex,
		userID,
	)

	if err != nil {
		return fmt.Errorf("failed to update user flags: %w", err)
	}

	return nil
}

func (r *Repository) TodayLikesCount(ctx context.Context, tx postgres.RowQueryer, userId int64) (count int, err error) {
	return r.TodayLikesCountTx(ctx, r.connPool, userId)
}

// TodayLikesCountTx возвращает количество лайков, которое поставил юзер за сегодня.
func (r *Repository) TodayLikesCountTx(ctx context.Context, tx postgres.RowQueryer, userId int64) (count int, err error) {
	query := `
		SELECT likes_count FROM daily_likes
		WHERE user_id = $1 AND date = CURRENT_DATE
	`
	row := tx.QueryRow(ctx, query, userId)
	err = row.Scan(&count)
	if !errors.Is(err, sql.ErrNoRows) && err != nil {
		return 0, err
	}
	return count, nil
}

func (r *Repository) IncrementTodayLikesTx(ctx context.Context, tx pgx.Tx, userId int64) error {
	query := `
			INSERT INTO daily_likes (user_id, likes_count)
			VALUES ($1, 1)
			ON CONFLICT (user_id, date) DO 
			UPDATE SET likes_count = daily_likes.likes_count + 1
		`
	_, err := tx.Exec(ctx, query, userId)
	return err
}
