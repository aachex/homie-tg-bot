-- +goose Up
-- +goose StatementBegin
CREATE TABLE IF NOT EXISTS report (
    id BIGSERIAL PRIMARY KEY,
    offer_id BIGINT NOT NULL REFERENCES tg_house_offer(id) ON DELETE CASCADE,
    reporter_id BIGINT NOT NULL,
    reason TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(offer_id, reporter_id)
);

CREATE INDEX idx_report_offer_id ON report(offer_id);
CREATE INDEX idx_report_reporter_id ON report(reporter_id);
CREATE INDEX idx_report_status ON report(status);
CREATE INDEX idx_report_created_at ON report(created_at);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP INDEX IF EXISTS idx_report_offer_id;
DROP INDEX IF EXISTS idx_report_reporter_id;
DROP INDEX IF EXISTS idx_report_status;
DROP INDEX IF EXISTS idx_report_created_at;

DROP TABLE IF EXISTS report;
-- +goose StatementEnd