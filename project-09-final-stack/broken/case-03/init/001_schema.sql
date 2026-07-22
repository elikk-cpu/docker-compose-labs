CREATE TABLE IF NOT EXISTS processed_jobs (
    id BIGSERIAL PRIMARY KEY,
    payload JSONB NOT NULL,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
