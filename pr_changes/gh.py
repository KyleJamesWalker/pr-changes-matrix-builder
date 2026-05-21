"""Handle all the Github CLI calls."""

import subprocess
import sys
from typing import List


def auth(github_token: str) -> None:
    """Authenticate with Github."""
    if not github_token:
        raise ValueError("Github token is required.")

    result = subprocess.run(
        ["gh", "auth", "login", "--with-token"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        input=github_token.encode(),
    )

    if result.stdout:
        print(result.stdout.decode("utf-8"))
    if result.stderr:
        print(result.stderr.decode("utf-8"), file=sys.stderr)

    if result.returncode != 0:
        sys.exit(result.returncode)


def get_changes(repo: str, pr_number: str) -> List[str]:
    """Get all the changes for a pull request."""
    cmd = [
        "gh",
        "pr",
        "view",
        str(pr_number),
        "--repo",
        repo,
        "--json",
        "files",
        "--jq",
        ".files.[].path",
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode != 0:
        if result.stderr:
            print(result.stderr.decode("utf-8"), file=sys.stderr)
        sys.exit(result.returncode)

    changes = [c for c in result.stdout.decode("utf-8").strip().split("\n") if c]
    print("Changes detected:\n  * ", "\n  * ".join(changes) if changes else "(none)")

    return changes
