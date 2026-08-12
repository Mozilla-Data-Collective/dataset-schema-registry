"""
Generates the machine-readable registry index at registry/index.json.

The index lists every dataset known to the MDC platform (from
docs/dataset_registry.json) together with a flag saying whether this registry
holds a `schema.yaml` for it, plus any schema in /registry that has no matching
platform dataset.

It is committed to the repository so that it is served from a stable,
unauthenticated URL:

    https://raw.githubusercontent.com/Mozilla-Data-Collective/dataset-schema-registry/main/registry/index.json

Usage:
    python src/dataset_schema_registry/generate_index.py

Requirements:
    uv sync
"""

import json
from datetime import datetime, timezone
from pathlib import Path

# Repo root
REPO_ROOT = Path(__file__).parents[2]

REGISTRY_DIR = REPO_ROOT / "registry"
REGISTRY_JSON = REPO_ROOT / "docs" / "dataset_registry.json"
OUTPUT_FILE = REGISTRY_DIR / "index.json"

SCHEMA_FILENAME = "schema.yaml"
REPOSITORY = "Mozilla-Data-Collective/dataset-schema-registry"
RAW_BASE_URL = f"https://raw.githubusercontent.com/{REPOSITORY}/main/registry"

# Bump when the shape of the index changes in a backwards-incompatible way.
INDEX_SCHEMA_VERSION = 1


def load_platform_datasets() -> list[dict]:
    """Load the dataset list the platform knows about."""
    if not REGISTRY_JSON.exists():
        raise FileNotFoundError(
            f"Registry JSON not found at {REGISTRY_JSON}. "
            "Run sync_dataset_registry.py first."
        )
    data = json.loads(REGISTRY_JSON.read_text(encoding="utf-8"))
    return data.get("datasets", [])


def get_registered_ids() -> set[str]:
    """Return the set of dataset IDs that have a schema.yaml in /registry."""
    if not REGISTRY_DIR.is_dir():
        return set()
    return {
        entry.name
        for entry in REGISTRY_DIR.iterdir()
        if entry.is_dir() and (entry / SCHEMA_FILENAME).exists()
    }


def build_entry(dataset_id: str, dataset: dict | None, has_schema: bool) -> dict:
    """Build a single index entry for one dataset ID."""
    dataset = dataset or {}
    return {
        "id": dataset_id,
        "has_schema": has_schema,
        # False when a schema exists for an ID the platform does not list
        # (e.g. an unpublished or removed dataset).
        "listed": bool(dataset),
        "name": dataset.get("name"),
        "slug": dataset.get("slug"),
        "dataset_url": dataset.get("url"),
        "lastmod": dataset.get("lastmod"),
        "schema_path": f"registry/{dataset_id}/{SCHEMA_FILENAME}"
        if has_schema
        else None,
        "schema_url": f"{RAW_BASE_URL}/{dataset_id}/{SCHEMA_FILENAME}"
        if has_schema
        else None,
    }


def build_index(datasets: list[dict], registered: set[str]) -> dict:
    """Build the full index payload."""
    by_id = {d["id"]: d for d in datasets}
    entries = [
        build_entry(dataset_id, by_id.get(dataset_id), dataset_id in registered)
        for dataset_id in sorted(set(by_id) | registered)
    ]

    listed = [e for e in entries if e["listed"]]
    with_schema = sum(1 for e in listed if e["has_schema"])

    return {
        "index_schema_version": INDEX_SCHEMA_VERSION,
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "repository": REPOSITORY,
        "raw_base_url": RAW_BASE_URL,
        "counts": {
            "listed_datasets": len(listed),
            "with_schema": with_schema,
            "without_schema": len(listed) - with_schema,
            "schemas_total": len(registered),
            "unlisted_schemas": len(entries) - len(listed),
        },
        "datasets": entries,
    }


def is_unchanged(index: dict) -> bool:
    """
    Return True when the existing index.json is identical to `index` apart from
    its `generated_at` stamp.

    Keeps CI from committing a new timestamp on every run.
    """
    if not OUTPUT_FILE.exists():
        return False
    try:
        existing = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return {k: v for k, v in existing.items() if k != "generated_at"} == {
        k: v for k, v in index.items() if k != "generated_at"
    }


def save_index(index: dict) -> None:
    """Write the index JSON, unless nothing but the timestamp would change."""
    if is_unchanged(index):
        print(f"{OUTPUT_FILE} is already up to date — not rewriting.")
        return
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(index['datasets'])} entries to {OUTPUT_FILE}")


def main() -> None:
    print(f"Loading dataset registry from {REGISTRY_JSON} …")
    datasets = load_platform_datasets()
    print(f"  Found {len(datasets)} dataset(s) in registry.")

    print(f"Scanning registry at {REGISTRY_DIR} …")
    registered = get_registered_ids()
    print(f"  Found {len(registered)} registered schema(s).")

    index = build_index(datasets, registered)
    counts = index["counts"]
    print(
        f"  {counts['with_schema']} listed dataset(s) with a schema, "
        f"{counts['without_schema']} without, "
        f"{counts['unlisted_schemas']} unlisted schema(s)."
    )

    save_index(index)
    print("Done ✓")


if __name__ == "__main__":
    main()