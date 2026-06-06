package controller

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"homie-api/internal/llm"
	"homie-api/internal/model"
	"homie-api/internal/repository/postgres/offers"
	"log/slog"
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
)

type houseOffersRepo interface {
	OfferById(ctx context.Context, id int64) (model.HouseOffer, error)
	OfferLikes(ctx context.Context, offerId int64) (likes []model.HouseOfferLike, err error)
	AddLike(ctx context.Context, like model.AddLikeRequest) error
	DeleteLike(ctx context.Context, offerId int64, userId int64) error
	RelevantOffer(ctx context.Context, userId int64, city string, user model.UserFlags) (model.RelevantOffer, error)
	GetOfferRelevance(ctx context.Context, offerId int64, userFlags model.UserFlags) (int, error)
	UserOffers(ctx context.Context, userId int64) ([]model.HouseOfferPreview, error)
	CreateOffer(ctx context.Context, data model.HouseOfferCreate) (int64, error)
	DeleteOffer(ctx context.Context, id int64) error
	SetActive(ctx context.Context, id int64, active bool) error
	UpdateOfferPreferences(ctx context.Context, offerId int64, prefs model.OfferFlags) error
}

type HouseOffers struct {
	logger          *slog.Logger
	llmClient       *llm.Client
	houseOffersRepo houseOffersRepo
}

func NewHouseOffers(logger *slog.Logger, llmClient *llm.Client, houseOffersRepo houseOffersRepo) *HouseOffers {
	return &HouseOffers{
		logger:          logger,
		llmClient:       llmClient,
		houseOffersRepo: houseOffersRepo,
	}
}

func (c HouseOffers) OfferById(ctx *gin.Context) {
	id, err := strconv.ParseInt(ctx.Param("id"), 10, 64)
	if err != nil {
		c.logger.Error("failed to parse offer id", "error", err, "param", ctx.Param("id"))
		controllerError(ctx, errors.New("invalid offer id"), http.StatusBadRequest)
		return
	}

	offer, err := c.houseOffersRepo.OfferById(ctx, id)
	if errors.Is(err, sql.ErrNoRows) {
		c.logger.Warn("offer not found", "offer_id", id)
		controllerError(ctx, errors.New("offer not found"), http.StatusNotFound)
		return
	}
	if err != nil {
		c.logger.Error("failed to get offer by id", "offer_id", id, "error", err)
		controllerError(ctx, errors.New("failed to get offer"), http.StatusInternalServerError)
		return
	}

	c.logger.Info("offer retrieved successfully", "offer_id", id)
	ctx.JSON(http.StatusOK, offer)
}

func (c HouseOffers) OfferLikes(ctx *gin.Context) {
	id, err := strconv.ParseInt(ctx.Param("id"), 10, 64)
	if err != nil {
		c.logger.Error("failed to parse offer id for likes", "error", err, "param", ctx.Param("id"))
		controllerError(ctx, errors.New("invalid offer id"), http.StatusBadRequest)
		return
	}

	likes, err := c.houseOffersRepo.OfferLikes(ctx, id)
	if err != nil && !errors.Is(err, sql.ErrNoRows) {
		c.logger.Error("failed to get likes for offer", "offer_id", id, "error", err)
		controllerError(ctx, errors.New("failed to get likes"), http.StatusInternalServerError)
		return
	}

	c.logger.Info("likes retrieved for offer", "offer_id", id, "count", len(likes))
	ctx.JSON(http.StatusOK, likes)
}

func (c HouseOffers) AddLike(ctx *gin.Context) {
	var like model.AddLikeRequest
	err := ctx.ShouldBindJSON(&like)
	if err != nil {
		c.logger.Error("add like: invalid JSON", "error", err)
		controllerError(ctx, errors.New("invalid request body"), http.StatusBadRequest)
		return
	}

	err = c.houseOffersRepo.AddLike(ctx, like)
	if err != nil {
		code := http.StatusInternalServerError
		if errors.Is(err, offers.ErrLikeAlreadyExists) {
			code = http.StatusConflict
			c.logger.Warn("like already exists", "offer_id", like.OfferId, "user_id", like.UserId)
			controllerError(ctx, errors.New("like already exists"), code)
		} else {
			c.logger.Error("failed to add like", "offer_id", like.OfferId, "user_id", like.UserId, "error", err)
			controllerError(ctx, errors.New("failed to like offer"), code)
		}
		return
	}

	c.logger.Info("like added successfully", "offer_id", like.OfferId, "user_id", like.UserId)
	ctx.JSON(http.StatusCreated, defaultResp{
		StatusCode: http.StatusCreated,
		Message:    fmt.Sprintf("added like to offer %d", like.OfferId),
	})
}

