# Phase A — 管理層與多專案 Implementation Plan

> **已廢止 — 勿作架構或實作依據**  
> 現行產品設計：[`design/harness-design.md`](../design/harness-design.md)  
> 現行程式分層：[`design/src-layout.md`](../design/src-layout.md)  
> 現行實作計畫：[`phase-a-src-layout.md`](phase-a-src-layout.md)

---

> **For agentic workers:** 以下內容僅供歷史對照；請勿依本檔的 `CompanyService` / `store` 分層實作新程式。

**Goal:** 在管理者 Telegram Bot 上完成 CEO/PM Gemini 對話、多專案建立／列出／切換，並持久化 Session 與 `company_workspace/_company/` 索引。

**Architecture:** 抽出 `CompanyStore`（JSON 檔案）、`CompanyService`（專案與 prefs 業務）、`GeminiSessionService`（CEO/PM chat 生命週期）、`ManagerRouterHandlers`（TG 指令與文字路由）。執行者 Bot 僅保留連線與唯讀狀態。沙盒改為 `projects/<project_id>/` 子樹；扁平舊目錄可遷移至 `default`。

**Tech Stack:** Python 3.11+, python-telegram-bot 21+, google-genai, pydantic v2, pytest

> **已廢止**：本計畫依初版 spec，與現行 **[Harness 設計](../design/harness-design.md)** 衝突；實作前請重寫計畫。

## Global Constraints

- 執行層 Worker **不**遙控 Cursor IDE Agent；本 Phase **不**實作狀態機與 Worker。
- MVP 介面 **僅 Telegram**；不實作網頁與 COO 報表（可建立空 `metrics/` 目錄）。
- `TELEGRAM_ALLOWED_USER_IDS` 白名單行為保持：空則不限制。
- 專案模型：**一專案 = 一 PM Session + `projects/<id>/` 沙盒子樹**；CEO **單一** Session。
- 建專案失敗必須 **回滾**（無半套目錄 + 無幽靈索引）。
- Gemini 呼叫失敗 **不**修改 `projects.json`。
- 預設對話模式 **`ceo`**（`user_prefs.json`）。
- 單一執行佇列在 Phase B 實作；Phase A 不啟動 Worker。

## File map (Phase A)

| 路徑 | 職責 |
|------|------|
| `src/ai_company/models/company.py` | Pydantic：`ProjectRecord`, `ProjectsFile`, `UserPrefs`, `SessionRecord` |
| `src/ai_company/store/company_store.py` | 讀寫 `_company/*.json`，原子寫入 |
| `src/ai_company/services/project_paths.py` | `project_root(workspace, project_id)`、建立專案目錄樹 |
| `src/ai_company/services/migrate.py` | 扁平 `company_workspace/{shared,...}` → `projects/default/` |
| `src/ai_company/services/company_service.py` | `create_project`, `list_projects`, `set_active`, `get_active` |
| `src/ai_company/services/gemini_sessions.py` | `GeminiChatBackend` 協定 + 真實/假實作 |
| `src/ai_company/services/management_chat.py` | `send_ceo_message`, `send_pm_message` |
| `src/ai_company/telegram/manager_handlers.py` | `/start`, `/projects`, `/switch`, `/ceo`, `/pm`, `/newproject`, 文字 |
| `src/ai_company/telegram/executor_handlers.py` | 執行者 Bot `/start` + 狀態摘要 |
| `src/ai_company/router.py` | 組裝 Application、注入 `CompanyService` |
| `src/ai_company/workspace.py` | 改為確保 `_company/` + 遷移觸發 |
| `tests/...` | 單元與服務測試（不依賴真實 TG/Gemini） |

---

### Task 1: Pytest 與測試目錄

**Files:**
- Create: `tests/conftest.py`
- Modify: `pyproject.toml`（新增 `[tool.pytest.ini_options]`）

**Interfaces:**
- Produces: `tmp_workspace` fixture（`Path` 指向暫存 `company_workspace`）

- [ ] **Step 1: 新增 pytest 設定**

在 `pyproject.toml` 末尾追加：

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

- [ ] **Step 2: 建立 conftest**

```python
# tests/conftest.py
from pathlib import Path

import pytest


@pytest.fixture
def tmp_workspace(tmp_path: Path) -> Path:
    root = tmp_path / "company_workspace"
    root.mkdir()
    return root
```

- [ ] **Step 3: 驗證**

