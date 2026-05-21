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
    """Return a stable MD5 hex digest of a JSON-serializable dict."""
    return hashlib.md5(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()


def generate_matrix(changes: List[str]) -> List[Dict]:
    """Generate the matrix of changes."""
    matrix = []
    generated = set()

    cfg = get_config()
    default_params = cfg.default_params
    inject_params = cfg.inject_params
    inject_primary_key = cfg.inject_primary_key
    extract_re = re.compile(cfg.extract_re)

    for c in changes:
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
            lookup_key = cur.get(inject_primary_key, "") if inject_primary_key else ""
            matrix.append(
                {
                    **default_params,
                    **inject_params.get(lookup_key, {}),
                    **cur,
                }
            )

    return matrix


def set_output(name: str, value: object) -> None:
    """Set an action output via environment file."""
    line = f"{name}={json.dumps(value)}\n"
    output_fn = os.getenv("GITHUB_OUTPUT")
    if output_fn:
        with open(output_fn, "a") as f:
            f.write(line)
    else:
        sys.stdout.write(line)


def include_file(fn: str) -> bool:
    """Return True if fn should be included."""
    paths_include = get_config().paths_include
    if paths_include is None:
        return True
    return any(fnmatch.fnmatch(fn, m) for m in paths_include)


def ignore_file(fn: str) -> bool:
    """Return True if fn should be excluded."""
    return any(fnmatch.fnmatch(fn, m) for m in (get_config().paths_ignore or []))
