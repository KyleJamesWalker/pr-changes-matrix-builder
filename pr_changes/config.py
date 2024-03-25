"""Configuration module."""

import yamlsettings

__CONFIG = None


def __validate__(cfg: yamlsettings.yamldict.YAMLDict):
    """Verify all values references in required_keys have been defined.

    Asserts if a value in the required_keys paths is not defined

    Args:
    ----
        cfg: Configuration Settings

    Raises:
    ------
        RuntimeError: When a required key is null

    """
    check_paths = [x.split(".") for x in cfg.get("required_keys", [])]

    def _null_traverse(path, node):
        """Yamlsettings traverse callback."""
        if node is None and any(path[: len(x)] == x for x in check_paths):
            raise RuntimeError("{} is not set".format(".".join(path)))
        return None

    cfg.traverse(_null_traverse)


def __process_config__(cfg: yamlsettings.yamldict.YAMLDict):
    """Process the configuration.

    Args:
    ----
        cfg: Configuration Settings

    """
    __validate__(cfg)

    return cfg


def get_config():
    """Get the configuration."""
    global __CONFIG

    if __CONFIG is None:
        __CONFIG = __process_config__(yamlsettings.load("pkg://pr_changes"))

    return __CONFIG


def reset():
    """Reset the configuration."""
    global __CONFIG
    __CONFIG = None

    # Flush YamlSettings Persistence
    settings_persistence = yamlsettings.registry.get_extension("pkg")._persistence
    if "pr_changes:settings.yaml" in settings_persistence:
        del settings_persistence["pr_changes:settings.yaml"]
