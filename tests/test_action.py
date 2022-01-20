"""Test Action."""
from pr_changes.action import generate_matrix


def test_action_simple(configuration):
    """Test the action with a simple configuration."""
    result = generate_matrix(
        [
            ".github/workflows/test-workflow.yml",
            "example_1/file.txt",
            "example_1/README.md",
            "example_2/README.md",
        ]
    )

    assert result == [
        {"baz": "qux", "foo": "bar", "project_name": ".github/workflows"},
        {"baz": "qux", "beans": True, "foo": "bar", "project_name": "example_1"},
        {"baz": "qux", "foo": "bar", "project_name": "example_2"},
    ]


def test_action_simple_ignore_workflow_changes(configuration):
    """Verify workflow changes are not surfaced."""
    configuration.update_env(
        {
            "INPUT_PR_NUMBER": "3",
            "INPUT_REPO": "TestUser/testrepo",
            "INPUT_DEFAULT_PARAMS": '{"foo": "bar", "baz": "qux"}',
            "INPUT_INJECT_PRIMARY_KEY": "project_name",
            "INPUT_INJECT_PARAMS": '{"example_1": {"beans": true}}',
            "INPUT_EXTRACT_RE": r"(?P<project_name>.*)/.*",
            "INPUT_PATHS_IGNORE": '[".github/**"]',
        }
    )
    result = generate_matrix(
        [
            ".github/workflows/test-workflow.yml",
            "example_1/file.txt",
            "example_1/README.md",
            "example_2/README.md",
        ]
    )

    assert result == [
        {"baz": "qux", "beans": True, "foo": "bar", "project_name": "example_1"},
        {"baz": "qux", "foo": "bar", "project_name": "example_2"},
    ]


def test_action_simple_include_folders_with_txt_changes(configuration):
    """Verify workflow changes are not surfaced."""
    configuration.update_env(
        {
            "INPUT_PR_NUMBER": "3",
            "INPUT_REPO": "TestUser/testrepo",
            "INPUT_DEFAULT_PARAMS": '{"foo": "bar", "baz": "qux"}',
            "INPUT_INJECT_PRIMARY_KEY": "project_name",
            "INPUT_INJECT_PARAMS": '{"example_1": {"beans": true}}',
            "INPUT_EXTRACT_RE": r"(?P<project_name>.*)/(?P<subpath>.*)",
            "INPUT_PATHS_INCLUDE": '["**/file.txt"]',
        }
    )
    result = generate_matrix(
        [
            ".github/workflows/test-workflow.yml",
            "example_1/file.txt",
            "example_1/README.md",
            "example_2/README.md",
        ]
    )

    assert result == [
        {
            "baz": "qux",
            "beans": True,
            "foo": "bar",
            "project_name": "example_1",
            "subpath": "file.txt",
        },
    ]


def test_many_combinations(configuration):
    """Test many changes in one folder."""
    configuration.update_env(
        {
            "INPUT_PR_NUMBER": "3",
            "INPUT_REPO": "TestUser/testrepo",
            "INPUT_DEFAULT_PARAMS": '{"foo": "bar", "baz": "qux"}',
            "INPUT_INJECT_PRIMARY_KEY": "project_name",
            "INPUT_INJECT_PARAMS": '{"example_1": {"beans": true}}',
            "INPUT_EXTRACT_RE": r"(?P<project_name>.*)/(?P<subpath>.*)",
            "INPUT_PATHS_INCLUDE": '["**/*.txt"]',
        }
    )
    result = generate_matrix(
        [
            "example_1/file.txt",
            "example_1/file2.txt",
        ]
    )

    assert result == [
        {
            "baz": "qux",
            "beans": True,
            "foo": "bar",
            "project_name": "example_1",
            "subpath": "file.txt",
        },
        {
            "baz": "qux",
            "beans": True,
            "foo": "bar",
            "project_name": "example_1",
            "subpath": "file2.txt",
        },
    ]


def test_action_no_changes(configuration):
    """Verify workflow surfaces nothing."""
    configuration.update_env(
        {
            "INPUT_PR_NUMBER": "3",
            "INPUT_REPO": "TestUser/testrepo",
            "INPUT_DEFAULT_PARAMS": '{"foo": "bar", "baz": "qux"}',
            "INPUT_INJECT_PRIMARY_KEY": "project_name",
            "INPUT_EXTRACT_RE": r"(?P<project_name>.*)/.*",
            "INPUT_PATHS_IGNORE": '["**"]',
        }
    )
    result = generate_matrix([])

    assert result == []
