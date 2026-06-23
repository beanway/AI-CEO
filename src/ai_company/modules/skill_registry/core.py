"""解析 repo 內 skills/registry 目錄。"""

from __future__ import annotations

from pathlib import Path

REGISTRY_DIRNAME = ("skills", "registry")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def registry_dir() -> Path:
    return repo_root().joinpath(*REGISTRY_DIRNAME)


def list_registered_skill_ids() -> list[str]:
    root = registry_dir()
    if not root.is_dir():
        return []
    ids: list[str] = []
    for child in sorted(root.iterdir()):
        if child.is_dir() and (child / "SKILL.md").is_file():
            ids.append(child.name)
    return ids


def skill_exists(skill_id: str) -> bool:
    if not skill_id or "/" in skill_id or skill_id.startswith("."):
        return False
    return (registry_dir() / skill_id / "SKILL.md").is_file()
