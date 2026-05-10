package controller

import (
	"context"
	"homie-api/internal/model"
	"net/http"

	"github.com/gin-gonic/gin"
)

type activitiesRepository interface {
	CreateUserActivity(ctx context.Context, activity model.UserActivityCreate) (int64, error)
}

// Stats является контроллером статистики.
type Stats struct {
	activitiesRepository activitiesRepository
}

func NewStats(activitiesRepository activitiesRepository) *Stats {
	return &Stats{
		activitiesRepository: activitiesRepository,
	}
}

func (c Stats) CreateUserActivity(ctx *gin.Context) {
	var activityData model.UserActivityCreate
	err := ctx.BindJSON(&activityData)
	if err != nil {
		controllerError(ctx, err, http.StatusBadRequest)
		return
	}

	_, err = c.activitiesRepository.CreateUserActivity(ctx, activityData)
	if err != nil {
		controllerError(ctx, err, http.StatusInternalServerError)
		return
	}

	ctx.JSON(http.StatusCreated, defaultResp{
		StatusCode: http.StatusCreated,
		Message:    "activity created successfully",
	})
}
