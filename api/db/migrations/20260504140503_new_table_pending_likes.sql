-- +goose Up
-- +goose StatementBegin
CREATE TABLE IF NOT EXISTS pending_likes (
    id BIGSERIAL PRIMARY KEY NOT NULL,
    user_id BIGINT NOT NULL REFERENCES tg_user(id) ON DELETE CASCADE,
    offer_id BIGINT NOT NULL REFERENCES tg_house_offer (id) ON DELETE CASCADE,
    relevance INT NOT NULL CHECK (0 <= relevance AND relevance <= 100),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(offer_id, user_id)
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS pending_likes;
-- +goose StatementEnd
