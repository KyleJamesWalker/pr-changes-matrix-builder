"""PR Changes Primary Action Module."""

import fnmatch
import hashlib
import json
import os
import re
import sys

from pr_changes.config import get_config
from typing import Dict, List


def dict_hash(data: Dict) -> str:
    """Generate a hash of a dictionary.

    Args:
    ----
        d: Dictionary to hash.

    Returns:
    -------
        Hash of the dictionary.

    """
    return hashlib.md5(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()


def generate_matrix(changes: List[str]) -> List[Dict]:
    """Generate the matrix of changes.

    Args:
    ----
        changes: List of changed files.

    Returns:
    -------
        Fully populated matrix of changes with injected values.

    """
    matrix = []
    generated = set()

    cfg = get_config()
    default_params = cfg.input.default_params
    inject_params = cfg.input.inject.params
    inject_primary_key = cfg.input.inject.primary_key
    extract_re = re.compile(cfg.input.extract_re)

    for c in changes:
        # Skip files that are ignored or not included
        if ignore_file(c) or not include_file(c):
            continue

        cur_match = extract_re.match(c)
        if cur_match is None:
            print("Warning: Unable to extract data from filename [bad regex]: ", c)
            continue

        cur = cur_match.groupdict()
        cur_hash = dict_hash(cur)
        if cur_hash not in generated:
            generated.add(cur_hash)
            matrix.append(
                {
                    **default_params,
                    **inject_params.get(cur[inject_primary_key], {}),
                    **cur,
                }
            )

    return matrix


def set_output(name: str, value: object) -> None:
    """Set an action output via environment file."""
    json_text = json.dumps(value)
    output_fn = os.getenv("GITHUB_OUTPUT")
    output_file = open(os.getenv("GITHUB_OUTPUT"), "a") if output_fn else sys.stdout
    output_file.write(f"{name}={json_text}\n")

    # Only close the file it it's not stdout
    if output_fn:
        output_file.close()


def include_file(fn: str) -> bool:
    """Check if the filename is an included match.

    Args:
    ----
        fn: Filename to check.

    Returns:
    -------
        True if the file should be included.

    """
    result = False
    if get_config().input.paths.include is None:
        # Default is all files are included
        result |= True

    for m in get_config().input.paths.include or []:
        result |= fnmatch.fnmatch(fn, m)

    return result


def ignore_file(fn: str) -> bool:
    """Check if the filename is an excluded match.

    Args:
    ----
        fn: Filename to check.

    Returns:
    -------
        True if the file should be excluded.

    """
    result = False

    for m in get_config().input.paths.ignore or []:
        result |= fnmatch.fnmatch(fn, m)

    return result
