"""Test Configuration."""

import pytest

from pr_changes.config import get_config


def test_default_config(configuration):
    """Test the default configuration test values."""
    cfg = get_config()
    assert cfg.input.pr_number == 3


def test_config_required_values_error(configuration):
    """Test the default configuration test values."""
    configuration.environ.clear()

    with pytest.raises(RuntimeError):
        get_config()


def test_new_config(configuration):
    """Test a full configuration."""
    configuration.update_env(
        {
            "INPUT_PR_NUMBER": "4",
            "INPUT_REPO": "TestUser/testrepo2",
            "INPUT_DEFAULT_PARAMS": '{"foo": "bar2", "baz": "qux2"}',
            "INPUT_INJECT_PRIMARY_KEY": "project_name2",
            "INPUT_INJECT_PARAMS": '{"example_2": {"beans:": true}}',
            "INPUT_EXTRACT_RE": r"(?P<project_name2>.*)/.*",
        }
    )
    cfg = get_config()
    assert cfg.input.pr_number == 4
    assert cfg.input.repo == "TestUser/testrepo2"
    assert cfg.input.default_params == {"foo": "bar2", "baz": "qux2"}
    assert cfg.input.inject.primary_key == "project_name2"
    assert cfg.input.inject.params == {"example_2": {"beans:": True}}
    assert cfg.input.extract_re == r"(?P<project_name2>.*)/.*"
