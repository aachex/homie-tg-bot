package controller

import (
	"context"
	"homie-api/internal/model"
	"log/slog"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

type statsRepo interface {
	CreateUserActivity(ctx context.Context, userId int64, action string, action_data map[string]any) (int64, error)
	DAU(ctx context.Context, fromDate time.Time, toDate time.Time) ([]model.DailyStat, error)
}

// Stats является контроллером статистики.
type Stats struct {
	logger    *slog.Logger
	statsRepo statsRepo
}

func NewStats(logger *slog.Logger, statsRepo statsRepo) *Stats {
	return &Stats{
		logger:    logger,
		statsRepo: statsRepo,
	}
}

func (c Stats) DAU(ctx *gin.Context) {
	type req struct {
		From time.Time `json:"from"`
		To   time.Time `json:"to"`
	}
	var data req
	err := ctx.BindJSON(&data)
	if err != nil {
		c.logger.Error("failed to bind JSON for DAU request", "error", err)
		controllerError(ctx, err, http.StatusBadRequest)
		return
	}

	c.logger.Info("getting DAU statistics",
		"from", data.From,
		"to", data.To,
	)

	dau, err := c.statsRepo.DAU(ctx, data.From, data.To)
	if err != nil {
		c.logger.Error("failed to get DAU from repository",
			"from", data.From,
			"to", data.To,
			"error", err,
		)
		controllerError(ctx, err, http.StatusInternalServerError)
		return
	}

	c.logger.Info("DAU statistics retrieved successfully",
		"from", data.From,
		"to", data.To,
		"days_count", len(dau),
	)

	ctx.JSON(http.StatusOK, dau)
}

func (c Stats) CreateUserActivity(ctx *gin.Context) {
	type req struct {
		UserId     int64          `json:"user_id"`
		Action     string         `json:"action"`
		ActionData map[string]any `json:"action_data"`
	}
	var activityData req
	err := ctx.BindJSON(&activityData)
	if err != nil {
		c.logger.Error("failed to bind JSON for user activity", "error", err)
		controllerError(ctx, err, http.StatusBadRequest)
		return
	}

	_, err = c.statsRepo.CreateUserActivity(ctx, activityData.UserId, activityData.Action, activityData.ActionData)
	if err != nil {
		c.logger.Error("failed to create user activity",
			"user_id", activityData.UserId,
			"action", activityData.Action,
			"error", err,
		)
		controllerError(ctx, err, http.StatusInternalServerError)
		return
	}

	ctx.JSON(http.StatusCreated, defaultResp{
		StatusCode: http.StatusCreated,
		Message:    "activity created successfully",
	})
}
