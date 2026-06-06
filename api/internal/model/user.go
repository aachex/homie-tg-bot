package model

// UserFlags представляет флаги арендатора.
type UserFlags struct {
	Smoking        *bool         `json:"smoking,omitempty"`
	Children       *ChildrenEnum `json:"children,omitempty"`
	Pets           *PetsEnum     `json:"pets,omitempty"`
	OccupantsCount *int          `json:"occupants_count,omitempty"`
	NoiseLvl       *NoiseLvlEnum `json:"noise_lvl,omitempty"`
	WorksFromHome  *bool         `json:"works_from_home,omitempty"`
	Alcohol        *AlcoholEnum  `json:"alcohol,omitempty"`
	AgeMin         *int          `json:"age_min,omitempty"`
	AgeMax         *int          `json:"age_max,omitempty"`
	Sex            *SexEnum      `json:"sex,omitempty"`
}

// User представляет все данные пользователя
type User struct {
	Id             int64     `json:"id"`
	Name           string    `json:"name"`
	City           string    `json:"city"`
	Description    string    `json:"description"`
	MediaFiles     []string  `json:"media_files"`
	FlagProcessing bool      `json:"flag_processing"`
	Flags          UserFlags `json:"flags"`
}

type UserCreate struct {
	Id          int64    `json:"id"`
	Name        string   `json:"name"`
	City        string   `json:"city"`
	Description string   `json:"description"`
	MediaFiles  []string `json:"media_files"`
}

// UserEdit представляет данные пользователя, которые можно менять
type UserEdit struct {
	Name        string   `json:"name"`
	City        string   `json:"city"`
	Description string   `json:"description"`
	MediaFiles  []string `json:"media_files"`
}

// UserLimits показывает какие лимиты есть у пользователя.
type UserLimits struct {
	IsPremium      bool `json:"is_premium"`
	MaxOffersCount int  `json:"max_offers_count"`
	MaxLikesPerDay int  `json:"max_likes_per_day"`
}

// RenewPremiumRequest представляет запрос на активацию премиума.
type RenewPremiumRequest struct {
	UserId    int64 `json:"user_id"`
	DaysCount int   `json:"days"`
}
