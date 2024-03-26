"""Handle all the Github CLI Class."""

import subprocess
import sys


def auth(github_token: str) -> None:
    """Authenticate with Github."""
    if not github_token:
        raise ValueError("Github token is required.")

    result = subprocess.run(
        ["gh", "auth", "login", "--with-token"],
        stdout=subprocess.PIPE,
        input=github_token.encode(),
    )

    print(result.stdout.decode("utf-8"))

    if result.returncode != 0:
        sys.exit(result.returncode)


def get_changes(repo: str, pr_number: int) -> None:
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
    result = subprocess.run(cmd, stdout=subprocess.PIPE)

    if result.returncode != 0:
        sys.exit(result.returncode)

    changes = result.stdout.decode("utf-8").strip().split("\n")
    print("Changes detected:\n  * ", "\n  * ".join(changes))

    return changes
