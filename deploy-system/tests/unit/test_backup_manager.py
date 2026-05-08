# ==============================================
# 备份管理器单元测试
# ==============================================

import os
import json
import tarfile
import pytest
from pathlib import Path


class TestBackupManager:
    """备份管理器测试套件"""

    def test_initialization(self, backup_manager_with_temp_dir):
        """测试初始化"""
        bm = backup_manager_with_temp_dir
        assert bm.backup_dir.exists()
        assert bm.backup_dir.name == "backups"

    def test_create_backup_creates_file(self, backup_manager_with_temp_dir):
        """测试创建备份生成正确的文件"""
        bm = backup_manager_with_temp_dir
        result = bm.create_backup(name="test_backup")

        assert result["success"] is True
        assert "test_backup.tar.gz" in result["backup_file"]
        assert Path(result["backup_file"]).exists()

    def test_backup_contains_manifest(self, backup_manager_with_temp_dir):
        """测试备份包含 manifest.json 清单"""
        bm = backup_manager_with_temp_dir
        result = bm.create_backup(name="test_backup")

        with tarfile.open(result["backup_file"], "r:gz") as tar:
            assert "test_backup/manifest.json" in tar.getnames()

            # 验证 manifest 内容
            manifest_member = tar.getmember("test_backup/manifest.json")
            manifest_file = tar.extractfile(manifest_member)
            manifest = json.load(manifest_file)
            assert manifest["backup_name"] == "test_backup"
            assert "sha256" in manifest
            assert "created_at" in manifest

    def test_list_backups(self, backup_manager_with_temp_dir):
        """测试列出备份"""
        bm = backup_manager_with_temp_dir

        # 创建几个备份
        for i in range(3):
            bm.create_backup(name=f"backup_{i}")

        backups = bm.list_backups()
        assert len(backups) == 3
        # 验证按时间倒序排列
        for i in range(2):
            assert backups[i]["created_at"] >= backups[i + 1]["created_at"]

    def test_verify_backup_integrity(self, backup_manager_with_temp_dir):
        """测试备份完整性验证"""
        bm = backup_manager_with_temp_dir
        result = bm.create_backup(name="test_backup")

        # 验证刚创建的备份
        verify_result = bm.verify_backup("test_backup")
        assert verify_result["success"] is True

    def test_cleanup_old_backups_by_count(self, backup_manager_with_temp_dir):
        """测试按数量清理旧备份"""
        bm = backup_manager_with_temp_dir

        # 创建 15 个备份
        for i in range(15):
            bm.create_backup(name=f"backup_{i}")

        # 保留 10 个
        result = bm.cleanup_old_backups(keep_days=999, keep_count=10)
        assert result["deleted_count"] == 5

    def test_backup_without_name_generates_timestamp(self, backup_manager_with_temp_dir):
        """测试不指定备份名称时自动生成时间戳"""
        bm = backup_manager_with_temp_dir
        result = bm.create_backup()

        assert result["success"] is True
        assert "openclaw_backup_" in result["backup_file"]


# ==============================================
# 版本：v1.0 | 最后更新：2026-05-08
# ==============================================
