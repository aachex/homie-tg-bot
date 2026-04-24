package controller

import (
	"context"
	"fmt"
	"homie-api/internal/model"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
)

type houseOffersRepo interface {
	RandOffer(ctx context.Context) (model.HouseOffer, error)
	CreateOffer(ctx context.Context, data model.HouseOfferCreate) (int64, error)
	DeleteOffer(ctx context.Context, id int64) error
	SetActive(ctx context.Context, id int64, active bool) error
}

type HouseOffers struct {
	houseOffersRepo houseOffersRepo
}

func NewHouseOffers(houseOffersRepo houseOffersRepo) *HouseOffers {
	return &HouseOffers{
		houseOffersRepo: houseOffersRepo,
	}
}

func (c HouseOffers) RandOffer(ctx *gin.Context) {
	offer, err := c.houseOffersRepo.RandOffer(ctx)
	if err != nil {
		controllerError(ctx, err, http.StatusInternalServerError)
		return
	}

	ctx.JSON(http.StatusOK, offer)
}

func (c HouseOffers) CreateOffer(ctx *gin.Context) {
	var data model.HouseOfferCreate
	err := ctx.BindJSON(&data)
	if err != nil {
		controllerError(ctx, err, http.StatusBadRequest)
		return
	}

	id, err := c.houseOffersRepo.CreateOffer(ctx, data)
	if err != nil {
		controllerError(ctx, err, http.StatusInternalServerError)
		return
	}

	resp := model.HouseOffer{
		Id:          id,
		IsActive:    true,
		Title:       data.Title,
		Description: data.Description,
		City:        data.City,
		Price:       data.Price,
		Type:        data.Type,
		OwnerId:     data.OwnerId,
		MediaFiles:  data.MediaFiles,
	}

	ctx.JSON(http.StatusOK, resp)
}

func (c HouseOffers) DeleteOffer(ctx *gin.Context) {
	id, err := strconv.ParseInt(ctx.Param("id"), 10, 64)
	if err != nil {
		controllerError(ctx, err, http.StatusBadRequest)
		return
	}

	err = c.houseOffersRepo.DeleteOffer(ctx, id)
	if err != nil {
		controllerError(ctx, err, http.StatusInternalServerError)
		return
	}

	ctx.JSON(http.StatusOK, defaultResp{
		StatusCode: http.StatusOK,
		Message:    fmt.Sprintf("offer %d succesfully deleted", id),
	})
}

func (c HouseOffers) SetActiveOffer(ctx *gin.Context) {
	id, err := strconv.ParseInt(ctx.Param("id"), 10, 64)
	if err != nil {
		controllerError(ctx, err, http.StatusBadRequest)
		return
	}

	isActive, err := strconv.ParseBool(ctx.Query("active"))
	if err != nil {
		controllerError(ctx, err, http.StatusBadRequest)
		return
	}

	err = c.houseOffersRepo.SetActive(ctx, id, isActive)
	if err != nil {
		controllerError(ctx, err, http.StatusInternalServerError)
		return
	}

	ctx.JSON(http.StatusOK, defaultResp{
		StatusCode: http.StatusOK,
		Message:    fmt.Sprintf("offer active = %t", isActive),
	})
}
