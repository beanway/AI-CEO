"""E-P 通道：resync／load-fixture 經 dispatch 與 CLI inbound。"""

from __future__ import annotations

import ai_company.work_flow._register  # noqa: F401


def _deps(tmp_path):
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.file_store import core as file_store

    file_store.ensure_company_dirs(tmp_path)
    return AppDeps(settings=Settings(company_workspace_root=tmp_path))


def test_load_fixture_scenario_via_dispatch(tmp_path):
    from ai_company.adapters.dispatch import dispatch
    from ai_company.schemas.commands import (
        AddWorkerCommand,
        CreateProjectCommand,
        LoadFixtureScenarioCommand,
    )

    deps = _deps(tmp_path)
    created = dispatch(CreateProjectCommand(name="Fix"), deps)
    assert created.success
    add = dispatch(AddWorkerCommand(template="backend"), deps)
    assert add.success

    loaded = dispatch(LoadFixtureScenarioCommand(scenario="backend_demo"), deps)
    assert loaded.success, loaded.message
    assert "backend_current_task.yaml" in loaded.message

    task = (
        tmp_path
        / "projects"
        / created.project_id
        / "pm"
        / "backend_current_task.yaml"
    )
    assert task.is_file()


def test_resync_worker_via_dispatch_restores_package(tmp_path):
    from ai_company.adapters.dispatch import dispatch
    from ai_company.modules.setup_project_folders import core as project_folders
    from ai_company.schemas.commands import (
        AddWorkerCommand,
        CreateProjectCommand,
        PmResyncWorkerCommand,
    )

    deps = _deps(tmp_path)
    created = dispatch(CreateProjectCommand(name="Sync"), deps)
    dispatch(AddWorkerCommand(template="backend"), deps)
    pkg = (
        project_folders.project_dir(tmp_path, created.project_id)
        / "workers"
        / "backend"
        / "package"
        / "backend_worker"
        / "run.py"
    )
    pkg.write_text("# broken\n", encoding="utf-8")

    resync = dispatch(
        PmResyncWorkerCommand(template="backend", force_package=True),
        deps,
    )
    assert resync.success
    assert "run_scripted" in pkg.read_text(encoding="utf-8")


def test_cli_inbound_load_fixture_scenario(tmp_path, monkeypatch, capsys):
    from ai_company.adapters.cli import inbound as cli_inbound
    from ai_company.config import Settings

    settings = Settings(company_workspace_root=tmp_path)
    monkeypatch.setattr(cli_inbound, "get_settings", lambda: settings)

    from ai_company.adapters.dispatch import dispatch
    from ai_company.schemas.commands import AddWorkerCommand, CreateProjectCommand

    deps = _deps(tmp_path)
    dispatch(CreateProjectCommand(name="CLI"), deps)
    dispatch(AddWorkerCommand(template="backend"), deps)

    code = cli_inbound.run_load_fixture_scenario("backend_demo")
    out = capsys.readouterr()
    assert code == 0
    assert "backend_demo" in out.out


def test_cli_main_resync_worker_argv(tmp_path, monkeypatch):
    from ai_company.adapters.cli import inbound as cli_inbound
    from ai_company.config import Settings

    settings = Settings(company_workspace_root=tmp_path)
    monkeypatch.setattr(cli_inbound, "get_settings", lambda: settings)

    from ai_company.adapters.dispatch import dispatch
    from ai_company.schemas.commands import AddWorkerCommand, CreateProjectCommand

    deps = _deps(tmp_path)
    dispatch(CreateProjectCommand(name="Main"), deps)
    dispatch(AddWorkerCommand(template="backend"), deps)

    from ai_company.adapters.cli.__main__ import main

    assert main(["resync-worker", "backend"]) == 0
