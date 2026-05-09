-- +goose Up
-- +goose StatementBegin
CREATE TABLE IF NOT EXISTS tg_house_offer (
    id BIGSERIAL PRIMARY KEY NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    price INTEGER NOT NULL,
    owner_id BIGINT NOT NULL,
    allowed_smoking BOOL NOT NULL DEFAULT FALSE,
    allowed_children BOOL NOT NULL DEFAULT FALSE,
    allowed_pets BOOL NOT NULL DEFAULT FALSE
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS tg_house_offer;
-- +goose StatementEnd
