#!/usr/bin/env python3
"""
Populate IRIS Unity Catalog server with demo asset management data
Based on 01_IRIS_Asset_Management_Demo notebook
"""

import requests
import json
import sys
from datetime import datetime

# Configuration - Cloud Run deployed server
UC_SERVER = "https://iris-uc-server-83839625123.us-central1.run.app"
API_BASE = f"{UC_SERVER}/api/2.1/unity-catalog"
CATALOG = "iris_ot_assets"
SCHEMA = "assets"

def test_connection():
    """Test connection to UC server"""
    try:
        print(f"Connecting to {UC_SERVER} (may take 30-60s for cold start)...")
        response = requests.get(f"{API_BASE}/catalogs", timeout=120)
        print(f"✅ Connected to Unity Catalog server at {UC_SERVER}")
        catalogs = response.json().get('catalogs', [])
        print(f"Available catalogs: {[c['name'] for c in catalogs]}")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def create_catalog():
    """Create the IRIS OT assets catalog"""
    data = {
        "name": CATALOG,
        "comment": "OT Asset Management catalog for Project IRIS"
    }

    response = requests.post(f"{API_BASE}/catalogs", json=data)
    if response.status_code in [200, 201]:
        print(f"✅ Created catalog: {CATALOG}")
        return True
    elif response.status_code == 409:
        print(f"ℹ️  Catalog '{CATALOG}' already exists")
        return True
    else:
        print(f"❌ Failed to create catalog: {response.status_code} - {response.text}")
        return False

def create_schema():
    """Create the assets schema"""
    data = {
        "catalog_name": CATALOG,
        "name": SCHEMA,
        "comment": "Asset definitions and instances"
    }

    response = requests.post(f"{API_BASE}/schemas", json=data)
    if response.status_code in [200, 201]:
        print(f"✅ Created schema: {SCHEMA}")
        return True
    elif response.status_code == 409:
        print(f"ℹ️  Schema '{SCHEMA}' already exists")
        return True
    else:
        print(f"❌ Failed to create schema: {response.status_code} - {response.text}")
        return False

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
    elif response.status_code == 409:
        print(f"ℹ️  Asset type '{name}' already exists")
        return {"name": name}
    else:
        print(f"❌ Failed to create {name}: {response.status_code} - {response.text}")
        return None

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
    elif response.status_code == 409:
        print(f"ℹ️  Asset '{name}' already exists")
        return {"name": name}
    else:
        print(f"❌ Failed to create {name}: {response.status_code} - {response.text}")
        return None

def main():
    """Main execution"""
    print("=" * 70)
    print("IRIS Unity Catalog - Demo Data Population")
    print("=" * 70)
    print()

    # 1. Test connection
    print("Step 1: Testing connection...")
    if not test_connection():
        print("\n❌ Cannot connect to UC server. Exiting.")
        sys.exit(1)
    print()

    # 2. Create catalog
    print("Step 2: Creating catalog...")
    if not create_catalog():
        print("\n❌ Failed to create catalog. Exiting.")
        sys.exit(1)
    print()

    # 3. Create schema
    print("Step 3: Creating schema...")
    if not create_schema():
        print("\n❌ Failed to create schema. Exiting.")
        sys.exit(1)
    print()

    # 4. Create asset types
    print("Step 4: Creating asset types...")
    print("-" * 70)

    # Industrial Motor type
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
                "data_type": "INTEGER",
                "is_required": True,
                "comment": "Rated speed in RPM"
            },
            {
                "name": "voltage",
                "data_type": "INTEGER",
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

    # Centrifugal Pump type
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

    # Industrial Sensor type
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

    print()

    # 5. Create asset hierarchy
    print("Step 5: Creating asset hierarchy...")
    print("-" * 70)

    # Create plant
    plant = create_asset(
        name="ManufacturingPlant01",
        asset_type_name="IndustrialMotor",  # Using as placeholder
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

    # Create pumps
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

    # Create motor
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

    print()

    # 6. Summary
    print("=" * 70)
    print("✅ POPULATION COMPLETE")
    print("=" * 70)
    print()
    print("Summary:")
    print(f"  • Catalog: {CATALOG}")
    print(f"  • Schema: {SCHEMA}")
    print(f"  • Asset Types: 3 (IndustrialMotor, CentrifugalPump, IndustrialSensor)")
    print(f"  • Assets: 7 (Plant → Pump Station → Pumps → Motor & Sensors)")
    print()
    print("Verification:")
    print(f"  • Catalogs: curl {UC_SERVER}/api/2.1/unity-catalog/catalogs")
    print(f"  • Assets: curl '{UC_SERVER}/api/2.1/unity-catalog/assets?catalog_name={CATALOG}&schema_name={SCHEMA}'")
    print()

if __name__ == "__main__":
    main()
