from ai_company.models.company import (
    GlobalConfigFile,
    GlobalSkillsFile,
    NotificationPolicy,
    ProjectRecord,
    ProjectsFile,
)
from ai_company.store.company_store import CompanyStore


def test_roundtrip_projects(tmp_workspace):
    store = CompanyStore(tmp_workspace)
    store.ensure_company_dirs()
    data = ProjectsFile(
        active_project_id="p1",
        projects=[ProjectRecord(id="p1", name="One")],
    )
    store.save_projects(data)
    loaded = store.load_projects()
    assert loaded.active_project_id == "p1"
    assert loaded.projects[0].name == "One"


def test_roundtrip_global_skills(tmp_workspace):
    store = CompanyStore(tmp_workspace)
    store.ensure_company_dirs()
    data = GlobalSkillsFile(enabled_skill_ids=["find-skills", "create-skill"])
    store.save_global_skills(data)
    loaded = store.load_global_skills()
    assert loaded.enabled_skill_ids == ["find-skills", "create-skill"]


def test_roundtrip_global_config(tmp_workspace):
    store = CompanyStore(tmp_workspace)
    store.ensure_company_dirs()
    data = GlobalConfigFile(
        default_model="gemini-2.5-pro",
        notification_policy=NotificationPolicy.FAILURES_ONLY,
    )
    store.save_global_config(data)
    loaded = store.load_global_config()
    assert loaded.default_model == "gemini-2.5-pro"
    assert loaded.notification_policy == NotificationPolicy.FAILURES_ONLY


def test_ensure_company_index_files_creates_defaults(tmp_workspace):
    store = CompanyStore(tmp_workspace)
    store.ensure_company_dirs()
    store.ensure_company_index_files()

    assert (store.company_dir / "projects.json").is_file()
    assert (store.company_dir / "global_skills.yaml").is_file()
    assert (store.company_dir / "global_config.yaml").is_file()

    assert store.load_projects().projects == []
    assert store.load_global_skills().enabled_skill_ids == []
    assert store.load_global_config().default_model == "gemini-2.5-flash"
