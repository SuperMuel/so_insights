import argparse
import subprocess
import json
from pathlib import Path

from src.api import app

# Define the default output paths
DEFAULT_SCHEMA_OUTPUT_PATH = Path("openapi.json")


def generate_openapi_schema(schema_output_path: Path):
    openapi_schema = app.openapi()
    with schema_output_path.open("w") as f:
        json.dump(openapi_schema, f, indent=2)
    print(f"OpenAPI schema saved to: {schema_output_path}")


def generate_sdk(schema_output_path: Path, sdk_output_dir: Path):
    command = [
        "openapi-python-client",
        "generate",
        "--path",
        str(schema_output_path),
        "--output-path",
        str(sdk_output_dir),
        "--overwrite",
    ]

    try:
        subprocess.run(command, check=True)
        print(f"SDK successfully generated at: {sdk_output_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while generating SDK: {e}")


def main():
    parser = argparse.ArgumentParser(description="Generate SDK from OpenAPI schema.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output directory for the SDK",
    )
    args = parser.parse_args()

    schema_output_path = DEFAULT_SCHEMA_OUTPUT_PATH
    sdk_output_dir = args.output

    # Generate the OpenAPI schema
    generate_openapi_schema(schema_output_path)

    # Generate the SDK
    generate_sdk(schema_output_path, sdk_output_dir)


if __name__ == "__main__":
    main()
