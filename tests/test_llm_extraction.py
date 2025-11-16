"""
Manual test script for LLM feature extraction.

Run from project root:
    python tests/test_llm_extraction.py

Or run specific example:
    python tests/test_llm_extraction.py --example 5
"""

import os
import sys
import json
import argparse
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.services.llm_service import LLMService
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Test examples: (input_text, expected_output)
TEST_EXAMPLES = [
    # Example 1: Comprehensive description
    (
        "2020 Toyota Camry, 45k miles, automatic transmission, one owner, no accidents, clean title, black interior, FWD, gets about 32 mpg",
        {
            "manufacturer": "Toyota",
            "year": 2020,
            "mileage": 45000,
            "transmission": "Automatic",
            "one_owner": 1,
            "accidents_or_damage": 0,
            "interior_color": "Black",
            "drivetrain": "front_wheel_drive",
            "mpg": 32.0,
            "fuel_type": None,
            "personal_use_only": None
        }
    ),

    # Example 2: Minimal information
    (
        "Used Honda Civic 2018",
        {
            "manufacturer": "Honda",
            "year": 2018,
            "mileage": None,
            "transmission": None,
            "one_owner": None,
            "accidents_or_damage": None,
            "interior_color": None,
            "drivetrain": None,
            "mpg": None,
            "fuel_type": None,
            "personal_use_only": None
        }
    ),

    # Example 3: Truck with 4WD
    (
        "Ford F-150 2021, 4x4, automatic, 30k miles, gray interior, no damage, personal use only",
        {
            "manufacturer": "Ford",
            "year": 2021,
            "mileage": 30000,
            "transmission": "Automatic",  # User said "automatic", not "10-speed"
            "one_owner": None,
            "accidents_or_damage": 0,
            "interior_color": "Gray",
            "drivetrain": "four_wheel_drive",
            "mpg": None,
            "fuel_type": None,
            "personal_use_only": 1
        }
    ),

    # Example 4: Manual transmission, accident history
    (
        "2019 Honda Civic manual transmission, 60k miles, black interior, minor accident reported, FWD",
        {
            "manufacturer": "Honda",
            "year": 2019,
            "mileage": 60000,
            "transmission": "6-Speed Manual",
            "one_owner": None,
            "accidents_or_damage": 1,
            "interior_color": "Black",
            "drivetrain": "front_wheel_drive",
            "mpg": None,
            "fuel_type": None,
            "personal_use_only": None
        }
    ),

    # Example 5: Luxury car with specific details
    (
        "Mercedes-Benz E-Class 2022, 15k miles, AWD, automatic, tan interior, single owner, clean history",
        {
            "manufacturer": "Mercedes-Benz",
            "year": 2022,
            "mileage": 15000,
            "transmission": "Automatic",  # User said "automatic", not "9-speed"
            "one_owner": 1,
            "accidents_or_damage": 0,
            "interior_color": "Tan",
            "drivetrain": "all_wheel_drive",
            "mpg": None,
            "fuel_type": None,
            "personal_use_only": None
        }
    ),

    # Example 6: Hybrid vehicle
    (
        "2020 Toyota Prius hybrid, 40k miles, CVT transmission, beige interior, 55 mpg, no accidents",
        {
            "manufacturer": "Toyota",
            "year": 2020,
            "mileage": 40000,
            "transmission": "Automatic CVT",
            "one_owner": None,
            "accidents_or_damage": 0,
            "interior_color": "Beige",
            "drivetrain": None,
            "mpg": 55.0,
            "fuel_type": "Hybrid",
            "personal_use_only": None
        }
    ),

    # Example 7: Jeep with off-road specs
    (
        "Jeep Wrangler 2021, 4WD, manual, 25k miles, clean title, one owner, charcoal interior",
        {
            "manufacturer": "Jeep",
            "year": 2021,
            "mileage": 25000,
            "transmission": "6-Speed Manual",
            "one_owner": 1,
            "accidents_or_damage": 0,
            "interior_color": "Charcoal",
            "drivetrain": "four_wheel_drive",
            "mpg": None,
            "fuel_type": None,
            "personal_use_only": None
        }
    ),

    # Example 8: CVT transmission specifically mentioned
    (
        "2019 Honda Accord, CVT transmission, 65k miles, FWD, gray interior, no accidents",
        {
            "manufacturer": "Honda",
            "year": 2019,
            "mileage": 65000,
            "transmission": "Automatic CVT",  # User specifically said "CVT transmission"
            "one_owner": None,
            "accidents_or_damage": 0,
            "interior_color": "Gray",
            "drivetrain": "front_wheel_drive",
            "mpg": None,
            "fuel_type": None,
            "personal_use_only": None
        }
    ),

    # Example 9: BMW with specific transmission
    (
        "BMW 3 Series 2023, 10k miles, 8-speed automatic, AWD, black interior, personal daily driver",
        {
            "manufacturer": "BMW",
            "year": 2023,
            "mileage": 10000,
            "transmission": "8-Speed Automatic",
            "one_owner": None,
            "accidents_or_damage": None,
            "interior_color": "Black",
            "drivetrain": "all_wheel_drive",
            "mpg": None,
            "fuel_type": None,
            "personal_use_only": 1
        }
    ),

    # Example 10: Diesel truck
    (
        "2020 Chevrolet Silverado diesel, 4x4, automatic, 50k miles, graphite interior, one owner",
        {
            "manufacturer": "Chevrolet",
            "year": 2020,
            "mileage": 50000,
            "transmission": "Automatic",  # User said "automatic", not "10-speed"
            "one_owner": 1,
            "accidents_or_damage": None,
            "interior_color": "Graphite",
            "drivetrain": "four_wheel_drive",
            "mpg": None,
            "fuel_type": "Diesel",
            "personal_use_only": None
        }
    ),

    # Example 11: 10-speed automatic specifically mentioned
    (
        "Ford F-150 2022, 10-speed automatic transmission, 4x4, 18k miles, black interior, clean title",
        {
            "manufacturer": "Ford",
            "year": 2022,
            "mileage": 18000,
            "transmission": "10-Speed Automatic",  # User specifically said "10-speed automatic"
            "one_owner": None,
            "accidents_or_damage": 0,
            "interior_color": "Black",
            "drivetrain": "four_wheel_drive",
            "mpg": None,
            "fuel_type": None,
            "personal_use_only": None
        }
    ),

    # Example 12: Kia with CVT
    (
        "2021 Kia Forte, CVT, FWD, 35k miles, jet black interior, no accidents, single owner",
        {
            "manufacturer": "Kia",
            "year": 2021,
            "mileage": 35000,
            "transmission": "Automatic CVT",
            "one_owner": 1,
            "accidents_or_damage": 0,
            "interior_color": "Jet Black",
            "drivetrain": "front_wheel_drive",
            "mpg": None,
            "fuel_type": None,
            "personal_use_only": None
        }
    ),

    # Example 13: 8-speed automatic specifically mentioned
    (
        "BMW X5 2023, 8-speed automatic, AWD, 12k miles, beige interior, one owner, no accidents",
        {
            "manufacturer": "BMW",
            "year": 2023,
            "mileage": 12000,
            "transmission": "8-Speed Automatic",  # User specifically said "8-speed automatic"
            "one_owner": 1,
            "accidents_or_damage": 0,
            "interior_color": "Beige",
            "drivetrain": "all_wheel_drive",
            "mpg": None,
            "fuel_type": None,
            "personal_use_only": None
        }
    ),

    # Example 14: Older vehicle with damage
    (
        "2012 Ford Focus, 90k miles, manual, front wheel drive, minor damage, gray interior",
        {
            "manufacturer": "Ford",
            "year": 2012,
            "mileage": 90000,
            "transmission": "6-Speed Manual",
            "one_owner": None,
            "accidents_or_damage": 1,
            "interior_color": "Gray",
            "drivetrain": "front_wheel_drive",
            "mpg": None,
            "fuel_type": None,
            "personal_use_only": None
        }
    ),

    # Example 15: Unknown brand fallback
    (
        "2021 Subaru Outback, AWD, automatic, 28k miles, charcoal black interior, clean title",
        {
            "manufacturer": "others",  # Subaru not in MANUFACTURERS list
            "year": 2021,
            "mileage": 28000,
            "transmission": "Automatic",  # User said "automatic", not CVT
            "one_owner": None,
            "accidents_or_damage": 0,
            "interior_color": "Charcoal Black",
            "drivetrain": "all_wheel_drive",
            "mpg": None,
            "fuel_type": None,
            "personal_use_only": None
        }
    ),
]


