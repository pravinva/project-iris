# PI Asset Framework to Unity Catalog Migration Tool

## Overview

The PI AF Migration Tool enables seamless migration of OT asset hierarchies from OSISoft PI Asset Framework to Unity Catalog's new asset management capabilities. This tool preserves the complete hierarchy, element templates, attributes, and relationships while mapping them to Unity Catalog's asset model.

## Features

- **Complete Hierarchy Migration**: Preserves parent-child relationships from PI AF
- **Template Mapping**: Converts PI Element Templates to Unity Catalog Asset Types
- **Attribute Conversion**: Maps PI attributes to Unity Catalog properties with appropriate data types
- **Batch Processing**: Efficiently processes large hierarchies with progress tracking
- **Rollback Capability**: Full rollback support if migration fails
- **Dry Run Mode**: Simulate migration without making changes
- **Detailed Reporting**: Comprehensive migration reports with warnings and errors
- **ISA-95 Compliance**: Maintains industrial standards compatibility

## Prerequisites

1. Unity Catalog server running with Asset Management extensions
2. Python 3.8+
3. Unity Catalog Python client library
4. Access to PI AF export data (JSON format)

## Installation

```bash
# Navigate to migration tool directory
cd tools/pi_af_migration

# Install dependencies (if needed)
pip install -r requirements.txt
```

## Usage

### Basic Migration

```bash
python pi_af_migrator.py sample_pi_export.json \
    --catalog unity \
    --schema default \
    --server http://localhost:8080
```

### Dry Run (Simulation)

```bash
python pi_af_migrator.py sample_pi_export.json \
    --dry-run \
    --report dry_run_report.json
```

### Rollback Previous Migration

```bash
python pi_af_migrator.py sample_pi_export.json \
    --rollback
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `export_file` | PI AF export file in JSON format | Required |
| `--catalog` | Target Unity Catalog catalog name | `unity` |
| `--schema` | Target Unity Catalog schema name | `default` |
| `--server` | Unity Catalog server URL | `http://localhost:8080` |
| `--dry-run` | Simulate migration without creating assets | `False` |
| `--rollback` | Rollback previous migration | `False` |
| `--report` | Migration report filename | `migration_report.json` |

## PI AF Export Format

The tool expects PI AF data in JSON format with the following structure:

```json
{
  "export_metadata": {
    "source_system": "OSISoft PI AF",
    "export_date": "2024-02-28T10:00:00Z",
    "database": "DatabaseName",
    "server": "ServerName",
    "version": "2018 SP3"
  },
  "templates": [
    {
      "name": "TemplateName",
      "base_template": "ParentTemplate",
      "description": "Template description",
      "categories": ["Category1", "Category2"],
      "attribute_templates": {
        "AttributeName": {
          "type": "DataType",
          "required": true,
          "description": "Attribute description"
        }
      }
    }
  ],
  "elements": [
    {
      "name": "ElementName",
      "path": "\\\\Server\\Database\\Path\\To\\Element",
      "template": "TemplateName",
      "parent_path": "\\\\Server\\Database\\Path\\To\\Parent",
      "description": "Element description",
      "categories": ["Category"],
      "attributes": {
        "AttributeName": "Value"
      }
    }
  ]
}
```

## Migration Process

### Phase 1: Asset Type Creation
1. Creates default asset types (PIServer, PIDatabase, GenericElement)
2. Converts PI Element Templates to Unity Catalog Asset Types
3. Maps PI attribute data types to UC property types

### Phase 2: Hierarchy Analysis
1. Analyzes element hierarchy depth
2. Sorts elements by level for proper creation order
3. Validates parent-child relationships

### Phase 3: Asset Creation
1. Creates assets level by level (top-down)
2. Preserves original PI paths as properties
3. Maintains parent-child relationships
4. Converts attributes to properties

### Phase 4: Validation & Reporting
1. Validates created assets
2. Generates comprehensive migration report
3. Saves migration state for rollback capability

## Data Type Mapping

| PI AF Type | Unity Catalog Type | Description |
|------------|-------------------|-------------|
| Double | FLOAT | Floating point numbers |
| Float32 | FLOAT | 32-bit float |
| Float64 | FLOAT | 64-bit float |
| Int16 | INT | 16-bit integer |
| Int32 | INT | 32-bit integer |
| Int64 | LONG | 64-bit integer |
| Boolean | BOOLEAN | True/False values |
| String | STRING | Text values |
| DateTime | TIMESTAMP | Date and time values |

