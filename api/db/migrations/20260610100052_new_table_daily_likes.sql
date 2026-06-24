-- +goose Up
-- +goose StatementBegin
CREATE TABLE IF NOT EXISTS daily_likes (
    id BIGSERIAL PRIMARY KEY NOT NULL,
    user_id BIGINT NOT NULL REFERENCES tg_user(id) ON DELETE CASCADE,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    likes_count INT NOT NULL DEFAULT 0,
    UNIQUE (user_id, date)
);

CREATE INDEX IF NOT EXISTS idx_daily_likes_user_date ON daily_likes(user_id, date);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP INDEX IF EXISTS idx_daily_likes_user_date;
DROP TABLE IF EXISTS daily_likes;
-- +goose StatementEnd