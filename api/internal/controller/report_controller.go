package controller

import (
	"context"
	"database/sql"
	"errors"
	"homie-api/internal/model"
	"log/slog"
	"net/http"

	"github.com/gin-gonic/gin"
)

type reportsRepo interface {
	Create(ctx context.Context, data model.ReportCreate) (id int64, err error)
}

type Reports struct {
	logger      *slog.Logger
	reportsRepo reportsRepo
}

func NewReports(logger *slog.Logger, reportsRepo reportsRepo) *Reports {
	return &Reports{
		logger:      logger,
		reportsRepo: reportsRepo,
	}
}

func (c Reports) CreateReport(ctx *gin.Context) {
	var req model.ReportCreate
	err := ctx.BindJSON(&req)
	if err != nil {
		c.logger.Error("failed to bind JSON for report", "error", err)
		controllerError(ctx, errors.New("invalid request body"), http.StatusBadRequest)
		return
	}

	c.logger.Info("creating report",
		"offer_id", req.OfferId,
		"reporter_id", req.ReporterId,
		"reason", req.Reason,
	)

	id, err := c.reportsRepo.Create(ctx, req)
	if err != nil {
		c.logger.Error("failed to create report", "error", err)

		code := http.StatusInternalServerError
		if errors.Is(err, sql.ErrNoRows) {
			code = http.StatusConflict
		}

		controllerError(ctx, errors.New("failed to create report"), code)
		return
	}

	c.logger.Info("report created successfully", "report_id", id)
	ctx.JSON(http.StatusCreated, defaultResp{
		StatusCode: http.StatusCreated,
		Message:    "report created successfully",
	})
}
