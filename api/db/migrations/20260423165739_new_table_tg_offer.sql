-- +goose Up
-- +goose StatementBegin
CREATE TABLE IF NOT EXISTS tg_house_offer (
    id BIGSERIAL PRIMARY KEY NOT NULL,
    owner_id BIGINT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    city TEXT NOT NULL,
    district TEXT NOT NULL DEFAULT '',
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    price INTEGER NOT NULL,
    media_files TEXT[] NOT NULL,
    flag_processing BOOL NOT NULL DEFAULT FALSE,

    -- Флаги предпочтений арендодателя (что он хочет от арендатора)
    preferred_smoking BOOL,
    preferred_children children_enum,
    preferred_pets pets_enum,
    preferred_occupants_count INT,
    preferred_noise_lvl noiselvl_enum,
    preferred_works_from_home BOOL,
    preferred_alcohol alcohol_enum,
    preferred_age_min INT,
    preferred_age_max INT,
    preferred_sex sex_enum
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS tg_house_offer;
-- +goose StatementEnd
