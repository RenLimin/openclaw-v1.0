# ==============================================
# Pytest 配置与 Fixture
# ==============================================

import os
import sys
import tempfile
import shutil
from pathlib import Path
import pytest

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def temp_dir():
    """创建临时目录，测试完成后自动清理"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_config():
    """示例配置 Fixture"""
    return {
        "env": "test",
        "llm": {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "temperature": 0.7
        },
        "monitoring": {
            "enabled": True,
            "alert_level": "warning"
        }
    }


@pytest.fixture
def backup_manager_with_temp_dir(temp_dir):
    """在临时目录中初始化备份管理器"""
    from deploy_system.scripts.backup_manager import BackupManager
    original_base_dir = os.getcwd()
    os.chdir(temp_dir)
    try:
        bm = BackupManager(base_dir=str(temp_dir))
        yield bm
    finally:
        os.chdir(original_base_dir)


@pytest.fixture
def tenant_manager_with_temp_dir(temp_dir):
    """在临时目录中初始化租户管理器"""
    from deploy_system.scripts.tenant_manager import TenantManager
    original_base_dir = os.getcwd()
    os.chdir(temp_dir)
    try:
        tm = TenantManager(base_dir=str(temp_dir))
        yield tm
    finally:
        os.chdir(original_base_dir)


# ==============================================
# 版本：v1.0 | 最后更新：2026-05-08
# ==============================================
