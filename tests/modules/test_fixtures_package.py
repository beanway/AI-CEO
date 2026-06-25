from ai_company.modules.setup_project_folders import core as project_folders
from ai_company.modules.worker_host import core as worker_host


def test_load_backend_demo_scenario(tmp_path):
    root = tmp_path / "proj"
    project_folders.ensure_project_tree(root)
    worker_host.install_fixtures_package(root)
    written = worker_host.load_demo_scenario(root, "backend_demo")
    assert "pm/backend_current_task.yaml" in written
    assert (root / "pm" / "backend_current_task.yaml").is_file()


def test_load_scheduler_demo_scenario(tmp_path):
    root = tmp_path / "proj"
    project_folders.ensure_project_tree(root)
    worker_host.install_fixtures_package(root)
    written = worker_host.load_demo_scenario(root, "scheduler_demo")
    assert "pm/scheduler_intake.yaml" in written
