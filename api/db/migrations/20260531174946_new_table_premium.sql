-- +goose Up
-- +goose StatementBegin
CREATE TABLE IF NOT EXISTS premium (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE,
    until TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_premium_user_id ON premium(user_id);
CREATE INDEX idx_premium_until ON premium(until);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP INDEX IF EXISTS idx_premium_user_id;
DROP INDEX IF EXISTS idx_premium_until;
DROP TABLE IF EXISTS premium;
-- +goose StatementEnd