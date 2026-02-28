#!/usr/bin/env python
"""
Unity Catalog Asset Management Example

This example demonstrates how to use the Unity Catalog Asset client to:
1. Create asset types for industrial equipment
2. Build an ISA-95 compliant asset hierarchy
3. Manage asset properties and relationships

The example creates a typical industrial plant hierarchy:
- Enterprise
  - Site (Plant)
    - Area (Production Line)
      - Work Center (Equipment)
        - Equipment Modules (Motor, Pump, Sensor)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../clients/python/src'))

from unitycatalog.client.asset_client import AssetClient
from unitycatalog.client.models import AssetPropertyDef


def create_asset_types(client: AssetClient):
    """Create asset types following ISA-95 hierarchy levels."""

    print("Creating Asset Types...")

    # Enterprise Level (Level 4)
    enterprise_type = client.create_asset_type(
        catalog_name="unity",
        schema_name="default",
        name="Enterprise",
        comment="Top-level enterprise in ISA-95 hierarchy",
        properties=[
            AssetPropertyDef(
                name="company_name",
                data_type="STRING",
                is_required=True,
                comment="Name of the company"
            ),
            AssetPropertyDef(
                name="industry",
                data_type="STRING",
                is_required=False,
                comment="Industry sector"
            )
        ]
    )
    print(f"  Created: {enterprise_type.full_name}")

    # Site Level (Level 3)
    site_type = client.create_asset_type(
        catalog_name="unity",
        schema_name="default",
        name="Site",
        comment="Manufacturing site or plant",
        properties=[
            AssetPropertyDef(
                name="location",
                data_type="STRING",
                is_required=True,
                comment="Geographic location"
            ),
            AssetPropertyDef(
                name="capacity",
                data_type="FLOAT",
                is_required=False,
                comment="Production capacity"
            )
        ]
    )
    print(f"  Created: {site_type.full_name}")

    # Area Level (Level 2)
    area_type = client.create_asset_type(
        catalog_name="unity",
        schema_name="default",
        name="ProductionArea",
        comment="Production area within a site",
        properties=[
            AssetPropertyDef(
                name="area_type",
                data_type="STRING",
                is_required=True,
                comment="Type of production area"
            )
        ]
    )
    print(f"  Created: {area_type.full_name}")

    # Equipment Types (Level 1 and 0)
    motor_type = client.create_asset_type(
        catalog_name="unity",
        schema_name="default",
        name="Motor",
        comment="Industrial motor equipment",
        properties=[
            AssetPropertyDef(
                name="rated_power",
                data_type="FLOAT",
                is_required=True,
                comment="Rated power in kW"
            ),
            AssetPropertyDef(
                name="manufacturer",
                data_type="STRING",
                is_required=False,
                comment="Equipment manufacturer"
            ),
            AssetPropertyDef(
                name="model",
                data_type="STRING",
                is_required=False,
                comment="Model number"
            ),
            AssetPropertyDef(
                name="efficiency",
                data_type="FLOAT",
                is_required=False,
                comment="Motor efficiency percentage"
            )
        ]
    )
    print(f"  Created: {motor_type.full_name}")

    pump_type = client.create_asset_type(
        catalog_name="unity",
        schema_name="default",
        name="Pump",
        comment="Industrial pump equipment",
        properties=[
            AssetPropertyDef(
                name="flow_rate",
                data_type="FLOAT",
                is_required=True,
                comment="Maximum flow rate in m3/h"
            ),
            AssetPropertyDef(
                name="head",
                data_type="FLOAT",
                is_required=True,
                comment="Maximum head in meters"
            ),
            AssetPropertyDef(
                name="manufacturer",
                data_type="STRING",
                is_required=False,
                comment="Equipment manufacturer"
            )
        ]
    )
    print(f"  Created: {pump_type.full_name}")

    sensor_type = client.create_asset_type(
        catalog_name="unity",
        schema_name="default",
        name="Sensor",
        comment="Industrial sensor",
        properties=[
            AssetPropertyDef(
                name="measurement_type",
                data_type="STRING",
                is_required=True,
                comment="Type of measurement (temperature, pressure, flow, etc.)"
            ),
            AssetPropertyDef(
                name="measurement_range",
                data_type="STRING",
                is_required=True,
                comment="Measurement range and units"
            ),
            AssetPropertyDef(
                name="accuracy",
                data_type="FLOAT",
                is_required=False,
                comment="Measurement accuracy percentage"
            )
        ]
    )
    print(f"  Created: {sensor_type.full_name}")


def create_asset_hierarchy(client: AssetClient):
    """Create an example asset hierarchy for a mining operation."""

    print("\nCreating Asset Hierarchy...")

    # Create Enterprise (Rio Tinto example)
    enterprise = client.create_asset(
        catalog_name="unity",
        schema_name="default",
        name="RioTinto",
        asset_type_full_name="unity.default.Enterprise",
        comment="Rio Tinto mining corporation",
        properties={
            "company_name": "Rio Tinto",
            "industry": "Mining"
        }
    )
    print(f"  Created Enterprise: {enterprise.full_name}")

    # Create Site (Iron ore mine)
    site = client.create_asset(
        catalog_name="unity",
        schema_name="default",
        name="PilbaraIronOreMine",
        asset_type_full_name="unity.default.Site",
        parent_asset_full_name=enterprise.full_name,
        comment="Pilbara iron ore mining operation",
        properties={
            "location": "Western Australia",
            "capacity": "330000000"  # 330 million tonnes per year
        }
    )
    print(f"  Created Site: {site.full_name}")

    # Create Production Areas
    crushing_area = client.create_asset(
        catalog_name="unity",
        schema_name="default",
        name="CrushingPlant",
        asset_type_full_name="unity.default.ProductionArea",
        parent_asset_full_name=site.full_name,
        comment="Ore crushing and screening area",
        properties={
            "area_type": "Primary Crushing"
        }
    )
    print(f"  Created Area: {crushing_area.full_name}")

    processing_area = client.create_asset(
        catalog_name="unity",
        schema_name="default",
        name="ProcessingPlant",
        asset_type_full_name="unity.default.ProductionArea",
        parent_asset_full_name=site.full_name,
        comment="Ore processing and beneficiation",
        properties={
            "area_type": "Ore Processing"
        }
    )
    print(f"  Created Area: {processing_area.full_name}")

    # Create Equipment in Crushing Plant
    crusher_motor = client.create_asset(
        catalog_name="unity",
        schema_name="default",
        name="CrusherMotor01",
        asset_type_full_name="unity.default.Motor",
        parent_asset_full_name=crushing_area.full_name,
        comment="Primary crusher drive motor",
        properties={
            "rated_power": "2000",  # 2MW
            "manufacturer": "ABB",
            "model": "AMZ2000",
            "efficiency": "95.5"
        }
    )
    print(f"    Created Motor: {crusher_motor.full_name}")

    conveyor_motor = client.create_asset(
        catalog_name="unity",
        schema_name="default",
        name="ConveyorMotor01",
        asset_type_full_name="unity.default.Motor",
        parent_asset_full_name=crushing_area.full_name,
        comment="Main conveyor belt motor",
        properties={
            "rated_power": "500",  # 500kW
            "manufacturer": "Siemens",
            "model": "1LA9",
            "efficiency": "94.0"
        }
    )
    print(f"    Created Motor: {conveyor_motor.full_name}")

    # Create Equipment in Processing Plant
    slurry_pump = client.create_asset(
        catalog_name="unity",
        schema_name="default",
        name="SlurryPump01",
        asset_type_full_name="unity.default.Pump",
        parent_asset_full_name=processing_area.full_name,
        comment="Main slurry transport pump",
        properties={
            "flow_rate": "1200",  # 1200 m3/h
            "head": "80",  # 80 meters
            "manufacturer": "Warman"
        }
    )
    print(f"    Created Pump: {slurry_pump.full_name}")

    # Create Sensors
    temp_sensor = client.create_asset(
        catalog_name="unity",
        schema_name="default",
        name="TempSensor01",
        asset_type_full_name="unity.default.Sensor",
        parent_asset_full_name=crusher_motor.full_name,
        comment="Motor temperature sensor",
        properties={
            "measurement_type": "Temperature",
            "measurement_range": "0-200°C",
            "accuracy": "0.5"
        }
    )
    print(f"      Created Sensor: {temp_sensor.full_name}")

    vibration_sensor = client.create_asset(
        catalog_name="unity",
        schema_name="default",
        name="VibSensor01",
        asset_type_full_name="unity.default.Sensor",
        parent_asset_full_name=crusher_motor.full_name,
        comment="Motor vibration sensor",
        properties={
            "measurement_type": "Vibration",
            "measurement_range": "0-50 mm/s",
            "accuracy": "1.0"
        }
    )
    print(f"      Created Sensor: {vibration_sensor.full_name}")

    flow_sensor = client.create_asset(
        catalog_name="unity",
        schema_name="default",
        name="FlowSensor01",
        asset_type_full_name="unity.default.Sensor",
        parent_asset_full_name=slurry_pump.full_name,
        comment="Slurry flow rate sensor",
        properties={
            "measurement_type": "Flow",
            "measurement_range": "0-2000 m3/h",
            "accuracy": "2.0"
        }
    )
    print(f"      Created Sensor: {flow_sensor.full_name}")


def query_assets(client: AssetClient):
    """Demonstrate querying and navigating the asset hierarchy."""

    print("\nQuerying Assets...")

    # List all motors
    print("\n  All Motors in the system:")
    assets = client.list_assets(
        catalog_name="unity",
        schema_name="default",
        asset_type_full_name="unity.default.Motor"
    )
    for asset in assets.assets or []:
        print(f"    - {asset.name}: {asset.properties.get('rated_power', 'N/A')} kW")

    # Find high-power motors
    print("\n  High-power motors (>1000 kW):")
    motors = client.find_assets_by_property(
        catalog_name="unity",
        schema_name="default",
        property_name="manufacturer",
        property_value="ABB"
    )
    for motor in motors:
        power = float(motor.properties.get('rated_power', '0'))
        if power > 1000:
            print(f"    - {motor.name}: {power} kW")

    # Get asset hierarchy
    print("\n  Asset Hierarchy for Pilbara Mine:")
    site = client.get_asset("unity.default.PilbaraIronOreMine")
    hierarchy = client.build_asset_hierarchy(site)
    print_hierarchy(hierarchy, indent=4)


def print_hierarchy(node, indent=0):
    """Pretty print asset hierarchy."""
    prefix = " " * indent
    print(f"{prefix}- {node['name']} ({node['type'].split('.')[-1]})")
    for key, value in node['properties'].items():
        print(f"{prefix}    {key}: {value}")
    for child in node['children']:
        print_hierarchy(child, indent + 2)


def cleanup(client: AssetClient):
    """Clean up created assets and types."""

    print("\nCleaning up...")

    # Delete assets (will cascade to children)
    try:
        client.delete_asset("unity.default.RioTinto")
        print("  Deleted asset hierarchy")
    except Exception as e:
        print(f"  Error deleting assets: {e}")

    # Delete asset types
    asset_types = [
        "unity.default.Sensor",
        "unity.default.Pump",
        "unity.default.Motor",
        "unity.default.ProductionArea",
        "unity.default.Site",
        "unity.default.Enterprise"
    ]

    for asset_type in asset_types:
        try:
            client.delete_asset_type(asset_type)
            print(f"  Deleted type: {asset_type}")
        except Exception as e:
            print(f"  Error deleting {asset_type}: {e}")


def main():
    """Main example execution."""

    print("Unity Catalog Asset Management Example")
    print("=" * 50)

    # Initialize client
    client = AssetClient()

    try:
        # Clean up any existing assets first
        print("\nInitial cleanup...")
        cleanup(client)

        # Create asset types
        create_asset_types(client)

        # Create asset hierarchy
        create_asset_hierarchy(client)

        # Query and display assets
        query_assets(client)

        # Clean up
        print("\nFinal cleanup...")
        cleanup(client)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

        # Try to clean up on error
        try:
            cleanup(client)
        except:
            pass


if __name__ == "__main__":
    main()