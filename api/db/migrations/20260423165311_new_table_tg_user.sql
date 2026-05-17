-- +goose Up
-- +goose StatementBegin
CREATE TYPE children_enum AS ENUM {'zero', 'one', 'two+', 'planning'}
CREATE TYPE pets_enum AS ENUM {'cats', 'dogs', 'other'}
CREATE TYPE noiselvl_enum AS ENUM {'quiet', 'normal', 'loud'}
CREATE TYPE alcohol_enum AS ENUM {'never', 'rare', 'regular'}

CREATE TABLE IF NOT EXISTS tg_user (
    id BIGINT PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    media_files TEXT[] NOT NULL DEFAULT '{}',
    
    -- Флаги арендатора. Если значение NULL, то значит, что у LLM не получилось его определить
    smoking BOOL,
    children children_enum,
    pets pets_enum,
    occupants_count INT,
    noise_lvl noiselvl_enum,
    works_from_home BOOL,
    alcohol alcohol_enum,
    age_min INT,
    age_max INT
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS tg_user;

DROP TYPE IF EXISTS alcohol_enum CASCADE;
DROP TYPE IF EXISTS noiselvl_enum CASCADE;
DROP TYPE IF EXISTS pets_enum CASCADE;
DROP TYPE IF EXISTS children_enum CASCADE;
-- +goose StatementEnd
