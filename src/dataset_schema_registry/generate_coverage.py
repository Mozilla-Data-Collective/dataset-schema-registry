"""
Reads all dataset IDs (and associated metadata) from the local
docs/dataset_registry.json, checks which ones have a registered schema
in the /registry directory, and write a Markdown coverage table to
docs/dataset-coverage.md.

Usage:
    python src/dataset_schema_registry/generate_coverage.py

Requirements:
    uv sync
"""

import json
from datetime import date
from pathlib import Path

# Repo root
REPO_ROOT = Path(__file__).parents[2]

REGISTRY_DIR = REPO_ROOT / "registry"
REGISTRY_JSON = REPO_ROOT / "docs" / "dataset_registry.json"
OUTPUT_FILE = REPO_ROOT / "docs" / "dataset-coverage.md"


def load_datasets_from_registry() -> list[dict]:
    """Load dataset list from the local JSON registry file."""
    if not REGISTRY_JSON.exists():
        raise FileNotFoundError(
            f"Registry JSON not found at {REGISTRY_JSON}. "
            "Run sync_dataset_registry.py first."
        )
    data = json.loads(REGISTRY_JSON.read_text(encoding="utf-8"))
    return data.get("datasets", [])


def get_registered_ids() -> set[str]:
    """Return the set of dataset IDs that have a schema.yaml in /registry."""
    registered: set[str] = set()
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
        "    [Home](index.md) for details.",
        "",
        f"**Last updated:** {today}  ",
        f"**Total datasets in sitemap:** {total}  ",
        f"**Schemas registered:** {supported} ✅  ",
        f"**Schemas missing:** {missing} ❌  ",
        "",
        "| ID | Name | Slug | Dataset page | Schema registered |",
        "|----|------|------|-------------|:-----------------:|",
    ]

    for d in sorted(datasets, key=lambda x: x["id"]):
        dataset_id = d["id"]
        dataset_url = d["url"]
        name = d.get("name", "")
        slug = d.get("slug", dataset_id)
        status = "✅" if dataset_id in registered else "❌"
        lines.append(
            f"| `{dataset_id}` | {name} | `{slug}` | [link]({dataset_url}) | {status} |"
        )

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    print(f"Loading dataset registry from {REGISTRY_JSON} …")
    datasets = load_datasets_from_registry()
    print(f"  Found {len(datasets)} dataset(s) in registry.")

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

