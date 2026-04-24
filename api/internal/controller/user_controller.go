package controller

import (
	"context"
	"errors"
	"homie-api/internal/model"
	"homie-api/internal/repository/postgres"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
)

type usersRepo interface {
	RandUser(ctx context.Context) (model.User, error)
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

func (c Users) GetRandUser(ctx *gin.Context) {
	user, err := c.usersRepo.RandUser(ctx)
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
