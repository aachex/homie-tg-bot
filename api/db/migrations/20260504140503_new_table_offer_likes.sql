-- +goose Up
-- +goose StatementBegin
CREATE TABLE IF NOT EXISTS offer_like (
    id BIGSERIAL PRIMARY KEY NOT NULL,
    offer_id BIGINT NOT NULL REFERENCES tg_house_offer (id),
    user_id BIGINT NOT NULL REFERENCES tg_user (id)
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS offer_like;
-- +goose StatementEnd
