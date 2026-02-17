import argparse

from app import EXPECTED_HEADER, app, import_from_csv


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import students from CSV")
    parser.add_argument("file", help="Path to students.csv")
    args = parser.parse_args()

    with app.app_context():
        inserted, errors = import_from_csv(args.file)

    print("Expected header:", ",".join(EXPECTED_HEADER))
    print(f"Inserted: {inserted}")
    if errors:
        print("Errors:")
        for error in errors:
            print("-", error)
