"""內建 Worker kind 與建局模板。"""

from ai_company.schemas.documents import WorkerEntry

BUILTIN_WORKER_KINDS = frozenset(
    {
        "planner",
        "backend",
        "frontend",
        "qa",
        "task_scheduler",
    }
)

WORKER_TEMPLATES: dict[str, list[WorkerEntry]] = {
    "five": [
        WorkerEntry(id="planner", kind="planner"),
        WorkerEntry(id="backend", kind="backend"),
        WorkerEntry(id="frontend", kind="frontend"),
        WorkerEntry(id="qa", kind="qa"),
        WorkerEntry(id="scheduler", kind="task_scheduler"),
    ],
    "three": [
        WorkerEntry(id="planner", kind="planner"),
        WorkerEntry(id="backend", kind="backend"),
        WorkerEntry(id="scheduler", kind="task_scheduler"),
    ],
}
