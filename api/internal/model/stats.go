package model

import "time"

type UserActivity struct {
	Id         int64          `json:"id"`
	UserId     int64          `json:"user_id"`
	Action     string         `json:"action"`
	Timestamp  time.Time      `json:"timestamp"`
	ActionData map[string]any `json:"action_data"`
}

type DailyStat struct {
	DAU  int       `json:"dau"`
	Date time.Time `json:"date"`
}
