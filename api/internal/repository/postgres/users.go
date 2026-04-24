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

func (r UsersRepo) RandUser(ctx context.Context) (user model.User, err error) {
	query := `SELECT id, name, age, description, city, media_files FROM tg_user ORDER BY RANDOM() LIMIT 1`
	row := r.connPool.QueryRow(ctx, query)
	err = row.Scan(&user.Id, &user.Name, &user.Age, &user.Description, &user.City, &user.MediaFiles)
	return user, err
}

func (r UsersRepo) NewUser(ctx context.Context, userData model.User) error {
	err := r.transaction(ctx, func(tx pgx.Tx) error {
		// Проверяем, что пользователь не существует
		userExists, err := r.existsTx(ctx, tx, userData.Id)
		if err != nil {
			return err
		}

		if userExists {
			return ErrUserExists
		}

		// Пользователь не существует - добавляем его в БД
		return r.createUserTx(ctx, tx, userData)
	})

	return err
}

func (r UsersRepo) EditUser(ctx context.Context, userId int64, patch model.UserEditData) error {
	args := pgx.NamedArgs{}

	query := "UPDATE tg_user SET "
	updates := []string{}

	if patch.Name != "" {
		updates = append(updates, "name = @name")
		args["name"] = patch.Name
	}
	if patch.Age != 0 {
		updates = append(updates, "age = @age")
		args["age"] = patch.Age
	}
	if patch.Description != "" {
		updates = append(updates, "description = @description")
		args["description"] = patch.Description
	}
	if patch.City != "" {
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

func (r UsersRepo) existsTx(ctx context.Context, tx pgx.Tx, userId int64) (exists bool, err error) {
	query := `SELECT EXISTS (SELECT id FROM tg_user WHERE id = $1)`
	row := tx.QueryRow(ctx, query, userId)
	err = row.Scan(&exists)
	return exists, err
}

func (r UsersRepo) createUserTx(ctx context.Context, tx pgx.Tx, userData model.User) error {
	query := `INSERT INTO tg_user (id, name, age, description, city) VALUES ($1, $2, $3, $4, $5)`
	_, err := tx.Exec(
		ctx,
		query,
		userData.Id,
		userData.Name,
		userData.Age,
		userData.Description,
		userData.City,
	)

	return err
}

func (r UsersRepo) transaction(ctx context.Context, f func(tx pgx.Tx) error) error {
	tx, err := r.connPool.Begin(ctx)
	if err != nil {
		return err
	}
	defer tx.Rollback(ctx)

	err = f(tx)
	if err != nil {
		return err
	}

	err = tx.Commit(ctx)
	return err
}
