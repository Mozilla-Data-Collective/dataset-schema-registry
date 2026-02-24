# Dev Scripts

Utility scripts for populating the dataset schema registry with Common Voice datasets.

---

### `fetch_cv_datasets.py`

Crawls the [Mozilla Data Collective sitemap](https://datacollective.mozillafoundation.org/sitemap.xml), extracts all dataset IDs, and queries each one via the `get_dataset_details` of the `datacollective` Python package. Datasets whose name matches **Common Voice Scripted Speech 24.0** are saved to `scripted_ids.json` (`id → name`), and those matching **Common Voice Spontaneous Speech 2.0** are saved to `spontaneous_ids.json` (`id → locale`). The process can be interrupted with **Ctrl+C** and will still save whatever was collected.

---

### `create_scripted_schemas.py`

Reads `scripted_ids.json` and, for each dataset ID, creates a `registry/<ID>/schema.yaml` file pre-filled with the standard **Scripted Speech** schema (multi-split TSV layout, `clips/` audio path, Common Voice column mappings).

---

### `create_spontaneous_schemas.py`

Reads `spontaneous_ids.json` and, for each dataset ID, creates a `registry/<ID>/schema.yaml` file pre-filled with the standard **Spontaneous Speech** schema (single TSV index file named after the locale, `audios/` audio path, spontaneous speech column mappings).

---

## Typical workflow

```zsh
# 1. Discover and classify datasets
python fetch_cv_datasets.py

# 2. Generate registry schemas
python create_scripted_schemas.py
python create_spontaneous_schemas.py
```

