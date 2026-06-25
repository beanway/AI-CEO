"""Worker 任務契約與 last_run 結構。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class BackendTaskContract(BaseModel):
    task_id: str
    goal: str
    acceptance_criteria: list[str] = Field(default_factory=list)
    allowed_paths: list[str] = Field(default_factory=list)
    context_refs: list[str] = Field(default_factory=list)


class BackendTestResult(BaseModel):
    command: str
    exit_code: int


class BackendLastRun(BaseModel):
    task_id: str
    status: str  # success | failed
    files_changed: list[str] = Field(default_factory=list)
    test_result: BackendTestResult | None = None
    summary: str = ""
    notes_for_reviewer: str = ""


class SchedulerIntakeContract(BaseModel):
    task_id: str
    user_goal: str
    context_refs: list[str] = Field(default_factory=list)


class QueuedWorkerTask(BaseModel):
    task_id: str
    kind: str
    worker_id: str
    goal: str
    acceptance_criteria: list[str] = Field(default_factory=list)


class TaskQueuePlan(BaseModel):
    plan_id: str
    summary: str = ""
    tasks: list[QueuedWorkerTask] = Field(default_factory=list)


class SchedulerLastRun(BaseModel):
    task_id: str
    status: str  # success | failed
    files_changed: list[str] = Field(default_factory=list)
    summary: str = ""
    notes_for_reviewer: str = ""
    plan_id: str | None = None
    tasks_planned: int = 0
