CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
INSERT INTO settings(key, value) VALUES ('welcome', 'first-version');
