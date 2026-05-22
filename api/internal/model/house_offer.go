package model

// OwnerPreferences представляет предпочтения арендодателя (кого он хочет)
type OwnerPreferences struct {
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

type HouseOffer struct {
	Id             int64    `json:"id"`
	IsActive       bool     `json:"is_active"`
	OwnerId        int64    `json:"owner_id"`
	Title          string   `json:"title"`
	Description    string   `json:"description"`
	City           string   `json:"city"`
	District       string   `json:"district"`
	Price          int      `json:"price"`
	MediaFiles     []string `json:"media_files"`
	FlagProcessing bool     `json:"flag_processing"`

	// Предпочтения арендодателя
	Preferences OwnerPreferences `json:"preferences"`
}

// HouseOfferCreate представляет данные, необходимые для создания объявления.
type HouseOfferCreate struct {
	OwnerId           int64    `json:"owner_id"`
	Title             string   `json:"title"`
	Description       string   `json:"description"`
	City              string   `json:"city"`
	District          string   `json:"district"`
	Price             int      `json:"price"`
	MediaFiles        []string `json:"media_files"`
	TenantDescription string   `json:"tenant_description"`
}

// HouseOfferPreview представляет поверхностные данные, которые видит владелец своих объявлений.
type HouseOfferPreview struct {
	Id         int64  `json:"id"`
	IsActive   bool   `json:"is_active"`
	Title      string `json:"title"`
	LikesCount int    `json:"likes_count"`
}

// HouseOfferLike представляет данные о лайке объявления.
type HouseOfferLike struct {
	Id      int64 `json:"id"`
	OfferId int64 `json:"offer_id"`
	UserId  int64 `json:"user_id"`
}

type RandRelevantOfferRequest struct {
	UserID              int64     `json:"user_id" binding:"required"`
	MinRelevancePercent int       `json:"min_rel" binding:"required"`
	City                string    `json:"city" binding:"required"`
	UserFlags           UserFlags `json:"user_flags"`
}

type RelevantOffer struct {
	RelevanceSum     int `json:"relevance_sum"`
	RelevancePercent int `json:"relevance_percent"`
	HouseOffer       `json:"offer"`
}
