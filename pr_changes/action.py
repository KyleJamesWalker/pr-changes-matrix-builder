"""PR Changes Primary Action Module."""
import json
import re

from typing import List, Dict
from pr_changes.config import get_config


def generate_matrix(changes: List[str]) -> Dict:
    """Generate the matrix of changes.

    Args:
        changes: List of changed files.

    Returns:
        Fully populated matrix of changes with injected values.
    """
    matrix = []
    # TODO: This should be an option to de-dupe
    #   How should we break up one primary key with many subkeys?
    primary_keys = set()

    cfg = get_config()
    default_params = cfg.input.default_params
    inject_params = cfg.input.inject.params
    inject_primary_key = cfg.input.inject.primary_key
    extract_re = re.compile(cfg.input.extract_re)

    for c in changes:
        cur = extract_re.match(c).groupdict()
        if cur[inject_primary_key] not in primary_keys:
            primary_keys.add(cur[inject_primary_key])
            matrix.append(
                {
                    **default_params,
                    **inject_params.get(cur[inject_primary_key], {}),
                    **cur,
                }
            )

    return {"params": matrix}


def set_output(name: str, value: object) -> None:
    """Set an action output via stdout."""
    json_text = json.dumps(value)
    print(f"::set-output name={name}::'{json_text}'")
