"""Entry point for the pr-changes-matrix-builder."""
from pr_changes import gh, action
from pr_changes.config import get_config


def main():
    """Entrypoint."""
    print("Generating PR changes")
    cfg = get_config()

    # Get the PR changes
    if False:
        gh.auth(cfg.input.github_token)
        files_changed = gh.get_changes(cfg.input.repo, cfg.input.pr_number)
    # Temporarily use a hardcoded list of changes
    else:
        files_changed = [
            ".github/workflows/test_pr_path.yaml",
            "example_1/README.md",
            "example_1/file.txt",
            "example_2/README.md",
        ]

    matrix = action.generate_matrix(files_changed)
    action.set_output("matrix", matrix)


if __name__ == "__main__":
    main()
