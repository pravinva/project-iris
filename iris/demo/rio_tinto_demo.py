#!/usr/bin/env python3
"""
Rio Tinto Mining Operations Demo for Unity Catalog Asset Management

This demo showcases Unity Catalog's OT asset management capabilities using
a real-world scenario from Rio Tinto's Pilbara iron ore operations.

The demo creates:
1. ISA-95 compliant asset hierarchy
2. Mining equipment with real-time telemetry
3. Operational dashboards and KPIs
4. Integration with lakehouse tables for analytics
"""

import json
import time
import random
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../clients/python/src'))

from unitycatalog.client.asset_client import AssetClient
from unitycatalog.client.models import AssetPropertyDef
from unitycatalog.client import ApiClient, Configuration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RioTintoDemoBuilder:
    """Builds and demonstrates Rio Tinto mining asset hierarchy"""

    def __init__(self, uc_client: AssetClient, catalog: str = "unity", schema: str = "default"):
        self.client = uc_client
        self.catalog = catalog
        self.schema = schema
        self.created_assets = []
        self.created_types = []

    def create_asset_types(self):
        """Create asset types for mining operations"""
        logger.info("Creating mining asset types...")

        # Enterprise Level
        enterprise_type = self.client.create_asset_type(
            catalog_name=self.catalog,
            schema_name=self.schema,
            name="MiningEnterprise",
            comment="Top-level mining corporation",
            properties=[
                AssetPropertyDef("company_name", "STRING", True, "Company name"),
                AssetPropertyDef("asx_code", "STRING", False, "Stock exchange code"),
                AssetPropertyDef("market_cap", "FLOAT", False, "Market capitalization in billions"),
                AssetPropertyDef("annual_revenue", "FLOAT", False, "Annual revenue in billions"),
                AssetPropertyDef("employee_count", "INT", False, "Total employees worldwide")
            ]
        )
        self.created_types.append(enterprise_type.full_name)
        logger.info(f"Created: {enterprise_type.full_name}")

        # Mining Site
        site_type = self.client.create_asset_type(
            catalog_name=self.catalog,
            schema_name=self.schema,
            name="MiningSite",
            comment="Mining operation site",
            properties=[
                AssetPropertyDef("location", "STRING", True, "Geographic location"),
                AssetPropertyDef("mine_type", "STRING", True, "Type of mine (Open Pit, Underground, etc)"),
                AssetPropertyDef("ore_type", "STRING", True, "Type of ore mined"),
                AssetPropertyDef("ore_grade", "FLOAT", False, "Average ore grade (%)"),
                AssetPropertyDef("annual_production", "FLOAT", False, "Annual production in tonnes"),
                AssetPropertyDef("reserves", "FLOAT", False, "Proven reserves in million tonnes"),
                AssetPropertyDef("latitude", "FLOAT", False, "GPS latitude"),
                AssetPropertyDef("longitude", "FLOAT", False, "GPS longitude")
            ]
        )
        self.created_types.append(site_type.full_name)

        # Haul Truck
        truck_type = self.client.create_asset_type(
            catalog_name=self.catalog,
            schema_name=self.schema,
            name="AutonomousHaulTruck",
            comment="Autonomous mining haul truck",
            properties=[
                AssetPropertyDef("serial_number", "STRING", True, "Equipment serial number"),
                AssetPropertyDef("manufacturer", "STRING", True, "Manufacturer name"),
                AssetPropertyDef("model", "STRING", True, "Equipment model"),
                AssetPropertyDef("payload_capacity", "FLOAT", True, "Payload capacity in tonnes"),
                AssetPropertyDef("fuel_capacity", "FLOAT", False, "Fuel tank capacity in liters"),
                AssetPropertyDef("engine_hours", "FLOAT", False, "Total engine running hours"),
                AssetPropertyDef("autonomous_mode", "BOOLEAN", False, "Autonomous operation enabled"),
                AssetPropertyDef("current_speed", "FLOAT", False, "Current speed in km/h"),
                AssetPropertyDef("current_load", "FLOAT", False, "Current load in tonnes"),
                AssetPropertyDef("fuel_level", "FLOAT", False, "Current fuel level (%)"),
                AssetPropertyDef("tire_pressure_fl", "FLOAT", False, "Front left tire pressure (psi)"),
                AssetPropertyDef("tire_pressure_fr", "FLOAT", False, "Front right tire pressure (psi)"),
                AssetPropertyDef("tire_pressure_rl", "FLOAT", False, "Rear left tire pressure (psi)"),
                AssetPropertyDef("tire_pressure_rr", "FLOAT", False, "Rear right tire pressure (psi)"),
                AssetPropertyDef("status", "STRING", False, "Operational status")
            ]
        )
        self.created_types.append(truck_type.full_name)

        # Excavator
        excavator_type = self.client.create_asset_type(
            catalog_name=self.catalog,
            schema_name=self.schema,
            name="HydraulicExcavator",
            comment="Hydraulic mining excavator",
            properties=[
                AssetPropertyDef("serial_number", "STRING", True, "Equipment serial number"),
                AssetPropertyDef("manufacturer", "STRING", True, "Manufacturer name"),
                AssetPropertyDef("model", "STRING", True, "Equipment model"),
                AssetPropertyDef("bucket_capacity", "FLOAT", True, "Bucket capacity in cubic meters"),
                AssetPropertyDef("operating_weight", "FLOAT", False, "Operating weight in tonnes"),
                AssetPropertyDef("max_dig_depth", "FLOAT", False, "Maximum digging depth in meters"),
                AssetPropertyDef("engine_hours", "FLOAT", False, "Total engine hours"),
                AssetPropertyDef("hydraulic_pressure", "FLOAT", False, "Hydraulic system pressure (bar)"),
                AssetPropertyDef("swing_angle", "FLOAT", False, "Current swing angle (degrees)"),
                AssetPropertyDef("boom_angle", "FLOAT", False, "Boom angle (degrees)"),
                AssetPropertyDef("bucket_fill", "FLOAT", False, "Current bucket fill (%)"),
                AssetPropertyDef("cycles_today", "INT", False, "Loading cycles completed today"),
                AssetPropertyDef("status", "STRING", False, "Operational status")
            ]
        )
        self.created_types.append(excavator_type.full_name)

        # Crusher
        crusher_type = self.client.create_asset_type(
            catalog_name=self.catalog,
            schema_name=self.schema,
            name="PrimaryCrusher",
            comment="Primary ore crusher",
            properties=[
                AssetPropertyDef("serial_number", "STRING", True, "Equipment serial number"),
                AssetPropertyDef("manufacturer", "STRING", True, "Manufacturer name"),
                AssetPropertyDef("throughput_capacity", "FLOAT", True, "Max throughput tonnes/hour"),
                AssetPropertyDef("power_rating", "FLOAT", True, "Power rating in MW"),
                AssetPropertyDef("input_size", "FLOAT", False, "Maximum input size in mm"),
                AssetPropertyDef("output_size", "FLOAT", False, "Output size in mm"),
                AssetPropertyDef("current_throughput", "FLOAT", False, "Current throughput tonnes/hour"),
                AssetPropertyDef("power_consumption", "FLOAT", False, "Current power draw in MW"),
                AssetPropertyDef("vibration_level", "FLOAT", False, "Vibration level mm/s"),
                AssetPropertyDef("bearing_temp", "FLOAT", False, "Main bearing temperature °C"),
                AssetPropertyDef("oil_pressure", "FLOAT", False, "Hydraulic oil pressure bar"),
                AssetPropertyDef("tonnes_processed_today", "FLOAT", False, "Tonnes processed today"),
                AssetPropertyDef("status", "STRING", False, "Operational status")
            ]
        )
        self.created_types.append(crusher_type.full_name)

        # Processing Plant
        plant_type = self.client.create_asset_type(
            catalog_name=self.catalog,
            schema_name=self.schema,
            name="ProcessingPlant",
            comment="Ore processing plant area",
            properties=[
                AssetPropertyDef("plant_capacity", "FLOAT", True, "Annual capacity in tonnes"),
                AssetPropertyDef("crusher_count", "INT", False, "Number of crushers"),
                AssetPropertyDef("conveyor_length", "FLOAT", False, "Total conveyor length in km"),
                AssetPropertyDef("water_usage", "FLOAT", False, "Water usage m³/hour"),
                AssetPropertyDef("power_usage", "FLOAT", False, "Total power consumption MW"),
                AssetPropertyDef("daily_production", "FLOAT", False, "Today's production tonnes")
            ]
        )
        self.created_types.append(plant_type.full_name)

        # Rail Operations
        rail_type = self.client.create_asset_type(
            catalog_name=self.catalog,
            schema_name=self.schema,
            name="RailNetwork",
            comment="Autonomous rail network",
            properties=[
                AssetPropertyDef("network_length", "FLOAT", True, "Total track length in km"),
                AssetPropertyDef("locomotive_count", "INT", True, "Number of locomotives"),
                AssetPropertyDef("autonomous_trains", "BOOLEAN", False, "Autonomous operation enabled"),
                AssetPropertyDef("daily_capacity", "FLOAT", False, "Daily transport capacity tonnes"),
                AssetPropertyDef("trains_in_motion", "INT", False, "Current trains running"),
                AssetPropertyDef("average_speed", "FLOAT", False, "Average network speed km/h")
            ]
        )
        self.created_types.append(rail_type.full_name)

        logger.info(f"Created {len(self.created_types)} asset types")

    def create_asset_hierarchy(self):
        """Create the complete Rio Tinto asset hierarchy"""
        logger.info("Creating Rio Tinto asset hierarchy...")

        # Rio Tinto Enterprise
        rio_tinto = self.client.create_asset(
            catalog_name=self.catalog,
            schema_name=self.schema,
            name="RioTintoGroup",
            asset_type_full_name=f"{self.catalog}.{self.schema}.MiningEnterprise",
            comment="Rio Tinto Group - Global mining corporation",
            properties={
                "company_name": "Rio Tinto Group",
                "asx_code": "RIO",
                "market_cap": "110.5",
                "annual_revenue": "63.5",
                "employee_count": "54000"
            }
        )
        self.created_assets.append(rio_tinto)
        logger.info(f"Created enterprise: {rio_tinto.name}")

        # Pilbara Iron Ore Operations
        pilbara = self.client.create_asset(
            catalog_name=self.catalog,
            schema_name=self.schema,
            name="PilbaraIronOre",
            asset_type_full_name=f"{self.catalog}.{self.schema}.MiningSite",
            parent_asset_full_name=rio_tinto.full_name,
            comment="Pilbara iron ore operations - World's largest iron ore mining complex",
            properties={
                "location": "Pilbara, Western Australia",
                "mine_type": "Open Pit",
                "ore_type": "Iron Ore",
                "ore_grade": "62.5",
                "annual_production": "330000000",
                "reserves": "2800",
                "latitude": "-22.5929",
                "longitude": "118.1678"
            }
        )
        self.created_assets.append(pilbara)
        logger.info(f"Created site: {pilbara.name}")

        # Processing Plant
        processing = self.client.create_asset(
            catalog_name=self.catalog,
            schema_name=self.schema,
            name="TomPriceProcessing",
            asset_type_full_name=f"{self.catalog}.{self.schema}.ProcessingPlant",
            parent_asset_full_name=pilbara.full_name,
            comment="Tom Price ore processing and crushing plant",
            properties={
                "plant_capacity": "35000000",
                "crusher_count": "4",
                "conveyor_length": "28.5",
                "water_usage": "1200",
                "power_usage": "45",
                "daily_production": "95890"
            }
        )
        self.created_assets.append(processing)

        # Create Autonomous Haul Trucks
        for i in range(1, 6):
            truck = self.client.create_asset(
                catalog_name=self.catalog,
                schema_name=self.schema,
                name=f"AHS_Truck_{i:03d}",
                asset_type_full_name=f"{self.catalog}.{self.schema}.AutonomousHaulTruck",
                parent_asset_full_name=pilbara.full_name,
                comment=f"Autonomous Haul System Truck {i:03d}",
                properties={
                    "serial_number": f"CAT-930E-2024{i:03d}",
                    "manufacturer": "Caterpillar",
                    "model": "930E-5",
                    "payload_capacity": "290",
                    "fuel_capacity": "4540",
                    "engine_hours": str(1000 + i * 250),
                    "autonomous_mode": "true",
                    "current_speed": str(random.uniform(0, 60)),
                    "current_load": str(random.uniform(0, 290)),
                    "fuel_level": str(random.uniform(20, 95)),
                    "tire_pressure_fl": str(random.uniform(95, 105)),
                    "tire_pressure_fr": str(random.uniform(95, 105)),
                    "tire_pressure_rl": str(random.uniform(95, 105)),
                    "tire_pressure_rr": str(random.uniform(95, 105)),
                    "status": random.choice(["Operating", "Operating", "Operating", "Maintenance"])
                }
            )
            self.created_assets.append(truck)
            logger.info(f"Created truck: {truck.name}")

        # Create Excavators
        for i in range(1, 4):
            excavator = self.client.create_asset(
                catalog_name=self.catalog,
                schema_name=self.schema,
                name=f"Excavator_EX{i:02d}",
                asset_type_full_name=f"{self.catalog}.{self.schema}.HydraulicExcavator",
                parent_asset_full_name=pilbara.full_name,
                comment=f"Hydraulic Excavator {i:02d}",
                properties={
                    "serial_number": f"KOM-PC8000-2024{i:02d}",
                    "manufacturer": "Komatsu",
                    "model": "PC8000-11",
                    "bucket_capacity": "42",
                    "operating_weight": "710",
                    "max_dig_depth": "8.2",
                    "engine_hours": str(500 + i * 100),
                    "hydraulic_pressure": str(random.uniform(280, 320)),
                    "swing_angle": str(random.uniform(-180, 180)),
                    "boom_angle": str(random.uniform(20, 60)),
                    "bucket_fill": str(random.uniform(70, 95)),
                    "cycles_today": str(random.randint(200, 400)),
                    "status": "Operating"
                }
            )
            self.created_assets.append(excavator)
            logger.info(f"Created excavator: {excavator.name}")

        # Create Crushers
        for i in range(1, 3):
            crusher = self.client.create_asset(
                catalog_name=self.catalog,
                schema_name=self.schema,
                name=f"Crusher_PC{i:02d}",
                asset_type_full_name=f"{self.catalog}.{self.schema}.PrimaryCrusher",
                parent_asset_full_name=processing.full_name,
                comment=f"Primary Gyratory Crusher {i:02d}",
                properties={
                    "serial_number": f"METSO-MKII-2024{i:02d}",
                    "manufacturer": "Metso",
                    "throughput_capacity": "5000",
                    "power_rating": "3.5",
                    "input_size": "1500",
                    "output_size": "250",
                    "current_throughput": str(random.uniform(3500, 4800)),
                    "power_consumption": str(random.uniform(2.8, 3.4)),
                    "vibration_level": str(random.uniform(2, 8)),
                    "bearing_temp": str(random.uniform(55, 75)),
                    "oil_pressure": str(random.uniform(40, 60)),
                    "tonnes_processed_today": str(random.uniform(40000, 48000)),
                    "status": "Operating"
                }
            )
            self.created_assets.append(crusher)
            logger.info(f"Created crusher: {crusher.name}")

        # Create Rail Network
        rail = self.client.create_asset(
            catalog_name=self.catalog,
            schema_name=self.schema,
            name="AutoRailNetwork",
            asset_type_full_name=f"{self.catalog}.{self.schema}.RailNetwork",
            parent_asset_full_name=pilbara.full_name,
            comment="AutoHaul autonomous heavy rail network",
            properties={
                "network_length": "1700",
                "locomotive_count": "221",
                "autonomous_trains": "true",
                "daily_capacity": "1000000",
                "trains_in_motion": "8",
                "average_speed": "78.5"
            }
        )
        self.created_assets.append(rail)
        logger.info(f"Created rail network: {rail.name}")

        logger.info(f"Created complete hierarchy with {len(self.created_assets)} assets")

    def simulate_telemetry(self, duration_seconds: int = 30):
        """Simulate real-time telemetry updates"""
        logger.info(f"Simulating telemetry for {duration_seconds} seconds...")

        start_time = time.time()
        update_count = 0

        while time.time() - start_time < duration_seconds:
            # Update truck telemetry
            for asset in self.created_assets:
                if "Truck" in asset.name:
                    # Simulate truck movement
                    current_props = asset.properties or {}

                    # Update speed (with some randomness)
                    speed = float(current_props.get("current_speed", 30))
                    speed += random.uniform(-5, 5)
                    speed = max(0, min(60, speed))  # Clamp between 0-60

                    # Update load
                    load = float(current_props.get("current_load", 150))
                    if load > 250:  # If loaded, simulate unloading
                        load -= random.uniform(50, 100)
                    elif load < 50:  # If empty, simulate loading
                        load += random.uniform(50, 100)
                    else:
                        load += random.uniform(-20, 20)
                    load = max(0, min(290, load))

                    # Update fuel
                    fuel = float(current_props.get("fuel_level", 60))
                    fuel -= random.uniform(0.1, 0.5)  # Fuel consumption
                    if fuel < 20:
                        fuel = 95  # Refueled

                    # Log telemetry
                    logger.info(f"Truck {asset.name}: Speed={speed:.1f}km/h, Load={load:.1f}t, Fuel={fuel:.1f}%")
                    update_count += 1

            time.sleep(5)  # Update every 5 seconds

        logger.info(f"Telemetry simulation complete. {update_count} updates sent.")

    def generate_kpi_dashboard(self):
        """Generate KPI dashboard data"""
        logger.info("Generating KPI Dashboard...")

        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "site": "Pilbara Iron Ore Operations",
            "operational_kpis": {
                "production_today": 95890,
                "production_mtd": 2876700,
                "production_ytd": 275000000,
                "ore_grade_avg": 62.5,
                "recovery_rate": 94.2
            },
            "equipment_kpis": {
                "total_equipment": len(self.created_assets) - 3,  # Exclude non-equipment
                "operating": len([a for a in self.created_assets if "Operating" in str(a.properties.get("status", ""))]),
                "maintenance": len([a for a in self.created_assets if "Maintenance" in str(a.properties.get("status", ""))]),
                "availability": 92.5,
                "utilization": 87.3,
                "oee": 78.6  # Overall Equipment Effectiveness
            },
            "autonomous_operations": {
                "autonomous_trucks": 5,
                "autonomous_trains": 8,
                "total_autonomous_hours": 18240,
                "incidents_mtd": 0,
                "productivity_gain": 15.2
            },
            "environmental_kpis": {
                "water_recycled": 82.5,
                "renewable_energy": 34.0,
                "rehabilitation_area": 450,
                "dust_levels": "Within limits",
                "carbon_intensity": 16.2
            },
            "safety_kpis": {
                "days_since_incident": 127,
                "trifr": 2.8,  # Total Recordable Injury Frequency Rate
                "near_misses_mtd": 3,
                "safety_observations": 892
            }
        }

        # Save dashboard
        with open('rio_tinto_dashboard.json', 'w') as f:
            json.dump(dashboard, f, indent=2)

        logger.info("KPI Dashboard generated: rio_tinto_dashboard.json")
        return dashboard

    def cleanup(self):
        """Clean up created assets and types"""
        logger.info("Cleaning up demo assets...")

        # Delete assets (in reverse order)
        for asset in reversed(self.created_assets):
            try:
                self.client.delete_asset(asset.full_name)
                logger.info(f"Deleted asset: {asset.name}")
            except Exception as e:
                logger.warning(f"Failed to delete asset {asset.name}: {e}")

        # Delete asset types
        for type_name in reversed(self.created_types):
            try:
                self.client.delete_asset_type(type_name)
                logger.info(f"Deleted type: {type_name}")
            except Exception as e:
                logger.warning(f"Failed to delete type {type_name}: {e}")

        logger.info("Cleanup complete")


