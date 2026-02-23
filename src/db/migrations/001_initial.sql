-- src/db/migrations/001_initial.sql
-- Migration: Initial database setup for Federated Learning Framework for Healthcare Data Sharing
-- Author: [Your Name]
-- Created: [Date]
-- Description: Sets up core tables, indexes, constraints, and audit columns.

BEGIN;

-- SCHEMA CREATION
CREATE SCHEMA IF NOT EXISTS healthcare_data AUTHORIZATION postgres;

-- TABLE: users
CREATE TABLE healthcare_data.users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'researcher', 'clinician')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

-- TABLE: organizations
CREATE TABLE healthcare_data.organizations (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    address TEXT NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

-- TABLE: datasets
CREATE TABLE healthcare_data.datasets (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    organization_id BIGINT NOT NULL REFERENCES healthcare_data.organizations(id) ON DELETE CASCADE,
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

-- TABLE: models
CREATE TABLE healthcare_data.models (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    dataset_id BIGINT NOT NULL REFERENCES healthcare_data.datasets(id) ON DELETE CASCADE,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

-- TABLE: training_jobs
CREATE TABLE healthcare_data.training_jobs (
    id BIGSERIAL PRIMARY KEY,
    model_id BIGINT NOT NULL REFERENCES healthcare_data.models(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

-- INDEXING STRATEGY
-- Indexes for faster lookups
CREATE INDEX idx_users_email ON healthcare_data.users(email);
CREATE INDEX idx_organizations_name ON healthcare_data.organizations(name);
CREATE INDEX idx_datasets_organization_id ON healthcare_data.datasets(organization_id);
CREATE INDEX idx_models_dataset_id ON healthcare_data.models(dataset_id);
CREATE INDEX idx_training_jobs_model_id ON healthcare_data.training_jobs(model_id);

-- PARTIAL INDEXES
-- Only index active users
CREATE INDEX idx_users_active ON healthcare_data.users(is_active) WHERE is_active = TRUE;

-- DATA INTEGRITY
-- Ensure soft delete consistency
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for automatic updated_at updates
CREATE TRIGGER trigger_users_updated_at
BEFORE UPDATE ON healthcare_data.users
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trigger_organizations_updated_at
BEFORE UPDATE ON healthcare_data.organizations
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trigger_datasets_updated_at
BEFORE UPDATE ON healthcare_data.datasets
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trigger_models_updated_at
BEFORE UPDATE ON healthcare_data.models
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trigger_training_jobs_updated_at
BEFORE UPDATE ON healthcare_data.training_jobs
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- AUDIT TRAIL (Optional)
-- Table to track changes for audit purposes
CREATE TABLE healthcare_data.audit_logs (
    id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(255) NOT NULL,
    operation VARCHAR(50) NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
    record_id BIGINT NOT NULL,
    changed_data JSONB,
    changed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    changed_by BIGINT REFERENCES healthcare_data.users(id) ON DELETE SET NULL
);

-- FUNCTION: Log changes for audit
CREATE OR REPLACE FUNCTION log_audit()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO healthcare_data.audit_logs (table_name, operation, record_id, changed_data, changed_at, changed_by)
    VALUES (TG_TABLE_NAME, TG_OP, NEW.id, row_to_json(NEW), NOW(), NULL); -- Replace NULL with session_user_id if available
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add triggers for audit logging
CREATE TRIGGER audit_users
AFTER INSERT OR UPDATE OR DELETE ON healthcare_data.users
FOR EACH ROW EXECUTE FUNCTION log_audit();

CREATE TRIGGER audit_organizations
AFTER INSERT OR UPDATE OR DELETE ON healthcare_data.organizations
FOR EACH ROW EXECUTE FUNCTION log_audit();

CREATE TRIGGER audit_datasets
AFTER INSERT OR UPDATE OR DELETE ON healthcare_data.datasets
FOR EACH ROW EXECUTE FUNCTION log_audit();

CREATE TRIGGER audit_models
AFTER INSERT OR UPDATE OR DELETE ON healthcare_data.models
FOR EACH ROW EXECUTE FUNCTION log_audit();

CREATE TRIGGER audit_training_jobs
AFTER INSERT OR UPDATE OR DELETE ON healthcare_data.training_jobs
FOR EACH ROW EXECUTE FUNCTION log_audit();

-- REPLICATION AND BACKUP CONSIDERATIONS
-- Ensure WAL archiving is enabled for point-in-time recovery (to be configured in PostgreSQL settings)

COMMIT;