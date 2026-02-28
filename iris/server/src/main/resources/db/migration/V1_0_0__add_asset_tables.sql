-- Migration script for adding OT Asset management tables to Unity Catalog
-- Version: 1.0.0
-- Description: Creates tables for AssetType and Asset entities to support ISA-95 compliant asset hierarchies

-- Create AssetType table
CREATE TABLE IF NOT EXISTS uc_asset_types (
    id UUID NOT NULL PRIMARY KEY,
    catalog_name VARCHAR(255) NOT NULL,
    schema_name VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    comment TEXT,
    properties TEXT, -- JSON array of AssetPropertyDef objects
    owner VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_at TIMESTAMP,
    updated_by VARCHAR(255),
    UNIQUE KEY unique_asset_type (catalog_name, schema_name, name),
    INDEX idx_asset_type_catalog (catalog_name),
    INDEX idx_asset_type_schema (schema_name)
);

-- Create Asset table with self-referential hierarchy support
CREATE TABLE IF NOT EXISTS uc_assets (
    id UUID NOT NULL PRIMARY KEY,
    catalog_name VARCHAR(255) NOT NULL,
    schema_name VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    asset_type_id UUID NOT NULL,
    parent_asset_id UUID,
    comment TEXT,
    properties TEXT, -- JSON key-value pairs for asset properties
    property_bindings TEXT, -- JSON array of AssetPropertyBinding objects
    owner VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_at TIMESTAMP,
    updated_by VARCHAR(255),
    UNIQUE KEY unique_asset (catalog_name, schema_name, name),
    INDEX idx_asset_catalog (catalog_name),
    INDEX idx_asset_schema (schema_name),
    INDEX idx_asset_type (asset_type_id),
    INDEX idx_parent_asset (parent_asset_id),
    CONSTRAINT fk_asset_type FOREIGN KEY (asset_type_id)
        REFERENCES uc_asset_types(id) ON DELETE RESTRICT,
    CONSTRAINT fk_parent_asset FOREIGN KEY (parent_asset_id)
        REFERENCES uc_assets(id) ON DELETE CASCADE
);

-- Add indexes for common query patterns
CREATE INDEX idx_asset_hierarchy ON uc_assets(parent_asset_id, name);
CREATE INDEX idx_asset_type_lookup ON uc_assets(asset_type_id, catalog_name, schema_name);

-- Comments for documentation
COMMENT ON TABLE uc_asset_types IS 'Stores asset type definitions with property schemas for OT asset management';
COMMENT ON TABLE uc_assets IS 'Stores asset instances with hierarchical relationships and property bindings';
COMMENT ON COLUMN uc_asset_types.properties IS 'JSON array of AssetPropertyDef objects defining the schema for assets of this type';
COMMENT ON COLUMN uc_assets.properties IS 'JSON object with key-value pairs for asset instance properties';
COMMENT ON COLUMN uc_assets.property_bindings IS 'JSON array of AssetPropertyBinding objects linking properties to lakehouse data sources';
COMMENT ON COLUMN uc_assets.parent_asset_id IS 'Self-referential foreign key enabling unlimited hierarchy depth';