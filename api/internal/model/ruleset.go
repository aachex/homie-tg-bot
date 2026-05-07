package model

type Ruleset struct {
	Smoking  bool `json:"is_smoking"`
	Children bool `json:"has_children"`
	Pets     bool `json:"has_pets"`
}
