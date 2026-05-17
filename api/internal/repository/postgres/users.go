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

func (r UsersRepo) CreateUser(ctx context.Context, userData model.User) error {
	query := `
		INSERT INTO tg_user (
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
		)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
		ON CONFLICT DO NOTHING
	`
	_, err := r.connPool.Exec(
		ctx,
		query,
		userData.Id,
		userData.Name,
		userData.City,
		userData.MediaFiles,
		userData.Flags.Smoking,
		userData.Flags.Children,
		userData.Flags.Pets,
		userData.Flags.OccupantsCount,
		userData.Flags.NoiseLvl,
		userData.Flags.WorksFromHome,
		userData.Flags.Alcohol,
		userData.Flags.AgeMin,
		userData.Flags.AgeMax,
	)

	return err
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
	if patch.Flags != nil {
		flagUpdates := map[string]any{
			"smoking":         patch.Flags.Smoking,
			"children":        patch.Flags.Children,
			"pets":            patch.Flags.Pets,
			"occupants_count": patch.Flags.OccupantsCount,
			"noise_lvl":       patch.Flags.NoiseLvl,
			"works_from_home": patch.Flags.WorksFromHome,
			"alcohol":         patch.Flags.Alcohol,
			"age_min":         patch.Flags.AgeMin,
			"age_max":         patch.Flags.AgeMax,
		}

		for column, value := range flagUpdates {
			if value != nil {
				updates = append(updates, fmt.Sprintf("%s = @%s", column, column))
				args[column] = value
			}
		}
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
