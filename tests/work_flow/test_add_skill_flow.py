def test_skill_registry_lists_example():
    from ai_company.modules.skill_registry import core as skill_registry

    assert skill_registry.skill_exists("example-ceo")
    assert "example-ceo" in skill_registry.list_registered_skill_ids()


def test_dispatch_add_skill_to_company(tmp_path):
    from ai_company.adapters.dispatch import dispatch
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.file_store import core as file_store
    from ai_company.schemas.commands import AddSkillToCompanyCommand

    settings = Settings(company_workspace_root=tmp_path)
    deps = AppDeps(settings=settings)
    file_store.ensure_company_dirs(tmp_path)

    result = dispatch(AddSkillToCompanyCommand(skill_id="example-ceo"), deps)
    assert result.success
    assert result.skill_id == "example-ceo"
    skills = file_store.load_global_skills(tmp_path)
    assert skills.enabled_skill_ids == ["example-ceo"]


def test_dispatch_add_skill_unknown(tmp_path):
    from ai_company.adapters.dispatch import dispatch
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.file_store import core as file_store
    from ai_company.schemas.commands import AddSkillToCompanyCommand

    settings = Settings(company_workspace_root=tmp_path)
    deps = AppDeps(settings=settings)
    file_store.ensure_company_dirs(tmp_path)

    result = dispatch(AddSkillToCompanyCommand(skill_id="no-such-skill"), deps)
    assert not result.success
    assert result.error_code == "skill_not_found"
