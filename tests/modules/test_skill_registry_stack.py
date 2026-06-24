def test_resolve_skill_stack_order(tmp_path):
    import yaml

    from ai_company.modules.file_store import core as file_store
    from ai_company.modules.setup_project_folders import core as project_folders
    from ai_company.modules.skill_registry import core as skill_registry
    from ai_company.schemas.documents import GlobalSkillsFile, ProjectSkillsFile, WorkerEntry, WorkersFile

    file_store.ensure_company_dirs(tmp_path)
    file_store.save_global_skills(tmp_path, GlobalSkillsFile(enabled_skill_ids=["g1", "g2"]))
    pid = "p1"
    root = project_folders.project_dir(tmp_path, pid)
    project_folders.ensure_project_tree(root)
    workers = WorkersFile(workers=[WorkerEntry(id="be", kind="backend")])
    project_folders.ensure_worker_directories(root, workers.workers)
    file_store.save_project_skills(tmp_path, pid, ProjectSkillsFile(enabled_skill_ids=["p1"]))
    role_path = root / "workers" / "be" / "role_skills.yaml"
    role_path.write_text(
        yaml.safe_dump({"enabled_skill_ids": ["r1", "g1"]}, allow_unicode=True),
        encoding="utf-8",
    )
    stack = skill_registry.resolve_skill_stack(tmp_path, pid, "be")
    assert stack == ["g1", "g2", "p1", "r1"]
