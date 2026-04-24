package model

import "github.com/shopspring/decimal"

// HouseOffer представляет все данные объявления о сдаче/продаже жилья.
type HouseOffer struct {
	Id          int64           `json:"id"`
	Title       string          `json:"title"`
	Description string          `json:"description"`
	Price       decimal.Decimal `json:"price"`
	Type        string          `json:"type"`
	OwnerId     int64           `json:"owner_id"`
	MediaFiles  []string        `json:"media_files"`
	IsActive    bool            `json:"is_active"`
}

// HouseOfferEditData представляет только изменяемые данные объявления о сдаче/продаже жилья.
type HouseOfferEditData struct {
	Title       string          `json:"title"`
	Description string          `json:"description"`
	Price       decimal.Decimal `json:"price"`
	Type        string          `json:"type"`
	OwnerId     int64           `json:"owner_id"`
	MediaFiles  []string        `json:"media_files"`
	IsActive    bool            `json:"is_active"`
}
