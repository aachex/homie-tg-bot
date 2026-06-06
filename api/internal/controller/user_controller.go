package controller

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"homie-api/internal/llm"
	"homie-api/internal/model"
	"log/slog"
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
)

type usersRepo interface {
	GetById(ctx context.Context, id int64) (model.User, error)
	CreateUser(ctx context.Context, userData model.UserCreate) error
	UpdateFlags(ctx context.Context, userID int64, flags model.UserFlags) error
	EditUser(ctx context.Context, userId int64, patch model.UserEdit) error
}

type premiumRepo interface {
	UserLimits(ctx context.Context, userId int64) (model.UserLimits, error)
	RenewPremium(ctx context.Context, userId int64, daysCount int) error
}

type Users struct {
	logger      *slog.Logger
	llmClient   *llm.Client
	usersRepo   usersRepo
	premiumRepo premiumRepo
}

func NewUsers(logger *slog.Logger, llmClient *llm.Client, usersRepo usersRepo, premiumRepo premiumRepo) *Users {
	return &Users{
		logger:      logger,
		llmClient:   llmClient,
		usersRepo:   usersRepo,
		premiumRepo: premiumRepo,
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

	text := fmt.Sprintf("\nМеня зовут %s. %s", user.Name, user.Description)
	go c.updateFlags(context.Background(), user.Id, text)
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

	text := fmt.Sprintf("\nМеня зовут %s. %s", patch.Name, patch.Description)
	go c.updateFlags(context.Background(), userId, text)
}

func (c Users) Limits(ctx *gin.Context) {
	// Получаем user_id из path параметра
	userIDStr := ctx.Param("id")
	userID, err := strconv.ParseInt(userIDStr, 10, 64)
	if err != nil {
		c.logger.Error("limits: invalid user id", "error", err, "user_id", userIDStr)
		controllerError(ctx, errors.New("invalid user id"), http.StatusBadRequest)
		return
	}

	c.logger.Info("getting user limits", "user_id", userID)

	limits, err := c.premiumRepo.UserLimits(ctx, userID)
	if err != nil {
		c.logger.Error("failed to get user limits", "user_id", userID, "error", err)
		controllerError(ctx, errors.New("failed to get user limits"), http.StatusInternalServerError)
		return
	}

	c.logger.Info("user limits retrieved",
		"user_id", userID,
		"is_premium", limits.IsPremium,
		"max_offers", limits.MaxOffersCount,
		"max_likes", limits.MaxLikesPerDay,
	)

	ctx.JSON(http.StatusOK, limits)
}

func (c Users) RenewPremium(ctx *gin.Context) {
	var request model.RenewPremiumRequest
	err := ctx.BindJSON(&request)
	if err != nil {
		c.logger.Error("failed to parse request body")
		controllerError(ctx, errors.New("activate premium: invalid request body"), http.StatusBadRequest)
		return
	}

	err = c.premiumRepo.RenewPremium(ctx, request.UserId, request.DaysCount)
	if err != nil {
		c.logger.Error("failed to activate premium", "user_id", request.UserId)
		controllerError(ctx, errors.New("failed to activate premium"), http.StatusInternalServerError)
		return
	}

	ctx.JSON(http.StatusOK, defaultResp{
		StatusCode: http.StatusOK,
		Message:    fmt.Sprintf("premium subscription is renewed by %d days", request.DaysCount),
	})
}

// updateFlags извлекает флаги из описания юзера и обновляет их в БД.
func (c Users) updateFlags(ctx context.Context, userId int64, text string) {
	const maxExtractFlagsTime = 30 * time.Second // Даём 30 секунд на извлечение флагов

	extractFlagsCtx, cancel := context.WithTimeout(ctx, maxExtractFlagsTime)
	defer cancel()

	flags, err := c.llmClient.ExtractUserFlags(extractFlagsCtx, text)
	if err != nil {
		c.logger.Error("failed to extract user flags from description",
			"user_id", userId,
			"description_length", len(text),
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
