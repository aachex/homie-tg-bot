package model

// ChildrenEnum тип для количества детей
type ChildrenEnum string

const (
	ChildrenZero     ChildrenEnum = "zero"
	ChildrenOne      ChildrenEnum = "one"
	ChildrenTwoPlus  ChildrenEnum = "two+"
	ChildrenPlanning ChildrenEnum = "planning"
)

// PetsEnum тип для животных
type PetsEnum string

const (
	PetsCats  PetsEnum = "cats"
	PetsDogs  PetsEnum = "dogs"
	PetsOther PetsEnum = "other"
)

// NoiseLvlEnum тип для уровня шума
type NoiseLvlEnum string

const (
	NoiseQuiet  NoiseLvlEnum = "quiet"
	NoiseNormal NoiseLvlEnum = "normal"
	NoiseLoud   NoiseLvlEnum = "loud"
)

// AlcoholEnum тип для употребления алкоголя
type AlcoholEnum string

const (
	AlcoholNever   AlcoholEnum = "never"
	AlcoholRare    AlcoholEnum = "rare"
	AlcoholRegular AlcoholEnum = "regular"
)

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
}

// User представляет все данные пользователя
type User struct {
	Id          int64     `json:"id"`
	Name        string    `json:"name"`
	City        string    `json:"city"`
	Description string    `json:"description"`
	MediaFiles  []string  `json:"media_files"`
	Flags       UserFlags `json:"flags"`
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
	Name        *string  `json:"name,omitempty"`
	City        *string  `json:"city,omitempty"`
	Description *string  `json:"description,omitempty"`
	MediaFiles  []string `json:"media_files,omitempty"`
}
