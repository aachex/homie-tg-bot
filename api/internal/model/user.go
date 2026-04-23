package model

type User struct {
	Id          int64  `json:"id"`
	Name        string `json:"name"`
	Age         uint8  `json:"age"`
	Description string `json:"description"`
	City        string `json:"city"`
}
