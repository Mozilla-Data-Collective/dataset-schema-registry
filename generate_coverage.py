"""
Fetches all dataset IDs from the MDC platform sitemap, checks which ones have
a registered schema in the /registry directory, and writes a Markdown coverage
table to docs/dataset-coverage.md.

Usage:
    python generate_coverage.py

Requirements:
    uv sync
"""

import re
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

import requests

SITEMAP_URL = "https://datacollective.mozillafoundation.org/sitemap.xml"
SITEMAP_NS = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

REGISTRY_DIR = Path(__file__).parent / "registry"
OUTPUT_FILE = Path(__file__).parent / "docs" / "dataset-coverage.md"

def fetch_sitemap(url: str) -> str:
    """Fetch the sitemap XML content."""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; DatasetChecker/1.0)"}
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def parse_sitemap_datasets(xml_content: str) -> list[dict]:
    """
    Parse the sitemap XML and extract dataset entries.

    Dataset URLs follow the pattern: /datasets/<id>
    """
    root = ET.fromstring(xml_content)
    datasets = []

    # Pattern to match dataset URLs and extract ID
    dataset_pattern = re.compile(
        r"^https://datacollective\.mozillafoundation\.org/datasets/([a-z0-9]+)$"
    )

    for url_element in root.findall("ns:url", SITEMAP_NS):
        loc = url_element.find("ns:loc", SITEMAP_NS)
        lastmod = url_element.find("ns:lastmod", SITEMAP_NS)

        if loc is None:
            continue

        url = loc.text
        match = dataset_pattern.match(url)

        if match:
            dataset_id = match.group(1)
            last_modified = lastmod.text if lastmod is not None else None

            datasets.append(
                {"id": dataset_id, "url": url, "lastmod": last_modified}
            )

    return datasets


def get_registered_ids() -> set[str]:
    """Return the set of dataset IDs that have a schema.yaml in /registry."""
    registered = set()
    if not REGISTRY_DIR.is_dir():
        return registered
    for entry in REGISTRY_DIR.iterdir():
        if entry.is_dir() and (entry / "schema.yaml").exists():
            registered.add(entry.name)
    return registered



def build_markdown(datasets: list[dict], registered: set[str]) -> str:
    """Build the full Markdown content for docs/dataset-coverage.md."""
    total = len(datasets)
    supported = sum(1 for d in datasets if d["id"] in registered)
    missing = total - supported
    today = date.today().isoformat()

    lines = [
        "# Dataset Schema Coverage",
        "",
        "This page shows which datasets listed in the MDC platform have a registered",
        "schema in this registry and which ones are still missing.",
        "",
        "!!! info \"How to add a schema\"",
        "    If your dataset is missing, open a pull-request and add a",
        "    `registry/<dataset_id>/schema.yaml` file.  See the",
        "    [README](README.md) for details.",
        "",
        f"**Last updated:** {today}  ",
        f"**Total datasets in sitemap:** {total}  ",
        f"**Schemas registered:** {supported} ✅  ",
        f"**Schemas missing:** {missing} ❌  ",
        "",
        "| ID | Dataset page | schema registered |",
        "|----|-------------|:-----------------:|",
    ]

    for d in sorted(datasets, key=lambda x: x["id"]):
        dataset_id = d["id"]
        dataset_url = d["url"]
        status = "✅" if dataset_id in registered else "❌"
        lines.append(f"| `{dataset_id}` | [link]({dataset_url}) | {status} |")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    print(f"Fetching sitemap from {SITEMAP_URL} …")
    xml_content = fetch_sitemap(SITEMAP_URL)

    print("Parsing dataset entries …")
    datasets = parse_sitemap_datasets(xml_content)
    print(f"  Found {len(datasets)} dataset(s) in the sitemap.")

    print(f"Scanning registry at {REGISTRY_DIR} …")
    registered = get_registered_ids()
    print(f"  Found {len(registered)} registered schema(s).")

    missing_ids = [d["id"] for d in datasets if d["id"] not in registered]
    print(f"  Missing schemas: {len(missing_ids)}")

    print(f"Writing coverage table to {OUTPUT_FILE} …")
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(build_markdown(datasets, registered), encoding="utf-8")
    print("Done ✓")


if __name__ == "__main__":
    main()

