import argparse
from pathlib import Path

import yaml
from datacollective import download_dataset
from datacollective.schema import _parse_schema
from datacollective.schema_loaders.registry import _load_dataset_from_schema

from dataset_schema_registry.utils import _extract_archive

REPO_ROOT = Path(__file__).parents[2]
DEFAULT_DOWNLOAD_DIR = REPO_ROOT / "data"


def extract_dataset_id(schema_path: Path) -> str:
    schema = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
    return str(schema["dataset_id"]).strip()


def validate_schema(schema_path: Path, download_dir: Path) -> None:
    dataset_id = extract_dataset_id(schema_path)
    download_path = download_dataset(dataset_id, download_directory=str(download_dir))
    # Extract the .tar.gz in the download path in the same download_dir
    extracted_path = _extract_archive(download_path, download_dir)
    schema = _parse_schema(schema_path)
    df = _load_dataset_from_schema(schema, extract_dir=extracted_path)
    if df.empty:
        raise ValueError(f"{schema_path.relative_to(REPO_ROOT)} loaded an empty DataFrame")
    print(f"Validated {schema_path.relative_to(REPO_ROOT)}")


def resolve_schema_path(schema_path: Path) -> Path:
    return schema_path if schema_path.is_absolute() else REPO_ROOT / schema_path


def iterate_over_schemas(schema_paths: list[Path] | None) -> None:
    if not schema_paths:
        print("No changed schema.yaml files to validate.")
        return

    DEFAULT_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    for schema_path in schema_paths:
        validate_schema(resolve_schema_path(schema_path), DEFAULT_DOWNLOAD_DIR)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate changed schema.yaml files by downloading and loading their datasets."
    )
    parser.add_argument(
        "--schema_paths",
        nargs="*",
        type=Path,
        help="Paths to changed schema.yaml files, relative to the repository root.",
    )
    args = parser.parse_args()
    iterate_over_schemas(args.schema_paths)
