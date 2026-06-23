from ai_company.schemas.documents import (
    GlobalConfigFile,
    GlobalSkillsFile,
    ProjectRecord,
    ProjectsFile,
)


def test_projects_file_defaults():
    pf = ProjectsFile()
    assert pf.active_project_id is None
    assert pf.projects == []


def test_project_record_slug():
    rec = ProjectRecord(id="abc12", name="Demo")
    assert rec.id == "abc12"


def test_global_skills_defaults():
    gs = GlobalSkillsFile()
    assert gs.enabled_skill_ids == []


def test_global_config_defaults():
    gc = GlobalConfigFile()
    assert gc.default_model == "gemini-2.5-flash"
    assert gc.notification_policy.value == "all"
