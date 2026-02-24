"""
Fetch dataset IDs from the Mozilla Data Collective sitemap, query each dataset's
metadata, and store matching IDs/names or locale into JSON files based on dataset name.
"""

import json
import re
import urllib.request
import xml.etree.ElementTree as ET

from datacollective import get_dataset_details

SITEMAP_URL = "https://datacollective.mozillafoundation.org/sitemap.xml"

# Regex to capture dataset IDs from sitemap URLs.
# IDs look like: cmm0nm2ua000eo007qs4r3m8q (alphanumeric, lowercase)
DATASET_ID_RE = re.compile(r"/datasets/([a-z0-9]+)(?:/|$)")

SCRIPTED_SPEECH_NAME = "Common Voice Scripted Speech 24.0"
SPONTANEOUS_SPEECH_NAME = "Common Voice Spontaneous Speech 2.0"


def fetch_sitemap_ids(url: str) -> list[str]:
    """Download the sitemap XML and extract unique dataset IDs."""
    with urllib.request.urlopen(url) as response:
        content = response.read()

    root = ET.fromstring(content)
    # The sitemap namespace
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    ids: list[str] = []
    seen: set[str] = set()

    for loc in root.findall(".//sm:loc", ns):
        text = loc.text or ""
        match = DATASET_ID_RE.search(text)
        if match:
            dataset_id = match.group(1)
            if dataset_id not in seen:
                seen.add(dataset_id)
                ids.append(dataset_id)

    return ids


def main() -> None:
    print(f"Fetching sitemap from {SITEMAP_URL} ...")
    dataset_ids = fetch_sitemap_ids(SITEMAP_URL)
    print(f"Found {len(dataset_ids)} unique dataset ID(s).")

    scripted: dict[str, str] = {}
    spontaneous: dict[str, str] = {}

    try:
        for i, dataset_id in enumerate(dataset_ids, start=1):
            print(f"[{i}/{len(dataset_ids)}] Querying dataset {dataset_id} ...", end=" ")
            try:
                details = get_dataset_details(dataset_id)
                name = details.get("name", "")
                locale = details.get("locale", "")
                print(f'"{name}"')
                print(f'"{locale}"')

                if SCRIPTED_SPEECH_NAME in name:
                    scripted[dataset_id] = name
                elif SPONTANEOUS_SPEECH_NAME in name:
                    spontaneous[dataset_id] = locale

            except Exception as exc:  # noqa: BLE001
                print(f"ERROR: {exc}")
    except KeyboardInterrupt:
        print("\nInterrupted by user — saving results collected so far ...")

    with open("scripted_ids.json", "w", encoding="utf-8") as f:
        json.dump(scripted, f, indent=2, ensure_ascii=False)
    print(f"\nWrote {len(scripted)} scripted speech dataset(s) to scripted_ids.json")

    with open("spontaneous_ids.json", "w", encoding="utf-8") as f:
        json.dump(spontaneous, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(spontaneous)} spontaneous speech dataset(s) to spontaneous_ids.json")


if __name__ == "__main__":
    main()

