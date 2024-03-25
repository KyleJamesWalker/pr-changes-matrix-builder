"""Pytest conftest file."""

import pr_changes.config
import pytest
import yamlsettings


@pytest.fixture(scope="function", autouse=True)
def configuration(monkeypatch):
    """Fixture to override and setup the project's configuration.

    Note: If a tests needs custom configuration the fixture returns an
    interface, with the following functions:

        * uninit: Restores the config to an uninitialized state
        * init: Sets the config to an initialized state
        * env: Sets the environment to a given dictionary

    """
    if pr_changes.config.__CONFIG is not None:
        raise ValueError("Local configuration dirty initialized before test")

    settings_persistence = yamlsettings.registry.get_extension("pkg")._persistence
    if "pr_changes:settings.yaml" in settings_persistence:
        raise ValueError("Yamlsettings configuration initialized before test")

    class ConfigFixtureInterface:
        """Fixture Interface."""

        def __init__(self) -> None:
            """Initialize the interface."""
            self.environ = {
                "INPUT_PR_NUMBER": "3",
                "INPUT_REPO": "TestUser/testrepo",
                "INPUT_DEFAULT_PARAMS": '{"foo": "bar", "baz": "qux"}',
                "INPUT_INJECT_PRIMARY_KEY": "project_name",
                "INPUT_INJECT_PARAMS": '{"example_1": {"beans": true}}',
                "INPUT_EXTRACT_RE": r"(?P<project_name>.*)/.*",
            }

        @classmethod
        def uninit(cls):
            """Restore init state."""
            pr_changes.config.reset()

        def update_env(self, env: None):
            """Update the environment for a new configuration."""
            self.uninit()
            self.environ.clear()
            self.environ.update(env)

    interface = ConfigFixtureInterface()

    # Mock out the environment for loading overrides
    monkeypatch.setattr("os.environ", interface.environ)

    yield interface

    # Restore the config to an uninitialized state
    interface.uninit()
