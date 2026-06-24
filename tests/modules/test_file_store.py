from ai_company.schemas.documents import (
    GlobalConfigFile,
    GlobalSkillsFile,
    NotificationPolicy,
    ProjectRecord,
    ProjectsFile,
)
from ai_company.modules.file_store import core as file_store


def test_roundtrip_projects(tmp_workspace):
    file_store.ensure_company_dirs(tmp_workspace)
    data = ProjectsFile(
        active_project_id="p1",
        projects=[ProjectRecord(id="p1", name="One")],
    )
    file_store.save_projects(tmp_workspace, data)
    loaded = file_store.load_projects(tmp_workspace)
    assert loaded.active_project_id == "p1"
    assert loaded.projects[0].name == "One"


def test_roundtrip_global_skills(tmp_workspace):
    file_store.ensure_company_dirs(tmp_workspace)
    data = GlobalSkillsFile(enabled_skill_ids=["find-skills", "create-skill"])
    file_store.save_global_skills(tmp_workspace, data)
    loaded = file_store.load_global_skills(tmp_workspace)
    assert loaded.enabled_skill_ids == ["find-skills", "create-skill"]


def test_roundtrip_global_config(tmp_workspace):
    file_store.ensure_company_dirs(tmp_workspace)
    data = GlobalConfigFile(
        default_model="gemini-2.5-pro",
        notification_policy=NotificationPolicy.FAILURES_ONLY,
        max_output_tokens=4096,
        thinking_budget=0,
        include_thoughts=False,
        temperature=0.2,
    )
    file_store.save_global_config(tmp_workspace, data)
    loaded = file_store.load_global_config(tmp_workspace)
    assert loaded.default_model == "gemini-2.5-pro"
    assert loaded.notification_policy == NotificationPolicy.FAILURES_ONLY
    assert loaded.max_output_tokens == 4096
    assert loaded.thinking_budget == 0
    assert loaded.temperature == 0.2


def test_ensure_company_index_files_writes_ai_fields_to_yaml(tmp_workspace):
    file_store.ensure_company_dirs(tmp_workspace)
    file_store.ensure_company_index_files(tmp_workspace)

    path = tmp_workspace / "_company" / "global_config.yaml"
    text = path.read_text(encoding="utf-8")
    assert "max_output_tokens:" in text
    assert "thinking_budget:" in text
    assert "include_thoughts:" in text
    cfg = file_store.load_global_config(tmp_workspace)
    assert cfg.max_output_tokens == 8192
    assert cfg.thinking_budget == 0


def test_upgrade_legacy_global_config_yaml(tmp_workspace):
    file_store.ensure_company_dirs(tmp_workspace)
    legacy = tmp_workspace / "_company" / "global_config.yaml"
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text(
        "default_model: gemini-2.5-flash\nnotification_policy: all\n",
        encoding="utf-8",
    )
    file_store.ensure_company_index_files(tmp_workspace)
    text = legacy.read_text(encoding="utf-8")
    assert "max_output_tokens:" in text
    assert "thinking_budget:" in text


def test_ensure_company_index_files_creates_defaults(tmp_workspace):
    file_store.ensure_company_dirs(tmp_workspace)
    file_store.ensure_company_index_files(tmp_workspace)

    root = tmp_workspace / "_company"
    assert (root / "projects.json").is_file()
    assert (root / "global_skills.yaml").is_file()
    assert (root / "global_config.yaml").is_file()

    assert file_store.load_projects(tmp_workspace).projects == []
    assert file_store.load_global_skills(tmp_workspace).enabled_skill_ids == []
    assert file_store.load_global_config(tmp_workspace).default_model == "gemini-2.5-flash"


def test_ensure_company_dirs_writes_gitignore(tmp_workspace):
    file_store.ensure_company_dirs(tmp_workspace)
    path = tmp_workspace / "_company" / ".gitignore"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "sessions/" in text
    assert "execution/" in text
    assert "metrics/" in text
