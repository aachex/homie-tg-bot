package controller

import (
	"context"
	"log/slog"
	"net/http"

	"github.com/gin-gonic/gin"
)

type activitiesRepository interface {
	CreateUserActivity(ctx context.Context, userId int64, action string, action_data map[string]any) (int64, error)
}

// Stats является контроллером статистики.
type Stats struct {
	logger               *slog.Logger
	activitiesRepository activitiesRepository
}

func NewStats(logger *slog.Logger, activitiesRepository activitiesRepository) *Stats {
	return &Stats{
		logger:               logger,
		activitiesRepository: activitiesRepository,
	}
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

	c.logger.Info("creating user activity",
		"user_id", activityData.UserId,
		"action", activityData.Action,
		"action_data", activityData.ActionData,
	)

	_, err = c.activitiesRepository.CreateUserActivity(ctx, activityData.UserId, activityData.Action, activityData.ActionData)
	if err != nil {
		c.logger.Error("failed to create user activity",
			"user_id", activityData.UserId,
			"action", activityData.Action,
			"error", err,
		)
		controllerError(ctx, err, http.StatusInternalServerError)
		return
	}

	c.logger.Info("user activity created successfully",
		"user_id", activityData.UserId,
		"action", activityData.Action,
	)

	ctx.JSON(http.StatusCreated, defaultResp{
		StatusCode: http.StatusCreated,
		Message:    "activity created successfully",
	})
}
