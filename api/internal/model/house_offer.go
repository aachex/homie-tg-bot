package model

import "github.com/shopspring/decimal"

type HouseOffer struct {
	Id          int64           `json:"id"`
	Title       string          `json:"title"`
	Description string          `json:"description"`
	Price       decimal.Decimal `json:"price"`
	Type        string          `json:"type"`
	OwnerId     int64           `json:"owner_id"`
}
