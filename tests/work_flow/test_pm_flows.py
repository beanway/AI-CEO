def test_set_user_mode_pm_requires_active_project(tmp_path):
    from ai_company.adapters.dispatch import dispatch
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.file_store import core as file_store
    from ai_company.schemas.commands import CreateProjectCommand, SetUserModeCommand
    from ai_company.schemas.documents import UserMode

    settings = Settings(company_workspace_root=tmp_path)
    deps = AppDeps(settings=settings)
    file_store.ensure_company_dirs(tmp_path)

    result = dispatch(
        SetUserModeCommand(telegram_user_id=1, mode=UserMode.PM),
        deps,
    )
    assert not result.success

    dispatch(CreateProjectCommand(name="X"), deps)
    result = dispatch(
        SetUserModeCommand(telegram_user_id=1, mode=UserMode.PM),
        deps,
    )
    assert result.success


def test_setup_workers_three_template(tmp_path):
    from ai_company.adapters.dispatch import dispatch
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.file_store import core as file_store
    from ai_company.schemas.commands import CreateProjectCommand, SetupWorkersCommand

    settings = Settings(company_workspace_root=tmp_path)
    deps = AppDeps(settings=settings)
    file_store.ensure_company_dirs(tmp_path)
    created = dispatch(CreateProjectCommand(name="Gamma"), deps)
    assert created.success

    result = dispatch(SetupWorkersCommand(template="three"), deps)
    assert result.success
    assert result.worker_count == 3
    workers = file_store.load_workers(tmp_path, created.project_id)
    assert len(workers.workers) == 3
    assert (tmp_path / "projects" / created.project_id / "workers" / "backend").is_dir()


def test_pm_chat_and_status(tmp_path):
    from ai_company.adapters.dispatch import dispatch
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.ai_core import core as ai_core
    from ai_company.modules.file_store import core as file_store
    from ai_company.schemas.commands import (
        CreateProjectCommand,
        PmChatCommand,
        SetupWorkersCommand,
        ShowProjectStatusCommand,
    )

    ai_core.reset_chat_backends_for_tests()
    settings = Settings(company_workspace_root=tmp_path, gemini_api_key="", google_api_key="")
    deps = AppDeps(settings=settings)
    file_store.ensure_company_dirs(tmp_path)
    created = dispatch(CreateProjectCommand(name="Delta"), deps)
    dispatch(SetupWorkersCommand(template="three", project_id=created.project_id), deps)

    chat = dispatch(PmChatCommand(text="hello pm"), deps)
    assert chat.success
    assert chat.reply

    status = dispatch(ShowProjectStatusCommand(project_id=created.project_id), deps)
    assert status.success
    assert "backend" in status.message
    ai_core.reset_chat_backends_for_tests()


def test_add_skill_to_project(tmp_path):
    from ai_company.adapters.dispatch import dispatch
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.file_store import core as file_store
    from ai_company.schemas.commands import AddSkillToProjectCommand, CreateProjectCommand

    settings = Settings(company_workspace_root=tmp_path)
    deps = AppDeps(settings=settings)
    file_store.ensure_company_dirs(tmp_path)
    created = dispatch(CreateProjectCommand(name="E"), deps)
    result = dispatch(
        AddSkillToProjectCommand(skill_id="example-ceo", project_id=created.project_id),
        deps,
    )
    assert result.success
    skills = file_store.load_project_skills(tmp_path, created.project_id)
    assert "example-ceo" in skills.enabled_skill_ids
