package controller

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"homie-api/internal/model"
	"homie-api/internal/repository/postgres"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
)

type houseOffersRepo interface {
	OfferById(ctx context.Context, id int64) (model.HouseOffer, error)
	OfferLikes(ctx context.Context, offerId int64) (likes []model.HouseOfferLike, err error)
	AddLike(ctx context.Context, offerId int64, userId int64) error
	RandOffer(ctx context.Context, userId int64, city string) (model.HouseOffer, error)
	UserOffers(ctx context.Context, userId int64) ([]model.HouseOfferPreview, error)
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

func (c HouseOffers) OfferById(ctx *gin.Context) {
	id, err := strconv.ParseInt(ctx.Param("id"), 10, 64)
	if err != nil {
		controllerError(ctx, err, http.StatusBadRequest)
		return
	}

	offer, err := c.houseOffersRepo.OfferById(ctx, id)
	if errors.Is(err, sql.ErrNoRows) {
		controllerError(ctx, err, http.StatusNotFound)
		return
	}
	if err != nil {
		controllerError(ctx, err, http.StatusInternalServerError)
		return
	}

	ctx.JSON(http.StatusOK, offer)
}

func (c HouseOffers) OfferLikes(ctx *gin.Context) {
	id, err := strconv.ParseInt(ctx.Param("id"), 10, 64)
	if err != nil {
		controllerError(ctx, err, http.StatusBadRequest)
		return
	}

	likes, err := c.houseOffersRepo.OfferLikes(ctx, id)
	if err != nil && !errors.Is(err, sql.ErrNoRows) {
		controllerError(ctx, err, http.StatusInternalServerError)
		return
	}

	ctx.JSON(http.StatusOK, likes)
}

func (c HouseOffers) AddLike(ctx *gin.Context) {
	offerId, err := strconv.ParseInt(ctx.Param("id"), 10, 64)
	if err != nil {
		controllerError(ctx, errors.New("invalid offer id"), http.StatusBadRequest)
		return
	}

	userId, err := strconv.ParseInt(ctx.Query("userId"), 10, 64)
	if err != nil {
		controllerError(ctx, errors.New("invalid userId format"), http.StatusBadRequest)
		return
	}

	err = c.houseOffersRepo.AddLike(ctx, offerId, userId)
	if err != nil {
		code := http.StatusInternalServerError
		// Лайк уже стоит - конфликт
		if errors.Is(err, postgres.ErrLikeAlreadyExists) {
			code = http.StatusConflict
		}
		controllerError(ctx, errors.New("failed to like offer"), code)
		return
	}

	ctx.JSON(http.StatusCreated, defaultResp{
		StatusCode: http.StatusCreated,
		Message:    fmt.Sprintf("added like to offer %d", offerId),
	})
}

func (c HouseOffers) RandOffer(ctx *gin.Context) {
	userId, err := strconv.ParseInt(ctx.Query("userId"), 10, 64)
	if err != nil {
		controllerError(ctx, err, http.StatusBadRequest)
		return
	}
	city := ctx.Query("city")

	offer, err := c.houseOffersRepo.RandOffer(ctx, userId, city)
	if errors.Is(err, sql.ErrNoRows) {
		controllerError(ctx, err, http.StatusNotFound)
		return
	}
	if err != nil {
		controllerError(ctx, err, http.StatusInternalServerError)
		return
	}

	ctx.JSON(http.StatusOK, offer)
}

func (c HouseOffers) UserOffers(ctx *gin.Context) {
	userId, err := strconv.ParseInt(ctx.Param("id"), 10, 64)
	if err != nil {
		controllerError(ctx, err, http.StatusBadRequest)
		return
	}

	offers, err := c.houseOffersRepo.UserOffers(ctx, userId)
	if err != nil && !errors.Is(err, sql.ErrNoRows) {
		controllerError(ctx, err, http.StatusInternalServerError)
		return
	}

	ctx.JSON(http.StatusOK, offers)
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
		District:    data.District,
		Price:       data.Price,
		OwnerId:     data.OwnerId,
		MediaFiles:  data.MediaFiles,
	}

	ctx.JSON(http.StatusCreated, resp)
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
