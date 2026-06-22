from pathlib import Path

import pytest


@pytest.fixture
def tmp_workspace(tmp_path: Path) -> Path:
    root = tmp_path / "company_workspace"
    root.mkdir()
    return root
