"""Entry point for the pr-changes-matrix-builder."""
from pr_changes import gh, action
from pr_changes.config import get_config


def main():
    """Entrypoint."""
    print("Generating PR changes")
    cfg = get_config()

    # Get the PR changes
    gh.auth(cfg.input.github_token)
    files_changed = gh.get_changes(cfg.input.repo, cfg.input.pr_number)

    # Process the files changed
    matrix = action.generate_matrix(files_changed)

    # Output the values for github
    action.set_output("matrix", matrix)
    action.set_output("matrix-populated", True if matrix else False)


if __name__ == "__main__":
    main()
