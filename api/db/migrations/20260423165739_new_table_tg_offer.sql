-- +goose Up
-- +goose StatementBegin
CREATE TABLE IF NOT EXISTS tg_house_offer (
    id BIGSERIAL PRIMARY KEY NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    price INTEGER NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('RENT', 'SELL')),
    owner_id BIGINT NOT NULL REFERENCES tg_user (id)
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS tg_house_offer;
-- +goose StatementEnd
