-- +goose Up
-- +goose StatementBegin
ALTER TABLE offer_like ADD CONSTRAINT unique_offer_user UNIQUE (offer_id, user_id);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE offer_like DROP CONSTRAINT unique_offer_user;
-- +goose StatementEnd
