from pathlib import Path

from datacollective import download_dataset
from datacollective.schema import _parse_schema
from datacollective.schema_loaders.registry import _load_dataset_from_schema

from dataset_schema_registry.utils import _extract_archive

REPO_ROOT = Path(__file__).parents[2]
DEFAULT_DOWNLOAD_DIR = REPO_ROOT / "downloads"
PATH_FOR_SCHEMA_FILES_TO_VALIDATE = REPO_ROOT / "validate"


def iterate_over_schemas() -> None:

    DEFAULT_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    for dataset_dir in PATH_FOR_SCHEMA_FILES_TO_VALIDATE.iterdir():
        dataset_id = dataset_dir.name
        schema_path = dataset_dir / "schema.yaml"
        try:
            validate_schema(dataset_id, schema_path)
        except Exception as e:
            print(f"\n\n!!!Validation failed for {dataset_id}: {e}\n\n")

def validate_schema(dataset_id: str, schema_path: Path) -> None:
    download_path = download_dataset(dataset_id, download_directory=str(DEFAULT_DOWNLOAD_DIR), enable_logging=True)
    extracted_path = _extract_archive(download_path, DEFAULT_DOWNLOAD_DIR, overwrite_extracted=True)
    schema = _parse_schema(schema_path)

    df = _load_dataset_from_schema(schema, extract_dir=extracted_path)
    if df.empty:
        raise ValueError(f"{schema_path.relative_to(REPO_ROOT)} loaded an empty DataFrame")

    print(f"~~~ DataFrame for {dataset_id} ~~~")
    print(f"DataFrame head: {df.head()}")
    print(f"DataFrame len: {len(df)}")
    print(f"DataFrame shape: {df.shape}")
    print(f"DataFrame iloc 0: \n{df.iloc[0]}\n")
    print(f"DataFrame iloc -1: \n{df.iloc[-1]}\n")
    print(f"Validated {schema_path.relative_to(REPO_ROOT)} for {dataset_id}\n\n")


if __name__ == "__main__":
    iterate_over_schemas()