func (c HouseOffers) DeleteLike(ctx *gin.Context) {
	offerID, err := strconv.ParseInt(ctx.Param("id"), 10, 64)
	if err != nil {
		c.logger.Error("delete like: invalid offer id", "error", err, "param", ctx.Param("id"))
		controllerError(ctx, errors.New("invalid offer id"), http.StatusBadRequest)
		return
	}

	userID, err := strconv.ParseInt(ctx.Query("userId"), 10, 64)
	if err != nil {
		c.logger.Error("delete like: invalid userId format", "error", err, "userId", ctx.Query("userId"))
		controllerError(ctx, errors.New("invalid userId format"), http.StatusBadRequest)
		return
	}

	err = c.houseOffersRepo.DeleteLike(ctx, offerID, userID)
	if err != nil {
		code := http.StatusInternalServerError
		if errors.Is(err, offers.ErrLikeNotFound) {
			code = http.StatusNotFound
			c.logger.Warn("like not found for deletion", "offer_id", offerID, "user_id", userID)
			controllerError(ctx, errors.New("like not found"), code)
		} else {
			c.logger.Error("failed to delete like", "offer_id", offerID, "user_id", userID, "error", err)
			controllerError(ctx, errors.New("failed to delete like"), code)
		}
		return
	}

	c.logger.Info("like deleted successfully", "offer_id", offerID, "user_id", userID)
	ctx.JSON(http.StatusOK, defaultResp{
		StatusCode: http.StatusOK,
		Message:    "successfully deleted like",
	})
}

func (c HouseOffers) RelevantOffer(ctx *gin.Context) {
	var req model.RandRelevantOfferRequest
	err := ctx.ShouldBindJSON(&req)
	if err != nil {
		c.logger.Error("rand offer: invalid JSON", "error", err)
		controllerError(ctx, errors.New("invalid request body"), http.StatusBadRequest)
		return
	}

	c.logger.Info("random offer request",
		"user_id", req.UserID,
		"city", req.City,
		"smoking", req.UserFlags.Smoking,
		"children", req.UserFlags.Children,
		"pets", req.UserFlags.Pets,
		"occupants_count", req.UserFlags.OccupantsCount,
		"noise_lvl", req.UserFlags.NoiseLvl,
		"works_from_home", req.UserFlags.WorksFromHome,
		"alcohol", req.UserFlags.Alcohol,
		"age_min", req.UserFlags.AgeMin,
		"age_max", req.UserFlags.AgeMax,
		"sex", req.UserFlags.Sex,
	)

	offer, err := c.houseOffersRepo.RelevantOffer(ctx, req.UserID, req.City, req.UserFlags)
	if errors.Is(err, sql.ErrNoRows) {
		c.logger.Warn("no random offer found", "user_id", req.UserID, "city", req.City)
		controllerError(ctx, errors.New("no offers found"), http.StatusNotFound)
		return
	}
	if err != nil {
		c.logger.Error("failed to get random offer", "user_id", req.UserID, "city", req.City, "error", err)
		controllerError(ctx, errors.New("failed to get random offer"), http.StatusInternalServerError)
		return
	}

	c.logger.Info(
		"offer retrieved",
		"user_id", req.UserID,
		"offer_id", offer.Id,
		"relevance", offer.RelevancePercent,
	)
	ctx.JSON(http.StatusOK, offer)
}

func (c HouseOffers) GetOfferRelevance(ctx *gin.Context) {
	var req struct {
		OfferID   int64           `json:"offer_id" binding:"required"`
		UserFlags model.UserFlags `json:"user_flags"`
	}

	err := ctx.ShouldBindJSON(&req)
	if err != nil {
		c.logger.Error("get offer relevance: invalid JSON", "error", err)
		controllerError(ctx, errors.New("invalid request body"), http.StatusBadRequest)
		return
	}

	c.logger.Info("get offer relevance request",
		"offer_id", req.OfferID,
		"smoking", req.UserFlags.Smoking,
		"children", req.UserFlags.Children,
		"pets", req.UserFlags.Pets,
		"occupants_count", req.UserFlags.OccupantsCount,
		"noise_lvl", req.UserFlags.NoiseLvl,
		"works_from_home", req.UserFlags.WorksFromHome,
		"alcohol", req.UserFlags.Alcohol,
		"age_min", req.UserFlags.AgeMin,
		"age_max", req.UserFlags.AgeMax,
		"sex", req.UserFlags.Sex,
	)

	relevancePercent, err := c.houseOffersRepo.GetOfferRelevance(ctx, req.OfferID, req.UserFlags)
	if errors.Is(err, sql.ErrNoRows) {
		c.logger.Warn("offer not found for relevance calculation", "offer_id", req.OfferID)
		controllerError(ctx, errors.New("offer not found"), http.StatusNotFound)
		return
	}
	if err != nil {
		c.logger.Error("failed to calculate offer relevance", "offer_id", req.OfferID, "error", err)
		controllerError(ctx, errors.New("failed to calculate relevance"), http.StatusInternalServerError)
		return
	}

	c.logger.Info("offer relevance calculated",
		"offer_id", req.OfferID,
		"relevance_percent", relevancePercent,
	)

	ctx.JSON(http.StatusOK, gin.H{
		"offer_id":          req.OfferID,
		"relevance_percent": relevancePercent,
	})
}

