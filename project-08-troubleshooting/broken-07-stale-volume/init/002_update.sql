INSERT INTO settings(key, value)
VALUES ('welcome', 'second-version')
ON CONFLICT (key)
DO UPDATE SET value = EXCLUDED.value;
