package postgres

import (
	"context"
	"fmt"
	"homie-api/internal/model"
	"strings"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

type UsersRepo struct {
	connPool *pgxpool.Pool
}

func NewUsersRepo(connPool *pgxpool.Pool) *UsersRepo {
	return &UsersRepo{
		connPool: connPool,
	}
}

func (r UsersRepo) GetById(ctx context.Context, id int64) (user model.User, err error) {
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

func (r UsersRepo) CreateUser(ctx context.Context, userData model.UserCreate) error {
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

func (r UsersRepo) EditUser(ctx context.Context, userId int64, patch model.UserEdit) error {
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

func (r UsersRepo) UpdateFlags(ctx context.Context, userID int64, flags model.UserFlags) error {
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

func (r UsersRepo) checkPremiumTx(ctx context.Context, tx pgx.Tx, userId int64) (hasPremium bool, err error) {
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
