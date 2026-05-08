#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏢 多租户管理器 v1.0

功能：
1. 创建新租户（独立环境）
2. 租户列表管理
3. 租户资源配额管理
4. 租户切换

创建时间：2026-05-08
"""

import os
import sys
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class TenantManager:
    """多租户管理器"""

    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.base_dir = Path(base_dir).resolve()
        self.tenants_dir = self.base_dir / "tenants"
        self.tenants_dir.mkdir(exist_ok=True)
        self.tenants_file = self.tenants_dir / "tenants.json"

        print("🏢 OpenClaw 多租户管理器 v1.0")
        print(f"   租户目录: {self.tenants_dir}")

        # 加载现有租户列表
        self.tenants = self._load_tenants()

    def _load_tenants(self) -> Dict[str, Dict]:
        """加载租户列表"""
        if self.tenants_file.exists():
            with open(self.tenants_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_tenants(self):
        """保存租户列表"""
        with open(self.tenants_file, 'w', encoding='utf-8') as f:
            json.dump(self.tenants, f, indent=2, ensure_ascii=False)

    def create_tenant(self, tenant_id: str, tenant_name: str = None,
                     quota: Dict = None) -> Dict[str, Any]:
        """创建新租户"""
        print(f"\n🆕 创建新租户: {tenant_id}")

        if tenant_id in self.tenants:
            print(f"❌ 租户已存在: {tenant_id}")
            return {"success": False, "error": "租户已存在"}

        if tenant_name is None:
            tenant_name = tenant_id

        # 默认配额
        default_quota = {
            "max_agents": 10,
            "max_memory_gb": 10,
            "max_daily_llm_calls": 1000,
            "max_users": 5
        }

        if quota:
            default_quota.update(quota)

        # 创建租户目录结构
        tenant_dir = self.tenants_dir / tenant_id
        tenant_dir.mkdir()

        # 创建子目录
        subdirs = ["config", "memory", "knowledge-base", "agents", "data", "logs"]
        for subdir in subdirs:
            (tenant_dir / subdir).mkdir()

        # 复制配置模板
        template_dir = self.base_dir / "deploy-system" / "config"
        if template_dir.exists():
            for config_file in template_dir.glob("*.yaml"):
                shutil.copy2(config_file, tenant_dir / "config" / config_file.name)

        # 保存租户信息
        tenant_info = {
            "tenant_id": tenant_id,
            "tenant_name": tenant_name,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "quota": default_quota,
            "usage": {
                "agent_count": 0,
                "memory_usage_mb": 0,
                "daily_llm_calls": 0
            },
            "directory": str(tenant_dir)
        }

        self.tenants[tenant_id] = tenant_info
        self._save_tenants()

        print(f"✅ 租户创建成功: {tenant_id} ({tenant_name})")
        print(f"   目录: {tenant_dir}")
        print(f"   Agent 配额: {default_quota['max_agents']} 个")

        return {
            "success": True,
            "tenant": tenant_info
        }

    def list_tenants(self) -> List[Dict[str, Any]]:
        """列出所有租户"""
        print("\n📋 租户列表:")

        if not self.tenants:
            print("   暂无租户")
            return []

        tenants_list = sorted(self.tenants.values(), key=lambda x: x["created_at"], reverse=True)

        for i, tenant in enumerate(tenants_list, 1):
            status_icon = "✅" if tenant["status"] == "active" else "❌"
            created_date = tenant["created_at"].split("T")[0]
            print(f"   {i}. {status_icon} {tenant['tenant_id']} - {tenant['tenant_name']}")
            print(f"      创建时间: {created_date}")
            print(f"      Agent 数量: {tenant['usage']['agent_count']}/{tenant['quota']['max_agents']}")
            print()

        return tenants_list

    def get_tenant_info(self, tenant_id: str) -> Dict[str, Any]:
        """获取租户信息"""
        if tenant_id not in self.tenants:
            print(f"❌ 租户不存在: {tenant_id}")
            return {}

        tenant = self.tenants[tenant_id]
        print(f"\nℹ️ 租户信息: {tenant_id}")
        print(f"   名称: {tenant['tenant_name']}")
        print(f"   状态: {tenant['status']}")
        print(f"   创建时间: {tenant['created_at']}")
        print(f"   目录: {tenant['directory']}")
        print(f"\n📊 配额信息:")
        print(f"   Agent 数量: {tenant['usage']['agent_count']}/{tenant['quota']['max_agents']}")
        print(f"   内存配额: {tenant['usage']['memory_usage_mb']}MB/{tenant['quota']['max_memory_gb']}GB")
        print(f"   日 LLM 调用: {tenant['usage']['daily_llm_calls']}/{tenant['quota']['max_daily_llm_calls']}")

        return tenant

    def update_tenant_quota(self, tenant_id: str, new_quota: Dict) -> Dict[str, Any]:
        """更新租户配额"""
        print(f"\n📝 更新租户配额: {tenant_id}")

        if tenant_id not in self.tenants:
            print(f"❌ 租户不存在: {tenant_id}")
            return {"success": False, "error": "租户不存在"}

        self.tenants[tenant_id]["quota"].update(new_quota)
        self._save_tenants()

        print(f"✅ 配额更新成功")
        for key, value in new_quota.items():
            print(f"   {key}: {value}")

        return {"success": True, "tenant": self.tenants[tenant_id]}

    def delete_tenant(self, tenant_id: str, force: bool = False) -> Dict[str, Any]:
        """删除租户"""
        print(f"\n⚠️ 删除租户: {tenant_id}")

        if tenant_id not in self.tenants:
            print(f"❌ 租户不存在: {tenant_id}")
            return {"success": False, "error": "租户不存在"}

        if not force:
            confirm = input(f"   ⚠️ 确认删除租户 {tenant_id}? 所有数据将丢失! (yes/no): ")
            if confirm.lower() != "yes":
                print("   已取消删除")
                return {"success": False, "error": "用户取消"}

        # 删除目录
        tenant_dir = Path(self.tenants[tenant_id]["directory"])
        if tenant_dir.exists():
            shutil.rmtree(tenant_dir)

        # 从列表移除
        del self.tenants[tenant_id]
        self._save_tenants()

        print(f"✅ 租户已删除: {tenant_id}")

        return {"success": True, "deleted_tenant": tenant_id}

    def switch_tenant(self, tenant_id: str) -> Dict[str, Any]:
        """切换当前租户"""
        print(f"\n🔄 切换到租户: {tenant_id}")

        if tenant_id not in self.tenants:
            print(f"❌ 租户不存在: {tenant_id}")
            return {"success": False, "error": "租户不存在"}

        tenant = self.tenants[tenant_id]
        tenant_dir = Path(tenant["directory"])

        # 创建 .tenant 文件标记当前租户
        with open(self.base_dir / ".current_tenant", 'w', encoding='utf-8') as f:
            f.write(tenant_id)

        print(f"✅ 已切换到租户: {tenant_id}")
        print(f"   配置目录: {tenant_dir / 'config'}")
        print(f"   记忆目录: {tenant_dir / 'memory'}")
        print(f"   知识库目录: {tenant_dir / 'knowledge-base'}")

        return {"success": True, "switched_to": tenant_id}

    def get_current_tenant(self) -> str:
        """获取当前租户"""
        current_tenant_file = self.base_dir / ".current_tenant"
        if current_tenant_file.exists():
            return current_tenant_file.read_text().strip()
        return "default"


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="OpenClaw 多租户管理器")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 创建租户
    create_parser = subparsers.add_parser("create", help="创建新租户")
    create_parser.add_argument("tenant_id", help="租户ID")
    create_parser.add_argument("--name", help="租户名称")
    create_parser.add_argument("--max-agents", type=int, default=10, help="最大Agent数量")
    create_parser.add_argument("--max-memory-gb", type=int, default=10, help="最大内存(GB)")

    # 列出租户
    subparsers.add_parser("list", help="列出所有租户")

    # 查看租户信息
    info_parser = subparsers.add_parser("info", help="查看租户信息")
    info_parser.add_argument("tenant_id", help="租户ID")

    # 更新租户配额
    quota_parser = subparsers.add_parser("quota", help="更新租户配额")
    quota_parser.add_argument("tenant_id", help="租户ID")
    quota_parser.add_argument("--max-agents", type=int, help="最大Agent数量")
    quota_parser.add_argument("--max-memory-gb", type=int, help="最大内存(GB)")
    quota_parser.add_argument("--max-llm-calls", type=int, help="日LLM调用上限")

    # 删除租户
    delete_parser = subparsers.add_parser("delete", help="删除租户")
    delete_parser.add_argument("tenant_id", help="租户ID")
    delete_parser.add_argument("--force", action="store_true", help="强制删除，不提示确认")

    # 切换租户
    switch_parser = subparsers.add_parser("switch", help="切换当前租户")
    switch_parser.add_argument("tenant_id", help="租户ID")

    args = parser.parse_args()

    tm = TenantManager()

    if args.command == "create":
        quota = {
            "max_agents": args.max_agents,
            "max_memory_gb": args.max_memory_gb,
        }
        tm.create_tenant(args.tenant_id, tenant_name=args.name, quota=quota)

    elif args.command == "list":
        tm.list_tenants()

    elif args.command == "info":
        tm.get_tenant_info(args.tenant_id)

    elif args.command == "quota":
        new_quota = {}
        if args.max_agents is not None:
            new_quota["max_agents"] = args.max_agents
        if args.max_memory_gb is not None:
            new_quota["max_memory_gb"] = args.max_memory_gb
        if args.max_llm_calls is not None:
            new_quota["max_daily_llm_calls"] = args.max_llm_calls
        tm.update_tenant_quota(args.tenant_id, new_quota)

    elif args.command == "delete":
        tm.delete_tenant(args.tenant_id, force=args.force)

    elif args.command == "switch":
        tm.switch_tenant(args.tenant_id)

    else:
        parser.print_help()
        print(f"\n💡 当前租户: {tm.get_current_tenant()}")


if __name__ == "__main__":
    main()
