# MDC Dataset Schema Registry

The registry that maps
[Mozilla Data Collective](https://datacollective.mozillafoundation.org)
dataset IDs to their `schema.yaml` files.

## Repository layout

```text
registry/
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

## Fetching a schema

### Python — with error handling

Copy the
[`fetch_schema.py`](https://github.com/Mozilla-Data-Collective/dataset-schema-registry/blob/main/fetch_schema.py)
helper into your project:

```python
from fetch_schema import fetch_schema

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
