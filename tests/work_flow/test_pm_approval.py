import subprocess


def test_telegram_high_risk_git_requires_approval(tmp_path):
    from ai_company.adapters.dispatch import dispatch
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.file_store import core as file_store
    from ai_company.schemas.commands import (
        Channel,
        CreateProjectCommand,
        ProjectGitCommand,
        ResolveApprovalCommand,
    )
    from ai_company.schemas.workspace_paths import project_dir

    settings = Settings(company_workspace_root=tmp_path)
    deps = AppDeps(settings=settings)
    file_store.ensure_company_dirs(tmp_path)
    created = dispatch(CreateProjectCommand(name="Appr"), deps)
    root = project_dir(tmp_path, created.project_id)
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)

    blocked = dispatch(
        ProjectGitCommand(
            channel=Channel.TELEGRAM,
            git_argv=["commit", "-m", "x"],
            project_id=created.project_id,
        ),
        deps,
    )
    assert not blocked.success
    assert blocked.error_code == "approval_required"
    assert blocked.approval_id

    still_blocked = dispatch(
        ProjectGitCommand(
            channel=Channel.TELEGRAM,
            git_argv=["commit", "-m", "x"],
            project_id=created.project_id,
        ),
        deps,
    )
    assert still_blocked.error_code == "approval_required"

    resolved = dispatch(
        ResolveApprovalCommand(approval_id=blocked.approval_id, approved=True),
        deps,
    )
    assert resolved.approved is True
    from ai_company.schemas.documents import ApprovalStatus

    record = file_store.get_pending_approval(tmp_path, blocked.approval_id)
    assert record is not None
    assert record.status == ApprovalStatus.COMPLETED


def test_telegram_add_skill_requires_approval(tmp_path):
    from ai_company.adapters.dispatch import dispatch
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.file_store import core as file_store
    from ai_company.schemas.commands import (
        AddSkillToProjectCommand,
        Channel,
        CreateProjectCommand,
        ResolveApprovalCommand,
    )

    settings = Settings(company_workspace_root=tmp_path)
    deps = AppDeps(settings=settings)
    file_store.ensure_company_dirs(tmp_path)
    created = dispatch(CreateProjectCommand(name="SkillAppr"), deps)

    pending = dispatch(
        AddSkillToProjectCommand(
            channel=Channel.TELEGRAM,
            skill_id="example-ceo",
            project_id=created.project_id,
        ),
        deps,
    )
    assert pending.error_code == "approval_required"
    assert pending.approval_id

    dispatch(ResolveApprovalCommand(approval_id=pending.approval_id, approved=True), deps)
    skills = file_store.load_project_skills(tmp_path, created.project_id)
    assert "example-ceo" in skills.enabled_skill_ids


def test_reject_approval_does_not_execute(tmp_path):
    from ai_company.adapters.dispatch import dispatch
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.file_store import core as file_store
    from ai_company.schemas.commands import (
        AddSkillToProjectCommand,
        Channel,
        CreateProjectCommand,
        ResolveApprovalCommand,
    )
    from ai_company.schemas.documents import ApprovalStatus

    settings = Settings(company_workspace_root=tmp_path)
    deps = AppDeps(settings=settings)
    file_store.ensure_company_dirs(tmp_path)
    created = dispatch(CreateProjectCommand(name="Reject"), deps)
    pending = dispatch(
        AddSkillToProjectCommand(
            channel=Channel.TELEGRAM,
            skill_id="example-ceo",
            project_id=created.project_id,
        ),
        deps,
    )
    dispatch(ResolveApprovalCommand(approval_id=pending.approval_id, approved=False), deps)
    record = file_store.get_pending_approval(tmp_path, pending.approval_id)
    assert record is not None
    assert record.status == ApprovalStatus.REJECTED
    skills = file_store.load_project_skills(tmp_path, created.project_id)
    assert "example-ceo" not in skills.enabled_skill_ids
