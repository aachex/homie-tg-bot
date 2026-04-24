-- +goose Up
-- +goose StatementBegin
ALTER TABLE tg_house_offer
ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE tg_house_offer
DROP COLUMN IF EXISTS is_active;
-- +goose StatementEnd
