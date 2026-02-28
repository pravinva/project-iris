#!/usr/bin/env python
"""
PI Asset Framework to Unity Catalog Migration Tool

This tool migrates OT asset hierarchies from OSISoft PI Asset Framework
to Unity Catalog's new Asset management capabilities.

Features:
- Full hierarchy migration preserving parent-child relationships
- Asset type mapping and creation
- Attribute to property conversion
- Batch processing with progress tracking
- Rollback capability
- Validation and reporting
"""

import json
import logging
import argparse
import sys
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import traceback

# Add parent directory to path for asset_client import
sys.path.append(os.path.join(os.path.dirname(__file__), '../../clients/python/src'))

from unitycatalog.client.asset_client import AssetClient
from unitycatalog.client.models import AssetPropertyDef

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class PIElement:
    """Represents a PI AF Element"""
    name: str
    path: str
    template: Optional[str]
    parent_path: Optional[str]
    attributes: Dict[str, Any]
    description: Optional[str]
    categories: List[str] = None


@dataclass
class PIElementTemplate:
    """Represents a PI AF Element Template"""
    name: str
    base_template: Optional[str]
    attribute_templates: Dict[str, Dict[str, Any]]
    description: Optional[str]
    categories: List[str] = None


class PIAFMigrator:
    """
    Migrates PI AF assets to Unity Catalog
    """

    def __init__(self,
                 uc_client: AssetClient,
                 catalog_name: str = "unity",
                 schema_name: str = "default",
                 dry_run: bool = False):
        """
        Initialize the migrator.

        Args:
            uc_client: Unity Catalog asset client
            catalog_name: Target catalog name
            schema_name: Target schema name
            dry_run: If True, only simulate migration
        """
        self.uc_client = uc_client
        self.catalog_name = catalog_name
        self.schema_name = schema_name
        self.dry_run = dry_run

        # Track migration state
        self.created_types = {}  # PI template -> UC asset type mapping
        self.created_assets = {}  # PI path -> UC full name mapping
        self.migration_report = {
            'start_time': datetime.now().isoformat(),
            'templates_migrated': 0,
            'assets_migrated': 0,
            'errors': [],
            'warnings': []
        }

    def map_pi_type_to_data_type(self, pi_type: str) -> str:
        """
        Map PI attribute type to UC property data type.

        Args:
            pi_type: PI attribute type

        Returns:
            UC data type (STRING, FLOAT, INT, BOOLEAN, TIMESTAMP)
        """
        type_mapping = {
            'Double': 'FLOAT',
            'Float32': 'FLOAT',
            'Float64': 'FLOAT',
            'Int16': 'INT',
            'Int32': 'INT',
            'Int64': 'LONG',
            'Boolean': 'BOOLEAN',
            'String': 'STRING',
            'DateTime': 'TIMESTAMP',
            'Timestamp': 'TIMESTAMP'
        }

        return type_mapping.get(pi_type, 'STRING')

    def create_asset_type_from_template(self, template: PIElementTemplate) -> str:
        """
        Create UC asset type from PI element template.

        Args:
            template: PI element template

        Returns:
            Full name of created asset type
        """
        # Check if already created
        if template.name in self.created_types:
            return self.created_types[template.name]

        # Convert attribute templates to property definitions
        properties = []
        for attr_name, attr_def in template.attribute_templates.items():
            prop_def = AssetPropertyDef(
                name=self.sanitize_name(attr_name),
                data_type=self.map_pi_type_to_data_type(attr_def.get('type', 'String')),
                is_required=attr_def.get('required', False),
                comment=attr_def.get('description', f'Migrated from PI attribute {attr_name}')
            )
            properties.append(prop_def)

        # Create asset type
        type_name = self.sanitize_name(template.name)

        if self.dry_run:
            logger.info(f"[DRY RUN] Would create asset type: {type_name}")
            full_name = f"{self.catalog_name}.{self.schema_name}.{type_name}"
        else:
            try:
                asset_type = self.uc_client.create_asset_type(
                    catalog_name=self.catalog_name,
                    schema_name=self.schema_name,
                    name=type_name,
                    comment=template.description or f"Migrated from PI template {template.name}",
                    properties=properties
                )
                full_name = asset_type.full_name
                logger.info(f"Created asset type: {full_name}")
                self.migration_report['templates_migrated'] += 1
            except Exception as e:
                logger.error(f"Failed to create asset type {type_name}: {e}")
                self.migration_report['errors'].append({
                    'type': 'asset_type_creation',
                    'template': template.name,
                    'error': str(e)
                })
                raise

        self.created_types[template.name] = full_name
        return full_name

    def create_default_asset_types(self):
        """
        Create default asset types for common PI AF elements.
        """
        default_types = [
            {
                'name': 'PIServer',
                'comment': 'PI Server or Data Archive',
                'properties': [
                    AssetPropertyDef('server_name', 'STRING', True, 'PI Server name'),
                    AssetPropertyDef('version', 'STRING', False, 'Server version'),
                    AssetPropertyDef('connection_string', 'STRING', False, 'Connection details')
                ]
            },
            {
                'name': 'PIDatabase',
                'comment': 'PI AF Database',
                'properties': [
                    AssetPropertyDef('database_name', 'STRING', True, 'Database name'),
                    AssetPropertyDef('description', 'STRING', False, 'Database description')
                ]
            },
            {
                'name': 'GenericElement',
                'comment': 'Generic PI AF Element',
                'properties': [
                    AssetPropertyDef('element_id', 'STRING', False, 'Original PI element ID'),
                    AssetPropertyDef('categories', 'STRING', False, 'Element categories'),
                    AssetPropertyDef('template', 'STRING', False, 'Original template name')
                ]
            }
        ]

        for type_def in default_types:
            if type_def['name'] not in self.created_types:
                if self.dry_run:
                    logger.info(f"[DRY RUN] Would create default asset type: {type_def['name']}")
                    self.created_types[type_def['name']] = \
                        f"{self.catalog_name}.{self.schema_name}.{type_def['name']}"
                else:
                    try:
                        asset_type = self.uc_client.create_asset_type(
                            catalog_name=self.catalog_name,
                            schema_name=self.schema_name,
                            name=type_def['name'],
                            comment=type_def['comment'],
                            properties=type_def['properties']
                        )
                        self.created_types[type_def['name']] = asset_type.full_name
                        logger.info(f"Created default asset type: {asset_type.full_name}")
                    except Exception as e:
                        if 'already exists' not in str(e).lower():
                            raise
                        # Type already exists, get it
                        full_name = f"{self.catalog_name}.{self.schema_name}.{type_def['name']}"
                        self.created_types[type_def['name']] = full_name

    def migrate_element(self, element: PIElement, parent_full_name: Optional[str] = None) -> str:
        """
        Migrate a single PI element to UC asset.

        Args:
            element: PI element to migrate
            parent_full_name: Parent asset full name in UC

        Returns:
            Full name of created asset
        """
        # Check if already migrated
        if element.path in self.created_assets:
            return self.created_assets[element.path]

        # Determine asset type
        if element.template and element.template in self.created_types:
            asset_type_full_name = self.created_types[element.template]
        else:
            # Use generic element type
            asset_type_full_name = self.created_types.get('GenericElement',
                f"{self.catalog_name}.{self.schema_name}.GenericElement")

        # Convert attributes to properties
        properties = {}
        for attr_name, attr_value in element.attributes.items():
            prop_name = self.sanitize_name(attr_name)
            # Convert value to string if necessary
            if isinstance(attr_value, (dict, list)):
                properties[prop_name] = json.dumps(attr_value)
            else:
                properties[prop_name] = str(attr_value)

        # Add metadata properties
        properties['pi_element_path'] = element.path
        if element.template:
            properties['template'] = element.template
        if element.categories:
            properties['categories'] = ','.join(element.categories)

        # Create asset
        asset_name = self.sanitize_name(element.name)

        if self.dry_run:
            logger.info(f"[DRY RUN] Would create asset: {asset_name} (parent: {parent_full_name})")
            full_name = f"{self.catalog_name}.{self.schema_name}.{asset_name}"
        else:
            try:
                asset = self.uc_client.create_asset(
                    catalog_name=self.catalog_name,
                    schema_name=self.schema_name,
                    name=asset_name,
                    asset_type_full_name=asset_type_full_name,
                    parent_asset_full_name=parent_full_name,
                    comment=element.description or f"Migrated from PI element: {element.path}",
                    properties=properties
                )
                full_name = asset.full_name
                logger.info(f"Created asset: {full_name}")
                self.migration_report['assets_migrated'] += 1
            except Exception as e:
                logger.error(f"Failed to create asset {asset_name}: {e}")
                self.migration_report['errors'].append({
                    'type': 'asset_creation',
                    'element': element.path,
                    'error': str(e)
                })
                raise

        self.created_assets[element.path] = full_name
        return full_name

    def migrate_hierarchy(self, elements: List[PIElement], templates: List[PIElementTemplate]):
        """
        Migrate complete PI AF hierarchy to UC.

        Args:
            elements: List of PI elements sorted by hierarchy level
            templates: List of PI element templates
        """
        logger.info(f"Starting migration of {len(templates)} templates and {len(elements)} elements")

        # Phase 1: Create default asset types
        logger.info("Phase 1: Creating default asset types")
        self.create_default_asset_types()

        # Phase 2: Create asset types from templates
        logger.info("Phase 2: Creating asset types from templates")
        for template in templates:
            try:
                self.create_asset_type_from_template(template)
            except Exception as e:
                logger.warning(f"Skipping template {template.name}: {e}")
                self.migration_report['warnings'].append({
                    'type': 'template_skipped',
                    'template': template.name,
                    'reason': str(e)
                })

        # Phase 3: Sort elements by hierarchy depth
        logger.info("Phase 3: Sorting elements by hierarchy")
        elements_by_depth = self.sort_elements_by_depth(elements)

        # Phase 4: Create assets level by level
        logger.info("Phase 4: Creating assets")
        for depth, level_elements in enumerate(elements_by_depth):
            logger.info(f"Processing hierarchy level {depth} with {len(level_elements)} elements")
            for element in level_elements:
                try:
                    # Find parent
                    parent_full_name = None
                    if element.parent_path:
                        parent_full_name = self.created_assets.get(element.parent_path)

                    self.migrate_element(element, parent_full_name)
                except Exception as e:
                    logger.warning(f"Skipping element {element.path}: {e}")
                    self.migration_report['warnings'].append({
                        'type': 'element_skipped',
                        'element': element.path,
                        'reason': str(e)
                    })

        # Phase 5: Generate report
        self.migration_report['end_time'] = datetime.now().isoformat()
        logger.info("Migration completed!")
        logger.info(f"Templates migrated: {self.migration_report['templates_migrated']}")
        logger.info(f"Assets migrated: {self.migration_report['assets_migrated']}")
        logger.info(f"Errors: {len(self.migration_report['errors'])}")
        logger.info(f"Warnings: {len(self.migration_report['warnings'])}")

    def sort_elements_by_depth(self, elements: List[PIElement]) -> List[List[PIElement]]:
        """
        Sort elements by hierarchy depth for proper parent-child creation order.

        Args:
            elements: List of PI elements

        Returns:
            List of element lists, grouped by depth
        """
        depth_map = {}

        for element in elements:
            depth = element.path.count('\\') if element.path else 0
            if depth not in depth_map:
                depth_map[depth] = []
            depth_map[depth].append(element)

        # Return sorted by depth
        return [depth_map[d] for d in sorted(depth_map.keys())]

    def sanitize_name(self, name: str) -> str:
        """
        Sanitize PI AF names for UC compatibility.

        Args:
            name: Original name

        Returns:
            Sanitized name
        """
        # Replace invalid characters
        sanitized = name.replace('\\', '_').replace('/', '_').replace('.', '_')
        sanitized = sanitized.replace(' ', '_').replace('-', '_')

        # Remove special characters
        sanitized = ''.join(c if c.isalnum() or c == '_' else '' for c in sanitized)

        # Ensure doesn't start with number
        if sanitized and sanitized[0].isdigit():
            sanitized = 'Asset_' + sanitized

        return sanitized or 'UnnamedAsset'

    def rollback(self):
        """
        Rollback the migration by deleting created assets and types.
        """
        logger.info("Starting rollback...")

        # Delete assets (in reverse order)
        for path in reversed(list(self.created_assets.keys())):
            full_name = self.created_assets[path]
            if not self.dry_run:
                try:
                    self.uc_client.delete_asset(full_name)
                    logger.info(f"Deleted asset: {full_name}")
                except Exception as e:
                    logger.error(f"Failed to delete asset {full_name}: {e}")

        # Delete asset types
        for template_name in self.created_types:
            full_name = self.created_types[template_name]
            if not self.dry_run:
                try:
                    self.uc_client.delete_asset_type(full_name)
                    logger.info(f"Deleted asset type: {full_name}")
                except Exception as e:
                    logger.error(f"Failed to delete asset type {full_name}: {e}")

        logger.info("Rollback completed")

    def save_report(self, filename: str):
        """
        Save migration report to file.

        Args:
            filename: Output filename
        """
        with open(filename, 'w') as f:
            json.dump(self.migration_report, f, indent=2)
        logger.info(f"Migration report saved to {filename}")


