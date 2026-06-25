"""從 worker_default/fixtures 載入 demo 場景到專案 pm/。"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any


def _fixtures_data_dir(host: Any) -> Path:
  project_data = Path(host.project_root) / "workers" / "_fixtures" / "fixtures"
  if project_data.is_dir() and any(project_data.iterdir()):
    return project_data
  return Path(host.fixtures_seed_root) / "fixtures"


def load_demo_scenario(host: Any, scenario: str) -> list[str]:
  """寫入 pm/ 下任務檔；回傳相對路徑列表。"""
  data = _fixtures_data_dir(host)
  written: list[str] = []
  project_root = Path(host.project_root)

  if scenario == "backend_demo":
    src = data / "backend_demo_task.yaml"
    if not src.is_file():
      raise FileNotFoundError(f"缺少場景檔：{src}")
    dest = project_root / "pm" / "backend_current_task.yaml"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    written.append("pm/backend_current_task.yaml")
    req = data / "shared_requirements_snippet.md"
    if req.is_file():
      shared = project_root / "shared" / "requirements.md"
      shared.parent.mkdir(parents=True, exist_ok=True)
      shutil.copy2(req, shared)
      written.append("shared/requirements.md")
    return written

  if scenario == "scheduler_demo":
    intake_src = data / "scheduler_intake_demo.yaml"
    if not intake_src.is_file():
      raise FileNotFoundError(f"缺少場景檔：{intake_src}")
    dest = project_root / "pm" / "scheduler_intake.yaml"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(intake_src, dest)
    written.append("pm/scheduler_intake.yaml")
    return written

  raise ValueError(f"不支援的 scenario：{scenario!r}")
