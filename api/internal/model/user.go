package model

// TODO: добавить поле для хранения фоток юзера

// User представляет все данные пользователя.
type User struct {
	Id          int64    `json:"id"`
	Name        string   `json:"name"`
	Age         uint8    `json:"age"`
	Description string   `json:"description"`
	City        string   `json:"city"`
	MediaFiles  []string `json:"mediaFiles"`
}

// UserEditData представляет все данные пользователя, которые можно менять.
type UserEditData struct {
	Name        string   `json:"name"`
	Age         uint8    `json:"age"`
	Description string   `json:"description"`
	City        string   `json:"city"`
	MediaFiles  []string `json:"mediaFiles"`
}
