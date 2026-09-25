#!/usr/bin/env python3
"""Work out which ROS packages a PR touches, so CI only tests those.

Usage: changed_packages.py <base-ref> [<head-ref>]

Each changed file is mapped to the ROS package that owns it by walking up
from the file to the nearest directory containing a package.xml. That way it
doesn't matter how deeply packages end up nested under src/ as the repo grows
more divisions (src/nodes/<pkg>, src/<division>/<pkg>, ...) -- no list of
package paths needs to be kept in sync here.

Writes two outputs to $GITHUB_OUTPUT (or prints them when run locally):
  mode      "all" (shared build/CI config changed -- test everything),
            "some" (test only `packages`) or "none" (nothing to test)
  packages  space-separated ROS package names (package.xml <name>, which can
            differ from the directory name), only meaningful for mode=some
"""

import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / 'src'

# Changes here alter the environment every package is built and tested in
# (the image, the entrypoint, this CI), so a PR touching them can break any
# package -- run the full suite rather than guessing.
GLOBAL_PREFIXES = ('.docker/', '.github/', 'docker-compose.yml')


def changed_files(base: str, head: str) -> list[str]:
    # Three-dot diff: only what the PR itself changed since it branched off
    # base, not unrelated commits that landed on base in the meantime.
    out = subprocess.run(
        ['git', 'diff', '--name-only', f'{base}...{head}'],
        cwd=REPO_ROOT, check=True, capture_output=True, text=True,
    ).stdout
    return [line for line in out.splitlines() if line]


def owning_package(rel_path: str) -> str | None:
    # Start from the file's directory rather than the file, and tolerate it
    # no longer existing -- a PR that deletes files should still count as a
    # change to the package they were deleted from.
    path = (REPO_ROOT / rel_path).parent
    while path != SRC and SRC in path.parents:
        manifest = path / 'package.xml'
        if manifest.is_file():
            return ET.parse(manifest).getroot().findtext('name').strip()
        path = path.parent
    return None


def main() -> None:
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    base = sys.argv[1]
    head = sys.argv[2] if len(sys.argv) == 3 else 'HEAD'

    files = changed_files(base, head)
    if any(f.startswith(GLOBAL_PREFIXES) for f in files):
        mode, packages = 'all', []
    else:
        packages = sorted({p for p in map(owning_package, files) if p})
        mode = 'some' if packages else 'none'

    outputs = f'mode={mode}\npackages={" ".join(packages)}\n'
    print(outputs, end='')
    if 'GITHUB_OUTPUT' in os.environ:
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write(outputs)


if __name__ == '__main__':
    main()
