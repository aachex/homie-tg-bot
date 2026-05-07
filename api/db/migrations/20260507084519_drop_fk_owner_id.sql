-- +goose Up
-- +goose StatementBegin
ALTER TABLE tg_house_offer 
DROP CONSTRAINT tg_house_offer_owner_id_fkey;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE tg_house_offer 
ADD CONSTRAINT tg_house_offer_owner_id_fkey 
FOREIGN KEY (owner_id) REFERENCES tg_user (id);
-- +goose StatementEnd
