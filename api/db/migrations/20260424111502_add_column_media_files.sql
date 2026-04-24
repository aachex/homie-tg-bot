-- +goose Up
-- +goose StatementBegin
ALTER TABLE tg_user
ADD COLUMN IF NOT EXISTS media_files TEXT[];

ALTER TABLE tg_house_offer
ADD COLUMN IF NOT EXISTS media_files TEXT[];
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE tg_user
DROP COLUMN IF EXISTS media_files;

ALTER TABLE tg_house_offer
DROP COLUMN IF EXISTS media_files;
-- +goose StatementEnd
