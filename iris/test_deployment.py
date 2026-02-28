#!/usr/bin/env python3
"""
Test script for Project IRIS deployment
Tests all asset management endpoints before deployment
"""

import json
import requests
import sys
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8080/api/2.1/unity-catalog"
CATALOG = "unity"
SCHEMA = "default"

# Test results
test_results = {
    "timestamp": datetime.now().isoformat(),
    "tests_passed": 0,
    "tests_failed": 0,
    "details": []
}


def test_endpoint(name, method, url, data=None):
    """Test a single endpoint"""
    print(f"\n📋 Testing: {name}")
    print(f"   Method: {method}")
    print(f"   URL: {url}")

    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            raise ValueError(f"Unsupported method: {method}")

        # Check response
        if response.status_code in [200, 201, 204]:
            print(f"   ✅ Status: {response.status_code}")
            test_results["tests_passed"] += 1
            test_results["details"].append({
                "test": name,
                "status": "PASSED",
                "code": response.status_code
            })

            # Return response for further testing
            if response.status_code != 204:
                return response.json()
            return None
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Error: {response.text}")
            test_results["tests_failed"] += 1
            test_results["details"].append({
                "test": name,
                "status": "FAILED",
                "code": response.status_code,
                "error": response.text
            })
            return None

    except Exception as e:
        print(f"   ❌ Exception: {e}")
        test_results["tests_failed"] += 1
        test_results["details"].append({
            "test": name,
            "status": "ERROR",
            "error": str(e)
        })
        return None


def run_tests():
    """Run all tests"""
    print("""
╔══════════════════════════════════════════════════════════╗
║     PROJECT IRIS - DEPLOYMENT TEST SUITE                  ║
╠══════════════════════════════════════════════════════════╣
║  Testing Asset Management Endpoints                       ║
╚══════════════════════════════════════════════════════════╝
    """)

    # Test 1: Create Asset Type
    asset_type_data = {
        "catalog_name": CATALOG,
        "schema_name": SCHEMA,
        "name": "DeploymentTestMotor",
        "comment": "Test motor for deployment verification",
        "properties": [
            {
                "name": "rated_power",
                "data_type": "FLOAT",
                "is_required": True,
                "comment": "Rated power in kW"
            },
            {
                "name": "manufacturer",
                "data_type": "STRING",
                "is_required": False,
                "comment": "Manufacturer name"
            }
        ]
    }

    asset_type = test_endpoint(
        "Create Asset Type",
        "POST",
        f"{BASE_URL}/asset-types",
        asset_type_data
    )

    # Test 2: List Asset Types
    test_endpoint(
        "List Asset Types",
        "GET",
        f"{BASE_URL}/asset-types?catalog_name={CATALOG}&schema_name={SCHEMA}"
    )

    if asset_type:
        # Test 3: Get Asset Type
        test_endpoint(
            "Get Asset Type",
            "GET",
            f"{BASE_URL}/asset-types/{asset_type.get('full_name', '')}"
        )

        # Test 4: Create Asset
        asset_data = {
            "catalog_name": CATALOG,
            "schema_name": SCHEMA,
            "name": "TestMotor001",
            "asset_type_full_name": asset_type.get('full_name', ''),
            "comment": "Test motor instance",
            "properties": {
                "rated_power": "500",
                "manufacturer": "TestCorp"
            }
        }

        asset = test_endpoint(
            "Create Asset",
            "POST",
            f"{BASE_URL}/assets",
            asset_data
        )

        if asset:
            # Test 5: Get Asset
            test_endpoint(
                "Get Asset",
                "GET",
                f"{BASE_URL}/assets/{asset.get('full_name', '')}"
            )

            # Test 6: List Assets
            test_endpoint(
                "List Assets",
                "GET",
                f"{BASE_URL}/assets?catalog_name={CATALOG}&schema_name={SCHEMA}"
            )

            # Test 7: Create Child Asset
            child_data = {
                "catalog_name": CATALOG,
                "schema_name": SCHEMA,
                "name": "TestSensor001",
                "asset_type_full_name": asset_type.get('full_name', ''),
                "parent_asset_full_name": asset.get('full_name', ''),
                "comment": "Test sensor attached to motor",
                "properties": {
                    "rated_power": "5"
                }
            }

            child = test_endpoint(
                "Create Child Asset",
                "POST",
                f"{BASE_URL}/assets",
                child_data
            )

            if child:
                # Test 8: List Child Assets
                test_endpoint(
                    "List Child Assets",
                    "GET",
                    f"{BASE_URL}/assets/{asset.get('full_name', '')}/children"
                )

                # Test 9: Delete Child Asset
                test_endpoint(
                    "Delete Child Asset",
                    "DELETE",
                    f"{BASE_URL}/assets/{child.get('full_name', '')}"
                )

            # Test 10: Delete Asset
            test_endpoint(
                "Delete Asset",
                "DELETE",
                f"{BASE_URL}/assets/{asset.get('full_name', '')}"
            )

        # Test 11: Delete Asset Type
        test_endpoint(
            "Delete Asset Type",
            "DELETE",
            f"{BASE_URL}/asset-types/{asset_type.get('full_name', '')}"
        )

    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"✅ Tests Passed: {test_results['tests_passed']}")
    print(f"❌ Tests Failed: {test_results['tests_failed']}")
    print(f"📊 Total Tests: {test_results['tests_passed'] + test_results['tests_failed']}")
    print(f"🎯 Success Rate: {(test_results['tests_passed'] / (test_results['tests_passed'] + test_results['tests_failed']) * 100):.1f}%")

    # Save results
    with open("test_results.json", "w") as f:
        json.dump(test_results, f, indent=2)
    print("\n📄 Detailed results saved to: test_results.json")

    # Return success/failure
    return test_results["tests_failed"] == 0


def verify_deployment_readiness():
    """Verify system is ready for deployment"""
    print("\n🔍 Verifying Deployment Readiness...")

    checks = {
        "Server Connectivity": False,
        "Database Connection": False,
        "API Endpoints": False,
        "Asset Operations": False
    }

    # Check server
    try:
        response = requests.get(f"{BASE_URL}/schemas?catalog_name=unity")
        if response.status_code == 200:
            checks["Server Connectivity"] = True
            checks["Database Connection"] = True
    except:
        pass

    # Check if tests passed
    if test_results["tests_failed"] == 0:
        checks["API Endpoints"] = True
        checks["Asset Operations"] = True

    # Display results
    print("\nDeployment Checklist:")
    for check, status in checks.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {check}")

    all_ready = all(checks.values())

    if all_ready:
        print("\n🚀 SYSTEM READY FOR DEPLOYMENT!")
    else:
        print("\n⚠️  Some checks failed. Please review before deployment.")

    return all_ready


if __name__ == "__main__":
    # Run tests
    success = run_tests()

    # Verify deployment readiness
    ready = verify_deployment_readiness()

    if success and ready:
        print("\n" + "🎉" * 30)
        print("ALL TESTS PASSED - READY TO DEPLOY TO FIELD ENGINEERING!")
        print("🎉" * 30)
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please fix issues before deployment.")
        sys.exit(1)