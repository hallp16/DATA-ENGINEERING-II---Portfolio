-- read-only role for the downstream ML application
CREATE ROLE ml_reader WITH LOGIN PASSWORD 'ml_reader_pw';
GRANT CONNECT ON DATABASE traffic_db TO ml_reader;
GRANT USAGE ON SCHEMA public TO ml_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ml_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO ml_reader;