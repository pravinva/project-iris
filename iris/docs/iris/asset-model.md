# IRIS Asset Model Design

## Object Types Added
- AssetType
- Asset
- AssetPropertyBinding

## Key Design Decisions
- Self-referential parent_asset_id enables unlimited hierarchy depth
- Typed bindings connect asset properties to any lakehouse data source