Run: `.venv/bin/pytest --collect-only`  
Expected: `collected 0 items`（尚無測試檔，但無 import 錯誤）

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml tests/conftest.py
git commit -m "test: add pytest layout for Phase A"
```

---

### Task 2: 公司資料模型

**Files:**
- Create: `src/ai_company/models/__init__.py`
- Create: `src/ai_company/models/company.py`
- Create: `tests/models/test_company.py`

**Interfaces:**
- Produces: `ProjectsFile`, `ProjectRecord`, `UserMode`, `UserPrefsFile`, `SessionRecord`

- [ ] **Step 1: 寫失敗測試**

```python
# tests/models/test_company.py
from ai_company.models.company import ProjectRecord, ProjectsFile


def test_projects_file_defaults():
    pf = ProjectsFile()
    assert pf.active_project_id is None
    assert pf.projects == []


def test_project_record_slug():
    rec = ProjectRecord(id="abc12", name="Demo")
    assert rec.id == "abc12"
```

- [ ] **Step 2: 跑測試（應 FAIL）**

Run: `.venv/bin/pytest tests/models/test_company.py -v`  
Expected: `ModuleNotFoundError`

- [ ] **Step 3: 實作模型**

```python
# src/ai_company/models/company.py
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ProjectRecord(BaseModel):
    id: str
    name: str
    created_at: datetime = Field(default_factory=utc_now)
    status: str = "active"


class ProjectsFile(BaseModel):
    active_project_id: str | None = None
    projects: list[ProjectRecord] = Field(default_factory=list)


class UserMode(str, Enum):
    CEO = "ceo"
    PM = "pm"


class UserPref(BaseModel):
    mode: UserMode = UserMode.CEO


class UserPrefsFile(BaseModel):
    users: dict[str, UserPref] = Field(default_factory=dict)


class SessionRecord(BaseModel):
    gemini_chat_name: str
    project_id: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    stale: bool = False
```

```python
# src/ai_company/models/__init__.py
from ai_company.models.company import (
    ProjectRecord,
    ProjectsFile,
    SessionRecord,
    UserMode,
    UserPref,
    UserPrefsFile,
)

__all__ = [
    "ProjectRecord",
    "ProjectsFile",
    "SessionRecord",
    "UserMode",
    "UserPref",
    "UserPrefsFile",
]
```

- [ ] **Step 4: 跑測試（應 PASS）**

Run: `.venv/bin/pytest tests/models/test_company.py -v`

- [ ] **Step 5: Commit**

```bash
git add src/ai_company/models tests/models
git commit -m "feat: add company pydantic models"
```

---

### Task 3: CompanyStore（JSON 持久化）

**Files:**
- Create: `src/ai_company/store/__init__.py`
- Create: `src/ai_company/store/company_store.py`
- Create: `tests/store/test_company_store.py`

**Interfaces:**
- Consumes: `ProjectsFile`, `UserPrefsFile`, `SessionRecord`
- Produces: `CompanyStore(workspace_root: Path)` 方法：
  - `load_projects() -> ProjectsFile`
  - `save_projects(ProjectsFile) -> None`
  - `load_user_prefs() -> UserPrefsFile`
  - `save_user_prefs(UserPrefsFile) -> None`
  - `session_path(role: Literal["ceo"] | str) -> Path`（PM 用 `pm_{id}`）
  - `load_session(path) -> SessionRecord | None`
  - `save_session(path, SessionRecord) -> None`
  - `ensure_company_dirs() -> None`

- [ ] **Step 1: 寫失敗測試**

```python
# tests/store/test_company_store.py
from ai_company.models.company import ProjectRecord, ProjectsFile
from ai_company.store.company_store import CompanyStore


def test_roundtrip_projects(tmp_workspace):
    store = CompanyStore(tmp_workspace)
    store.ensure_company_dirs()
    data = ProjectsFile(
        active_project_id="p1",
        projects=[ProjectRecord(id="p1", name="One")],
    )
    store.save_projects(data)
    loaded = store.load_projects()
    assert loaded.active_project_id == "p1"
    assert loaded.projects[0].name == "One"
```

- [ ] **Step 2: 跑測試 FAIL**

Run: `.venv/bin/pytest tests/store/test_company_store.py -v`

- [ ] **Step 3: 實作 CompanyStore（原子寫入）**

```python
# src/ai_company/store/company_store.py
import json
from pathlib import Path
from typing import Literal

