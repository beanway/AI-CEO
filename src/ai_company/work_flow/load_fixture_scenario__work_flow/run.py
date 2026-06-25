from __future__ import annotations

from ai_company.app_deps import AppDeps
from ai_company.modules.setup_project_folders import core as project_folders
from ai_company.modules.worker_host import core as worker_host
from ai_company.schemas.commands import BaseCommand, CommandType, LoadFixtureScenarioCommand
from ai_company.schemas.results import LoadFixtureScenarioResult
from ai_company.work_flow._shared.pm_project import require_active_project_id
from ai_company.work_flow.registry import WorkFlowRegistry


def run(command: BaseCommand, deps: AppDeps) -> LoadFixtureScenarioResult:
    if not isinstance(command, LoadFixtureScenarioCommand):
        return LoadFixtureScenarioResult(success=False, message="指令類型錯誤", error_code="bad_command")
    try:
        project_id = require_active_project_id(deps.workspace_root, command.project_id)
    except ValueError as exc:
        return LoadFixtureScenarioResult(success=False, message=str(exc), error_code="no_project")

    root = project_folders.project_dir(deps.workspace_root, project_id)
    project_folders.ensure_project_tree(root)
    worker_host.install_fixtures_package(root)
    try:
        written = worker_host.load_demo_scenario(root, command.scenario.strip())
    except (ValueError, FileNotFoundError) as exc:
        return LoadFixtureScenarioResult(
            success=False,
            message=str(exc),
            error_code="bad_scenario",
            project_id=project_id,
            scenario=command.scenario,
        )
    return LoadFixtureScenarioResult(
        success=True,
        message=f"已載入場景 {command.scenario!r}：{', '.join(written)}",
        project_id=project_id,
        scenario=command.scenario,
        files_written=written,
    )


def register(registry: WorkFlowRegistry) -> None:
    registry.register(
        CommandType.LOAD_FIXTURE_SCENARIO,
        flow_id="load_fixture_scenario__work_flow",
        description_zh="載入 worker_default fixtures 場景到 pm/",
        runner=run,
    )
