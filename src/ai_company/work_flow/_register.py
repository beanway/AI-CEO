"""Register all *__work_flow packages via each flow's run.py."""

from ai_company.work_flow.add_skill_to_company__work_flow.run import (
    register as register_add_skill_to_company,
)
from ai_company.work_flow.add_skill_to_project__work_flow.run import (
    register as register_add_skill_to_project,
)
from ai_company.work_flow.ceo_chat__work_flow.run import register as register_ceo_chat
from ai_company.work_flow.create_project__work_flow.run import register as register_create_project
from ai_company.work_flow.init_workspace__work_flow.run import register as register_init_workspace
from ai_company.work_flow.list_projects__work_flow.run import register as register_list_projects
from ai_company.work_flow.pm_repair__work_flow.run import register as register_pm_repair
from ai_company.work_flow.pm_chat__work_flow.run import register as register_pm_chat
from ai_company.work_flow.project_git__work_flow.run import register as register_project_git
from ai_company.work_flow.resolve_approval__work_flow.run import (
    register as register_resolve_approval,
)
from ai_company.work_flow.run_execution_step__work_flow.run import (
    register as register_run_execution_step,
)
from ai_company.work_flow.resolve_execution_failure__work_flow.run import (
    register as register_resolve_execution_failure,
)
from ai_company.work_flow.list_registry_skills__work_flow.run import (
    register as register_list_registry_skills,
)
from ai_company.work_flow.create_registry_skill__work_flow.run import (
    register as register_create_registry_skill,
)
from ai_company.work_flow.set_user_mode__work_flow.run import register as register_set_user_mode
from ai_company.work_flow.setup_workers__work_flow.run import register as register_setup_workers
from ai_company.work_flow.show_global_config__work_flow.run import (
    register as register_show_global_config,
)
from ai_company.work_flow.show_project_status__work_flow.run import (
    register as register_show_project_status,
)
from ai_company.work_flow.switch_project__work_flow.run import register as register_switch_project
from ai_company.work_flow.update_global_config__work_flow.run import (
    register as register_update_global_config,
)
from ai_company.work_flow.registry import registry

register_init_workspace(registry)
register_list_projects(registry)
register_create_project(registry)
register_ceo_chat(registry)
register_switch_project(registry)
register_show_global_config(registry)
register_add_skill_to_company(registry)
register_update_global_config(registry)
register_set_user_mode(registry)
register_pm_chat(registry)
register_pm_repair(registry)
register_project_git(registry)
register_resolve_approval(registry)
register_run_execution_step(registry)
register_resolve_execution_failure(registry)
register_list_registry_skills(registry)
register_create_registry_skill(registry)
register_setup_workers(registry)
register_add_skill_to_project(registry)
register_show_project_status(registry)

_REGISTERED = frozenset(registry.list_flows())
