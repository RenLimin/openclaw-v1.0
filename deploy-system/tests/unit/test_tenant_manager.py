# ==============================================
# 多租户管理器单元测试
# ==============================================

import json
import pytest
from pathlib import Path


class TestTenantManager:
    """租户管理器测试套件"""

    def test_initialization(self, tenant_manager_with_temp_dir):
        """测试初始化"""
        tm = tenant_manager_with_temp_dir
        assert tm.tenants_dir.exists()
        assert tm.tenants_dir.name == "tenants"

    def test_create_tenant_creates_structure(self, tenant_manager_with_temp_dir):
        """测试创建租户生成正确的目录结构"""
        tm = tenant_manager_with_temp_dir
        result = tm.create_tenant(tenant_id="test_tenant", tenant_name="Test Tenant")

        assert result["success"] is True
        assert "test_tenant" in tm.tenants

        # 验证目录结构
        tenant_dir = tm.tenants_dir / "test_tenant"
        assert tenant_dir.exists()
        assert (tenant_dir / "config").exists()
        assert (tenant_dir / "memory").exists()
        assert (tenant_dir / "knowledge-base").exists()
        assert (tenant_dir / "agents").exists()
        assert (tenant_dir / "data").exists()
        assert (tenant_dir / "logs").exists()

    def test_tenant_has_default_quota(self, tenant_manager_with_temp_dir):
        """测试新建租户有默认配额"""
        tm = tenant_manager_with_temp_dir
        tm.create_tenant(tenant_id="test_tenant")

        tenant = tm.tenants["test_tenant"]
        assert tenant["quota"]["max_agents"] == 10
        assert tenant["quota"]["max_memory_gb"] == 10
        assert tenant["quota"]["max_daily_llm_calls"] == 1000

    def test_list_tenants_empty(self, tenant_manager_with_temp_dir):
        """测试空租户列表"""
        tm = tenant_manager_with_temp_dir
        tenants = tm.list_tenants()
        assert len(tenants) == 0

    def test_list_tenants_with_data(self, tenant_manager_with_temp_dir):
        """测试列出租户"""
        tm = tenant_manager_with_temp_dir
        for i in range(3):
            tm.create_tenant(tenant_id=f"tenant_{i}", tenant_name=f"Tenant {i}")

        tenants = tm.list_tenants()
        assert len(tenants) == 3

    def test_get_tenant_info(self, tenant_manager_with_temp_dir):
        """测试获取租户详情"""
        tm = tenant_manager_with_temp_dir
        tm.create_tenant(tenant_id="test_tenant", tenant_name="Test Tenant")

        info = tm.get_tenant_info("test_tenant")
        assert info["tenant_name"] == "Test Tenant"
        assert "quota" in info
        assert "usage" in info

    def test_update_tenant_quota(self, tenant_manager_with_temp_dir):
        """测试更新租户配额"""
        tm = tenant_manager_with_temp_dir
        tm.create_tenant(tenant_id="test_tenant")

        result = tm.update_tenant_quota(
            "test_tenant",
            {"max_agents": 20, "max_memory_gb": 50}
        )

        assert result["success"] is True
        assert tm.tenants["test_tenant"]["quota"]["max_agents"] == 20
        assert tm.tenants["test_tenant"]["quota"]["max_memory_gb"] == 50

    def test_delete_tenant_removes_files(self, tenant_manager_with_temp_dir):
        """测试删除租户（需要绕过确认保护）"""
        tm = tenant_manager_with_temp_dir
        tm.create_tenant(tenant_id="test_tenant")

        tenant_dir = tm.tenants_dir / "test_tenant"
        assert tenant_dir.exists()

        result = tm.delete_tenant("test_tenant", force=True)
        assert result["success"] is True
        assert "test_tenant" not in tm.tenants
        assert not tenant_dir.exists()

    def test_switch_tenant_creates_marker_file(self, tenant_manager_with_temp_dir):
        """测试切换租户创建标记文件"""
        tm = tenant_manager_with_temp_dir
        tm.create_tenant(tenant_id="test_tenant")

        result = tm.switch_tenant("test_tenant")
        assert result["success"] is True

        current_marker = Path(tm.base_dir) / ".current_tenant"
        assert current_marker.exists()
        assert current_marker.read_text() == "test_tenant"

    def test_get_current_tenant(self, tenant_manager_with_temp_dir):
        """测试获取当前租户"""
        tm = tenant_manager_with_temp_dir
        tm.create_tenant(tenant_id="test_tenant")
        tm.switch_tenant("test_tenant")

        current = tm.get_current_tenant()
        assert current == "test_tenant"

    def test_nonexistent_tenant_returns_none(self, tenant_manager_with_temp_dir):
        """测试获取不存在的租户返回空"""
        tm = tenant_manager_with_temp_dir
        info = tm.get_tenant_info("nonexistent")
        assert info == {}


# ==============================================
# 版本：v1.0 | 最后更新：2026-05-08
# ==============================================
