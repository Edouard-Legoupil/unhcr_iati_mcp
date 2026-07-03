#!/usr/bin/env python
"""
Model generation script for UNHCR IATI MCP Server.

This script generates Pydantic models from IATI Datastore sample data
using datamodel-code-generator.

Usage:
    python scripts/generate_models.py

Requirements:
    pip install datamodel-code-generator

Sample files will be downloaded from IATI Datastore if not present.
"""

import os
import json
import asyncio
import httpx
from pathlib import Path
from datamodel_code_generator import generate, InputFileType


# Configuration
SAMPLES_DIR = Path("samples")
OUTPUT_DIR = Path("src/unhcr_iati_mcp/models/generated")
IATI_BASE_URL = "https://api.iatistandard.org/datastore"

# Collections to generate models for
COLLECTIONS = ["activity", "transaction", "budget"]


async def download_sample(collection: str, output_path: Path) -> None:
    """
    Download a sample of data from IATI Datastore.
    
    Args:
        collection: The collection name
        output_path: Path to save the sample JSON
    """
    url = f"{IATI_BASE_URL}/{collection}/select"
    
    params = {
        "q": 'reporting_org_ref:"XM-DAC-41121"',
        "rows": 1,
        "wt": "json",
        "fl": "*"
    }
    
    print(f"Downloading sample {collection} data from IATI Datastore...")
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Save to file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)
            
            print(f"  ✓ Saved to {output_path}")
    except Exception as e:
        print(f"  ✗ Error downloading {collection}: {e}")
        # Create a minimal sample for offline development
        minimal_sample = {
            "response": {
                "numFound": 0,
                "docs": []
            }
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(minimal_sample, f, indent=2)
        print(f"  ✓ Created minimal sample at {output_path}")


def ensure_samples() -> None:
    """Ensure all sample files exist, downloading if necessary."""
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    
    for collection in COLLECTIONS:
        sample_path = SAMPLES_DIR / f"{collection}.json"
        if not sample_path.exists():
            # Run async download
            asyncio.run(download_sample(collection, sample_path))


def generate_models() -> None:
    """Generate Pydantic models from sample data."""
    ensure_samples()
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("\nGenerating Pydantic models...")
    
    for collection in COLLECTIONS:
        sample_path = SAMPLES_DIR / f"{collection}.json"
        output_path = OUTPUT_DIR / f"{collection}.py"
        
        if sample_path.exists():
            print(f"Generating model for {collection}...")
            try:
                generate(
                    input_=str(sample_path),
                    input_file_type=InputFileType.Json,
                    output=str(output_path),
                    output_model_type="pydantic.BaseModel",
                )
                print(f"  ✓ Generated {output_path}")
            except Exception as e:
                print(f"  ✗ Error generating {collection}: {e}")
        else:
            print(f"  ✗ Sample file not found: {sample_path}")


if __name__ == "__main__":
    print("UNHCR IATI MCP Model Generator")
    print("=" * 40)
    generate_models()
    print("\nModel generation complete!")
    print(f"Models saved to: {OUTPUT_DIR}")