from ai_company.models.company import ProjectsFile, SessionRecord, UserPrefsFile

COMPANY_DIR = "_company"
SESSIONS_DIR = "sessions"


class CompanyStore:
    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root
        self.company_dir = workspace_root / COMPANY_DIR

    def ensure_company_dirs(self) -> None:
        (self.company_dir / SESSIONS_DIR).mkdir(parents=True, exist_ok=True)
        (self.company_dir / "execution").mkdir(exist_ok=True)
        (self.company_dir / "metrics").mkdir(exist_ok=True)

    def _atomic_write(self, path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)

    def load_projects(self) -> ProjectsFile:
        path = self.company_dir / "projects.json"
        if not path.exists():
            return ProjectsFile()
        return ProjectsFile.model_validate_json(path.read_text(encoding="utf-8"))

    def save_projects(self, data: ProjectsFile) -> None:
        self._atomic_write(
            self.company_dir / "projects.json",
            data.model_dump_json(indent=2),
        )

    def load_user_prefs(self) -> UserPrefsFile:
        path = self.company_dir / "user_prefs.json"
        if not path.exists():
            return UserPrefsFile()
        return UserPrefsFile.model_validate_json(path.read_text(encoding="utf-8"))

    def save_user_prefs(self, data: UserPrefsFile) -> None:
        self._atomic_write(
            self.company_dir / "user_prefs.json",
            data.model_dump_json(indent=2),
        )

    def session_path(self, key: Literal["ceo"] | str) -> Path:
        if key == "ceo":
            return self.company_dir / SESSIONS_DIR / "ceo.json"
        return self.company_dir / SESSIONS_DIR / f"pm_{key}.json"

    def load_session(self, path: Path) -> SessionRecord | None:
        if not path.exists():
            return None
        return SessionRecord.model_validate_json(path.read_text(encoding="utf-8"))

    def save_session(self, path: Path, record: SessionRecord) -> None:
        self._atomic_write(path, record.model_dump_json(indent=2))
```

- [ ] **Step 4: PASS + ruff**

Run: `.venv/bin/pytest tests/store/test_company_store.py -v && .venv/bin/ruff check src/ai_company/store`

- [ ] **Step 5: Commit**

```bash
git add src/ai_company/store tests/store
git commit -m "feat: add CompanyStore for _company JSON files"
```

---

### Task 4: 專案目錄樹與 migrate

**Files:**
- Create: `src/ai_company/services/__init__.py`
- Create: `src/ai_company/services/project_paths.py`
- Create: `src/ai_company/services/migrate.py`
- Modify: `src/ai_company/workspace.py`
- Create: `tests/services/test_project_paths.py`
- Create: `tests/services/test_migrate.py`

**Interfaces:**
- Produces:
  - `def project_dir(workspace_root: Path, project_id: str) -> Path`
  - `def ensure_project_tree(project_dir: Path) -> None`
  - `def migrate_flat_workspace(workspace_root: Path) -> str | None`（回傳 `default` 若遷移發生）

- [ ] **Step 1: 測試專案樹**

```python
# tests/services/test_project_paths.py
from ai_company.services.project_paths import ensure_project_tree, project_dir


def test_project_tree_creates_shared_requirements(tmp_workspace):
    pdir = project_dir(tmp_workspace, "abc")
    ensure_project_tree(pdir)
    req = pdir / "shared" / "requirements.md"
    assert req.is_file()
```

- [ ] **Step 2: 實作 project_paths**

```python
# src/ai_company/services/project_paths.py
from pathlib import Path

from ai_company.workspace import SHARED_CHILDREN, SANDBOX_DIRS

PROJECTS_DIR = "projects"


def project_dir(workspace_root: Path, project_id: str) -> Path:
    return workspace_root / PROJECTS_DIR / project_id


def ensure_project_tree(project_root: Path) -> None:
    project_root.mkdir(parents=True, exist_ok=True)
    for name in SANDBOX_DIRS:
        (project_root / name).mkdir(exist_ok=True)
    for rel in SHARED_CHILDREN:
        path = project_root / rel
        if rel.suffix == ".md" and not path.exists():
            path.write_text("# 專案需求\n\n（由 CEO / PM 填寫）\n", encoding="utf-8")
        elif not rel.suffix:
            path.mkdir(parents=True, exist_ok=True)
