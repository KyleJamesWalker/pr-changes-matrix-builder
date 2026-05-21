"""Configuration module."""

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Config:
    github_token: str
    repo: str
    pr_number: str
    default_params: Dict[str, Any] = field(default_factory=dict)
    inject_primary_key: Optional[str] = None
    inject_params: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    extract_re: str = "(?P<project_name>.*)/.*"
    paths_include: Optional[List[str]] = None
    paths_ignore: Optional[List[str]] = None


_config: Optional[Config] = None


def _load() -> Config:
    def _env(key: str) -> Optional[str]:
        return os.environ.get(key) or None

    def _json(key: str, default: Any) -> Any:
        val = _env(key)
        return json.loads(val) if val is not None else default

    token = _env("INPUT_GITHUB_TOKEN")
    repo = _env("INPUT_REPO")
    pr_number = _env("INPUT_PR_NUMBER")

    if not token:
        raise RuntimeError("INPUT_GITHUB_TOKEN is not set")
    if not repo:
        raise RuntimeError("INPUT_REPO is not set")
    if not pr_number:
        raise RuntimeError("INPUT_PR_NUMBER is not set")

    return Config(
        github_token=token,
        repo=repo,
        pr_number=pr_number,
        default_params=_json("INPUT_DEFAULT_PARAMS", {}),
        inject_primary_key=_env("INPUT_INJECT_PRIMARY_KEY"),
        inject_params=_json("INPUT_INJECT_PARAMS", {}),
        extract_re=_env("INPUT_EXTRACT_RE") or "(?P<project_name>.*)/.*",
        paths_include=_json("INPUT_PATHS_INCLUDE", None),
        paths_ignore=_json("INPUT_PATHS_IGNORE", None),
    )


def get_config() -> Config:
    global _config
    if _config is None:
        _config = _load()
    return _config


def reset() -> None:
    global _config
    _config = None
