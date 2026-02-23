-- File: src/db/migrations/002_add_model_tracking.sql
-- Description: Migration script to add model tracking and versioning support
-- Author: Database Architect
-- Created At: 2023-10-10
-- Project: Federated Learning Framework for Healthcare Data Sharing

BEGIN;

-- 1. Create the `models` table to store model metadata
CREATE TABLE IF NOT EXISTS models (
    id BIGSERIAL PRIMARY KEY, -- Unique identifier for each model
    name VARCHAR(255) NOT NULL, -- Model name
    description TEXT, -- Detailed description of the model
    framework VARCHAR(100) NOT NULL, -- Framework used (e.g., TensorFlow, PyTorch)
    version VARCHAR(50) NOT NULL, -- Semantic versioning (e.g., 1.0.0)
    created_by UUID NOT NULL, -- User ID of the creator (foreign key to users table)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, -- Audit column
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, -- Audit column
    deleted_at TIMESTAMP NULL, -- Soft delete column
    CONSTRAINT unique_model_name_version UNIQUE (name, version), -- Ensure unique name-version pairs
    CONSTRAINT chk_model_version_format CHECK (version ~ '^[0-9]+\.[0-9]+\.[0-9]+$') -- Enforce semantic versioning
);

-- 2. Create the `model_versions` table to track model versions
CREATE TABLE IF NOT EXISTS model_versions (
    id BIGSERIAL PRIMARY KEY, -- Unique identifier for each version
    model_id BIGINT NOT NULL, -- Foreign key to models table
    version VARCHAR(50) NOT NULL, -- Semantic versioning
    file_path TEXT NOT NULL, -- Path to the model file (e.g., S3 bucket or local storage)
    checksum CHAR(64) NOT NULL, -- SHA-256 checksum for file integrity
    metadata JSONB, -- Additional metadata (e.g., training parameters, hyperparameters)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, -- Audit column
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, -- Audit column
    deleted_at TIMESTAMP NULL, -- Soft delete column
    CONSTRAINT fk_model FOREIGN KEY (model_id) REFERENCES models (id) ON DELETE CASCADE,
    CONSTRAINT unique_model_version_file UNIQUE (model_id, version), -- Ensure unique version per model
    CONSTRAINT chk_checksum_length CHECK (LENGTH(checksum) = 64) -- Ensure checksum is valid
);

-- 3. Create indexes for performance optimization
CREATE INDEX idx_models_name ON models (name);
CREATE INDEX idx_model_versions_model_id ON model_versions (model_id);
CREATE INDEX idx_model_versions_checksum ON model_versions (checksum);

-- 4. Add triggers for automatic `updated_at` timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at_on_models
BEFORE UPDATE ON models
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_updated_at_on_model_versions
BEFORE UPDATE ON model_versions
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- 5. Add soft delete functionality with query filters
CREATE OR REPLACE FUNCTION soft_delete_model()
RETURNS TRIGGER AS $$
BEGIN
    NEW.deleted_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER soft_delete_on_models
BEFORE DELETE ON models
FOR EACH ROW
EXECUTE FUNCTION soft_delete_model();

CREATE TRIGGER soft_delete_on_model_versions
BEFORE DELETE ON model_versions
FOR EACH ROW
EXECUTE FUNCTION soft_delete_model();

-- 6. Add a materialized view for reporting (e.g., latest model versions)
CREATE MATERIALIZED VIEW latest_model_versions AS
SELECT
    m.id AS model_id,
    m.name AS model_name,
    mv.version AS latest_version,
    mv.file_path AS latest_file_path,
    mv.metadata AS latest_metadata,
    mv.created_at AS version_created_at
FROM
    models m
INNER JOIN LATERAL (
    SELECT *
    FROM model_versions mv
    WHERE mv.model_id = m.id
    ORDER BY mv.created_at DESC
    LIMIT 1
) mv ON true
WHERE m.deleted_at IS NULL AND mv.deleted_at IS NULL;

-- Index for materialized view
CREATE UNIQUE INDEX idx_latest_model_versions_model_id ON latest_model_versions (model_id);

-- 7. Add a partitioning strategy for large datasets (optional, based on use case)
-- Example: Partition `model_versions` by `model_id` for scalability
CREATE TABLE model_versions_partitioned (
    LIKE model_versions INCLUDING ALL
) PARTITION BY HASH (model_id);

-- Move existing data to the partitioned table (if applicable)
-- INSERT INTO model_versions_partitioned SELECT * FROM model_versions;

-- 8. Add replication/backup considerations (e.g., logical replication slots)
-- This will depend on the specific database setup and requirements.

COMMIT;