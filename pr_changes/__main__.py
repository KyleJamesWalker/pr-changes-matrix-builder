"""Entry point for the pr-changes-matrix-builder."""

from pr_changes import action, gh
from pr_changes.config import get_config


def main():
    """Entrypoint."""
    print("Generating PR changes")
    cfg = get_config()

    gh.auth(cfg.github_token)
    files_changed = gh.get_changes(cfg.repo, cfg.pr_number)

    matrix = action.generate_matrix(files_changed)

    action.set_output("matrix", matrix)
    action.set_output("matrix-populated", bool(matrix))


if __name__ == "__main__":
    main()
