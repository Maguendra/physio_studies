import json
from pathlib import Path


SOURCE_FILES = ["mulligan_studies.json", "mdt_studies.json"]
OUTPUT_FILE = "studies_summary.json"


def extract_authors(study: dict) -> list[str]:
    authors = []
    for authorship in study.get("authorships", []):
        author = authorship.get("author", {})
        name = author.get("display_name")
        if name:
            authors.append(name)
    return authors


def build_summary(source_file: str) -> list[dict]:
    path = Path(source_file)
    if not path.exists():
        return []

    data = json.loads(path.read_text(encoding="utf-8"))
    summary = []

    for study in data.get("results", []):
        summary.append(
            {
                "source_file": source_file,
                "title": study.get("title"),
                "publication_year": study.get("publication_year"),
                "authors": extract_authors(study),
            }
        )

    return summary


def main() -> None:
    all_studies = []
    for source_file in SOURCE_FILES:
        all_studies.extend(build_summary(source_file))

    Path(OUTPUT_FILE).write_text(
        json.dumps(all_studies, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"{len(all_studies)} études écrites dans {OUTPUT_FILE}")


if __name__ == "__main__":
    main()