## Migration Report

The tool generates a detailed JSON report containing:

```json
{
  "start_time": "2024-02-28T10:00:00",
  "end_time": "2024-02-28T10:05:00",
  "templates_migrated": 5,
  "assets_migrated": 150,
  "errors": [],
  "warnings": [
    {
      "type": "element_skipped",
      "element": "\\\\Path\\To\\Element",
      "reason": "Parent not found"
    }
  ]
}
```

## Example: Rio Tinto Mining Migration

The included `sample_pi_export.json` demonstrates migration of a Rio Tinto mining operation hierarchy:

```
RioTintoMining (Enterprise)
├── PilbaraOperations (Site)
│   ├── TomPriceMine (Mine)
│   │   ├── MiningFleet (Area)
│   │   │   ├── HaulTruck_AHS001 (Autonomous Haul Truck)
│   │   │   ├── HaulTruck_AHS002 (Autonomous Haul Truck)
│   │   │   └── Excavator_EX001 (Hydraulic Excavator)
│   │   └── ProcessingPlant (Area)
│   │       ├── PrimaryCrusher01 (Gyratory Crusher)
│   │       └── MainConveyor01 (Overland Conveyor)
│   ├── HopeDowns4 (Mine)
│   ├── RailOperations (Infrastructure)
│   └── PortOperations (Port Facilities)
```

### Running the Example

```bash
# Dry run first to verify
python pi_af_migrator.py sample_pi_export.json --dry-run

# Perform actual migration
python pi_af_migrator.py sample_pi_export.json

# Check migration report
cat migration_report.json
```

## Rollback

If a migration needs to be reverted:

```bash
# Rollback using saved state
python pi_af_migrator.py sample_pi_export.json --rollback
```

The tool maintains `migration_state.json` which tracks:
- Created asset types with their full names
- Created assets with their full names
- Mapping between PI paths and UC assets

## Best Practices

1. **Always run dry-run first**: Verify the migration plan before execution
2. **Backup before migration**: Ensure you have backups of both systems
3. **Validate exports**: Check PI AF export completeness
4. **Review mappings**: Verify data type mappings are appropriate
5. **Test in development**: Run migrations in dev environment first
6. **Monitor logs**: Check logs for warnings about skipped elements
7. **Verify hierarchy**: Confirm parent-child relationships are preserved

## Troubleshooting

### Common Issues

1. **"Asset type already exists"**
   - Asset types from previous migration exist
   - Solution: Use rollback or manually delete existing types

2. **"Parent not found"**
   - Element references non-existent parent
   - Solution: Verify export completeness, check hierarchy

3. **"Invalid name"**
   - PI AF names contain invalid characters for UC
   - Solution: Tool auto-sanitizes names, check migration report

4. **Connection errors**
   - Unity Catalog server not accessible
   - Solution: Verify server URL and network connectivity

### Debug Mode

For detailed debugging, modify the logging level:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Extending the Tool

### Custom Template Mappings

Add custom template mappings in `create_asset_type_from_template()`:

```python
def custom_template_mapping(template_name):
    mappings = {
        'YourCustomTemplate': 'TargetAssetType',
        'AnotherTemplate': 'AnotherType'
    }
    return mappings.get(template_name)
```

### Additional Attribute Processing

Extend `migrate_element()` to process specific attributes:

```python
def process_custom_attributes(element, properties):
    if 'SpecialAttribute' in element.attributes:
        # Custom processing
        properties['processed_value'] = transform(
            element.attributes['SpecialAttribute']
        )
    return properties
```

## Performance Considerations

- **Batch Size**: Default processes all elements, consider chunking for very large migrations
- **Parallel Processing**: Currently sequential, can be extended for parallel asset creation
- **API Rate Limits**: Respect Unity Catalog API limits
- **Memory Usage**: Large exports may require streaming processing

## Security

- **Credentials**: Use environment variables or secure config for authentication
- **Data Sanitization**: Tool sanitizes names and values automatically
- **Audit Trail**: Migration reports provide full audit trail
- **Rollback Safety**: State files enable safe rollback

## Support

For issues or questions:
1. Check the migration report for specific errors
2. Review Unity Catalog server logs
3. Consult the troubleshooting section
4. File issues in the project repository

## License

This tool is part of the Unity Catalog Asset Management extension and follows the same Apache 2.0 license.