# Databricks notebook source
# MAGIC %md
# MAGIC # Project IRIS - OT Asset Management Demo
# MAGIC ## Unity Catalog Extension for Industrial Assets
# MAGIC
# MAGIC This notebook demonstrates the core capabilities of Project IRIS - extending Unity Catalog with Operational Technology (OT) asset management.
# MAGIC
# MAGIC ### Key Features:
# MAGIC - ISA-95 compliant asset hierarchies
# MAGIC - Asset types (templates) and asset instances
# MAGIC - Parent-child relationships
# MAGIC - Custom properties with type safety
# MAGIC - Integration with Unity Catalog governance

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Setup and Configuration

# COMMAND ----------

import requests
import json
from datetime import datetime
import pandas as pd

# Configuration
UC_SERVER = "http://localhost:8080"  # Unity Catalog server with IRIS extensions
API_BASE = f"{UC_SERVER}/api/2.1/unity-catalog"
CATALOG = "iris_ot_assets"
SCHEMA = "assets"

# Test connection
def test_connection():
    try:
        response = requests.get(f"{API_BASE}/catalogs")
        print(f"✅ Connected to Unity Catalog server")
        print(f"Available catalogs: {[c['name'] for c in response.json()['catalogs']]}")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

test_connection()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Create Asset Types (Templates)

# COMMAND ----------

def create_asset_type(name, properties, comment=""):
    """Create an asset type (template) in Unity Catalog"""

    data = {
        "catalog_name": CATALOG,
        "schema_name": SCHEMA,
        "name": name,
        "comment": comment,
        "properties": properties
    }

    response = requests.post(f"{API_BASE}/asset-types", json=data)
    if response.status_code in [200, 201]:
        print(f"✅ Created asset type: {name}")
        return response.json()
    else:
        print(f"❌ Failed to create {name}: {response.status_code}")
        return None

# Create Motor asset type
motor_type = create_asset_type(
    name="IndustrialMotor",
    comment="Template for industrial electric motors",
    properties=[
        {
            "name": "rated_power",
            "data_type": "FLOAT",
            "is_required": True,
            "comment": "Rated power in kW"
        },
        {
            "name": "rated_speed",
            "data_type": "INT",
            "is_required": True,
            "comment": "Rated speed in RPM"
        },
        {
            "name": "voltage",
            "data_type": "INT",
            "is_required": False,
            "comment": "Operating voltage"
        },
        {
            "name": "manufacturer",
            "data_type": "STRING",
            "is_required": False,
            "comment": "Motor manufacturer"
        },
        {
            "name": "efficiency_class",
            "data_type": "STRING",
            "is_required": False,
            "comment": "IE efficiency class (IE1-IE4)"
        }
    ]
)

# Create Pump asset type
pump_type = create_asset_type(
    name="CentrifugalPump",
    comment="Template for centrifugal pumps",
    properties=[
        {
            "name": "flow_rate",
            "data_type": "FLOAT",
            "is_required": True,
            "comment": "Flow rate in m3/h"
        },
        {
            "name": "head",
            "data_type": "FLOAT",
            "is_required": True,
            "comment": "Head in meters"
        },
        {
            "name": "impeller_diameter",
            "data_type": "FLOAT",
            "is_required": False,
            "comment": "Impeller diameter in mm"
        },
        {
            "name": "suction_size",
            "data_type": "STRING",
            "is_required": False,
            "comment": "Suction flange size"
        }
    ]
)

