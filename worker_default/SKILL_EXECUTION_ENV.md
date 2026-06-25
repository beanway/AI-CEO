# Skill 執行環境（Worker 最基本能力）

**規格**：[`docs/design/execution-layer-v2.md`](../docs/design/execution-layer-v2.md)、[`docs/design/harness-design.md`](../docs/design/harness-design.md) §8  
**模板**：[`backend/SKILL.md`](backend/SKILL.md)、[`backend/skills/`](backend/skills/)  
**不使用 MCP**：Worker 透過 Harness 內建 **沙盒 subprocess + ToolPolicy + 本機 `workers/<id>/skills/`** 與 LLM 互動。

---

## Worker 在做什麼

在 **單一專案沙盒**（`company_workspace/projects/<project_id>/`）內，依 **任務契約**（`pm/backend_current_task.yaml`）與 **角色／技能劇本**，用 **白名單工具** 讀寫檔案、跑測試，並寫入 `workers/<id>/last_run.json`。終端 **stdout／stderr** 回饋給模型以修正；測試通過且 `complete_task` 驗證通過才視為成功。

Worker **不**遙控 Cursor IDE，**不**修改框架 `src/`。

---

## 三件套（Harness 版）

| 組件 | 職責 | 程式落點 |
|------|------|----------|
| **安全沙盒** | 專案根 cwd；路徑與 argv 白名單 | `modules/sandbox_runner` + `backend_tool_policy` |
| **Skill（各自管理）** | 劇本在 **`workers/<id>/skills/*.md`**，非全公司 registry 共用 | `list_skills` / `read_skill`（`modules/worker_runner`） |
| **工具回饋迴圈** | Function calling → 執行 → 結果塞回對話 | `modules/worker_runner` + Gemini（或測試用 Scripted Agent） |

### 與全權 bash 的差異

- E1：**argv 白名單**（`pytest`、`python3 -m pytest`、`ruff` 等），禁止任意 `pip install`／網路安裝。
- 依賴應在專案／任務契約中聲明，或由 PM 建局預先準備 venv。

---

## 基本 Worker 建局流程

1. **沙盒目錄**：`projects/<id>/`（`shared/`、`workers/<id>/`、可選 `pm/`）。
2. **複製種子**：自 [`worker_default/backend/`](backend/) 複製 `SKILL.md`、`skills/` 至 `workers/<id>/`（見 `worker_runner.seed_worker_from_default`）。
3. **技能劇本**：將審核過的 Markdown（可參考 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) 等）放入 **`workers/<id>/skills/`**，勿未審即從網路自動拉取。
4. **執行**：`run_backend_worker` 注入 system prompt（角色 + 任務 + 工具說明），直到 `complete_task` 或達輪次上限。

### 外部 Skill 庫（參考）

| 來源 | 用途 |
|------|------|
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 工作流與驗證閘道，偏後端實作 |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | 索引與比對後選少數匯入 |
| [orchestra-research/AI-research-SKILLs](https://github.com/orchestra-research/AI-research-SKILLs) | 研究／實驗型劇本 |

與 Cursor 分離：`.cursor/skills/` 供框架開發；虛擬公司 Worker 用 **專案內 `workers/<id>/skills/`**。

---

## Harness 暴露給 AI 的工具

- `list_skills` / `read_skill`
- `read_file` / `write_file`（路徑限沙盒政策）
- `run_terminal`（argv 陣列，經 ToolPolicy）
- `complete_task`（寫 `last_run.json`；success 須 `test_exit_code == 0`）

細節見 [`backend/SKILL.md`](backend/SKILL.md)、[`modules/worker_runner/README.md`](../src/ai_company/modules/worker_runner/README.md)。
