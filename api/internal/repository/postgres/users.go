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
			media_files,
			smoking,
			children,
			pets,
			occupants_count,
			noise_lvl,
			works_from_home,
			alcohol,
			age_min,
			age_max
		FROM tg_user WHERE id = $1`
	row := r.connPool.QueryRow(ctx, query, id)
	err = row.Scan(
		&user.Id,
		&user.Name,
		&user.City,
		&user.MediaFiles,
		&user.Flags.Smoking,
		&user.Flags.Children,
		&user.Flags.Pets,
		&user.Flags.OccupantsCount,
		&user.Flags.NoiseLvl,
		&user.Flags.WorksFromHome,
		&user.Flags.Alcohol,
		&user.Flags.AgeMin,
		&user.Flags.AgeMax,
	)
	return user, err
}

func (r UsersRepo) CreateUser(ctx context.Context, userData model.UserCreate) error {
	query := `
		INSERT INTO tg_user (
			id,
			name,
			city,
			media_files
		)
		VALUES ($1, $2, $3, $4)
		ON CONFLICT DO NOTHING
	`
	_, err := r.connPool.Exec(
		ctx,
		query,
		userData.Id,
		userData.Name,
		userData.City,
		userData.MediaFiles,
	)

	return err
}

func (r UsersRepo) UpdateFlags(ctx context.Context, userID int64, flags model.UserFlags) error {
	query := `
		UPDATE tg_user SET
			smoking = COALESCE($1, smoking),
			children = COALESCE($2, children),
			pets = COALESCE($3, pets),
			occupants_count = COALESCE($4, occupants_count),
			noise_lvl = COALESCE($5, noise_lvl),
			works_from_home = COALESCE($6, works_from_home),
			alcohol = COALESCE($7, alcohol),
			age_min = COALESCE($8, age_min),
			age_max = COALESCE($9, age_max)
		WHERE id = $10
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
		userID,
	)

	if err != nil {
		return fmt.Errorf("failed to update user flags: %w", err)
	}

	return nil
}

func (r UsersRepo) EditUser(ctx context.Context, userId int64, patch model.UserEdit) error {
	args := pgx.NamedArgs{}

	query := "UPDATE tg_user SET "
	updates := []string{}

	if patch.Name != nil {
		updates = append(updates, "name = @name")
		args["name"] = patch.Name
	}
	if patch.City != nil {
		updates = append(updates, "city = @city")
		args["city"] = patch.City
	}
	if patch.MediaFiles != nil {
		updates = append(updates, "media_files = @media_files")
		args["media_files"] = patch.MediaFiles
	}

	if len(updates) == 0 {
		return nil
	}

	query += strings.Join(updates, ",")

	query += " WHERE id = @id"
	args["id"] = userId

	_, err := r.connPool.Exec(ctx, query, args)
	return err
}
