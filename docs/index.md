# MDC Dataset Schema Registry

The registry that maps
[Mozilla Data Collective](https://datacollective.mozillafoundation.org)
dataset IDs to their `schema.yaml` files.

## Repository layout

```text
registry/
├── index.json           # generated: which dataset IDs have a schema
└── <dataset_id>/
    └── schema.yaml
```

## Schema format

A `schema.yaml` file describes a single dataset. Here is an annotated
example:

```yaml
dataset_id: "cmihqro9h0238o207fgg5cmf6"
task: "TTS"                       # machine-learning task
format: "csv"                     # file format of the index file
encoding: "utf-8-sig"            # character encoding
checksum: "c29134fe..."           # SHA-256 of the original archive

index_file: "metadata.csv"       # path to the main tabular file
base_audio_path: "audios/"       # base directory for audio assets

columns:                          # column definitions
  audio_path:
    source_column: "Audio File Name (.wav)"
    dtype: "string"
  transcription:
    source_column: "Transcript"
    dtype: "string"
  speaker_id:
    source_column: "Pseudo ID"
    dtype: "category"
  gender:
    source_column: "Gender"
    dtype: "category"
    optional: true                # column may be absent
  duration:
    source_column: "Duration"
    dtype: "float"
    optional: true
```

## Access pattern — raw GitHub URLs

Schemas are plain text files committed to this repo. GitHub exposes every
file at a stable, unauthenticated URL:

```
https://raw.githubusercontent.com/Mozilla-Data-Collective/dataset-schema-registry
    /<git-ref>/registry/<dataset_id>/schema.yaml
```

| `<git-ref>` | Meaning |
|---|---|
| `main` | Latest schema |
| `abc1234` | Exact commit SHA |

## Registry index

To discover which dataset IDs have a schema — without crawling the repository —
read the index at its stable path:

```
https://raw.githubusercontent.com/Mozilla-Data-Collective/dataset-schema-registry/main/registry/index.json
```

It is regenerated and committed by this repository's CI on every merge to
`main`, so it always matches the schemas on `main`. The
[Dataset Coverage](dataset-coverage.md) page is rendered from it.

```json
{
  "index_schema_version": 1,
  "generated_at": "2026-08-12T16:46:58.594999+00:00",
  "repository": "Mozilla-Data-Collective/dataset-schema-registry",
  "raw_base_url": "https://raw.githubusercontent.com/Mozilla-Data-Collective/dataset-schema-registry/main/registry",
  "counts": {
    "listed_datasets": 1021,
    "with_schema": 415,
    "without_schema": 606,
    "schemas_total": 416,
    "unlisted_schemas": 1
  },
  "datasets": [
    {
      "id": "cmhkl8z2a007rnr07p9bm5kmz",
      "has_schema": true,
      "listed": true,
      "name": "Tetelancingo Nahuatl",
      "slug": "tetelancingo-nahuatl-4dd81077",
      "dataset_url": "https://mozilladatacollective.com/datasets/cmhkl8z2a007rnr07p9bm5kmz",
      "lastmod": "2026-01-08T18:54:46.535Z",
      "schema_path": "registry/cmhkl8z2a007rnr07p9bm5kmz/schema.yaml",
      "schema_url": "https://raw.githubusercontent.com/Mozilla-Data-Collective/dataset-schema-registry/main/registry/cmhkl8z2a007rnr07p9bm5kmz/schema.yaml"
    }
  ]
}
```

| Field | Meaning |
|---|---|
| `has_schema` | Whether `registry/<id>/schema.yaml` exists on `main` |
| `listed` | Whether the MDC platform lists this dataset (`false` for a schema whose dataset is unpublished or removed) |
| `schema_path` / `schema_url` | Repository path and raw URL of the schema, `null` when `has_schema` is `false` |

```python
import json
import urllib.request

INDEX_URL = (
    "https://raw.githubusercontent.com/Mozilla-Data-Collective"
    "/dataset-schema-registry/main/registry/index.json"
)

with urllib.request.urlopen(INDEX_URL) as r:
    index = json.load(r)

with_schema = {d["id"] for d in index["datasets"] if d["has_schema"]}
```

## Fetching a schema

### Python — with error handling

Copy the
[`fetch_schema.py`](https://github.com/Mozilla-Data-Collective/dataset-schema-registry/blob/main/src/dataset_schema_registry/fetch_schema.py)
helper into your project:

```python
from src.dataset_schema_registry.fetch_schema import fetch_schema

content = fetch_schema("cmihqro9h0238o207fgg5cmf6")
```

### Python — one-liner

```python
import urllib.request

def fetch_schema(dataset_id: str) -> str:
    url = (
        f"https://raw.githubusercontent.com/"
        f"Mozilla-Data-Collective/dataset-schema-registry"
        f"/main/registry/{dataset_id}/schema.yaml"
    )
    with urllib.request.urlopen(url) as r:
        return r.read().decode("utf-8")

content = fetch_schema("cmihqro9h0238o207fgg5cmf6")
```

### curl

```bash
curl -sL \
  https://raw.githubusercontent.com/Mozilla-Data-Collective/dataset-schema-registry/main/registry/cmihqro9h0238o207fgg5cmf6/schema.yaml
```

## Contributing

### Adding a new schema

1. Fork and clone the repository.
2. Create the folder `registry/<dataset_id>/`.
3. Add a `schema.yaml` following the format above.
4. Open a pull-request against `main`.

## License

This project is licensed under the
[Mozilla Public License 2.0](https://github.com/Mozilla-Data-Collective/dataset-schema-registry/blob/main/LICENSE).
