"""Worker 狀態機骨架（階段三實作）。"""

from enum import Enum


class WorkerState(str, Enum):
    TASK_SCHEDULER = "TASK_SCHEDULER"
    PLANNER = "PLANNER"
    BACKEND = "BACKEND"
    FRONTEND = "FRONTEND"
    QA = "QA"
    PROJECT_DONE = "PROJECT_DONE"


class WorkerStateMachine:
    def __init__(self, shared_dir: str) -> None:
        self.current_state = WorkerState.TASK_SCHEDULER
        self.shared_dir = shared_dir

    def step(self) -> WorkerState:
        """單步推進；Gemini Agent 整合待階段三接上。"""
        if self.current_state == WorkerState.PROJECT_DONE:
            return self.current_state
        # 佔位：下一版由 scheduler_agent.analyze(shared_dir) 決定轉換
        self.current_state = WorkerState.PROJECT_DONE
        return self.current_state
