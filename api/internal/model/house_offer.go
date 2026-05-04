package model

import "github.com/shopspring/decimal"

// HouseOffer представляет все данные объявления.
type HouseOffer struct {
	Id          int64           `json:"id"`
	IsActive    bool            `json:"is_active"`
	OwnerId     int64           `json:"owner_id"`
	Title       string          `json:"title"`
	Description string          `json:"description"`
	City        string          `json:"city"`
	District    string          `json:"district"`
	Price       decimal.Decimal `json:"price"`
	MediaFiles  []string        `json:"media_files"`
}

// HouseOfferCreate представляет данные, необходимые для создания объявления.
type HouseOfferCreate struct {
	OwnerId     int64           `json:"owner_id"`
	Title       string          `json:"title"`
	Description string          `json:"description"`
	City        string          `json:"city"`
	District    string          `json:"district"`
	Price       decimal.Decimal `json:"price"`
	MediaFiles  []string        `json:"media_files"`
}

// HouseOfferPreview представляет поверхностные данные, которые видит владелец своих объявлений.
type HouseOfferPreview struct {
	Id       int64  `json:"id"`
	IsActive bool   `json:"is_active"`
	Title    string `json:"title"`
}

// HouseOfferLike представляет данные о лайке объявления.
type HouseOfferLike struct {
	Id      int64 `json:"id"`
	OfferId int64 `json:"offer_id"`
	UserId  int64 `json:"user_id"`
}
