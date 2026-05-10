package model

import "time"

type UserActivity struct {
	Id        int64     `json:"id"`
	UserId    int64     `json:"user_id"`
	Action    string    `json:"action"`
	Timestamp time.Time `json:"timestamp"`
}

type UserActivityCreate struct {
	UserId    int64     `json:"user_id"`
	Action    string    `json:"action"`
	Timestamp time.Time `json:"timestamp"`
}