func (c HouseOffers) UserOffers(ctx *gin.Context) {
	userId, err := strconv.ParseInt(ctx.Param("id"), 10, 64)
	if err != nil {
		c.logger.Error("user offers: invalid user id", "error", err, "param", ctx.Param("id"))
		controllerError(ctx, errors.New("invalid user id"), http.StatusBadRequest)
		return
	}

	offers, err := c.houseOffersRepo.UserOffers(ctx, userId)
	if err != nil && !errors.Is(err, sql.ErrNoRows) {
		c.logger.Error("failed to get user offers", "user_id", userId, "error", err)
		controllerError(ctx, errors.New("failed to get user offers"), http.StatusInternalServerError)
		return
	}

	c.logger.Info("user offers retrieved", "user_id", userId, "count", len(offers))
	ctx.JSON(http.StatusOK, offers)
}

func (c HouseOffers) CreateOffer(ctx *gin.Context) {
	var data model.HouseOfferCreate
	err := ctx.BindJSON(&data)
	if err != nil {
		c.logger.Error("create offer: invalid JSON", "error", err)
		controllerError(ctx, errors.New("invalid request body"), http.StatusBadRequest)
		return
	}

	id, err := c.houseOffersRepo.CreateOffer(ctx, data)
	if err != nil {
		c.logger.Error("failed to create offer", "owner_id", data.OwnerId, "error", err)
		controllerError(ctx, errors.New("failed to create offer"), http.StatusInternalServerError)
		return
	}

	c.logger.Info("offer created successfully", "offer_id", id, "owner_id", data.OwnerId)
	ctx.JSON(http.StatusCreated, defaultResp{
		StatusCode: http.StatusCreated,
		Message:    "offer created successfully",
	})

	go c.updatePreferences(context.Background(), id, data.Description)
}

func (c HouseOffers) DeleteOffer(ctx *gin.Context) {
	id, err := strconv.ParseInt(ctx.Param("id"), 10, 64)
	if err != nil {
		c.logger.Error("delete offer: invalid offer id", "error", err, "param", ctx.Param("id"))
		controllerError(ctx, errors.New("invalid offer id"), http.StatusBadRequest)
		return
	}

	err = c.houseOffersRepo.DeleteOffer(ctx, id)
	if err != nil {
		c.logger.Error("failed to delete offer", "offer_id", id, "error", err)
		controllerError(ctx, errors.New("failed to delete offer"), http.StatusInternalServerError)
		return
	}

	c.logger.Info("offer deleted successfully", "offer_id", id)
	ctx.JSON(http.StatusOK, defaultResp{
		StatusCode: http.StatusOK,
		Message:    fmt.Sprintf("offer %d successfully deleted", id),
	})
}

func (c HouseOffers) SetActiveOffer(ctx *gin.Context) {
	id, err := strconv.ParseInt(ctx.Param("id"), 10, 64)
	if err != nil {
		c.logger.Error("set active offer: invalid offer id", "error", err, "param", ctx.Param("id"))
		controllerError(ctx, errors.New("invalid offer id"), http.StatusBadRequest)
		return
	}

	isActive, err := strconv.ParseBool(ctx.Query("active"))
	if err != nil {
		c.logger.Error("set active offer: invalid active flag", "error", err, "active", ctx.Query("active"))
		controllerError(ctx, errors.New("invalid active flag"), http.StatusBadRequest)
		return
	}

	err = c.houseOffersRepo.SetActive(ctx, id, isActive)
	if err != nil {
		c.logger.Error("failed to set offer active status", "offer_id", id, "active", isActive, "error", err)
		controllerError(ctx, errors.New("failed to update offer status"), http.StatusInternalServerError)
		return
	}

	c.logger.Info("offer active status updated", "offer_id", id, "active", isActive)
	ctx.JSON(http.StatusOK, defaultResp{
		StatusCode: http.StatusOK,
		Message:    fmt.Sprintf("offer active = %t", isActive),
	})
}

func (c HouseOffers) updatePreferences(ctx context.Context, offerId int64, text string) {
	const maxExtractFlagsTime = 30 * time.Second // Даём 30 секунд на извлечение флагов

	extractPrefsCtx, cancel := context.WithTimeout(ctx, maxExtractFlagsTime)
	defer cancel()

	prefs, err := c.llmClient.ExtractOfferFlags(extractPrefsCtx, text)
	if err != nil {
		c.logger.Error("failed to extract preferences",
			"offer_id", offerId,
			"error", err,
		)
	}

	err = c.houseOffersRepo.UpdateOfferPreferences(ctx, offerId, prefs)
	if err != nil {
		c.logger.Error("failed to update preferences",
			"offer_id", offerId,
			"error", err,
		)
		return
	}

	c.logger.Info("preferences updated successfully",
		"offer_id", offerId,
		"smoking", prefs.Smoking,
		"children", prefs.Children,
		"pets", prefs.Pets,
	)
}
