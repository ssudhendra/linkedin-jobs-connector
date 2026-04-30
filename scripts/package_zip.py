from __future__ import annotations

import pathlib
import zipfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST_DIR = ROOT / "dist"
OUTPUT_FILE = DIST_DIR / "linkedin_connector_bundle.zip"

INCLUDE_DIRS = ["src", "examples", "tests", "scripts"]
INCLUDE_FILES = ["README.md", "pyproject.toml", ".gitignore", ".env.example", "connector.manifest.json"]


def main() -> None:
    DIST_DIR.mkdir(exist_ok=True)
    with zipfile.ZipFile(OUTPUT_FILE, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_name in INCLUDE_FILES:
            file_path = ROOT / file_name
            archive.write(file_path, arcname=file_name)

        for directory_name in INCLUDE_DIRS:
            directory = ROOT / directory_name
            for path in directory.rglob("*"):
                if path.is_file():
                    archive.write(path, arcname=path.relative_to(ROOT))

    print(f"Created {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
