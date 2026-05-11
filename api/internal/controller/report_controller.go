package controller

import (
	"context"
	"database/sql"
	"errors"
	"homie-api/internal/model"
	"log/slog"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
)

type reportsRepo interface {
	ByID(ctx context.Context, id int64) (*model.Report, error)
	PendingReportIDs(ctx context.Context, offset, limit int) (report_ids []int64, err error)
	Count(ctx context.Context) (int, error)
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

func (c Reports) PendingReports(ctx *gin.Context) {
	// Получаем параметры пагинации из query-строки
	offset, err := strconv.Atoi(ctx.DefaultQuery("offset", "0"))
	if err != nil {
		c.logger.Error("invalid offset parameter", "error", err)
		controllerError(ctx, errors.New("invalid offset parameter"), http.StatusBadRequest)
		return
	}

	limit, err := strconv.Atoi(ctx.DefaultQuery("limit", "20"))
	if err != nil {
		c.logger.Error("invalid limit parameter", "error", err)
		controllerError(ctx, errors.New("invalid limit parameter"), http.StatusBadRequest)
		return
	}

	if limit > 100 {
		limit = 100
	}

	c.logger.Info("getting reports batch", "offset", offset, "limit", limit)

	reportIds, err := c.reportsRepo.PendingReportIDs(ctx, offset, limit)
	if err != nil {
		c.logger.Error("failed to get reports batch", "error", err)
		controllerError(ctx, errors.New("failed to get reports"), http.StatusInternalServerError)
		return
	}

	c.logger.Info("reports batch retrieved successfully",
		"count", len(reportIds),
		"offset", offset,
		"limit", limit,
	)

	ctx.JSON(http.StatusOK, reportIds)
}

func (c Reports) ByID(ctx *gin.Context) {
	idStr := ctx.Param("id")
	id, err := strconv.ParseInt(idStr, 10, 64)
	if err != nil {
		c.logger.Error("invalid report id", "error", err, "id", idStr)
		controllerError(ctx, errors.New("invalid report id"), http.StatusBadRequest)
		return
	}

	c.logger.Info("getting report by id", "report_id", id)

	report, err := c.reportsRepo.ByID(ctx, id)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			c.logger.Warn("report not found", "report_id", id)
			controllerError(ctx, errors.New("report not found"), http.StatusNotFound)
			return
		}
		c.logger.Error("failed to get report by id", "report_id", id, "error", err)
		controllerError(ctx, errors.New("failed to get report"), http.StatusInternalServerError)
		return
	}

	c.logger.Info("report retrieved successfully", "report_id", id)
	ctx.JSON(http.StatusOK, report)
}

func (c Reports) Count(ctx *gin.Context) {
	count, err := c.reportsRepo.Count(ctx)
	if err != nil {
		c.logger.Error("failed to count reports", "error", err)
		controllerError(ctx, err, http.StatusInternalServerError)
		return
	}

	c.logger.Info("reports count retrieved successfully", "count", count)
	ctx.JSON(http.StatusOK, gin.H{
		"count": count,
	})
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
