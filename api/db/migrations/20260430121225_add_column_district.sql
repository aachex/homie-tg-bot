-- +goose Up
-- +goose StatementBegin
ALTER TABLE tg_house_offer
    ADD COLUMN IF NOT EXISTS district TEXT NOT NULL DEFAULT '';
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE tg_house_offer
    DROP COLUMN IF EXISTS district;
-- +goose StatementEnd
