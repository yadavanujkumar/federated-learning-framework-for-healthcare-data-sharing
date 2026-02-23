-- src/db/schema.sql

-- Enable extensions for advanced features
CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; -- For generating UUIDs
CREATE EXTENSION IF NOT EXISTS "pgcrypto"; -- For cryptographic functions
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For full-text search optimization

-- ============================
-- Table: Users
-- ============================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'researcher', 'clinician')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- ============================
-- Table: Organizations
-- ============================
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    address TEXT,
    contact_email VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- ============================
-- Table: Models
-- ============================
CREATE TABLE models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(50) NOT NULL,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- ============================
-- Table: Model Artifacts
-- ============================
CREATE TABLE model_artifacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID NOT NULL REFERENCES models(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    checksum TEXT NOT NULL,
    file_size BIGINT NOT NULL CHECK (file_size > 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- ============================
-- Table: Training Metadata
-- ============================
CREATE TABLE training_metadata (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID NOT NULL REFERENCES models(id) ON DELETE CASCADE,
    training_data_source TEXT NOT NULL,
    training_parameters JSONB NOT NULL,
    training_start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    training_end_time TIMESTAMP WITH TIME ZONE,
    accuracy FLOAT CHECK (accuracy >= 0 AND accuracy <= 1),
    loss FLOAT CHECK (loss >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- ============================
-- Table: Audit Logs
-- ============================
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(255) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- ============================
-- Indexing for Performance
-- ============================
-- Index for fast lookup on email
CREATE UNIQUE INDEX idx_users_email ON users (email);

-- Index for soft delete filtering
CREATE INDEX idx_users_not_deleted ON users (deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_organizations_not_deleted ON organizations (deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_models_not_deleted ON models (deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_model_artifacts_not_deleted ON model_artifacts (deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_training_metadata_not_deleted ON training_metadata (deleted_at) WHERE deleted_at IS NULL;

-- Index for full-text search on model name and description
CREATE INDEX idx_models_fulltext ON models USING gin(to_tsvector('english', name || ' ' || description));

-- ============================
-- Partitioning Strategy (Optional)
-- ============================
-- Partitioning for audit_logs table by time
CREATE TABLE audit_logs_2023 PARTITION OF audit_logs FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');
CREATE TABLE audit_logs_2024 PARTITION OF audit_logs FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

-- ============================
-- Triggers for Audit Columns
-- ============================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger to tables
CREATE TRIGGER set_updated_at_trigger
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER set_updated_at_trigger
BEFORE UPDATE ON organizations
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER set_updated_at_trigger
BEFORE UPDATE ON models
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER set_updated_at_trigger
BEFORE UPDATE ON model_artifacts
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER set_updated_at_trigger
BEFORE UPDATE ON training_metadata
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- ============================
-- Seed Data (Optional)
-- ============================
INSERT INTO users (email, password_hash, full_name, role) VALUES
('admin@example.com', crypt('securepassword', gen_salt('bf')), 'Admin User', 'admin');

INSERT INTO organizations (name, address, contact_email) VALUES
('Global Health Org', '123 Health St, City, Country', 'contact@health.org');

-- ============================
-- End of Schema
-- ============================