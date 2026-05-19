package model

// ChildrenEnum тип для количества детей
type ChildrenEnum string

const (
	ChildrenNone     ChildrenEnum = "none"
	ChildrenOne      ChildrenEnum = "one"
	ChildrenTwoPlus  ChildrenEnum = "two+"
	ChildrenPlanning ChildrenEnum = "planning"
)

// PetsEnum тип для животных
type PetsEnum string

const (
	PetsNone  PetsEnum = "none"
	PetsCats  PetsEnum = "cats"
	PetsDogs  PetsEnum = "dogs"
	PetsOther PetsEnum = "other"
	PetsAny   PetsEnum = "any"
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

// SexEnum тип для пола
type SexEnum string

const (
	Male   SexEnum = "male"
	Female SexEnum = "female"
)