# Create Sensor asset type
sensor_type = create_asset_type(
    name="IndustrialSensor",
    comment="Template for industrial sensors",
    properties=[
        {
            "name": "measurement_type",
            "data_type": "STRING",
            "is_required": True,
            "comment": "Type of measurement (temperature, pressure, flow, etc.)"
        },
        {
            "name": "range_min",
            "data_type": "FLOAT",
            "is_required": True,
            "comment": "Minimum measurement range"
        },
        {
            "name": "range_max",
            "data_type": "FLOAT",
            "is_required": True,
            "comment": "Maximum measurement range"
        },
        {
            "name": "accuracy",
            "data_type": "FLOAT",
            "is_required": False,
            "comment": "Measurement accuracy in %"
        },
        {
            "name": "protocol",
            "data_type": "STRING",
            "is_required": False,
            "comment": "Communication protocol (4-20mA, HART, Modbus, etc.)"
        }
    ]
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. List Asset Types

# COMMAND ----------

def list_asset_types():
    """List all asset types in the catalog"""
    response = requests.get(f"{API_BASE}/asset-types?catalog_name={CATALOG}&schema_name={SCHEMA}")
    if response.status_code == 200:
        types = response.json().get('asset_types', [])
        df = pd.DataFrame(types)
        return df[['name', 'full_name', 'comment', 'created_at']] if not df.empty else df
    return pd.DataFrame()

asset_types_df = list_asset_types()
display(asset_types_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Create Asset Hierarchy

# COMMAND ----------

def create_asset(name, asset_type_name, parent_name=None, properties=None, comment=""):
    """Create an asset instance in Unity Catalog"""

    data = {
        "catalog_name": CATALOG,
        "schema_name": SCHEMA,
        "name": name,
        "asset_type_full_name": f"{CATALOG}.{SCHEMA}.{asset_type_name}",
        "comment": comment
    }

    if parent_name:
        data["parent_asset_full_name"] = f"{CATALOG}.{SCHEMA}.{parent_name}"

    if properties:
        data["properties"] = properties

    response = requests.post(f"{API_BASE}/assets", json=data)
    if response.status_code in [200, 201]:
        print(f"✅ Created asset: {name}")
        return response.json()
    else:
        print(f"❌ Failed to create {name}: {response.status_code}")
        return None

# Create production line hierarchy
plant = create_asset(
    name="ManufacturingPlant01",
    asset_type_name="IndustrialMotor",  # Using motor type as placeholder for plant
    comment="Main manufacturing facility",
    properties={
        "rated_power": "10000",
        "rated_speed": "1"
    }
)

# Create pump station
pump_station = create_asset(
    name="PumpStation_A",
    asset_type_name="CentrifugalPump",
    parent_name="ManufacturingPlant01",
    comment="Main cooling water pump station",
    properties={
        "flow_rate": "500",
        "head": "45"
    }
)

# Create individual pumps
pump1 = create_asset(
    name="Pump_CW_001",
    asset_type_name="CentrifugalPump",
    parent_name="PumpStation_A",
    comment="Cooling water pump #1",
    properties={
        "flow_rate": "250",
        "head": "45",
        "impeller_diameter": "450",
        "suction_size": "DN200"
    }
)

pump2 = create_asset(
    name="Pump_CW_002",
    asset_type_name="CentrifugalPump",
    parent_name="PumpStation_A",
    comment="Cooling water pump #2 (Standby)",
    properties={
        "flow_rate": "250",
        "head": "45",
        "impeller_diameter": "450",
        "suction_size": "DN200"
    }
)

# Create motor for pump
motor1 = create_asset(
    name="Motor_CW_001",
    asset_type_name="IndustrialMotor",
    parent_name="Pump_CW_001",
    comment="Drive motor for pump CW-001",
    properties={
        "rated_power": "75",
        "rated_speed": "2980",
        "voltage": "400",
        "manufacturer": "ABB",
        "efficiency_class": "IE3"
    }
)

# Create sensors
temp_sensor = create_asset(
    name="TT_CW_001",
    asset_type_name="IndustrialSensor",
    parent_name="Pump_CW_001",
    comment="Discharge temperature transmitter",
    properties={
        "measurement_type": "temperature",
        "range_min": "0",
        "range_max": "100",
        "accuracy": "0.5",
        "protocol": "4-20mA"
    }
)

pressure_sensor = create_asset(
    name="PT_CW_001",
    asset_type_name="IndustrialSensor",
    parent_name="Pump_CW_001",
    comment="Discharge pressure transmitter",
    properties={
        "measurement_type": "pressure",
        "range_min": "0",
        "range_max": "10",
        "accuracy": "0.25",
        "protocol": "HART"
    }
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. View Asset Hierarchy

# COMMAND ----------

def get_asset_hierarchy(parent_name=None, level=0):
    """Recursively get asset hierarchy"""

    if parent_name:
        # Get children of specific asset
        response = requests.get(f"{API_BASE}/assets/{CATALOG}.{SCHEMA}.{parent_name}/children")
    else:
        # Get root assets
        response = requests.get(f"{API_BASE}/assets?catalog_name={CATALOG}&schema_name={SCHEMA}")

    if response.status_code == 200:
        assets = response.json().get('assets', [])

        for asset in assets:
            # Print asset with indentation
            indent = "  " * level
            print(f"{indent}├── {asset['name']} ({asset.get('asset_type', {}).get('name', 'N/A')})")

            # Recursively get children
            if asset.get('has_children'):
                get_asset_hierarchy(asset['name'], level + 1)

print("Asset Hierarchy:")
print("=" * 50)
get_asset_hierarchy()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Query Assets with Properties

# COMMAND ----------

def list_assets_with_details():
    """List all assets with their properties"""
    response = requests.get(f"{API_BASE}/assets?catalog_name={CATALOG}&schema_name={SCHEMA}")

    if response.status_code == 200:
        assets = response.json().get('assets', [])

        # Create detailed dataframe
        asset_details = []
        for asset in assets:
            asset_detail = {
                'name': asset['name'],
                'type': asset.get('asset_type', {}).get('name', 'N/A'),
                'parent': asset.get('parent_asset', {}).get('name', 'Root'),
                'comment': asset.get('comment', ''),
                'created_at': asset.get('created_at', '')
            }

            # Add properties as columns
            if 'properties' in asset:
                for key, value in asset['properties'].items():
                    asset_detail[f'prop_{key}'] = value

            asset_details.append(asset_detail)

        return pd.DataFrame(asset_details)

    return pd.DataFrame()

assets_df = list_assets_with_details()
display(assets_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Asset Search and Filtering

# COMMAND ----------

# Simulate asset search (would be implemented server-side)
def search_assets(asset_type=None, property_filter=None):
    """Search assets by type or property values"""

    response = requests.get(f"{API_BASE}/assets?catalog_name={CATALOG}&schema_name={SCHEMA}")

    if response.status_code == 200:
        assets = response.json().get('assets', [])

        # Filter by asset type
        if asset_type:
            assets = [a for a in assets if a.get('asset_type', {}).get('name') == asset_type]

        # Filter by property
        if property_filter:
            filtered = []
            for asset in assets:
                props = asset.get('properties', {})
                match = True
                for key, value in property_filter.items():
                    if key not in props or float(props[key]) != float(value):
                        match = False
                        break
                if match:
                    filtered.append(asset)
            assets = filtered

        return assets

    return []

# Find all pumps
print("All Pumps:")
pumps = search_assets(asset_type="CentrifugalPump")
for pump in pumps:
    print(f"  - {pump['name']}: Flow={pump.get('properties', {}).get('flow_rate', 'N/A')} m3/h")

print("\nHigh Power Motors (>50kW):")
motors = search_assets(asset_type="IndustrialMotor")
for motor in motors:
    power = float(motor.get('properties', {}).get('rated_power', 0))
    if power > 50:
        print(f"  - {motor['name']}: {power} kW")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Asset Lineage and Dependencies

# COMMAND ----------

def get_asset_lineage(asset_name):
    """Get complete lineage of an asset (ancestors and descendants)"""

    full_name = f"{CATALOG}.{SCHEMA}.{asset_name}"

    # Get asset details
    response = requests.get(f"{API_BASE}/assets/{full_name}")
    if response.status_code != 200:
        print(f"Asset not found: {asset_name}")
        return

    asset = response.json()

    print(f"Asset Lineage for: {asset_name}")
    print("=" * 50)

    # Get ancestors
    print("\nAncestors (Parent Chain):")
    current = asset
    level = 0
    ancestors = []
    while 'parent_asset' in current and current['parent_asset']:
        parent = current['parent_asset']
        ancestors.append(parent['name'])
        print(f"  {'  ' * level}↑ {parent['name']}")

        # Fetch parent details
        parent_response = requests.get(f"{API_BASE}/assets/{parent['full_name']}")
        if parent_response.status_code == 200:
            current = parent_response.json()
        else:
            break
        level += 1

    # Get descendants
    print(f"\nCurrent Asset:")
    print(f"  ● {asset_name} ({asset.get('asset_type', {}).get('name', 'N/A')})")

    print("\nDescendants (Children):")

    def print_descendants(parent_name, level=1):
        response = requests.get(f"{API_BASE}/assets/{CATALOG}.{SCHEMA}.{parent_name}/children")
        if response.status_code == 200:
            children = response.json().get('assets', [])
            for child in children:
                print(f"  {'  ' * level}↓ {child['name']} ({child.get('asset_type', {}).get('name', 'N/A')})")
                if child.get('has_children'):
                    print_descendants(child['name'], level + 1)

    print_descendants(asset_name)

# Show lineage for a pump
get_asset_lineage("Pump_CW_001")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Integration with Unity Catalog Features

# COMMAND ----------

# Demonstrate how assets integrate with UC features
print("Unity Catalog Integration Points:")
print("=" * 50)
print("\n1. Governance:")
print("   - Assets inherit catalog and schema permissions")
print("   - Row-level security can be applied to asset properties")
print("   - Audit logging tracks all asset operations")

print("\n2. Data Lineage:")
print("   - Assets can be linked to Delta tables containing telemetry")
print("   - Asset hierarchy provides context for operational data")
print("   - Properties can reference data locations")

print("\n3. Discovery:")
print("   - Assets searchable through UC catalog browser")
print("   - Tags and comments enable asset classification")
print("   - Full-text search across asset properties")

print("\n4. Integration:")
print("   - Asset IDs can be foreign keys in Delta tables")
print("   - Telemetry data joins with asset metadata")
print("   - Analytics leverage asset hierarchy for aggregation")

# Example: Link assets to telemetry table
print("\n" + "=" * 50)
print("Example SQL Query with Assets:")
print("=" * 50)
print("""
-- Join telemetry data with asset metadata
SELECT
    t.timestamp,
    t.sensor_id,
    a.name as asset_name,
    a.properties:measurement_type as measurement_type,
    t.value,
    a.properties:range_min as min_range,
    a.properties:range_max as max_range,
    CASE
        WHEN t.value < a.properties:range_min OR t.value > a.properties:range_max
        THEN 'OUT_OF_RANGE'
        ELSE 'NORMAL'
    END as status
FROM iris_ot_assets.telemetry.sensor_readings t
JOIN iris_ot_assets.assets.assets a ON t.sensor_id = a.asset_id
WHERE a.asset_type = 'IndustrialSensor'
  AND t.timestamp >= current_date() - 7
ORDER BY t.timestamp DESC
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10. Cleanup (Optional)

# COMMAND ----------

def cleanup_demo():
    """Remove demo assets and types"""

    print("Cleaning up demo assets...")

    # Delete assets (children first)
    assets_to_delete = [
        "PT_CW_001", "TT_CW_001", "Motor_CW_001",
        "Pump_CW_002", "Pump_CW_001",
        "PumpStation_A", "ManufacturingPlant01"
    ]

    for asset_name in assets_to_delete:
        response = requests.delete(f"{API_BASE}/assets/{CATALOG}.{SCHEMA}.{asset_name}")
        if response.status_code in [200, 204]:
            print(f"  ✅ Deleted asset: {asset_name}")
        else:
            print(f"  ⚠️  Could not delete: {asset_name}")

    # Delete asset types
    types_to_delete = ["IndustrialSensor", "CentrifugalPump", "IndustrialMotor"]

    for type_name in types_to_delete:
        response = requests.delete(f"{API_BASE}/asset-types/{CATALOG}.{SCHEMA}.{type_name}")
        if response.status_code in [200, 204]:
            print(f"  ✅ Deleted type: {type_name}")
        else:
            print(f"  ⚠️  Could not delete: {type_name}")

    print("Cleanup complete!")

# Uncomment to run cleanup
# cleanup_demo()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC This notebook demonstrated the core capabilities of **Project IRIS**:
# MAGIC
# MAGIC ✅ **Asset Types** - Defined reusable templates for motors, pumps, and sensors
# MAGIC ✅ **Asset Instances** - Created actual equipment with properties
# MAGIC ✅ **Hierarchies** - Built parent-child relationships (Plant → Pump Station → Pumps → Components)
# MAGIC ✅ **Properties** - Stored technical specifications with type safety
# MAGIC ✅ **Search & Filter** - Queried assets by type and property values
# MAGIC ✅ **Lineage** - Traced asset dependencies up and down the hierarchy
# MAGIC ✅ **UC Integration** - Demonstrated governance, discovery, and data integration points
# MAGIC
# MAGIC ### Next Steps:
# MAGIC 1. Run the **Rio Tinto Mining Demo** for a real-world example
# MAGIC 2. Try the **PI AF Migration** tool to import existing assets
# MAGIC 3. Connect telemetry data to assets for operational analytics
# MAGIC 4. Build dashboards combining asset metadata with time-series data