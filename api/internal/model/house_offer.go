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
	Price       decimal.Decimal `json:"price"`
	Type        string          `json:"type"`
	MediaFiles  []string        `json:"media_files"`
}

// HouseOfferCreate представляет данные, необходимые для создания объявления.
type HouseOfferCreate struct {
	OwnerId     int64           `json:"owner_id"`
	Title       string          `json:"title"`
	Description string          `json:"description"`
	City        string          `json:"city"`
	Price       decimal.Decimal `json:"price"`
	Type        string          `json:"type"`
	MediaFiles  []string        `json:"media_files"`
}
