-- +goose Up
-- +goose StatementBegin
CREATE TABLE IF NOT EXISTS user_activities (
    id BIGSERIAL PRIMARY KEY NOT NULL,
    time TIMESTAMP NOT NULL DEFAULT NOW(),
    user_id BIGINT NOT NULL,
    action VARCHAR(30) NOT NULL,
    action_data JSONB NOT NULL
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS user_activities;
-- +goose StatementEnd
