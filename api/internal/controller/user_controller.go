package controller

import (
	"context"
	"database/sql"
	"errors"
	"homie-api/internal/llm"
	"homie-api/internal/model"
	"log/slog"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
)

type usersRepo interface {
	GetById(ctx context.Context, id int64) (model.User, error)
	CreateUser(ctx context.Context, userData model.UserCreate) error
	UpdateFlags(ctx context.Context, userID int64, flags model.UserFlags) error
	EditUser(ctx context.Context, userId int64, patch model.UserEdit) error
}

type Users struct {
	logger    *slog.Logger
	llmClient *llm.Client
	usersRepo usersRepo
}

func NewUsers(logger *slog.Logger, llmClient *llm.Client, usersRepo usersRepo) *Users {
	return &Users{
		logger:    logger,
		llmClient: llmClient,
		usersRepo: usersRepo,
	}
}

func (c Users) UserById(ctx *gin.Context) {
	userId, err := strconv.ParseInt(ctx.Param("id"), 10, 64)
	if err != nil {
		c.logger.Error("user by id: invalid id", "error", err, "param", ctx.Param("id"))
		controllerError(ctx, errors.New("invalid user id"), http.StatusBadRequest)
		return
	}

	user, err := c.usersRepo.GetById(ctx, userId)
	if errors.Is(err, sql.ErrNoRows) {
		c.logger.Warn("user not found", "user_id", userId)
		controllerError(ctx, errors.New("user not found"), http.StatusNotFound)
		return
	}
	if err != nil {
		c.logger.Error("failed to get user by id", "user_id", userId, "error", err)
		controllerError(ctx, errors.New("failed to get user"), http.StatusInternalServerError)
		return
	}

	c.logger.Info("user retrieved successfully", "user_id", userId)
	ctx.JSON(http.StatusOK, user)
}

func (c Users) CreateUser(ctx *gin.Context) {
	var user model.UserCreate
	err := ctx.BindJSON(&user)
	if err != nil {
		c.logger.Error("create user: invalid JSON", "error", err)
		controllerError(ctx, errors.New("invalid request body"), http.StatusBadRequest)
		return
	}

	err = c.usersRepo.CreateUser(ctx, user)
	if err != nil {
		c.logger.Error("failed to create user", "user_id", user.Id, "error", err)
		controllerError(ctx, errors.New("failed to create user"), http.StatusInternalServerError)
		return
	}

	c.logger.Info("user created successfully", "user_id", user.Id)
	ctx.JSON(http.StatusCreated, defaultResp{
		StatusCode: http.StatusOK,
		Message:    "user created successfully",
	})

	go c.updateFlags(user.Id, user.Description)
}

func (c Users) EditUser(ctx *gin.Context) {
	userIdStr := ctx.Param("id")
	userId, err := strconv.ParseInt(userIdStr, 10, 64)
	if err != nil {
		c.logger.Error("edit user: invalid id", "error", err, "param", userIdStr)
		controllerError(ctx, errors.New("invalid user id"), http.StatusBadRequest)
		return
	}

	var patch model.UserEdit
	err = ctx.BindJSON(&patch)
	if err != nil {
		c.logger.Error("edit user: invalid JSON", "error", err, "user_id", userId)
		controllerError(ctx, errors.New("invalid request body"), http.StatusBadRequest)
		return
	}

	err = c.usersRepo.EditUser(ctx, userId, patch)
	if err != nil {
		c.logger.Error("failed to edit user", "user_id", userId, "error", err)
		controllerError(ctx, errors.New("failed to update user"), http.StatusInternalServerError)
		return
	}

	c.logger.Info("user edited successfully", "user_id", userId)
	ctx.JSON(http.StatusOK, defaultResp{
		StatusCode: http.StatusOK,
		Message:    "user data updated",
	})

	if patch.Description != nil {
		go c.updateFlags(userId, *patch.Description)
	}
}

// updateFlags извлекает флаги из описания юзера и обновляет их в БД.
func (c Users) updateFlags(userId int64, description string) {
	ctx := context.Background()

	flags, err := c.llmClient.ExtractUserFlags(ctx, description)
	if err != nil {
		c.logger.Error("failed to extract user flags from description",
			"user_id", userId,
			"description_length", len(description),
			"error", err,
		)
		// Не заканчиваем выполнение при ошибке т.к. нужно,
		// чтобы выполнился c.usersRepo.UpdateFlags, который поставит flag_processing = FALSE
	}

	err = c.usersRepo.UpdateFlags(ctx, userId, flags)
	if err != nil {
		c.logger.Error("failed to update flags",
			"user_id", userId,
			"error", err,
		)
		return
	}

	c.logger.Info("successfully extracted flags",
		"user_id", userId,
	)
}
