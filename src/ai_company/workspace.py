from pathlib import Path

from ai_company.services.migrate import migrate_flat_workspace
from ai_company.store.company_store import CompanyStore

# 舊版扁平沙盒目錄名（僅供 migrate 辨識）
SHARED = "shared"
BACKEND = "backend_workspace"
FRONTEND = "frontend_workspace"
QA = "qa_workspace"
PM = "pm_workspace"

SANDBOX_DIRS = (SHARED, BACKEND, FRONTEND, QA, PM)

SHARED_CHILDREN = (
    Path(SHARED) / "requirements.md",
    Path(SHARED) / "api_docs",
    Path(SHARED) / "builds",
)


def ensure_workspace(root: Path) -> None:
    """建立 Harness 工作區：遷移舊扁平目錄、_company 索引與 projects/ 容器。"""
    root.mkdir(parents=True, exist_ok=True)
    migrate_flat_workspace(root)
    store = CompanyStore(root)
    store.ensure_company_dirs()
    store.ensure_company_index_files()
