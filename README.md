# MDC Dataset Schema Registry

A lightweight, Git-native registry that maps MDC dataset IDs to their
`schema.yaml` files. Schemas are served directly from GitHub's raw-content CDN.

---

## How it works

### Repository layout

```
registry/
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


## Fetching a schema

### Python example with basic error handling:

Copy-paste the [fetch_schema.py](fetch_schema.py) file into your project and import it:

```python
from fetch_schema import fetch_schema

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