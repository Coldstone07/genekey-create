"""CLI entry point for Gene Keys hologenetic profile calculator."""

import argparse
import os
from calculator import calculate_profile
from report import generate_report


def main():
    parser = argparse.ArgumentParser(
        description="Generate a Gene Keys hologenetic profile PDF report."
    )
    parser.add_argument("--name", required=True, help="Person's name")
    parser.add_argument("--date", required=True, help="Birth date (YYYY-MM-DD)")
    parser.add_argument("--time", default="12:00", help="Birth time in 24h format (HH:MM), default 12:00")
    parser.add_argument("--location", default="Greenwich, UK", help="Birth location (city, country)")
    parser.add_argument("--output", default=None, help="Output PDF path (default: <name>_genekeys.pdf)")
    args = parser.parse_args()

    output = args.output or f"{args.name.replace(' ', '_')}_genekeys.pdf"

    print(f"Calculating Gene Keys profile for {args.name}...")
    print(f"  Birth: {args.date} at {args.time}")
    print(f"  Location: {args.location}")

    profile = calculate_profile(args.date, args.time, args.location)

    print("\nProfile Results:")
    print("-" * 50)
    for sphere, info in profile.items():
        print(f"  {sphere:15s}  Gene Key {info['gate']:2d}.{info['line']}")

    print(f"\nGenerating PDF report...")
    generate_report(profile, args.name, args.date, args.time, args.location, output)
    print(f"Report saved to: {os.path.abspath(output)}")


if __name__ == "__main__":
    main()
