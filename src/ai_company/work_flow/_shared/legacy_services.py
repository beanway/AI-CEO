"""過渡期：組裝尚未遷入 modules/ 的服務。刪除 services/ 時移除此檔。"""

from __future__ import annotations

from ai_company.app_deps import AppDeps
from ai_company.services.company_service import CompanyService
from ai_company.store.company_store import CompanyStore
from ai_company.workspace import ensure_workspace


def ensure_workspace_for_deps(deps: AppDeps) -> None:
    ensure_workspace(deps.workspace_root)


def company_service(deps: AppDeps) -> CompanyService:
    ensure_workspace_for_deps(deps)
    store = CompanyStore(deps.workspace_root)
    return CompanyService(deps.workspace_root, store)
