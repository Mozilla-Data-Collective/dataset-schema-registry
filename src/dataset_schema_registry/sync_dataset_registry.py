"""
Crawls the MDC platform sitemap.xml, fetches the name and slug for every
dataset page, and saves the result to docs/dataset_registry.json.

The JSON is committed to the repository so that it can be used by generate_coverage.py

Usage:
    python src/dataset_schema_registry/sync_dataset_registry.py

Requirements:
    uv sync
"""

import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import requests
from datacollective import get_dataset_details

SITEMAP_URL = "https://mozilladatacollective.com/sitemap.xml"
SITEMAP_NS = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

# Repo root -> docs/dataset_registry.json
REPO_ROOT = Path(__file__).parents[2]
OUTPUT_FILE = REPO_ROOT / "docs" / "dataset_registry.json"

DATASET_PATTERN = re.compile(
    r"^https://mozilladatacollective\.com/datasets/([a-z0-9]+)$"
)

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; DatasetRegistrySync/1.0)"}


def fetch_sitemap(url: str) -> str:
    """Fetch the sitemap XML content."""
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.text


def parse_sitemap_datasets(xml_content: str) -> list[dict]:
    """Return a list of {id, url, lastmod} dicts for every dataset URL."""
    root = ET.fromstring(xml_content)
    datasets: list[dict] = []

    for url_element in root.findall("ns:url", SITEMAP_NS):
        loc = url_element.find("ns:loc", SITEMAP_NS)
        lastmod = url_element.find("ns:lastmod", SITEMAP_NS)

        if loc is None:
            continue

        url = loc.text or ""
        match = DATASET_PATTERN.match(url)
        if not match:
            continue

        datasets.append(
            {
                "id": match.group(1),
                "url": url,
                "lastmod": lastmod.text if lastmod is not None else None,
            }
        )

    return datasets


def load_existing_registry() -> dict[str, dict]:
    """
    Load the existing registry JSON if it exists.

    Returns a dict mapping dataset_id -> record.
    """
    if not OUTPUT_FILE.exists():
        return {}
    try:
        data = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
        return {entry["id"]: entry for entry in data.get("datasets", [])}
    except (json.JSONDecodeError, KeyError) as exc:
        print(f"Warning: could not parse existing registry: {exc}")
        return {}


def save_registry(datasets: list[dict]) -> None:
    """Serialise and write the registry JSON."""
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "updated_at": datetime.now(tz=timezone.utc).isoformat(),
        "total": len(datasets),
        "datasets": sorted(datasets, key=lambda d: d["id"]),
    }
    OUTPUT_FILE.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Saved {len(datasets)} dataset(s) to {OUTPUT_FILE}")


def main() -> None:
    print(f"Fetching sitemap from {SITEMAP_URL} …")
    xml_content = fetch_sitemap(SITEMAP_URL)
    sitemap_datasets = parse_sitemap_datasets(xml_content)
    print(f"  Found {len(sitemap_datasets)} dataset(s) in sitemap.")

    # Load what we already know to avoid re-fetching unchanged entries.
    existing = load_existing_registry()
    print(f"  Existing registry has {len(existing)} dataset(s).")

    enriched: list[dict] = []
    new_count = 0

    try:
        for entry in sitemap_datasets:
            dataset_id = entry["id"]
            cached = existing.get(dataset_id)

            # Re-use cached record when the lastmod hasn't changed.
            if (
                cached is not None
                and cached.get("lastmod") == entry["lastmod"]
                and cached.get("name")
                and cached.get("slug")
            ):
                enriched.append(cached)
                continue

            # Fetch fresh details from the API.
            print(f"  Fetching details for {dataset_id} …")
            details = get_dataset_details(dataset_id)
            new_count += 1

            enriched.append(
                {
                    "id": dataset_id,
                    "url": entry["url"],
                    "lastmod": entry["lastmod"],
                    "name": details["name"],
                    "slug": details["slug"],
                }
            )
    except KeyboardInterrupt:
        print(f"\n⚠️  Interrupted after {new_count} new/updated dataset(s). Saving partial results …")
    else:
        print(f"  Fetched details for {new_count} new/updated dataset(s).")

    save_registry(enriched)
    print("Done ✓")


if __name__ == "__main__":
    main()

