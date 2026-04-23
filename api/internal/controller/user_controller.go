package controller

import (
	"context"
	"errors"
	"homie-api/internal/model"
	"homie-api/internal/repository/postgres"
	"net/http"

	"github.com/gin-gonic/gin"
)

type usersRepo interface {
	RandUser(ctx context.Context) (model.User, error)
	NewUser(ctx context.Context, userData model.User) error
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
		c.error(ctx, err, http.StatusInternalServerError)
		return
	}

	ctx.JSON(http.StatusOK, user)
}

func (c Users) CreateUser(ctx *gin.Context) {
	// Читаем тело запроса
	var user model.User
	err := ctx.BindJSON(&user)
	if err != nil {
		c.error(ctx, err, http.StatusBadRequest)
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
		c.error(ctx, err, code)
		return
	}
}

type errorResp struct {
	StatusCode   int    `json:"statusCode"`
	ErrorMessage string `json:"message"`
}

func (c Users) error(ctx *gin.Context, err error, code int) {
	ctx.AbortWithStatusJSON(code, errorResp{
		StatusCode:   code,
		ErrorMessage: err.Error(),
	})
}
