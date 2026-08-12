# MDC Dataset Schema Registry

A lightweight, Git-native registry that maps MDC dataset IDs to their
`schema.yaml` files. Schemas are served directly from GitHub's raw-content CDN.

---

## How it works

### Repository layout

```
registry/
├── index.json           # generated: which dataset IDs have a schema
└── <dataset_id>/
    └── schema.yaml      # the canonical schema (always up-to-date on main)
```

Each `<dataset_id>` is the unique opaque ID used across the MDC platform
(e.g. `cmihqro9h0238o207fgg5cmf6`).

### Access pattern — raw GitHub URLs

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

To find out which dataset IDs have a schema without crawling the repository,
read the index at its stable path:

```
https://raw.githubusercontent.com/Mozilla-Data-Collective/dataset-schema-registry/main/registry/index.json
```

It is regenerated and committed by this repository's CI on every merge to
`main`, so it always matches the schemas on `main`.

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

The human-readable view of the same data is the
[Dataset Coverage](https://Mozilla-Data-Collective.github.io/dataset-schema-registry/dataset-coverage/)
page, which is generated from `index.json`.


## Fetching a schema

### Python example with basic error handling:

Copy-paste the [fetch_schema.py](src/dataset_schema_registry/fetch_schema.py) file into your project and import it:

```python
from src.dataset_schema_registry.fetch_schema import fetch_schema

content = fetch_schema("cmihqro9h0238o207fgg5cmf6")
```

### One-liner Python example:


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


### One-liner using `curl`:

```bash
curl -sL \
    https://raw.githubusercontent.com/Mozilla-Data-Collective/dataset-schema-registry/main/registry/cmihqro9h0238o207fgg5cmf6/schema.yaml
```