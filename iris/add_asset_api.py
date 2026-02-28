#!/usr/bin/env python3
import yaml

# Load the existing OpenAPI spec
with open('api/all.yaml', 'r') as f:
    spec = yaml.safe_load(f)

# Add Asset-related paths
asset_paths = {
    '/unity-catalog/asset-types': {
        'get': {
            'summary': 'List asset types',
            'description': 'Gets an array of asset types in the given parent catalog and schema.',
            'operationId': 'list-asset-types',
            'parameters': [
                {'name': 'catalog_name', 'in': 'query', 'description': 'The name of the catalog', 'required': True, 'schema': {'type': 'string'}},
                {'name': 'schema_name', 'in': 'query', 'description': 'The name of the schema', 'required': True, 'schema': {'type': 'string'}},
                {'name': 'max_results', 'in': 'query', 'description': 'Maximum number of asset types to return', 'schema': {'type': 'integer', 'format': 'int32'}},
                {'name': 'page_token', 'in': 'query', 'description': 'Opaque pagination token to go to next page', 'schema': {'type': 'string'}}
            ],
            'responses': {
                '200': {
                    'description': 'The asset types list was successfully retrieved',
                    'content': {'application/json': {'schema': {'$ref': '#/components/schemas/AssetTypeList'}}}
                }
            },
            'tags': ['Assets']
        },
        'post': {
            'summary': 'Create an asset type',
            'description': 'Creates a new asset type.',
            'operationId': 'create-asset-type',
            'requestBody': {
                'required': True,
                'content': {'application/json': {'schema': {'$ref': '#/components/schemas/CreateAssetType'}}}
            },
            'responses': {
                '201': {
                    'description': 'The asset type was successfully created',
                    'content': {'application/json': {'schema': {'$ref': '#/components/schemas/AssetTypeInfo'}}}
                }
            },
            'tags': ['Assets']
        }
    },
    '/unity-catalog/asset-types/{full_name}': {
        'get': {
            'summary': 'Get an asset type',
            'description': 'Gets an asset type by its full name',
            'operationId': 'get-asset-type',
            'parameters': [
                {'name': 'full_name', 'in': 'path', 'description': 'Full name of the asset type', 'required': True, 'schema': {'type': 'string'}}
            ],
            'responses': {
                '200': {
                    'description': 'The asset type was successfully retrieved',
                    'content': {'application/json': {'schema': {'$ref': '#/components/schemas/AssetTypeInfo'}}}
                }
            },
            'tags': ['Assets']
        },
        'delete': {
            'summary': 'Delete an asset type',
            'description': 'Deletes an asset type by its full name',
            'operationId': 'delete-asset-type',
            'parameters': [
                {'name': 'full_name', 'in': 'path', 'description': 'Full name of the asset type', 'required': True, 'schema': {'type': 'string'}}
            ],
            'responses': {
                '204': {'description': 'The asset type was successfully deleted'}
            },
            'tags': ['Assets']
        }
    },
    '/unity-catalog/assets': {
        'get': {
            'summary': 'List assets',
            'description': 'Gets an array of assets',
            'operationId': 'list-assets',
            'parameters': [
                {'name': 'catalog_name', 'in': 'query', 'description': 'The name of the catalog', 'required': True, 'schema': {'type': 'string'}},
                {'name': 'schema_name', 'in': 'query', 'description': 'The name of the schema', 'required': True, 'schema': {'type': 'string'}},
                {'name': 'asset_type_full_name', 'in': 'query', 'description': 'Filter by asset type full name', 'schema': {'type': 'string'}},
                {'name': 'parent_asset_full_name', 'in': 'query', 'description': 'Filter by parent asset full name (for children)', 'schema': {'type': 'string'}},
                {'name': 'max_results', 'in': 'query', 'description': 'Maximum number of assets to return', 'schema': {'type': 'integer', 'format': 'int32'}},
                {'name': 'page_token', 'in': 'query', 'description': 'Opaque pagination token to go to next page', 'schema': {'type': 'string'}}
            ],
            'responses': {
                '200': {
                    'description': 'The assets list was successfully retrieved',
                    'content': {'application/json': {'schema': {'$ref': '#/components/schemas/AssetList'}}}
                }
            },
            'tags': ['Assets']
        },
        'post': {
            'summary': 'Create an asset',
            'description': 'Creates a new asset',
            'operationId': 'create-asset',
            'requestBody': {
                'required': True,
                'content': {'application/json': {'schema': {'$ref': '#/components/schemas/CreateAsset'}}}
            },
            'responses': {
                '201': {
                    'description': 'The asset was successfully created',
                    'content': {'application/json': {'schema': {'$ref': '#/components/schemas/AssetInfo'}}}
                }
            },
            'tags': ['Assets']
        }
    },
    '/unity-catalog/assets/{full_name}': {
        'get': {
            'summary': 'Get an asset',
            'description': 'Gets an asset by its full name',
            'operationId': 'get-asset',
            'parameters': [
                {'name': 'full_name', 'in': 'path', 'description': 'Full name of the asset', 'required': True, 'schema': {'type': 'string'}}
            ],
            'responses': {
                '200': {
                    'description': 'The asset was successfully retrieved',
                    'content': {'application/json': {'schema': {'$ref': '#/components/schemas/AssetInfo'}}}
                }
            },
            'tags': ['Assets']
        },
        'delete': {
            'summary': 'Delete an asset',
            'description': 'Deletes an asset by its full name',
            'operationId': 'delete-asset',
            'parameters': [
                {'name': 'full_name', 'in': 'path', 'description': 'Full name of the asset', 'required': True, 'schema': {'type': 'string'}}
            ],
            'responses': {
                '204': {'description': 'The asset was successfully deleted'}
            },
            'tags': ['Assets']
        }
    },
    '/unity-catalog/assets/{full_name}/children': {
        'get': {
            'summary': 'List child assets',
            'description': 'Lists all child assets of a given parent asset',
            'operationId': 'list-child-assets',
            'parameters': [
                {'name': 'full_name', 'in': 'path', 'description': 'Full name of the parent asset', 'required': True, 'schema': {'type': 'string'}},
                {'name': 'max_results', 'in': 'query', 'description': 'Maximum number of child assets to return', 'schema': {'type': 'integer', 'format': 'int32'}},
                {'name': 'page_token', 'in': 'query', 'description': 'Opaque pagination token to go to next page', 'schema': {'type': 'string'}}
            ],
            'responses': {
                '200': {
                    'description': 'The child assets list was successfully retrieved',
                    'content': {'application/json': {'schema': {'$ref': '#/components/schemas/AssetList'}}}
                }
            },
            'tags': ['Assets']
        }
    }
}

