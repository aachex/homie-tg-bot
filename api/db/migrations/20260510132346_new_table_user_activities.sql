-- +goose Up
-- +goose StatementBegin
CREATE TABLE IF NOT EXISTS user_activities (
    id BIGSERIAL PRIMARY KEY NOT NULL,
    user_id BIGINT NOT NULL,
    action VARCHAR(20) NOT NULL,
    time TIMESTAMP NOT NULL DEFAULT NOW()
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS user_activities;
-- +goose StatementEnd
