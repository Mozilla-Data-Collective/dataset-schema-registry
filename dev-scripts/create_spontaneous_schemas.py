"""
Reads spontaneous_ids.json and creates a registry folder + schema.yaml for each dataset ID.
The JSON maps ID -> locale.
"""

import json
import os

SPONTANEOUS_IDS_FILE = "spontaneous_ids.json"
REGISTRY_DIR = "../registry"

SCHEMA_TEMPLATE = """\
dataset_id: "{dataset_id}"
task: "ASR"
format: "tsv"

index_file: "ss-corpus-{locale}.tsv"
base_audio_path: "audios/"

columns:
  audio_path:
    source_column: "audio_file"
    dtype: "file_path"
  transcription:
    source_column: "transcription"
    dtype: "string"
  speaker_id:
    source_column: "client_id"
    dtype: "category"
    optional: true
  audio_id:
    source_column: "audio_id"
    dtype: "string"
    optional: true
  duration_ms:
    source_column: "duration_ms"
    dtype: "int"
    optional: true
  prompt_id:
    source_column: "prompt_id"
    dtype: "string"
    optional: true
  prompt:
    source_column: "prompt"
    dtype: "string"
    optional: true
  votes:
    source_column: "votes"
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
  language:
    source_column: "language"
    dtype: "category"
    optional: true
  split:
    source_column: "split"
    dtype: "category"
    optional: true
  char_per_sec:
    source_column: "char_per_sec"
    dtype: "float"
    optional: true
  quality_tags:
    source_column: "quality_tags"
    dtype: "string"
    optional: true
"""


def main() -> None:
    with open(SPONTANEOUS_IDS_FILE, encoding="utf-8") as f:
        spontaneous_ids: dict[str, str] = json.load(f)

    print(f"Found {len(spontaneous_ids)} dataset(s) in {SPONTANEOUS_IDS_FILE}.")

    for dataset_id, locale in spontaneous_ids.items():
        folder = os.path.join(REGISTRY_DIR, dataset_id)
        os.makedirs(folder, exist_ok=True)

        schema_path = os.path.join(folder, "schema.yaml")
        with open(schema_path, "w", encoding="utf-8") as f:
            f.write(SCHEMA_TEMPLATE.format(dataset_id=dataset_id, locale=locale))

        print(f"  Created {schema_path}  (locale: {locale})")

    print("Done.")


if __name__ == "__main__":
    main()

