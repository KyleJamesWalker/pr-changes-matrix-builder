"""Pytest conftest file."""

import pr_changes.config
import pytest


@pytest.fixture(scope="function", autouse=True)
def configuration(monkeypatch):
    """Fixture to override and setup the project's configuration."""
    if pr_changes.config._config is not None:
        raise ValueError("Configuration dirty initialized before test")

    class ConfigFixtureInterface:
        """Fixture Interface."""

        def __init__(self) -> None:
            self.environ = {
                "INPUT_GITHUB_TOKEN": "test_token",
                "INPUT_PR_NUMBER": "3",
                "INPUT_REPO": "TestUser/testrepo",
                "INPUT_DEFAULT_PARAMS": '{"foo": "bar", "baz": "qux"}',
                "INPUT_INJECT_PRIMARY_KEY": "project_name",
                "INPUT_INJECT_PARAMS": '{"example_1": {"beans": true}}',
                "INPUT_EXTRACT_RE": r"(?P<project_name>.*)/.*",
            }

        @classmethod
        def uninit(cls):
            pr_changes.config.reset()

        def update_env(self, env):
            self.uninit()
            self.environ.clear()
            self.environ.update(env)

    interface = ConfigFixtureInterface()
    monkeypatch.setattr("os.environ", interface.environ)
    yield interface
    interface.uninit()
