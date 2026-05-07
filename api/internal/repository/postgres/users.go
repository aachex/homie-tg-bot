package postgres

import (
	"context"
	"errors"
	"homie-api/internal/model"
	"strings"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

var (
	ErrUserExists = errors.New("this user already exists")
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
	query := `SELECT id, name, age, description, city, media_files FROM tg_user WHERE id = $1`
	row := r.connPool.QueryRow(ctx, query, id)
	err = row.Scan(&user.Id, &user.Name, &user.Age, &user.Description, &user.City, &user.MediaFiles)
	return user, err
}

func (r UsersRepo) CreateUser(ctx context.Context, userData model.User) error {
	query := `
		INSERT INTO tg_user (
			id,
			name,
			age,
			description,
			city,
			media_files,
			is_smoking,
			has_children,
			has_pets
		)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
		ON CONFLICT DO NOTHING
	`
	_, err := r.connPool.Exec(
		ctx,
		query,
		userData.Id,
		userData.Name,
		userData.Age,
		userData.Description,
		userData.City,
		userData.MediaFiles,
		userData.Details.Smoking,
		userData.Details.Children,
		userData.Details.Pets,
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
	if patch.Age != nil {
		updates = append(updates, "age = @age")
		args["age"] = patch.Age
	}
	if patch.Description != nil {
		updates = append(updates, "description = @description")
		args["description"] = patch.Description
	}
	if patch.City != nil {
		updates = append(updates, "city = @city")
		args["city"] = patch.City
	}
	if patch.MediaFiles != nil {
		updates = append(updates, "media_files = @media_files")
		args["media_files"] = patch.MediaFiles
	}
	if patch.Details != nil {
		updates = append(updates, "is_smoking = @is_smoking")
		args["is_smoking"] = patch.Details.Smoking

		updates = append(updates, "has_children = @has_children")
		args["has_children"] = patch.Details.Children

		updates = append(updates, "has_pets = @has_pets")
		args["has_pets"] = patch.Details.Pets
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