# Add paths to spec
for path, methods in asset_paths.items():
    spec['paths'][path] = methods

# Add Asset-related schemas
asset_schemas = {
    'AssetPropertyDef': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'The name of the asset property'},
            'data_type': {'type': 'string', 'description': 'The data type of the property (e.g., DOUBLE, STRING, INTEGER)'},
            'unit': {'type': 'string', 'description': 'The unit of measurement for the property'},
            'description': {'type': 'string', 'description': 'Description of the property'}
        },
        'required': ['name', 'data_type']
    },
    'AssetTypeInfo': {
        'type': 'object',
        'properties': {
            'catalog_name': {'type': 'string', 'description': 'The name of the catalog where the asset type is'},
            'schema_name': {'type': 'string', 'description': 'The name of the schema where the asset type is'},
            'name': {'type': 'string', 'description': 'The name of the asset type'},
            'full_name': {'type': 'string', 'description': 'Full name of the asset type (catalog.schema.name)'},
            'comment': {'type': 'string', 'description': 'The comment attached to the asset type'},
            'properties': {'type': 'array', 'items': {'$ref': '#/components/schemas/AssetPropertyDef'}, 'description': 'List of property definitions for this asset type'},
            'created_at': {'type': 'integer', 'format': 'int64', 'description': 'Time at which this asset type was created, in epoch milliseconds'},
            'created_by': {'type': 'string', 'description': 'The identifier of the user who created the asset type'},
            'updated_at': {'type': 'integer', 'format': 'int64', 'description': 'Time at which this asset type was last modified, in epoch milliseconds'},
            'updated_by': {'type': 'string', 'description': 'The identifier of the user who updated the asset type last time'},
            'owner': {'type': 'string', 'description': 'The identifier of the user who owns the asset type'}
        },
        'required': ['catalog_name', 'schema_name', 'name', 'full_name']
    },
    'CreateAssetType': {
        'type': 'object',
        'properties': {
            'catalog_name': {'type': 'string', 'description': 'The name of the catalog where the asset type will be created'},
            'schema_name': {'type': 'string', 'description': 'The name of the schema where the asset type will be created'},
            'name': {'type': 'string', 'description': 'The name of the asset type'},
            'comment': {'type': 'string', 'description': 'The comment attached to the asset type'},
            'properties': {'type': 'array', 'items': {'$ref': '#/components/schemas/AssetPropertyDef'}, 'description': 'List of property definitions for this asset type'}
        },
        'required': ['catalog_name', 'schema_name', 'name']
    },
    'AssetInfo': {
        'type': 'object',
        'properties': {
            'catalog_name': {'type': 'string', 'description': 'The name of the catalog where the asset is'},
            'schema_name': {'type': 'string', 'description': 'The name of the schema where the asset is'},
            'name': {'type': 'string', 'description': 'The name of the asset'},
            'full_name': {'type': 'string', 'description': 'Full name of the asset (catalog.schema.name)'},
            'asset_type_full_name': {'type': 'string', 'description': 'Full name of the asset type this asset belongs to'},
            'parent_asset_full_name': {'type': 'string', 'description': 'Full name of the parent asset (if this is a child asset)'},
            'comment': {'type': 'string', 'description': 'The comment attached to the asset'},
            'properties': {'type': 'object', 'additionalProperties': {'type': 'string'}, 'description': 'Key-value properties of the asset'},
            'property_bindings': {'type': 'array', 'items': {'$ref': '#/components/schemas/AssetPropertyBinding'}, 'description': 'List of property bindings for this asset'},
            'created_at': {'type': 'integer', 'format': 'int64', 'description': 'Time at which this asset was created, in epoch milliseconds'},
            'created_by': {'type': 'string', 'description': 'The identifier of the user who created the asset'},
            'updated_at': {'type': 'integer', 'format': 'int64', 'description': 'Time at which this asset was last modified, in epoch milliseconds'},
            'updated_by': {'type': 'string', 'description': 'The identifier of the user who updated the asset last time'},
            'owner': {'type': 'string', 'description': 'The identifier of the user who owns the asset'}
        },
        'required': ['catalog_name', 'schema_name', 'name', 'full_name', 'asset_type_full_name']
    },
    'CreateAsset': {
        'type': 'object',
        'properties': {
            'catalog_name': {'type': 'string', 'description': 'The name of the catalog where the asset will be created'},
            'schema_name': {'type': 'string', 'description': 'The name of the schema where the asset will be created'},
            'name': {'type': 'string', 'description': 'The name of the asset'},
            'asset_type_full_name': {'type': 'string', 'description': 'Full name of the asset type this asset belongs to'},
            'parent_asset_full_name': {'type': 'string', 'description': 'Full name of the parent asset (if this is a child asset)'},
            'comment': {'type': 'string', 'description': 'The comment attached to the asset'},
            'properties': {'type': 'object', 'additionalProperties': {'type': 'string'}, 'description': 'Key-value properties of the asset'}
        },
        'required': ['catalog_name', 'schema_name', 'name', 'asset_type_full_name']
    },
    'AssetPropertyBinding': {
        'type': 'object',
        'properties': {
            'property_name': {'type': 'string', 'description': 'The name of the property being bound'},
            'binding_type': {'type': 'string', 'enum': ['TABLE_COLUMN', 'VOLUME_FILE', 'FUNCTION_OUTPUT', 'METRIC_VALUE'], 'description': 'The type of binding'},
            'table_full_name': {'type': 'string', 'description': 'Full name of the table (for TABLE_COLUMN binding)'},
            'column_name': {'type': 'string', 'description': 'Column name in the table (for TABLE_COLUMN binding)'},
            'volume_full_name': {'type': 'string', 'description': 'Full name of the volume (for VOLUME_FILE binding)'},
            'file_path': {'type': 'string', 'description': 'Path to the file in the volume (for VOLUME_FILE binding)'},
            'function_full_name': {'type': 'string', 'description': 'Full name of the function (for FUNCTION_OUTPUT binding)'},
            'metric_name': {'type': 'string', 'description': 'Name of the metric (for METRIC_VALUE binding)'}
        },
        'required': ['property_name', 'binding_type']
    },
    'AssetList': {
        'type': 'object',
        'properties': {
            'assets': {'type': 'array', 'items': {'$ref': '#/components/schemas/AssetInfo'}, 'description': 'List of assets'},
            'next_page_token': {'type': 'string', 'description': 'Opaque token to retrieve the next page of results'}
        }
    },
    'AssetTypeList': {
        'type': 'object',
        'properties': {
            'asset_types': {'type': 'array', 'items': {'$ref': '#/components/schemas/AssetTypeInfo'}, 'description': 'List of asset types'},
            'next_page_token': {'type': 'string', 'description': 'Opaque token to retrieve the next page of results'}
        }
    }
}

# Add schemas to components
for schema_name, schema_def in asset_schemas.items():
    spec['components']['schemas'][schema_name] = schema_def

# Write the updated spec back
with open('api/all.yaml', 'w') as f:
    yaml.dump(spec, f, default_flow_style=False, sort_keys=False, width=120)

print("Successfully added Asset API to OpenAPI specification")