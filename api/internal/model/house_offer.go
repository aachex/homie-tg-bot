package model

// OfferFlags представляет предпочтения арендодателя (кого он хочет)
type OfferFlags struct {
	Price      *int    `json:"price"`
	RoomsCount *int    `json:"rooms_count"`
	District   *string `json:"district"`

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
	Description    string   `json:"description"`
	City           string   `json:"city"`
	MediaFiles     []string `json:"media_files"`
	FlagProcessing bool     `json:"flag_processing"`

	// Флаги объявления
	OfferFlags `json:"flags"`
}

// HouseOfferCreate представляет данные, необходимые для создания объявления.
type HouseOfferCreate struct {
	OwnerId     int64    `json:"owner_id" binding:"required"`
	Description string   `json:"description" binding:"required"`
	City        string   `json:"city" binding:"required"`
	MediaFiles  []string `json:"media_files" binding:"required"`
}

// HouseOfferPreview представляет поверхностные данные, которые видит владелец своих объявлений.
type HouseOfferPreview struct {
	Id         int64  `json:"id"`
	IsActive   bool   `json:"is_active"`
	Title      string `json:"title"`
	LikesCount int    `json:"likes_count"`
}

type AddLikeRequest struct {
	OfferId   int64 `json:"offer_id"`
	UserId    int64 `json:"user_id"`
	Relevance int   `json:"relevance"`
}

// HouseOfferLike представляет данные о лайке объявления.
type HouseOfferLike struct {
	Id        int64 `json:"id"`
	OfferId   int64 `json:"offer_id"`
	UserId    int64 `json:"user_id"`
	Relevance int   `json:"relevance"`
}

type RandRelevantOfferRequest struct {
	UserID    int64     `json:"user_id" binding:"required"`
	City      string    `json:"city" binding:"required"`
	UserFlags UserFlags `json:"user_flags"`
}

type RelevantOffer struct {
	RelevanceSum     int `json:"relevance_sum"`
	RelevancePercent int `json:"relevance_percent"`
	HouseOffer       `json:"offer"`
}
