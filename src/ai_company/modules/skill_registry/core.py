"""解析 repo 內 skills/registry 目錄。"""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_company.modules.file_store import core as file_store
from ai_company.schemas.workspace_paths import project_dir

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


def find_registered_skills(*, query: str | None = None) -> list[str]:
    ids = list_registered_skill_ids()
    if not query or not query.strip():
        return ids
    q = query.strip().lower()
    return [sid for sid in ids if q in sid.lower()]


def create_registry_skill_stub(skill_id: str, *, description: str = "") -> Path:
    if not skill_id or "/" in skill_id or skill_id.startswith("."):
        raise ValueError("無效的 skill id")
    target = registry_dir() / skill_id
    target.mkdir(parents=True, exist_ok=False)
    body = description.strip() or f"Registry skill `{skill_id}`（框架開發用 stub）。"
    (target / "SKILL.md").write_text(f"# {skill_id}\n\n{body}\n", encoding="utf-8")
    return target


def _load_role_skill_ids(workspace_root, project_id: str, worker_id: str) -> list[str]:
    path = project_dir(workspace_root, project_id) / "workers" / worker_id / "role_skills.yaml"
    if not path.is_file():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    raw = data.get("enabled_skill_ids") or []
    return [str(x) for x in raw]


def resolve_skill_stack(
    workspace_root,
    project_id: str,
    worker_id: str,
) -> list[str]:
    """疊加順序：global → project → role（harness §5.4）。"""
    global_ids = file_store.load_global_skills(workspace_root).enabled_skill_ids
    project_ids = file_store.load_project_skills(workspace_root, project_id).enabled_skill_ids
    role_ids = _load_role_skill_ids(workspace_root, project_id, worker_id)
    ordered: list[str] = []
    seen: set[str] = set()
    for sid in [*global_ids, *project_ids, *role_ids]:
        if sid not in seen:
            ordered.append(sid)
            seen.add(sid)
    return ordered
