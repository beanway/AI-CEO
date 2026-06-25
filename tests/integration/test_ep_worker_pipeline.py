"""E-P 整合：fixtures → worker_host → run-step（無 TG／無 live API）。"""

from __future__ import annotations

import ai_company.work_flow._register  # noqa: F401


def _deps(tmp_path):
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.file_store import core as file_store

    file_store.ensure_company_dirs(tmp_path)
    return AppDeps(settings=Settings(company_workspace_root=tmp_path))


def test_ep_backend_pipeline_fixture_load_and_run_step(tmp_path):
    from ai_company.adapters.dispatch import dispatch
    from ai_company.modules.worker_runner import core as worker_runner
    from ai_company.schemas.commands import (
        AddWorkerCommand,
        CreateProjectCommand,
        LoadFixtureScenarioCommand,
        RunExecutionStepCommand,
    )

    deps = _deps(tmp_path)
    created = dispatch(CreateProjectCommand(name="E-P"), deps)
    assert created.success
    pid = created.project_id

    assert dispatch(AddWorkerCommand(template="backend"), deps).success
    assert dispatch(LoadFixtureScenarioCommand(scenario="backend_demo"), deps).success

    step = dispatch(RunExecutionStepCommand(project_id=pid), deps)
    assert step.success, step.message
    assert step.worker_id == "backend"

    last = worker_runner.load_last_run(tmp_path, pid, "backend")
    assert last is not None and last.status == "success"


def test_ep_scheduler_fixture_and_scripted_package(tmp_path):
    import yaml

    from ai_company.adapters.dispatch import dispatch
    from ai_company.modules.setup_project_folders import core as project_folders
    from ai_company.modules.worker_runner import core as worker_runner
    from ai_company.modules.worker_runner.core import (
        BackendTaskContract,
        PlannedToolCall,
        ScriptedAgentTurn,
    )
    from ai_company.schemas.commands import (
        AddWorkerCommand,
        CreateProjectCommand,
        LoadFixtureScenarioCommand,
    )

    queue_yaml = (
        worker_runner.worker_default_fixtures_dir() / "scheduler_demo_task_queue.yaml"
    ).read_text(encoding="utf-8")
    plan = yaml.safe_load(queue_yaml)
    first = plan["tasks"][0]
    backend_task = BackendTaskContract(
        task_id=first["task_id"],
        goal=first["goal"],
        acceptance_criteria=first.get("acceptance_criteria", []),
        allowed_paths=["workers/backend/"],
        context_refs=["shared/requirements.md"],
    )
    backend_yaml = yaml.safe_dump(
        backend_task.model_dump(), allow_unicode=True, sort_keys=False
    )
    turns = [
        ScriptedAgentTurn(
            tool_calls=[
                PlannedToolCall(
                    "write_file",
                    {"path": "pm/task_queue.yaml", "content": queue_yaml},
                ),
                PlannedToolCall(
                    "write_file",
                    {
                        "path": "pm/backend_current_task.yaml",
                        "content": backend_yaml,
                    },
                ),
                PlannedToolCall(
                    "complete_task",
                    {"status": "success", "summary": "E-P integration plan"},
                ),
            ],
        ),
    ]

    deps = _deps(tmp_path)
    created = dispatch(CreateProjectCommand(name="Sch"), deps)
    pid = created.project_id
    assert dispatch(AddWorkerCommand(template="scheduler"), deps).success
    assert dispatch(LoadFixtureScenarioCommand(scenario="scheduler_demo"), deps).success

    root = project_folders.project_dir(tmp_path, pid)
    assert (root / "pm" / "scheduler_intake.yaml").is_file()

    result = worker_runner.run_scheduler_worker_scripted(
        tmp_path, pid, "scheduler", turns
    )
    assert result.success
    assert (root / "pm" / "task_queue.yaml").is_file()
    last = worker_runner.load_scheduler_last_run(tmp_path, pid, "scheduler")
    assert last is not None and last.status == "success"


def test_ep_resync_then_repair_health(tmp_path):
    from ai_company.adapters.dispatch import dispatch
    from ai_company.modules.setup_project_folders import core as project_folders
    from ai_company.schemas.commands import (
        AddWorkerCommand,
        CreateProjectCommand,
        PmRepairCommand,
        PmResyncWorkerCommand,
    )

    deps = _deps(tmp_path)
    created = dispatch(CreateProjectCommand(name="Health"), deps)
    pid = created.project_id
    dispatch(AddWorkerCommand(template="backend"), deps)

    root = project_folders.project_dir(tmp_path, pid)
    manifest = root / "workers" / "backend" / "worker_manifest.yaml"
    manifest.unlink()

    broken = dispatch(PmRepairCommand(project_id=pid), deps)
    assert broken.success
    assert "worker_manifest.yaml" in broken.message or "manifest" in broken.message.lower()

    dispatch(PmResyncWorkerCommand(template="backend", force_package=True), deps)
    fixed = dispatch(PmRepairCommand(project_id=pid), deps)
    assert fixed.success
    assert manifest.is_file()
