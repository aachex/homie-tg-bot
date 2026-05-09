package model

// HouseOffer представляет все данные объявления.
type HouseOffer struct {
	Id          int64    `json:"id"`
	IsActive    bool     `json:"is_active"`
	OwnerId     int64    `json:"owner_id"`
	Title       string   `json:"title"`
	Description string   `json:"description"`
	City        string   `json:"city"`
	District    string   `json:"district"`
	Price       int      `json:"price"`
	MediaFiles  []string `json:"media_files"`
	Ruleset     Ruleset  `json:"ruleset"`
}

// HouseOfferCreate представляет данные, необходимые для создания объявления.
type HouseOfferCreate struct {
	OwnerId     int64    `json:"owner_id"`
	Title       string   `json:"title"`
	Description string   `json:"description"`
	City        string   `json:"city"`
	District    string   `json:"district"`
	Price       int      `json:"price"`
	MediaFiles  []string `json:"media_files"`
	Ruleset     Ruleset  `json:"ruleset"`
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
