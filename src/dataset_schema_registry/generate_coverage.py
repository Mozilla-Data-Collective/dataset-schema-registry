"""
Renders the human-readable coverage page from registry/index.json, the
machine-readable index produced by generate_index.py.

The index is the single source of truth for which dataset IDs have a schema;
this script only turns it into a Markdown table at docs/dataset-coverage.md.

Usage:
    python src/dataset_schema_registry/generate_index.py
    python src/dataset_schema_registry/generate_coverage.py

Requirements:
    uv sync
"""

import json
from pathlib import Path

# Repo root
REPO_ROOT = Path(__file__).parents[2]

INDEX_FILE = REPO_ROOT / "registry" / "index.json"
OUTPUT_FILE = REPO_ROOT / "docs" / "dataset-coverage.md"

INDEX_URL = (
    "https://raw.githubusercontent.com/Mozilla-Data-Collective"
    "/dataset-schema-registry/main/registry/index.json"
)


def load_index() -> dict:
    """Load the registry index."""
    if not INDEX_FILE.exists():
        raise FileNotFoundError(
            f"Registry index not found at {INDEX_FILE}. Run generate_index.py first."
        )
    return json.loads(INDEX_FILE.read_text(encoding="utf-8"))


def build_markdown(index: dict) -> str:
    """Build the full Markdown content for docs/dataset-coverage.md."""
    counts = index["counts"]
    # `generated_at` is an ISO-8601 UTC timestamp; show the date part only.
    generated_on = index["generated_at"][:10]

    lines = [
        "# Dataset Schema Coverage",
        "",
        "This page shows which datasets listed in the MDC platform have a registered",
        "schema in this registry and which ones are still missing.",
        "",
        f"It is generated from [`registry/index.json`]({INDEX_URL}), the",
        "machine-readable index of the registry — use that file if you need this",
        "data programmatically.",
        "",
        '!!! info "How to add a schema"',
        "    If your dataset is missing, open a pull-request and add a",
        "    `registry/<dataset_id>/schema.yaml` file.  See the",
        "    [Home](index.md) for details.",
        "",
        f"**Last updated:** {generated_on}  ",
        f"**Total datasets in sitemap:** {counts['listed_datasets']}  ",
        f"**Schemas registered:** {counts['with_schema']} ✅  ",
        f"**Schemas missing:** {counts['without_schema']} ❌  ",
        "",
        "| ID | Name | Slug | Dataset page | Schema registered |",
        "|----|------|------|-------------|:-----------------:|",
    ]

    for entry in index["datasets"]:
        if not entry["listed"]:
            continue
        dataset_id = entry["id"]
        status = "✅" if entry["has_schema"] else "❌"
        lines.append(
            f"| `{dataset_id}` | {entry.get('name') or ''} "
            f"| `{entry.get('slug') or dataset_id}` "
            f"| [link]({entry['dataset_url']}) | {status} |"
        )

    unlisted = [e for e in index["datasets"] if not e["listed"]]
    if unlisted:
        lines += [
            "",
            "## Schemas without a platform dataset",
            "",
            "These schemas live in the registry but their dataset ID is not listed on",
            "the MDC platform — usually a dataset that is unpublished, renamed or used",
            "for testing.",
            "",
            "| ID | Schema |",
            "|----|--------|",
        ]
        lines += [
            f"| `{e['id']}` | [schema.yaml]({e['schema_url']}) |" for e in unlisted
        ]

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    print(f"Loading registry index from {INDEX_FILE} …")
    index = load_index()
    counts = index["counts"]
    print(
        f"  {counts['listed_datasets']} listed dataset(s), "
        f"{counts['with_schema']} with a schema, {counts['without_schema']} without."
    )

    print(f"Writing coverage table to {OUTPUT_FILE} …")
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(build_markdown(index), encoding="utf-8")
    print("Done ✓")


if __name__ == "__main__":
    main()