#!/usr/bin/env python3
"""Work out which ROS packages a PR touches, so CI only tests those.

Usage: changed_packages.py <base-ref> [<head-ref>]

Checks the git diff of the changed files between the base and head.  After
getting all the files it searches parent directories up to the root until it
finds the package.xml that the file belongs to.  With that, each node or set of
nodes that work closely together should have a ROS package (package.xml).  Each
package.xml declares its dependencies so that everything relevant to the code
changes will get tested.

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

# If any of these are changed, the entire testing suite will run
GLOBAL_PREFIXES = ('.docker/', '.github/', 'docker-compose.yml')


def changed_files(base: str, head: str) -> list[str]:
    # get list of changed files from `git diff --name-only base...head`
    out = subprocess.run(
        ['git', 'diff', '--name-only', f'{base}...{head}'],
        cwd=REPO_ROOT, check=True, capture_output=True, text=True,
    ).stdout
    # Return list of non-empty lines
    return [line for line in out.splitlines() if line]


def owning_package(rel_path: str) -> str | None:
    # path to file location (not to file itself)
    path = (REPO_ROOT / rel_path).parent
    # Go up path until package.xml is found
    while path != SRC and SRC in path.parents:
        manifest = path / 'package.xml'
        if manifest.is_file():
            # parse the xml to get the package name and return it
            return ET.parse(manifest).getroot().findtext('name').strip()
        path = path.parent
    return None


def main() -> None:
    # Check usage: `changed_packages.py <base-ref> [<head-ref>]`
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__) # Exit and print file's docstring with usage

    # base and head refer to the branches compared in the PR.
    base = sys.argv[1]
    head = sys.argv[2] if len(sys.argv) == 3 else 'HEAD'

    # Get list of changed files from git diff
    files = changed_files(base, head)
    # Check which packages must be checked
    if any(f.startswith(GLOBAL_PREFIXES) for f in files):
        mode, packages = 'all', []
    else:
        # sort dictionary keys to eliminate duplicates
        packages = sorted({p for p in map(owning_package, files) if p})
        mode = 'some' if packages else 'none'

    # ci.yml references these as 'outputs.mode' and 'outputs.packages'
    # (see lines 38-39)
    outputs = f'mode={mode}\npackages={" ".join(packages)}\n'
    print(outputs, end='')
    # GITHUB_OUTPUT is an environment variable available in Github Actions
    # that we write to here so that Github Actions knows what tests to run
    if 'GITHUB_OUTPUT' in os.environ:
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write(outputs)


if __name__ == '__main__':
    main()