def load_pi_export(filename: str) -> Tuple[List[PIElement], List[PIElementTemplate]]:
    """
    Load PI AF export file.

    Args:
        filename: Path to PI AF export file (JSON format)

    Returns:
        Tuple of (elements, templates)
    """
    with open(filename, 'r') as f:
        data = json.load(f)

    # Parse templates
    templates = []
    for template_data in data.get('templates', []):
        template = PIElementTemplate(
            name=template_data['name'],
            base_template=template_data.get('base_template'),
            attribute_templates=template_data.get('attribute_templates', {}),
            description=template_data.get('description'),
            categories=template_data.get('categories', [])
        )
        templates.append(template)

    # Parse elements
    elements = []
    for element_data in data.get('elements', []):
        element = PIElement(
            name=element_data['name'],
            path=element_data['path'],
            template=element_data.get('template'),
            parent_path=element_data.get('parent_path'),
            attributes=element_data.get('attributes', {}),
            description=element_data.get('description'),
            categories=element_data.get('categories', [])
        )
        elements.append(element)

    return elements, templates


def main():
    parser = argparse.ArgumentParser(description='Migrate PI AF assets to Unity Catalog')
    parser.add_argument('export_file', help='PI AF export file (JSON format)')
    parser.add_argument('--catalog', default='unity', help='Target catalog name')
    parser.add_argument('--schema', default='default', help='Target schema name')
    parser.add_argument('--server', default='http://localhost:8080', help='Unity Catalog server URL')
    parser.add_argument('--dry-run', action='store_true', help='Simulate migration without creating assets')
    parser.add_argument('--rollback', action='store_true', help='Rollback previous migration')
    parser.add_argument('--report', default='migration_report.json', help='Migration report filename')

    args = parser.parse_args()

    # Initialize Unity Catalog client
    from unitycatalog.client import ApiClient, Configuration

    configuration = Configuration()
    configuration.host = f"{args.server}/api/2.1/unity-catalog"
    api_client = ApiClient(configuration)
    uc_client = AssetClient(api_client)

    # Create migrator
    migrator = PIAFMigrator(
        uc_client=uc_client,
        catalog_name=args.catalog,
        schema_name=args.schema,
        dry_run=args.dry_run
    )

    try:
        if args.rollback:
            # Load previous migration state if exists
            if os.path.exists('migration_state.json'):
                with open('migration_state.json', 'r') as f:
                    state = json.load(f)
                    migrator.created_assets = state.get('created_assets', {})
                    migrator.created_types = state.get('created_types', {})
            migrator.rollback()
        else:
            # Load PI AF export
            elements, templates = load_pi_export(args.export_file)

            # Perform migration
            migrator.migrate_hierarchy(elements, templates)

            # Save migration state
            if not args.dry_run:
                with open('migration_state.json', 'w') as f:
                    json.dump({
                        'created_assets': migrator.created_assets,
                        'created_types': migrator.created_types
                    }, f, indent=2)

        # Save report
        migrator.save_report(args.report)

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        logger.error(traceback.format_exc())

        if not args.dry_run and not args.rollback:
            response = input("Do you want to rollback? (y/n): ")
            if response.lower() == 'y':
                migrator.rollback()

        sys.exit(1)


if __name__ == "__main__":
    main()