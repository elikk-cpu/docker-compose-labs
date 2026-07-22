CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

INSERT INTO settings(key, value)
VALUES ('release', 'second-version')
ON CONFLICT (key) DO NOTHING;
