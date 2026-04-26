package controller

import (
	"context"
	"database/sql"
	"errors"
	"homie-api/internal/model"
	"homie-api/internal/repository/postgres"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
)

type usersRepo interface {
	GetById(ctx context.Context, id int64) (model.User, error)
	NewUser(ctx context.Context, userData model.User) error
	EditUser(ctx context.Context, userId int64, patch model.UserEdit) error
}

type Users struct {
	usersRepo usersRepo
}

func NewUsers(usersRepo usersRepo) *Users {
	return &Users{
		usersRepo: usersRepo,
	}
}

func (c Users) UserById(ctx *gin.Context) {
	userId, err := strconv.ParseInt(ctx.Param("id"), 10, 64)
	if err != nil {
		controllerError(ctx, err, http.StatusBadRequest)
		return
	}

	user, err := c.usersRepo.GetById(ctx, userId)
	if errors.Is(err, sql.ErrNoRows) {
		controllerError(ctx, errors.New("user not found"), http.StatusNotFound)
		return
	}

	if err != nil {
		controllerError(ctx, err, http.StatusInternalServerError)
		return
	}

	ctx.JSON(http.StatusOK, user)
}

func (c Users) CreateUser(ctx *gin.Context) {
	// Читаем тело запроса
	var user model.User
	err := ctx.BindJSON(&user)
	if err != nil {
		controllerError(ctx, err, http.StatusBadRequest)
		return
	}

	// Добавляем пользователя в БД
	err = c.usersRepo.NewUser(ctx, user)
	if err != nil {
		code := http.StatusInternalServerError
		// Пользователь уже существует - конфликт
		if errors.Is(err, postgres.ErrUserExists) {
			code = http.StatusConflict
		}
		controllerError(ctx, err, code)
		return
	}

	ctx.JSON(http.StatusOK, defaultResp{
		StatusCode: http.StatusOK,
		Message:    "user created",
	})
}

func (c Users) EditUser(ctx *gin.Context) {
	userIdStr := ctx.Param("id")
	userId, err := strconv.ParseInt(userIdStr, 10, 64)
	if err != nil {
		controllerError(ctx, err, http.StatusBadRequest)
		return
	}

	var patch model.UserEdit
	err = ctx.BindJSON(&patch)
	if err != nil {
		controllerError(ctx, err, http.StatusBadRequest)
		return
	}

	err = c.usersRepo.EditUser(ctx, userId, patch)
	if err != nil {
		controllerError(ctx, err, http.StatusInternalServerError)
		return
	}

	ctx.JSON(http.StatusOK, defaultResp{
		StatusCode: http.StatusOK,
		Message:    "user data updated",
	})
}
