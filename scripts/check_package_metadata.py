import os
import subprocess
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT_DIR = Path(__file__).resolve().parent.parent / "src"
# All fields that we need to check
FIELDS = ["name", "version", "description", "maintainer", "maintainer-email", "license"]

incorrect_packages: dict[str, list[str]] = {}

# ANSI red, only when the output can show it (a terminal or GitHub Actions logs)
USE_COLOR = (sys.stdout.isatty() or "GITHUB_ACTIONS" in os.environ) and "NO_COLOR" not in os.environ
RED = "\033[31m" if USE_COLOR else ""
RESET = "\033[0m" if USE_COLOR else ""


def clean(value: str | None) -> str | None:
    """Normalize whitespace so multi-line text matches single line."""
    return " ".join(value.split()) if value is not None else None


for package_xml in ROOT_DIR.rglob("package.xml"):
    pkg_dir = package_xml.parent

    # Reads fields from setup.py
    result = subprocess.run(
        [sys.executable, "setup.py", *(f"--{f}" for f in FIELDS)],
        cwd=pkg_dir, capture_output=True, text=True,
    )
    # Throw an error if the above command didn't run, probably because setuptools wasn't set up
    if result.returncode != 0:
        print(f"{pkg_dir}: setup.py failed\n{result.stderr}")
        continue
    setup_values = dict(zip(FIELDS, result.stdout.splitlines()))

    # Now read from package.xml
    root = ET.parse(package_xml).getroot()
    maintainer = root.find("maintainer")
    # Check maintainer to avoid null pointer
    if maintainer is None:
        incorrect_packages[pkg_dir.name] = ["maintainer (missing from package.xml)"]
        continue
    xml_values = {
        "name": clean(root.findtext("name")),
        "version": clean(root.findtext("version")),
        "description": clean(root.findtext("description")),
        "maintainer": clean(maintainer.text),
        "maintainer-email": clean(maintainer.get("email")),
        "license": clean(root.findtext("license")),
    }

    mismatched_fields: list[str] = []

    # Print errors in red color
    for field in FIELDS:
        if setup_values[field] != xml_values[field]:
            print(f"{RED}{pkg_dir.name}: {field} mismatch\n"
                  f"  setup.py:    {setup_values[field]}\n"
                  f"  package.xml: {xml_values[field]}{RESET}")
            mismatched_fields.append(field)
    
    if mismatched_fields:
        incorrect_packages[package_xml.parent.name] = mismatched_fields
    
if len(incorrect_packages):
    print(f"\n{RED}Mismatched fields in the following packages ({len(incorrect_packages)}):")
    print("\n".join([f"  {package}: {fields}" for package, fields in incorrect_packages.items()]))
    print(RESET, end='')

    # Throw error so this can be used as a test in CI
    sys.exit(1)
sys.exit(0)
