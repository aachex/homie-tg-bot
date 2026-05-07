-- +goose Up
-- +goose StatementBegin
CREATE TABLE IF NOT EXISTS tg_user (
    id BIGINT PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    age INT NOT NULL CHECK (0 <= age AND age <= 150),
    description TEXT NOT NULL DEFAULT '',
    city TEXT NOT NULL,
    is_smoking BOOL NOT NULL,
    has_children BOOL NOT NULL
    has_pets BOOL NOT NULL,
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS tg_user;
-- +goose StatementEnd
