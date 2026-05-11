package model

import "time"

type Report struct {
	Id         int64     `json:"id"`
	OfferId    int64     `json:"offer_id"`
	ReporterId int64     `json:"reporter_id"`
	Reason     string    `json:"reason"`
	Status     string    `json:"status"`
	CreatedAt  time.Time `json:"created_at"`
}

type ReportCreate struct {
	OfferId    int64  `json:"offer_id" binding:"required"`
	ReporterId int64  `json:"reporter_id" binding:"required"`
	Reason     string `json:"reason" binding:"required"`
}
