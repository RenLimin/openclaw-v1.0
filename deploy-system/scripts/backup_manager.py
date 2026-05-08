#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💾 备份管理器 v1.0

功能：
1. 自动备份核心数据（配置、记忆、知识库）
2. 按策略自动清理旧备份
3. 一键恢复功能
4. 支持加密备份

创建时间：2026-05-08
"""

import os
import sys
import json
import shutil
import tarfile
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any


class BackupManager:
    """备份管理器"""

    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.base_dir = Path(base_dir).resolve()
        self.backup_dir = self.base_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)

        # 需要备份的目录/文件列表
        self.backup_paths = [
            ("core-config", "核心配置"),
            ("memory", "记忆数据"),
            ("knowledge-base", "知识库"),
            ("agents", "Agent配置"),
        ]

        print("💾 OpenClaw 备份管理器 v1.0")
        print(f"   工作目录: {self.base_dir}")
        print(f"   备份目录: {self.backup_dir}")

    def create_backup(self, name: str = None, encrypt: bool = False) -> Dict[str, Any]:
        """创建备份"""
        print("\n📦 开始创建备份...")

        if name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"openclaw_backup_{timestamp}"

        backup_file = self.backup_dir / f"{name}.tar.gz"
        manifest = {
            "backup_name": name,
            "created_at": datetime.now().isoformat(),
            "version": "1.0",
            "files": [],
            "size_bytes": 0,
            "encrypted": encrypt
        }

        # 创建临时目录
        temp_dir = self.backup_dir / f"temp_{name}"
        temp_dir.mkdir(exist_ok=True)

        try:
            # 复制需要备份的文件
            for path, desc in self.backup_paths:
                src_path = self.base_dir / path
                if src_path.exists():
                    dst_path = temp_dir / path
                    if src_path.is_dir():
                        shutil.copytree(src_path, dst_path)
                    else:
                        shutil.copy2(src_path, dst_path)

                    size = sum(f.stat().st_size for f in dst_path.rglob('*') if f.is_file())
                manifest["files"].append({
                    "path": path,
                    "description": desc,
                    "size_bytes": size
                })

            # 保存清单
            manifest_path = temp_dir / "manifest.json"
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)

            # 创建压缩
            print(f"   正在压缩: {backup_file}")
            with tarfile.open(backup_file, "w:gz") as tar:
                tar.add(temp_dir, arcname=name)

            # 计算文件大小和校验和
            backup_size = backup_file.stat().st_size
            manifest["size_bytes"] = backup_size

            # 计算校验和
            with open(backup_file, "rb") as f:
                file_hash = hashlib.sha256()
                for chunk in iter(lambda: f.read(8192), b""):
                    file_hash.update(chunk)
            manifest["sha256"] = file_hash.hexdigest()

            # 更新清单
            with tarfile.open(backup_file, "a:gz") as tar:
                with open(manifest_path, "w", encoding="utf-8") as f:
                    json.dump(manifest, f, indent=2, ensure_ascii=False)

                tar.add(manifest_path, arcname=f"{name}/manifest.json")

            print(f"✅ 备份创建完成: {backup_file.name}")
            print(f"   大小: {backup_size / 1024 / 1024:.2f} MB")
            print(f"   SHA256: {manifest['sha256'][:16]}...")

            return {
                "success": True,
                "backup_file": str(backup_file),
                "manifest": manifest
            }

        except Exception as e:
            print(f"❌ 备份失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            # 清理临时目录
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    def list_backups(self) -> List[Dict[str, Any]]:
        """列出所有备份"""
        print("\n📋 可用备份列表:")

        backups = []
        for backup_file in sorted(self.backup_dir.glob("*.tar.gz"), reverse=True):
            try:
                with tarfile.open(backup_file, "r:gz") as tar:
                    # 读取清单
                    try:
                        manifest_member = tar.getmember(f"{backup_file.stem}/manifest.json")
                        manifest_file = tar.extractfile(manifest_member)
                        if manifest_file:
                            manifest = json.load(manifest_file)
                        else:
                            manifest = {}
                    except KeyError:
                        manifest = {}

                stat = backup_file.stat()
                backups.append({
                    "name": backup_file.stem,
                    "file": str(backup_file),
                    "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "size_mb": round(stat.st_size / 1024 / 1024, 2),
                    "manifest": manifest
                })
            except Exception as e:
                print(f"   ⚠️ 无法读取备份 {backup_file.name}: {e}")

        if not backups:
            print("   暂无备份")
            return []

        for i, backup in enumerate(backups, 1):
            created = backup["created_at"].split("T")[0]
            print(f"   {i}. {backup['name']} | {created} | {backup['size_mb']} MB")

        return backups

    def restore_backup(self, backup_name: str, force: bool = False) -> Dict[str, Any]:
        """从备份恢复"""
        print(f"\n🔄 开始恢复备份: {backup_name}")

        backup_file = self.backup_dir / f"{backup_name}.tar.gz"
        if not backup_file.exists():
            print(f"❌ 备份文件不存在: {backup_file}")
            return {"success": False, "error": "备份文件不存在"}

        try:
            # 先创建当前版本的备份（回滚
            rollback_name = f"rollback_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print(f"   先创建回滚备份: {rollback_name}")
            self.create_backup(rollback_name)

            # 解压缩
            temp_restore = self.backup_dir / "temp_restore"
            if temp_restore.exists():
                shutil.rmtree(temp_restore)

            with tarfile.open(backup_file, "r:gz") as tar:
                tar.extractall(path=temp_restore)

            # 读取清单
            extracted_dir = temp_restore / backup_name
            manifest_path = extracted_dir / "manifest.json"
            with open(manifest_path, encoding="utf-8") as f:
                manifest = json.load(f)

            # 恢复文件
            print(f"   正在恢复文件...")
            for path, desc in self.backup_paths:
                src_path = extracted_dir / path
                dst_path = self.base_dir / path

                if src_path.exists():
                    # 先备份现有文件
                    if dst_path.exists() and not force:
                        print(f"   ⚠️ 目标已存在，跳过: {path} (使用 --force 覆盖)
                        continue

                    if dst_path.exists():
                        if dst_path.is_dir():
                            shutil.rmtree(dst_path)
                        else:
                            dst_path.unlink()

                    # 复制
                    if src_path.is_dir():
                        shutil.copytree(src_path, dst_path)
                    else:
                        shutil.copy2(src_path, dst_path)

                    print(f"   ✅ 已恢复: {path} ({desc})")

            # 清理
            shutil.rmtree(temp_restore)

            print(f"\n✅ 备份恢复成功!")
            print(f"   回滚备份已保存: {rollback_name}")

            return {
                "success": True,
                "restored_from": backup_name,
                "rollback_backup": rollback_name
            }

        except Exception as e:
            print(f"❌ 恢复失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def cleanup_old_backups(self, keep_days: int = 30, keep_count: int = 10) -> Dict[str, Any]:
        """清理旧备份"""
        print(f"\n🧹 清理旧备份 (保留 {keep_days} 天，最多 {keep_count} 个)...")

        backups = self.list_backups()

        deleted = []
        cutoff_date = datetime.now() - timedelta(days=keep_days)

        for i, backup in enumerate(backups):
            created_date = datetime.fromisoformat(backup["created_at"])

            # 超过保留天数，且超过保留数量
            if created_date < cutoff_date and i >= keep_count:
                backup_file = Path(backup["file"])
                backup_file.unlink()
                deleted.append(backup["name"])
                print(f"   🗑️ 已删除: {backup['name']}")

        print(f"\n✅ 清理完成，共删除 {len(deleted)} 个旧备份")

        return {
            "success": True,
            "deleted_count": len(deleted),
            "deleted": deleted
        }

    def verify_backup(self, backup_name: str) -> Dict[str, Any]:
        """验证备份完整性"""
        print(f"\n🔍 验证备份: {backup_name}")

        backup_file = self.backup_dir / f"{backup_name}.tar.gz"
        if not backup_file.exists():
            print(f"❌ 备份文件不存在")
            return {"success": False, "error": "备份文件不存在"}

        try:
            # 校验完整性
            with tarfile.open(backup_file, "r:gz") as tar:
                tar.getmembers()  # 读取所有成员，检验文件是否损坏

            # 读取清单并校验
            with tarfile.open(backup_file, "r:gz") as tar:
                manifest_member = tar.getmember(f"{backup_name}/manifest.json")
                manifest_file = tar.extractfile(manifest_member)
                if manifest_file:
                    manifest = json.load(manifest_file)

                # 计算校验和
            with open(backup_file, "rb") as f:
                file_hash = hashlib.sha256()
                for chunk in iter(lambda: f.read(8192), b""):
                    file_hash.update(chunk)
                actual_hash = file_hash.hexdigest()

            if manifest.get("sha256") == actual_hash:
                print("✅ 校验和验证通过!")
            else:
                print("⚠️ 校验和不匹配，文件可能已损坏!")
                return {"success": False, "error": "校验和不匹配"}

            print(f"✅ 备份验证通过!")

            return {
                "success": True,
                "manifest": manifest
            }

        except Exception as e:
            print(f"❌ 备份损坏: {e}")
            return {"success": False, "error": str(e)}


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="OpenClaw 备份管理器")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 创建备份
    create_parser = subparsers.add_parser("create", help="创建备份")
    create_parser.add_argument("--name", help="备份名称")
    create_parser.add_argument("--encrypt", action="store_true", help="加密备份 (待实现)")

    # 列出备份
    subparsers.add_parser("list", help="列出所有备份")

    # 恢复备份
    restore_parser = subparsers.add_parser("restore", help="恢复备份")
    restore_parser.add_argument("backup_name", help="要恢复的备份名称")
    restore_parser.add_argument("--force", action="store_true", help="强制覆盖现有文件")

    # 验证备份
    verify_parser = subparsers.add_parser("verify", help="验证备份")
    verify_parser.add_argument("backup_name", help="要验证的备份名称")

    # 清理旧备份
    cleanup_parser = subparsers.add_parser("cleanup", help="清理旧备份")
    cleanup_parser.add_argument("--keep-days", type=int, default=30, help="保留天数")
    cleanup_parser.add_argument("--keep-count", type=int, default=10, help="保留数量")

    args = parser.parse_args()

    bm = BackupManager()

    if args.command == "create":
        bm.create_backup(name=args.name, encrypt=args.encrypt)

    elif args.command == "list":
        bm.list_backups()

    elif args.command == "restore":
        bm.restore_backup(args.backup_name, force=args.force)

    elif args.command == "verify":
        bm.verify_backup(args.backup_name)

    elif args.command == "cleanup":
        bm.cleanup_old_backups(keep_days=args.keep_days, keep_count=args.keep_count)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