def test_extraction_example(llm_service, input_text, expected_output, example_num, output_lines):
    """Test a single extraction example."""
    def log(msg):
        """Print and save to output lines."""
        print(msg)
        output_lines.append(msg)

    log(f"\n{'='*80}")
    log(f"EXAMPLE {example_num}")
    log(f"{'='*80}")
    log(f"\nInput: {input_text}")
    log(f"\nExpected Output (user-provided features only):")
    log(json.dumps(expected_output, indent=2))

    try:
        actual_output = llm_service.extract_car_features(input_text)
        log(f"\nActual Output (with all defaults filled):")
        log(json.dumps(actual_output, indent=2))

        # Compare only the fields that were in expected_output
        log(f"\n--- Comparison (user-provided features) ---")
        all_match = True
        for key, expected_value in expected_output.items():
            actual_value = actual_output.get(key)

            # Handle None in expected (means LLM should NOT extract it)
            if expected_value is None:
                # We just check it was filled with default
                match_symbol = "○"  # Neutral - default was applied
                status = f"(default: {actual_value})"
            else:
                # Check if extracted value matches expected
                match = actual_value == expected_value
                match_symbol = "✓" if match else "✗"
                status = ""
                if not match:
                    all_match = False

            log(f"{match_symbol} {key}: expected={expected_value}, actual={actual_value} {status}")

        log(f"\n{'✓ PASS' if all_match else '✗ FAIL'}")
        return all_match

    except Exception as e:
        log(f"\n❌ ERROR: {str(e)}")
        import traceback
        error_trace = traceback.format_exc()
        log(error_trace)
        return False


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Test LLM feature extraction")
    parser.add_argument(
        "--example",
        type=int,
        help="Run specific example number (1-15)",
        default=None
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path (default: tests/results_TIMESTAMP.txt)",
        default=None
    )
    args = parser.parse_args()

    # Prepare output file
    if args.output:
        output_file = Path(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path(__file__).parent / f"results_{timestamp}.txt"

    output_lines = []

    # Initialize service
    def log(msg):
        """Print and save to output lines."""
        print(msg)
        output_lines.append(msg)

    log("Initializing LLM Service...")
    api_key = os.getenv("GEMINI_API_KEY")
    llm_service = LLMService(api_key=api_key)
    log(f"Using model: {llm_service.model_name}")
    log(f"Results will be saved to: {output_file}\n")

    # Run tests
    if args.example:
        # Run specific example
        if 1 <= args.example <= len(TEST_EXAMPLES):
            input_text, expected_output = TEST_EXAMPLES[args.example - 1]
            test_extraction_example(llm_service, input_text, expected_output, args.example, output_lines)
        else:
            log(f"ERROR: Example number must be between 1 and {len(TEST_EXAMPLES)}")
            sys.exit(1)
    else:
        # Run all examples
        results = []
        for i, (input_text, expected_output) in enumerate(TEST_EXAMPLES, 1):
            result = test_extraction_example(llm_service, input_text, expected_output, i, output_lines)
            results.append((i, result))

            if i < len(TEST_EXAMPLES):
                log("\nWaiting 3 seconds before next example...")
                time.sleep(3)

        # Summary
        log(f"\n{'='*80}")
        log("SUMMARY")
        log(f"{'='*80}")
        passed = sum(1 for _, result in results if result)
        total = len(results)
        log(f"\nPassed: {passed}/{total}")
        log(f"Failed: {total - passed}/{total}")

        if total - passed > 0:
            log("\nFailed examples:")
            for num, result in results:
                if not result:
                    log(f"  - Example {num}")

    # Save results to file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))

    log(f"\n{'='*80}")
    log(f"Results saved to: {output_file}")
    log(f"{'='*80}")


if __name__ == "__main__":
    main()
