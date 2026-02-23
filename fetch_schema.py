import urllib.error
import urllib.request

REGISTRY_RAW_BASE = (
    "https://raw.githubusercontent.com/"
    "Mozilla-Data-Collective/dataset-schema-registry"
)

def fetch_schema(dataset_id: str) -> str:
    """
    Download and return the schema.yaml content for *dataset_id*.

    Args:
        dataset_id: The registry dataset ID (the folder name under /registry/).

    Returns:
        The raw content of the schema.yaml as a UTF-8 string.
    Raises:
        ValueError
            If the dataset is not found (HTTP 404).
        RuntimeError
            For any other network / HTTP error.
    """

    url = f"{REGISTRY_RAW_BASE}/main/registry/{dataset_id}/schema.yaml"

    try:
        with urllib.request.urlopen(url) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise ValueError(
                f"Dataset '{dataset_id}' not found in the registry.\n"
                f"URL tried: {url}"
            ) from exc
        raise RuntimeError(f"HTTP {exc.code} while fetching {url}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error while fetching {url}: {exc.reason}") from exc


