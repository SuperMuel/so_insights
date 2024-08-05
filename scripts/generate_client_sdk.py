import subprocess
import json
from pathlib import Path

import sys

# make what's in ./backend accessible
sys.path.append("backend")

# Import your FastAPI app
from backend.src.api import (
    app,
)

# Define the output paths
SCHEMA_OUTPUT_PATH = Path("openapi.json")
SDK_OUTPUT_DIR = Path("frontend/src/sdk")


# Step 1: Generate the OpenAPI Schema
def generate_openapi_schema():
    openapi_schema = app.openapi()
    with SCHEMA_OUTPUT_PATH.open("w") as f:
        json.dump(openapi_schema, f, indent=2)
    print(f"OpenAPI schema saved to: {SCHEMA_OUTPUT_PATH}")


# Step 2: Generate the Python SDK using openapi-python-client with --overwrite
def generate_sdk():
    command = [
        "openapi-python-client",
        "generate",
        "--path",
        str(SCHEMA_OUTPUT_PATH),
        "--output-path",
        str(SDK_OUTPUT_DIR),
        "--overwrite",
    ]

    try:
        subprocess.run(command, check=True)
        print(f"SDK successfully generated at: {SDK_OUTPUT_DIR}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while generating SDK: {e}")


def main():
    # Generate the OpenAPI schema
    generate_openapi_schema()

    # Generate the SDK
    generate_sdk()


if __name__ == "__main__":
    main()
