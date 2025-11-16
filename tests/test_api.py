"""
Simple test script for the FastAPI endpoints.

Make sure the API server is running before running this script:
    uvicorn backend.app.main:app --reload

Then run this script:
    python tests/test_api.py
"""

import requests
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8000/api/v1"


def print_response(title: str, response: requests.Response):
    """Pretty print API response."""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")
    print(f"Status Code: {response.status_code}")
    print(f"\nResponse:")
    try:
        print(json.dumps(response.json(), indent=2))
    except Exception:
        print(response.text)
    print(f"{'='*80}\n")


def test_health_check():
    """Test the health check endpoint."""
    print("\n🔍 Testing Health Check Endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print_response("Health Check", response)
    return response.status_code == 200


def test_prediction(description: str):
    """Test the prediction endpoint with a car description."""
    print(f"\n🚗 Testing Prediction: {description[:60]}...")

    payload = {
        "description": description
    }

    response = requests.post(
        f"{BASE_URL}/predict",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    print_response(f"Prediction for: {description[:60]}", response)
    return response.status_code == 200


def test_empty_description():
    """Test prediction with empty description (should fail)."""
    print("\n❌ Testing Empty Description (expect error)...")

    payload = {
        "description": ""
    }

    response = requests.post(
        f"{BASE_URL}/predict",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    print_response("Empty Description Error", response)
    return response.status_code == 422  # Validation error expected


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("FASTAPI ENDPOINT TESTS")
    print("="*80)
    print("\nMake sure the API server is running:")
    print("  uvicorn backend.app.main:app --reload")
    print("\n" + "="*80)

    # Test examples
    test_cases = [
        # Example 1: Comprehensive description
        "2020 Toyota Camry, 45k miles, automatic transmission, one owner, no accidents, clean title, black interior, FWD, gets about 32 mpg",

        # Example 2: Minimal information
        "Used Honda Civic 2018",

        # Example 3: Luxury car
        "Mercedes-Benz E-Class 2022, 15k miles, AWD, automatic, tan interior, single owner, clean history",

        # Example 4: Truck
        "Ford F-150 2021, 4x4, automatic, 30k miles, gray interior, no damage, personal use only",

        # Example 5: Hybrid
        "2020 Toyota Prius hybrid, 40k miles, CVT transmission, beige interior, 55 mpg, no accidents",
    ]

    results = []

    # Test health check
    print("\n\n" + "🏥 HEALTH CHECK TEST " + "="*60)
    health_ok = test_health_check()
    results.append(("Health Check", health_ok))

    if not health_ok:
        print("\n❌ Health check failed. Is the server running?")
        print("   Start with: uvicorn backend.app.main:app --reload")
        return

    # Test predictions
    print("\n\n" + "📊 PREDICTION TESTS " + "="*60)
    for i, description in enumerate(test_cases, 1):
        success = test_prediction(description)
        results.append((f"Prediction {i}", success))

    # Test error handling
    print("\n\n" + "⚠️  ERROR HANDLING TEST " + "="*60)
    error_ok = test_empty_description()
    results.append(("Empty Description Error", error_ok))

    # Summary
    print("\n\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")

    if total - passed > 0:
        print("\nFailed tests:")
        for name, result in results:
            if not result:
                print(f"  ❌ {name}")
    else:
        print("\n✅ All tests passed!")

    print("\n" + "="*80)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API server")
        print("   Make sure the server is running:")
        print("   uvicorn backend.app.main:app --reload")
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
