"""Register all *__work_flow packages via each flow's run.py."""

from ai_company.work_flow.init_workspace__work_flow.run import register as register_init_workspace
from ai_company.work_flow.list_projects__work_flow.run import register as register_list_projects
from ai_company.work_flow.show_global_config__work_flow.run import (
    register as register_show_global_config,
)
from ai_company.work_flow.switch_project__work_flow.run import register as register_switch_project
from ai_company.work_flow.registry import registry

register_init_workspace(registry)
register_list_projects(registry)
register_switch_project(registry)
register_show_global_config(registry)

_REGISTERED = frozenset(registry.list_flows())
