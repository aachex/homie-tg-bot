package model

// User представляет все данные пользователя.
type User struct {
	Id          int64    `json:"id"`
	Name        string   `json:"name"`
	Age         uint8    `json:"age"`
	Description string   `json:"description"`
	City        string   `json:"city"`
	MediaFiles  []string `json:"media_files"`
	Details     Ruleset  `json:"details"`
}

// UserEdit представляет все данные пользователя, которые можно менять.
type UserEdit struct {
	Name        *string  `json:"name"`
	Age         *uint8   `json:"age"`
	Description *string  `json:"description"`
	City        *string  `json:"city"`
	MediaFiles  []string `json:"media_files"`
	Details     *Ruleset `json:"details"`
}