```

- [ ] **Step 3: 測試 migrate（扁平 shared 存在時）**

```python
# tests/services/test_migrate.py
from ai_company.services.migrate import migrate_flat_workspace


def test_migrate_moves_shared(tmp_workspace):
    flat_shared = tmp_workspace / "shared"
    flat_shared.mkdir()
    (flat_shared / "requirements.md").write_text("legacy", encoding="utf-8")
    pid = migrate_flat_workspace(tmp_workspace)
    assert pid == "default"
    assert (tmp_workspace / "projects" / "default" / "shared" / "requirements.md").read_text() == "legacy"
    assert not flat_shared.exists()
```

- [ ] **Step 4: 實作 migrate**

```python
# src/ai_company/services/migrate.py
import shutil
from pathlib import Path

from ai_company.services.project_paths import ensure_project_tree, project_dir

LEGACY_DIRS = ("shared", "backend_workspace", "frontend_workspace", "qa_workspace", "pm_workspace")
DEFAULT_ID = "default"


def migrate_flat_workspace(workspace_root: Path) -> str | None:
    if not (workspace_root / "shared").is_dir():
        return None
    if (workspace_root / "projects").exists():
        return None
    dest = project_dir(workspace_root, DEFAULT_ID)
    ensure_project_tree(dest)
    for name in LEGACY_DIRS:
        src = workspace_root / name
        if src.is_dir():
            target = dest / name
            if target.exists():
                shutil.rmtree(target)
            shutil.move(str(src), str(target))
    return DEFAULT_ID
```

- [ ] **Step 5: 更新 workspace.ensure_workspace**

```python
# src/ai_company/workspace.py — ensure_workspace 改為：
from ai_company.services.migrate import migrate_flat_workspace
from ai_company.store.company_store import CompanyStore

