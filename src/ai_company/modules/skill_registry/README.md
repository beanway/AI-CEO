# skill_registry

**Skill 註冊表路徑**：讀取 repo `skills/registry/<id>/SKILL.md` 是否存在。

## 對外接口（`core.py`）

- `list_registered_skill_ids()`、`skill_exists(skill_id)`

## 呼叫者

僅 `work_flow/*__work_flow/run.py`。
