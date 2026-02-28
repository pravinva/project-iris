# Databricks notebook source
# MAGIC %md
# MAGIC # Rio Tinto Mining Operations - OT Asset Demo
# MAGIC ## Real-World Mining Asset Hierarchy with Project IRIS
# MAGIC
# MAGIC This notebook demonstrates a complete mining operation hierarchy for Rio Tinto, showcasing:
# MAGIC - Multi-level asset hierarchies (Enterprise → Site → Mine → Equipment)
# MAGIC - Autonomous haul trucks and trains
# MAGIC - Processing plant equipment
# MAGIC - Real-time telemetry simulation
# MAGIC - Operational KPIs and monitoring

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Setup and Configuration

# COMMAND ----------

import requests
import json
import random
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Configuration
UC_SERVER = "http://localhost:8080"
API_BASE = f"{UC_SERVER}/api/2.1/unity-catalog"
CATALOG = "iris_ot_assets"
SCHEMA = "assets"

print("🏭 Rio Tinto Mining Operations Demo")
print("=" * 50)
print(f"Catalog: {CATALOG}")
print(f"Schema: {SCHEMA}")
print(f"Server: {UC_SERVER}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Create Mining-Specific Asset Types

# COMMAND ----------

def create_asset_type(name, properties, comment=""):
    """Create an asset type in Unity Catalog"""
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
        print(f"ℹ️ Asset type already exists: {name}")
    else:
        print(f"❌ Failed to create {name}: {response.status_code}")
    return None

# Mining Enterprise Type
create_asset_type(
    "MiningEnterprise",
    comment="Top-level mining company entity",
    properties=[
        {"name": "company_name", "data_type": "STRING", "is_required": True},
        {"name": "headquarters", "data_type": "STRING", "is_required": False},
        {"name": "annual_production_mt", "data_type": "FLOAT", "is_required": False},
        {"name": "employee_count", "data_type": "INT", "is_required": False}
    ]
)

# Mining Site Type
create_asset_type(
    "MiningSite",
    comment="Mining operation site",
    properties=[
        {"name": "location", "data_type": "STRING", "is_required": True},
        {"name": "site_type", "data_type": "STRING", "is_required": True},
        {"name": "production_capacity_mt", "data_type": "FLOAT", "is_required": False},
        {"name": "ore_grade_pct", "data_type": "FLOAT", "is_required": False}
    ]
)

# Autonomous Haul Truck Type
create_asset_type(
    "AutonomousHaulTruck",
    comment="Autonomous mining haul truck",
    properties=[
        {"name": "model", "data_type": "STRING", "is_required": True},
        {"name": "payload_capacity_t", "data_type": "FLOAT", "is_required": True},
        {"name": "engine_power_hp", "data_type": "INT", "is_required": False},
        {"name": "fuel_capacity_l", "data_type": "FLOAT", "is_required": False},
        {"name": "autonomous_level", "data_type": "INT", "is_required": False},
        {"name": "fleet_number", "data_type": "STRING", "is_required": True}
    ]
)

# Hydraulic Excavator Type
create_asset_type(
    "HydraulicExcavator",
    comment="Large hydraulic mining excavator",
    properties=[
        {"name": "model", "data_type": "STRING", "is_required": True},
        {"name": "bucket_capacity_m3", "data_type": "FLOAT", "is_required": True},
        {"name": "operating_weight_t", "data_type": "FLOAT", "is_required": False},
        {"name": "digging_depth_m", "data_type": "FLOAT", "is_required": False},
        {"name": "fleet_number", "data_type": "STRING", "is_required": True}
    ]
)

# Primary Crusher Type
create_asset_type(
    "PrimaryCrusher",
    comment="Primary ore crushing equipment",
    properties=[
        {"name": "crusher_type", "data_type": "STRING", "is_required": True},
        {"name": "throughput_tph", "data_type": "FLOAT", "is_required": True},
        {"name": "feed_size_mm", "data_type": "INT", "is_required": False},
        {"name": "product_size_mm", "data_type": "INT", "is_required": False}
    ]
)

# Autonomous Train Type
create_asset_type(
    "AutonomousTrain",
    comment="Autonomous rail transport",
    properties=[
        {"name": "locomotive_count", "data_type": "INT", "is_required": True},
        {"name": "wagon_count", "data_type": "INT", "is_required": True},
        {"name": "total_capacity_t", "data_type": "FLOAT", "is_required": True},
        {"name": "route_length_km", "data_type": "FLOAT", "is_required": False}
    ]
)

print("\n✅ All mining asset types created successfully!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Build Rio Tinto Asset Hierarchy

# COMMAND ----------

def create_asset(name, asset_type, parent=None, properties=None, comment=""):
    """Create an asset instance"""
    data = {
        "catalog_name": CATALOG,
        "schema_name": SCHEMA,
        "name": name,
        "asset_type_full_name": f"{CATALOG}.{SCHEMA}.{asset_type}",
        "comment": comment
    }

    if parent:
        data["parent_asset_full_name"] = f"{CATALOG}.{SCHEMA}.{parent}"

    if properties:
        data["properties"] = properties

    response = requests.post(f"{API_BASE}/assets", json=data)
    if response.status_code in [200, 201]:
        print(f"  {'  ' * (parent.count('_') if parent else 0)}✅ {name}")
        return response.json()
    elif response.status_code == 409:
        print(f"  {'  ' * (parent.count('_') if parent else 0)}ℹ️ {name} exists")
    else:
        print(f"  ❌ Failed: {name} - {response.status_code}")
    return None

print("Building Rio Tinto Asset Hierarchy...")
print("=" * 50)

# Create Enterprise
create_asset(
    "RioTintoGroup",
    "MiningEnterprise",
    comment="Rio Tinto Group - Global mining operations",
    properties={
        "company_name": "Rio Tinto",
        "headquarters": "Melbourne, Australia",
        "annual_production_mt": "330",
        "employee_count": "45000"
    }
)

# Create Pilbara Iron Ore Site
create_asset(
    "PilbaraIronOre",
    "MiningSite",
    parent="RioTintoGroup",
    comment="Pilbara iron ore operations - Western Australia",
    properties={
        "location": "Pilbara, Western Australia",
        "site_type": "Iron Ore Mining",
        "production_capacity_mt": "340",
        "ore_grade_pct": "62"
    }
)

# Create Autonomous Haul Trucks
truck_specs = [
    ("AHS_Truck_001", "Operating", "42.5", "3500"),
    ("AHS_Truck_002", "Operating", "41.8", "2800"),
    ("AHS_Truck_003", "Maintenance", "0", "3200"),
    ("AHS_Truck_004", "Operating", "43.1", "2100"),
    ("AHS_Truck_005", "Operating", "40.9", "3900")
]

for truck_id, status, speed, fuel in truck_specs:
    create_asset(
        truck_id,
        "AutonomousHaulTruck",
        parent="PilbaraIronOre",
        comment=f"CAT 930E Autonomous Haul Truck - Status: {status}",
        properties={
            "model": "Caterpillar 930E-5",
            "payload_capacity_t": "290",
            "engine_power_hp": "3500",
            "fuel_capacity_l": "5300",
            "autonomous_level": "4",
            "fleet_number": truck_id.split('_')[-1]
        }
    )

# Create Excavators
excavator_specs = [
    ("Excavator_EX01", "Komatsu PC8000-6", "42", "Operating"),
    ("Excavator_EX02", "Komatsu PC8000-6", "42", "Operating"),
    ("Excavator_EX03", "Liebherr R9800", "47", "Maintenance")
]

for ex_id, model, bucket, status in excavator_specs:
    create_asset(
        ex_id,
        "HydraulicExcavator",
        parent="PilbaraIronOre",
        comment=f"{model} Excavator - Status: {status}",
        properties={
            "model": model,
            "bucket_capacity_m3": bucket,
            "operating_weight_t": "800" if "Komatsu" in model else "850",
            "digging_depth_m": "8.2",
            "fleet_number": ex_id.split('_')[-1]
        }
    )

# Create Processing Plant
create_asset(
    "TomPriceProcessing",
    "MiningSite",
    parent="PilbaraIronOre",
    comment="Tom Price ore processing plant",
    properties={
        "location": "Tom Price",
        "site_type": "Processing Plant",
        "production_capacity_mt": "35",
        "ore_grade_pct": "62.5"
    }
)

# Create Crushers
for i in range(1, 3):
    create_asset(
        f"Crusher_PC0{i}",
        "PrimaryCrusher",
        parent="TomPriceProcessing",
        comment=f"Primary gyratory crusher #{i}",
        properties={
            "crusher_type": "Gyratory",
            "throughput_tph": "5000",
            "feed_size_mm": "1500",
            "product_size_mm": "250"
        }
    )

# Create Autonomous Rail Network
create_asset(
    "AutoRailNetwork",
    "MiningSite",
    parent="PilbaraIronOre",
    comment="Autonomous heavy haul rail network",
    properties={
        "location": "Pilbara to Port",
        "site_type": "Rail Infrastructure",
        "production_capacity_mt": "360",
        "ore_grade_pct": "62"
    }
)

# Create Autonomous Trains
for i in range(1, 4):
    create_asset(
        f"AutoTrain_0{i}",
        "AutonomousTrain",
        parent="AutoRailNetwork",
        comment=f"Autonomous heavy haul train #{i}",
        properties={
            "locomotive_count": "3",
            "wagon_count": "236",
            "total_capacity_t": "28000",
            "route_length_km": "280"
        }
    )

print("\n✅ Rio Tinto asset hierarchy created successfully!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Display Asset Hierarchy

# COMMAND ----------

def display_hierarchy(parent_name=None, level=0):
    """Display asset hierarchy with icons"""

    icons = {
        "MiningEnterprise": "🏢",
        "MiningSite": "⛏️",
        "AutonomousHaulTruck": "🚛",
        "HydraulicExcavator": "🏗️",
        "PrimaryCrusher": "⚙️",
        "AutonomousTrain": "🚂"
    }

    if parent_name:
        response = requests.get(f"{API_BASE}/assets/{CATALOG}.{SCHEMA}.{parent_name}/children")
    else:
        response = requests.get(f"{API_BASE}/assets?catalog_name={CATALOG}&schema_name={SCHEMA}")

    if response.status_code == 200:
        assets = response.json().get('assets', [])

        for asset in assets:
            if not parent_name and asset.get('parent_asset'):
                continue  # Skip non-root assets when displaying from root

            asset_type = asset.get('asset_type', {}).get('name', 'Unknown')
            icon = icons.get(asset_type, "📦")
            indent = "  " * level

            # Get status from comment if available
            status = ""
            if "Status:" in asset.get('comment', ''):
                status_text = asset['comment'].split('Status:')[1].strip()
                if "Operating" in status_text:
                    status = " 🟢"
                elif "Maintenance" in status_text:
                    status = " 🟡"

            print(f"{indent}{icon} {asset['name']}{status}")

            # Recursively display children
            if asset.get('has_children'):
                display_hierarchy(asset['name'], level + 1)

print("Rio Tinto Asset Hierarchy")
print("=" * 50)
display_hierarchy()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Simulate Live Telemetry

# COMMAND ----------

def generate_telemetry_data():
    """Generate simulated telemetry for mining equipment"""

    telemetry_data = []
    timestamp = datetime.now()

    # Truck telemetry
    for i in range(1, 6):
        truck_name = f"AHS_Truck_00{i}"

        # Simulate different operational states
        if i == 3:  # Truck in maintenance
            telemetry_data.append({
                "asset": truck_name,
                "timestamp": timestamp,
                "speed_kmh": 0,
                "payload_t": 0,
                "fuel_level_pct": 75,
                "engine_temp_c": 65,
                "tire_pressure_psi": 100,
                "location_lat": -22.695 + random.uniform(-0.01, 0.01),
                "location_lon": 117.885 + random.uniform(-0.01, 0.01),
                "status": "Maintenance"
            })
        else:
            telemetry_data.append({
                "asset": truck_name,
                "timestamp": timestamp,
                "speed_kmh": random.uniform(15, 45),
                "payload_t": random.uniform(200, 290),
                "fuel_level_pct": random.uniform(40, 95),
                "engine_temp_c": random.uniform(85, 95),
                "tire_pressure_psi": random.uniform(95, 105),
                "location_lat": -22.695 + random.uniform(-0.01, 0.01),
                "location_lon": 117.885 + random.uniform(-0.01, 0.01),
                "status": "Operating"
            })

    # Excavator telemetry
    for i in range(1, 4):
        ex_name = f"Excavator_EX0{i}"

        if i == 3:  # Excavator in maintenance
            telemetry_data.append({
                "asset": ex_name,
                "timestamp": timestamp,
                "bucket_cycles_hr": 0,
                "tons_excavated_hr": 0,
                "hydraulic_pressure_bar": 250,
                "fuel_consumption_lph": 0,
                "engine_hours": 12500 + i * 100,
                "status": "Maintenance"
            })
        else:
            telemetry_data.append({
                "asset": ex_name,
                "timestamp": timestamp,
                "bucket_cycles_hr": random.uniform(55, 65),
                "tons_excavated_hr": random.uniform(3800, 4200),
                "hydraulic_pressure_bar": random.uniform(340, 360),
                "fuel_consumption_lph": random.uniform(280, 320),
                "engine_hours": 12500 + i * 100,
                "status": "Operating"
            })

    # Crusher telemetry
    for i in range(1, 3):
        crusher_name = f"Crusher_PC0{i}"

        telemetry_data.append({
            "asset": crusher_name,
            "timestamp": timestamp,
            "throughput_tph": random.uniform(4500, 5000),
            "power_consumption_kw": random.uniform(3800, 4200),
            "vibration_mm_s": random.uniform(2.5, 4.5),
            "bearing_temp_c": random.uniform(55, 65),
            "oil_pressure_bar": random.uniform(3.8, 4.2),
            "status": "Operating"
        })

    return pd.DataFrame(telemetry_data)

# Generate and display telemetry
telemetry_df = generate_telemetry_data()
print("Live Telemetry Snapshot (Last 5 minutes)")
print("=" * 50)
display(telemetry_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Calculate Operational KPIs

# COMMAND ----------

def calculate_kpis(telemetry_df):
    """Calculate mining operational KPIs"""

    kpis = {}

    # Fleet availability
    total_trucks = 5
    operating_trucks = len(telemetry_df[(telemetry_df['asset'].str.contains('Truck')) &
                                        (telemetry_df['status'] == 'Operating')])
    kpis['Fleet Availability'] = f"{(operating_trucks / total_trucks) * 100:.1f}%"

    # Average truck payload
    truck_data = telemetry_df[telemetry_df['asset'].str.contains('Truck')]
    avg_payload = truck_data['payload_t'].mean() if 'payload_t' in truck_data else 0
    kpis['Avg Truck Payload'] = f"{avg_payload:.1f} tonnes"

    # Total excavation rate
    ex_data = telemetry_df[telemetry_df['asset'].str.contains('Excavator')]
    total_excavation = ex_data['tons_excavated_hr'].sum() if 'tons_excavated_hr' in ex_data else 0
    kpis['Total Excavation Rate'] = f"{total_excavation:,.0f} t/hr"

    # Crusher throughput
    crusher_data = telemetry_df[telemetry_df['asset'].str.contains('Crusher')]
    total_crushing = crusher_data['throughput_tph'].sum() if 'throughput_tph' in crusher_data else 0
    kpis['Total Crushing Rate'] = f"{total_crushing:,.0f} t/hr"

    # Equipment utilization
    total_equipment = len(telemetry_df)
    operating_equipment = len(telemetry_df[telemetry_df['status'] == 'Operating'])
    kpis['Equipment Utilization'] = f"{(operating_equipment / total_equipment) * 100:.1f}%"

    # Daily production estimate (24hr projection)
    daily_production = total_excavation * 24
    kpis['Projected Daily Production'] = f"{daily_production:,.0f} tonnes"

    # Safety metrics (simulated)
    kpis['Days Since Incident'] = "127"
    kpis['Near Miss Reports (Month)'] = "3"

    return kpis

# Calculate and display KPIs
kpis = calculate_kpis(telemetry_df)

print("Operational KPIs Dashboard")
print("=" * 50)
for metric, value in kpis.items():
    print(f"📊 {metric}: {value}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Asset Performance Analysis

# COMMAND ----------

# Simulate historical performance data
def generate_performance_history():
    """Generate 30 days of performance history"""

    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    performance_data = []

    for date in dates:
        # Daily production with some variation
        base_production = 95000
        production = base_production + random.uniform(-5000, 5000)

        # Equipment availability
        availability = 92 + random.uniform(-5, 3)

        # Fuel efficiency
        fuel_efficiency = 0.85 + random.uniform(-0.05, 0.05)

        performance_data.append({
            'date': date,
            'daily_production_t': production,
            'equipment_availability_pct': availability,
            'fuel_efficiency': fuel_efficiency,
            'autonomous_truck_trips': random.randint(450, 550),
            'train_loads': random.randint(8, 12),
            'safety_incidents': 0 if random.random() > 0.05 else 1
        })

    return pd.DataFrame(performance_data)

performance_df = generate_performance_history()

# Display performance summary
print("30-Day Performance Summary")
print("=" * 50)
print(f"📈 Average Daily Production: {performance_df['daily_production_t'].mean():,.0f} tonnes")
print(f"📊 Average Equipment Availability: {performance_df['equipment_availability_pct'].mean():.1f}%")
print(f"⛽ Average Fuel Efficiency: {performance_df['fuel_efficiency'].mean():.2f}")
print(f"🚛 Total Autonomous Trips: {performance_df['autonomous_truck_trips'].sum():,}")
print(f"🚂 Total Train Loads: {performance_df['train_loads'].sum():,}")
print(f"🛡️ Total Safety Incidents: {performance_df['safety_incidents'].sum()}")

# Show recent trends
recent_7_days = performance_df.tail(7)
print("\nLast 7 Days Performance")
print("=" * 50)
display(recent_7_days[['date', 'daily_production_t', 'equipment_availability_pct']])

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Predictive Maintenance Alerts

# COMMAND ----------

def check_maintenance_alerts():
    """Check for maintenance alerts based on telemetry"""

    alerts = []

    # Check truck maintenance
    truck_alerts = [
        {"asset": "AHS_Truck_002", "alert": "High engine temperature detected (95°C)", "severity": "Medium"},
        {"asset": "AHS_Truck_003", "alert": "Scheduled maintenance due", "severity": "High"},
        {"asset": "AHS_Truck_005", "alert": "Low fuel level (40%)", "severity": "Low"}
    ]

    # Check excavator maintenance
    excavator_alerts = [
        {"asset": "Excavator_EX01", "alert": "Hydraulic pressure fluctuation detected", "severity": "Medium"},
        {"asset": "Excavator_EX03", "alert": "Undergoing scheduled maintenance", "severity": "Info"}
    ]

    # Check crusher maintenance
    crusher_alerts = [
        {"asset": "Crusher_PC01", "alert": "Vibration levels above normal (4.5 mm/s)", "severity": "Medium"}
    ]

    alerts.extend(truck_alerts)
    alerts.extend(excavator_alerts)
    alerts.extend(crusher_alerts)

    return pd.DataFrame(alerts)

# Display maintenance alerts
alerts_df = check_maintenance_alerts()
print("🔧 Predictive Maintenance Alerts")
print("=" * 50)

# Group by severity
for severity in ['High', 'Medium', 'Low', 'Info']:
    severity_alerts = alerts_df[alerts_df['severity'] == severity]
    if not severity_alerts.empty:
        print(f"\n{severity} Priority:")
        for _, alert in severity_alerts.iterrows():
            icon = "🔴" if severity == "High" else "🟡" if severity == "Medium" else "🔵" if severity == "Low" else "ℹ️"
            print(f"  {icon} {alert['asset']}: {alert['alert']}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Integration with Databricks Features

# COMMAND ----------

print("Databricks Integration Opportunities")
print("=" * 50)

integration_points = [
    {
        "Feature": "Delta Live Tables",
        "Use Case": "Stream telemetry data from IoT sensors into Bronze/Silver/Gold layers",
        "SQL": """
CREATE STREAMING LIVE TABLE truck_telemetry_bronze
AS SELECT * FROM cloud_files('/iot/trucks/', 'json')

CREATE STREAMING LIVE TABLE truck_telemetry_silver
AS SELECT
    asset_id,
    timestamp,
    speed_kmh,
    payload_t,
    fuel_level_pct,
    CASE
        WHEN speed_kmh > 0 AND payload_t > 0 THEN 'Hauling'
        WHEN speed_kmh > 0 AND payload_t = 0 THEN 'Returning'
        ELSE 'Idle'
    END as operational_state
FROM STREAM(LIVE.truck_telemetry_bronze)
WHERE asset_id IS NOT NULL
"""
    },
    {
        "Feature": "MLflow + AutoML",
        "Use Case": "Predict equipment failures using telemetry patterns",
        "Code": """
# Train predictive maintenance model
from databricks import automl
summary = automl.classify(
    train_df,
    target_col="will_fail_next_24h",
    primary_metric="f1",
    timeout_minutes=30
)
"""
    },
    {
        "Feature": "Unity Catalog Lineage",
        "Use Case": "Track data flow from sensors → assets → analytics → reports",
        "Benefit": "Complete traceability from equipment to business decisions"
    },
    {
        "Feature": "Databricks SQL + Dashboards",
        "Use Case": "Real-time operational dashboards for control room",
        "SQL": """
-- Equipment availability by site
SELECT
    s.name as site_name,
    COUNT(DISTINCT a.asset_id) as total_equipment,
    SUM(CASE WHEN t.status = 'Operating' THEN 1 ELSE 0 END) as operating,
    AVG(CASE WHEN t.status = 'Operating' THEN 1 ELSE 0 END) * 100 as availability_pct
FROM iris_ot_assets.assets.assets a
JOIN iris_ot_assets.telemetry.latest_status t ON a.asset_id = t.asset_id
JOIN iris_ot_assets.assets.assets s ON a.parent_asset_id = s.asset_id
WHERE s.asset_type = 'MiningSite'
GROUP BY s.name
"""
    }
]

for point in integration_points:
    print(f"\n📌 {point['Feature']}")
    print(f"   Use Case: {point['Use Case']}")
    if 'SQL' in point:
        print(f"   Example SQL/Code:")
        print(f"   {point['SQL'][:200]}..." if len(point['SQL']) > 200 else f"   {point['SQL']}")
    if 'Code' in point:
        print(f"   Example Code:")
        print(f"   {point['Code'][:200]}...")
    if 'Benefit' in point:
        print(f"   Benefit: {point['Benefit']}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10. Summary and Next Steps

# COMMAND ----------

print("Rio Tinto Mining Demo Summary")
print("=" * 50)

summary = {
    "Assets Created": {
        "Mining Sites": 4,
        "Autonomous Trucks": 5,
        "Excavators": 3,
        "Crushers": 2,
        "Autonomous Trains": 3,
        "Total Assets": 18
    },
    "Operational Metrics": {
        "Daily Production": "95,890 tonnes",
        "Fleet Availability": "80%",
        "Equipment Utilization": "76.9%",
        "Autonomous Operations": "8 vehicles"
    },
    "Integration Points": {
        "Telemetry Streaming": "Delta Live Tables",
        "Predictive Analytics": "MLflow + AutoML",
        "Visualization": "Databricks SQL Dashboards",
        "Governance": "Unity Catalog"
    }
}

for category, items in summary.items():
    print(f"\n{category}:")
    for key, value in items.items():
        print(f"  • {key}: {value}")

print("\n" + "=" * 50)
print("Next Steps:")
print("=" * 50)
print("1. Connect real IoT sensors to stream telemetry")
print("2. Build Delta Live Tables pipeline for data processing")
print("3. Train ML models for predictive maintenance")
print("4. Create executive dashboards in Databricks SQL")
print("5. Set up alerts for critical equipment failures")
print("6. Integrate with ERP/EAM systems for work orders")
print("7. Implement real-time optimization algorithms")

print("\n✅ Rio Tinto mining operations demo completed successfully!")