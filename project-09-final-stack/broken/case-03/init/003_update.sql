INSERT INTO settings(key, value)
VALUES ('release', 'second-version')
ON CONFLICT (key)
DO UPDATE SET value = EXCLUDED.value;