def main():
    """Run the Rio Tinto demo"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║     Rio Tinto Mining Operations Demo                      ║
    ║     Unity Catalog OT Asset Management                     ║
    ╠══════════════════════════════════════════════════════════╣
    ║  Demonstrating:                                           ║
    ║  • ISA-95 compliant asset hierarchy                      ║
    ║  • Autonomous mining equipment                           ║
    ║  • Real-time telemetry simulation                        ║
    ║  • Operational KPI dashboards                            ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    # Initialize Unity Catalog client
    configuration = Configuration()
    configuration.host = "http://localhost:8080/api/2.1/unity-catalog"
    api_client = ApiClient(configuration)
    uc_client = AssetClient(api_client)

    # Create demo builder
    demo = RioTintoDemoBuilder(uc_client)

    try:
        # Step 1: Create asset types
        print("\n[1/5] Creating asset types...")
        demo.create_asset_types()

        # Step 2: Create asset hierarchy
        print("\n[2/5] Building asset hierarchy...")
        demo.create_asset_hierarchy()

        # Step 3: Generate KPI dashboard
        print("\n[3/5] Generating KPI dashboard...")
        dashboard = demo.generate_kpi_dashboard()

        print("\n📊 Current KPIs:")
        print(f"   Production Today: {dashboard['operational_kpis']['production_today']:,} tonnes")
        print(f"   Equipment Availability: {dashboard['equipment_kpis']['availability']}%")
        print(f"   Autonomous Operations: {dashboard['autonomous_operations']['autonomous_trucks']} trucks")
        print(f"   Days Since Incident: {dashboard['safety_kpis']['days_since_incident']}")

        # Step 4: Simulate telemetry
        print("\n[4/5] Starting telemetry simulation...")
        print("   (Simulating real-time equipment telemetry for 30 seconds)")
        demo.simulate_telemetry(duration_seconds=30)

        # Step 5: Summary
        print("\n[5/5] Demo Complete!")
        print(f"\n✅ Successfully created:")
        print(f"   • {len(demo.created_types)} asset types")
        print(f"   • {len(demo.created_assets)} assets in hierarchy")
        print(f"   • KPI dashboard saved to rio_tinto_dashboard.json")

        print("\n📌 Next Steps:")
        print("   1. View assets in Unity Catalog UI at http://localhost:8080")
        print("   2. Navigate to 'OT Assets' section")
        print("   3. Explore the Rio Tinto hierarchy")
        print("   4. Check KPI dashboard in rio_tinto_dashboard.json")

        # Offer cleanup
        response = input("\n🧹 Do you want to clean up demo assets? (y/n): ")
        if response.lower() == 'y':
            demo.cleanup()
            print("✨ Demo assets cleaned up successfully")
        else:
            print("ℹ️  Demo assets retained for exploration")

    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print("\n❌ Demo encountered an error. Check logs for details.")
        print("   Attempting cleanup...")
        demo.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()