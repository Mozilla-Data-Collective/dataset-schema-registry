"""
Reads scripted_ids.json and creates a registry folder + schema.yaml for each dataset ID.
"""

import json
import os

SCRIPTED_IDS_FILE = "scripted_ids.json"
REGISTRY_DIR = "registry"

SCHEMA_TEMPLATE = """\
dataset_id: "{dataset_id}"
task: "ASR"
root_strategy: "multi_split"

splits:
  - dev
  - invalidated
  - other
  - reported
  - test
  - train
  - validated

splits_file_pattern: "**/*.tsv"
base_audio_path: "clips/"

columns:
  audio_path:
    source_column: "path"
    dtype: "file_path"
  transcription:
    source_column: "sentence"
    dtype: "string"
  speaker_id:
    source_column: "client_id"
    dtype: "category"
    optional: true
  sentence_id:
    source_column: "sentence_id"
    dtype: "string"
    optional: true
  sentence_domain:
    source_column: "sentence_domain"
    dtype: "category"
    optional: true
  up_votes:
    source_column: "up_votes"
    dtype: "int"
    optional: true
  down_votes:
    source_column: "down_votes"
    dtype: "int"
    optional: true
  age:
    source_column: "age"
    dtype: "category"
    optional: true
  gender:
    source_column: "gender"
    dtype: "category"
    optional: true
  accents:
    source_column: "accents"
    dtype: "category"
    optional: true
  variant:
    source_column: "variant"
    dtype: "category"
    optional: true
  locale:
    source_column: "locale"
    dtype: "category"
    optional: true
"""


def main() -> None:
    with open(SCRIPTED_IDS_FILE, encoding="utf-8") as f:
        scripted_ids: dict[str, str] = json.load(f)

    print(f"Found {len(scripted_ids)} dataset(s) in {SCRIPTED_IDS_FILE}.")

    for dataset_id, name in scripted_ids.items():
        folder = os.path.join(REGISTRY_DIR, dataset_id)
        os.makedirs(folder, exist_ok=True)

        schema_path = os.path.join(folder, "schema.yaml")
        with open(schema_path, "w", encoding="utf-8") as f:
            f.write(SCHEMA_TEMPLATE.format(dataset_id=dataset_id))

        print(f"  Created {schema_path}  ({name})")

    print("Done.")


if __name__ == "__main__":
    main()

