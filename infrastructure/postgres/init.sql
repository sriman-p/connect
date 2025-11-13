-- Connect Database Initialization Script
-- Memory-optimized settings for 5000 users in <512MB

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For full-text search

-- Set optimal configuration for memory efficiency
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET work_mem = '4MB';

-- Logging
ALTER SYSTEM SET log_statement = 'none';
ALTER SYSTEM SET log_duration = off;
ALTER SYSTEM SET log_line_prefix = '%t [%p]: ';

-- Optimize for read-heavy workloads (typical for collaboration apps)
ALTER SYSTEM SET random_page_cost = 1.1;  -- For SSD storage
ALTER SYSTEM SET effective_io_concurrency = 200;

-- Connection pooling settings
ALTER SYSTEM SET max_connections = 200;

-- Vacuum settings for better performance
ALTER SYSTEM SET autovacuum_max_workers = 3;
ALTER SYSTEM SET autovacuum_naptime = '1min';

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE connect_db TO connect_user;

SELECT pg_reload_conf();