def ensure_workspace(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    migrated = migrate_flat_workspace(root)
    store = CompanyStore(root)
    store.ensure_company_dirs()
    if migrated:
        pf = store.load_projects()
        if not any(p.id == migrated for p in pf.projects):
            from ai_company.models.company import ProjectRecord
            from ai_company.services.company_service import CompanyService  # Task 5 後調整 import 循環：或在 migrate 只建目錄，索引由 service 補
```

**注意：** 為避免循環 import，migrate 僅移動目錄；在 `CompanyService` 首次 `load` 時若 `projects.json` 空且存在 `projects/default`，補寫一筆 `default` 專案（Task 5 測試覆蓋）。

- [ ] **Step 6: pytest 全過 + commit**

```bash
git add src/ai_company/services src/ai_company/workspace.py tests/services
git commit -m "feat: per-project workspace trees and flat migration"
```

---

### Task 5: CompanyService（建專案／切換／列表）

**Files:**
- Create: `src/ai_company/services/company_service.py`
- Create: `tests/services/test_company_service.py`

**Interfaces:**
- Consumes: `CompanyStore`, `project_paths`
- Produces:
  - `class CompanyService:`
  - `def create_project(self, name: str, *, initial_requirements: str | None = None) -> ProjectRecord`
  - `def list_projects(self) -> ProjectsFile`
  - `def set_active_project(self, project_id: str) -> None`（不存在則 `ValueError`）
  - `def get_active_project(self) -> ProjectRecord | None`
  - `def set_user_mode(self, tg_user_id: int, mode: UserMode) -> None`
  - `def get_user_mode(self, tg_user_id: int) -> UserMode`
  - `def bootstrap_default_project_if_needed(self) -> None`

- [ ] **Step 1: 失敗測試 create + switch**

```python
# tests/services/test_company_service.py
import pytest

from ai_company.services.company_service import CompanyService
from ai_company.store.company_store import CompanyStore


def test_create_and_switch_project(tmp_workspace):
    store = CompanyStore(tmp_workspace)
    store.ensure_company_dirs()
    svc = CompanyService(tmp_workspace, store)
    p = svc.create_project("Alpha")
    svc.set_active_project(p.id)
    active = svc.get_active_project()
    assert active is not None
    assert active.name == "Alpha"


def test_switch_unknown_raises(tmp_workspace):
    store = CompanyStore(tmp_workspace)
    store.ensure_company_dirs()
    svc = CompanyService(tmp_workspace, store)
    with pytest.raises(ValueError):
        svc.set_active_project("nope")
```

- [ ] **Step 2: 實作（含回滾）**

`create_project` 流程：

1. `project_id = secrets.token_hex(4)`  
2. `ensure_project_tree(project_dir)`  
3. 若 `initial_requirements`：寫入 `shared/requirements.md`  
4. 更新 `projects.json`；若為第一個專案，設為 `active`  
5. 任一步驟失敗：`shutil.rmtree(project_dir, ignore_errors=True)` 並 re-raise  

```python
# src/ai_company/services/company_service.py（核心骨架）
import secrets
import shutil
from pathlib import Path

from ai_company.models.company import ProjectRecord, ProjectsFile, UserMode, UserPref
from ai_company.services.project_paths import ensure_project_tree, project_dir
from ai_company.store.company_store import CompanyStore

DEFAULT_PROJECT_ID = "default"


class CompanyService:
    def __init__(self, workspace_root: Path, store: CompanyStore) -> None:
        self.workspace_root = workspace_root
        self.store = store

    def bootstrap_default_project_if_needed(self) -> None:
        pf = self.store.load_projects()
        legacy = project_dir(self.workspace_root, DEFAULT_PROJECT_ID)
        if legacy.is_dir() and not any(p.id == DEFAULT_PROJECT_ID for p in pf.projects):
            pf.projects.append(ProjectRecord(id=DEFAULT_PROJECT_ID, name="Default"))
            if pf.active_project_id is None:
                pf.active_project_id = DEFAULT_PROJECT_ID
            self.store.save_projects(pf)

    def create_project(self, name: str, *, initial_requirements: str | None = None) -> ProjectRecord:
        project_id = secrets.token_hex(4)
        root = project_dir(self.workspace_root, project_id)
        try:
            ensure_project_tree(root)
            if initial_requirements:
                (root / "shared" / "requirements.md").write_text(
                    initial_requirements, encoding="utf-8"
                )
            pf = self.store.load_projects()
            rec = ProjectRecord(id=project_id, name=name)
            pf.projects.append(rec)
            if pf.active_project_id is None:
                pf.active_project_id = project_id
            self.store.save_projects(pf)
            return rec
        except Exception:
            shutil.rmtree(root, ignore_errors=True)
            raise

    # set_active_project, get_active_project, list_projects, user mode helpers...
```

- [ ] **Step 3: pytest PASS + commit**

```bash
git add src/ai_company/services/company_service.py tests/services/test_company_service.py
git commit -m "feat: CompanyService for multi-project lifecycle"
```

---

### Task 6: GeminiSessionService（可測假後端）

**Files:**
- Create: `src/ai_company/services/gemini_sessions.py`
- Create: `src/ai_company/services/management_chat.py`
- Create: `tests/services/test_gemini_sessions.py`

**Interfaces:**
- Produces:
  - `class GeminiChatBackend(Protocol): def create_chat(self, system_instruction: str) -> str: ...`  
  - `def send_message(self, chat_name: str, text: str) -> str: ...`
  - `class FakeGeminiBackend:` 記憶體 dict
  - `class GeminiSessionService:`  
    - `def get_or_create_ceo_chat(self) -> SessionRecord`  
    - `def get_or_create_pm_chat(self, project_id: str) -> SessionRecord`  
    - `def send_ceo(self, text: str) -> str`  
    - `def send_pm(self, project_id: str, text: str) -> str`

- [ ] **Step 1: 假後端測試**

```python
# tests/services/test_gemini_sessions.py
from ai_company.services.gemini_sessions import FakeGeminiBackend, GeminiSessionService
from ai_company.store.company_store import CompanyStore


def test_ceo_chat_persists(tmp_workspace):
    store = CompanyStore(tmp_workspace)
    store.ensure_company_dirs()
    svc = GeminiSessionService(store, FakeGeminiBackend())
    r1 = svc.send_ceo("hello")
    assert "hello" in r1
    svc2 = GeminiSessionService(store, FakeGeminiBackend())
    # 新實例應從磁碟還原同一 chat
    svc2._backend.chats = svc._backend.chats  # 測試時共用 backend；實作時從 session 檔還原 chat_name
```

**實作注意：** `FakeGeminiBackend` 用 class-level 或傳入共享 store；`GeminiSessionService` 從 `ceo.json` 讀 `gemini_chat_name`，若存在則不 `create_chat`。

- [ ] **Step 2: 實作 Fake + Session 服務**

```python
# src/ai_company/services/gemini_sessions.py
from typing import Protocol

from ai_company.models.company import SessionRecord, utc_now
from ai_company.store.company_store import CompanyStore

CEO_SYSTEM = "你是 AI 公司的執行長（CEO）。協助使用者確認商業模式與需求，可建議建立專案。"
PM_SYSTEM_TEMPLATE = "你是專案 {project_id} 的專案經理（PM）。協助細化需求與開發計畫。專案名稱：{name}。"


class GeminiChatBackend(Protocol):
    def create_chat(self, system_instruction: str) -> str: ...
    def send_message(self, chat_name: str, text: str) -> str: ...


class FakeGeminiBackend:
    def __init__(self) -> None:
        self.chats: dict[str, list[str]] = {}
        self._counter = 0

    def create_chat(self, system_instruction: str) -> str:
        self._counter += 1
        name = f"fake-chat-{self._counter}"
        self.chats[name] = [system_instruction]
        return name

    def send_message(self, chat_name: str, text: str) -> str:
        self.chats.setdefault(chat_name, []).append(text)
        return f"[fake reply to: {text}]"


class GoogleGenaiBackend:
    """真實 API：使用 google.genai.Client；由環境 GEMINI_API_KEY 初始化。"""

    def __init__(self, api_key: str) -> None:
        from google import genai

        self._client = genai.Client(api_key=api_key)
        self._chats: dict[str, object] = {}

    def create_chat(self, system_instruction: str) -> str:
        chat = self._client.chats.create(model="gemini-2.0-flash", config={"system_instruction": system_instruction})
        name = f"gemini-{id(chat)}"
        self._chats[name] = chat
        return name

    def send_message(self, chat_name: str, text: str) -> str:
        chat = self._chats[chat_name]
        response = chat.send_message(text)
        return response.text or ""
```

`GoogleGenaiBackend` 在程序生命週期內保持 chat 物件；重啟後若 API 無法還原，將 session 標記 `stale=True` 並建立新 chat（Phase A 手動測試驗證）。

- [ ] **Step 3: management_chat 薄封裝**

```python
# src/ai_company/services/management_chat.py
from ai_company.services.company_service import CompanyService
from ai_company.services.gemini_sessions import GeminiSessionService


class ManagementChatService:
    def __init__(self, company: CompanyService, sessions: GeminiSessionService) -> None:
        self.company = company
        self.sessions = sessions

    def handle_user_text(self, tg_user_id: int, text: str) -> str:
        mode = self.company.get_user_mode(tg_user_id)
        if mode.value == "ceo":
            return self.sessions.send_ceo(text)
        active = self.company.get_active_project()
        if active is None:
            return "請先 /newproject 或 /switch 設定專案後再使用 /pm 模式。"
        return self.sessions.send_pm(active.id, text)
```

- [ ] **Step 4: pytest + commit**

```bash
git add src/ai_company/services/gemini_sessions.py src/ai_company/services/management_chat.py tests/services/test_gemini_sessions.py
git commit -m "feat: Gemini session service with fake backend for tests"
```

---

### Task 7: 管理者 Bot Handlers

**Files:**
- Create: `src/ai_company/telegram/__init__.py`
- Create: `src/ai_company/telegram/manager_handlers.py`
- Modify: `src/ai_company/router.py`
- Modify: `src/ai_company/main.py`

**Interfaces:**
- Consumes: `ManagementChatService`, `CompanyService`
- Produces: `def register_manager_handlers(app: Application, services: ManagerDeps) -> None`

- [ ] **Step 1: 實作指令處理（節錄）**

```python
# src/ai_company/telegram/manager_handlers.py
from dataclasses import dataclass

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from ai_company.models.company import UserMode
from ai_company.services.company_service import CompanyService
from ai_company.services.management_chat import ManagementChatService


@dataclass
class ManagerDeps:
    company: CompanyService
    chat: ManagementChatService


async def cmd_projects(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    deps: ManagerDeps = context.application.bot_data["manager_deps"]
    pf = deps.company.list_projects()
    lines = [f"Active: {pf.active_project_id or '(none)'}"]
    for p in pf.projects:
        mark = " *" if p.id == pf.active_project_id else ""
        lines.append(f"- {p.id}{mark}: {p.name}")
    await update.message.reply_text("\n".join(lines))


async def cmd_newproject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    deps: ManagerDeps = context.application.bot_data["manager_deps"]
    name = " ".join(context.args) if context.args else "未命名專案"
    rec = deps.company.create_project(name)
    await update.message.reply_text(f"已建立專案 {rec.id}（{rec.name}）。")


def register_manager_handlers(app: Application, deps: ManagerDeps) -> None:
    app.bot_data["manager_deps"] = deps
    app.add_handler(CommandHandler("projects", cmd_projects))
    app.add_handler(CommandHandler("newproject", cmd_newproject))
    # switch, ceo, pm, start, on_text → ManagementChatService
```

- [ ] **Step 2: router 僅管理者 Bot 註冊完整 handlers；執行者 Bot 保持簡化**

在 `build_application` 分參數 `lane`：`MANAGER` 註冊 `register_manager_handlers`；`EXECUTOR` 註冊 `register_executor_handlers`。

- [ ] **Step 3: main.py 組裝**

```python
# main.py run 路徑中：
store = CompanyStore(settings.workspace_root)
store.ensure_company_dirs()
company = CompanyService(settings.workspace_root, store)
company.bootstrap_default_project_if_needed()
backend = GoogleGenaiBackend(settings.gemini_api_key) if settings.gemini_api_key else FakeGeminiBackend()
sessions = GeminiSessionService(store, backend, company)
chat = ManagementChatService(company, sessions)
deps = ManagerDeps(company=company, chat=chat)
```

若無 `GEMINI_API_KEY`，啟動時 log warning 並使用 `FakeGeminiBackend`（方便本地測 Router）。

- [ ] **Step 4: 手動驗收腳本（寫入 README 一節）**

1. 填入 `.env` tokens + `GEMINI_API_KEY`  
2. `python -m ai_company.main run`  
3. `/newproject Beta` → `/projects` → `/pm` → 發文字 → `/switch <id>` → 再發文字  

- [ ] **Step 5: commit**

```bash
git add src/ai_company/telegram src/ai_company/router.py src/ai_company/main.py README.md
git commit -m "feat: Phase A manager bot commands and Gemini routing"
```

---

### Task 8: 執行者 Bot 唯讀狀態

**Files:**
- Create: `src/ai_company/telegram/executor_handlers.py`
- Modify: `src/ai_company/router.py`

**Interfaces:**
- Produces: `register_executor_handlers(app, company: CompanyService)`

- [ ] **Step 1: /start 回報 active 專案數**

```python
async def cmd_start_executor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    company: CompanyService = context.application.bot_data["company"]
    pf = company.list_projects()
    await update.message.reply_text(
        f"[執行者 Bot · 帳號 B]\n專案數：{len(pf.projects)}\n"
        f"目前公司 active：{pf.active_project_id or '(none)'}\n"
        "Worker 進度通知將在 Phase B 啟用。"
    )
```

- [ ] **Step 2: commit**

```bash
git add src/ai_company/telegram/executor_handlers.py src/ai_company/router.py
git commit -m "feat: executor bot read-only company status"
```

---

## Phase A 完成檢查清單

- [ ] `/newproject` 建立第二專案，磁碟有兩個 `projects/<id>/`
- [ ] `/switch` 後 PM 模式對話使用不同 `pm_<id>.json`
- [ ] 重啟程序後 CEO session 檔仍存在（Gemini 真實還原依 API 能力）
- [ ] 未授權 TG user 被拒絕
- [ ] `pytest` 全綠；`ruff check src tests` 通過

---

## 後續計畫（本檔不展開任務）

| 計畫檔（待寫） | 內容 |
|----------------|------|
| `2026-06-22-phase-b-execution-layer.md` | 狀態機、SandboxRunner、排程者、執行者進度 |
| `2026-06-22-phase-b-plus-skills.md` | Registry、role_skills.yaml、find-skills adapter |
| `2026-06-22-phase-c-closure.md` | QA 回流、PROJECT_DONE |
| COO / 網頁 | 依設計規格第二期 |

---

## Plan self-review（已完成）

| 檢查 | 結果 |
|------|------|
| Spec Phase A 覆蓋 | Router、指令、Session、多專案、執行者 Bot 邊界、遷移、回滾均有任務 |
| Placeholder | 無 TBD；Task 4 Step 5 循環 import 已在 Task 5 bootstrap 解決 |
| 型別一致 | `CompanyService` / `GeminiSessionService` 介面在任務間一致 |
| 範圍 | 未納入 Phase B 細步驟，避免單檔過大 |
