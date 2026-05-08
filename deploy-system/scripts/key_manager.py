#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔐 API Key 安全管理器 v1.0

功能：
1. 安全存储 API Key（加密存储）
2. Key 使用审计与日志
3. 权限分级管理
4. Key 轮换与过期提醒
5. 使用量统计与限额告警

创建时间：2026-05-08
"""

import os
import sys
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("⚠️  cryptography 库未安装，加密功能不可用")


class APIKeyManager:
    """API Key 安全管理器"""

    def __init__(self, storage_dir: str = None):
        if storage_dir is None:
            storage_dir = os.path.expanduser("~/.openclaw/keys")

        self.storage_dir = Path(storage_dir).resolve()
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.keys_file = self.storage_dir / "api_keys.enc"
        self.audit_file = self.storage_dir / "audit.log"
        self.key_file = self.storage_dir / ".master_key"

        print("🔐 OpenClaw API Key 安全管理器 v1.0")
        print(f"   存储目录: {self.storage_dir}")

        # 初始化或加载主密钥
        self._init_master_key()
        self._fernet = Fernet(self._master_key) if CRYPTO_AVAILABLE else None

        # 加载已存储的 Keys
        self.keys = self._load_keys()

    def _init_master_key(self):
        """初始化主密钥"""
        if self.key_file.exists():
            with open(self.key_file, "rb") as f:
                self._master_key = f.read()
        else:
            if not CRYPTO_AVAILABLE:
                raise RuntimeError("请先安装 cryptography: pip install cryptography")

            # 生成新的主密钥
            self._master_key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(self._master_key)

            # 设置文件权限（仅所有者可读）
            os.chmod(self.key_file, 0o600)
            print("✅ 已生成新的主密钥")

    def _load_keys(self) -> Dict:
        """加载加密存储的 Keys"""
        if not self.keys_file.exists():
            return {}

        try:
            with open(self.keys_file, "rb") as f:
                encrypted_data = f.read()

            decrypted_data = self._fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            print(f"⚠️ 加载密钥存储失败: {e}")
            return {}

    def _save_keys(self):
        """保存加密的 Keys"""
        data = json.dumps(self.keys, ensure_ascii=False).encode()
        encrypted = self._fernet.encrypt(data)

        with open(self.keys_file, "wb") as f:
            f.write(encrypted)

        # 设置文件权限
        os.chmod(self.keys_file, 0o600)

    def _audit_log(self, action: str, key_name: str, details: str = ""):
        """记录审计日志"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {action}: {key_name} {details}\n"

        with open(self.audit_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

    def add_key(self, name: str, key_value: str, provider: str = "openai",
                permissions: List[str] = None, expires_days: int = 90,
                monthly_limit: float = None) -> bool:
        """添加新的 API Key"""
        if name in self.keys:
            print(f"❌ 密钥名称已存在: {name}")
            return False

        now = datetime.now()
        expires_at = now + timedelta(days=expires_days) if expires_days else None

        key_data = {
            "name": name,
            "provider": provider,
            "key_hash": hashlib.sha256(key_value.encode()).hexdigest(),
            "encrypted_key": self._fernet.encrypt(key_value.encode()).decode(),
            "permissions": permissions or ["read"],
            "created_at": now.isoformat(),
            "expires_at": expires_at.isoformat() if expires_at else None,
            "monthly_limit_usd": monthly_limit,
            "usage": {
                "total_calls": 0,
                "total_cost_usd": 0,
                "current_month_cost": 0,
                "last_used": None
            }
        }

        self.keys[name] = key_data
        self._save_keys()
        self._audit_log("ADD", name, f"provider={provider}")
        print(f"✅ 已添加密钥: {name}")

        return True

    def get_key(self, name: str, track_usage: bool = True) -> Optional[str]:
        """获取 API Key（追踪使用）"""
        if name not in self.keys:
            print(f"❌ 密钥不存在: {name}")
            return None

        key_data = self.keys[name]

        # 检查是否过期
        if key_data["expires_at"]:
            expires_at = datetime.fromisoformat(key_data["expires_at"])
            if datetime.now() > expires_at:
                print(f"⚠️ 密钥已过期: {name}")
                return None

        # 检查月度限额
        monthly_limit = key_data.get("monthly_limit_usd")
        current_cost = key_data["usage"].get("current_month_cost", 0)
        if monthly_limit and current_cost > monthly_limit * 0.9:
            print(f"⚠️ 密钥月度使用已达 {current_cost:.2f}/{monthly_limit} USD")
            if current_cost > monthly_limit:
                print(f"❌ 密钥已超出月度限额")
                return None

        # 追踪使用
        if track_usage:
            key_data["usage"]["total_calls"] += 1
            key_data["usage"]["last_used"] = datetime.now().isoformat()
            self._save_keys()
            self._audit_log("ACCESS", name)

        # 返回解密后的密钥
        encrypted_key = key_data["encrypted_key"].encode()
        return self._fernet.decrypt(encrypted_key).decode()

    def list_keys(self, show_details: bool = False):
        """列出所有密钥"""
        if not self.keys:
            print("   暂无存储的密钥")
            return

        print(f"\n{'='*80}")
        print(f"{'密钥名称':<25} {'提供商':<15} {'状态':<10} {'调用次数':<10} {'月度成本':<12}")
        print("-" * 80)

        for name, key_data in self.keys.items():
            status = "✅ 正常"

            # 检查过期
            if key_data["expires_at"]:
                expires_at = datetime.fromisoformat(key_data["expires_at"])
                if datetime.now() > expires_at:
                    status = "❌ 已过期"
                elif (expires_at - datetime.now()).days < 7:
                    status = "⚠️ 即将过期"

            usage = key_data["usage"]
            total_calls = usage["total_calls"]
            monthly_cost = usage.get("current_month_cost", 0)

            print(f"{name:<25} {key_data['provider']:<15} {status:<10} {total_calls:<10} ${monthly_cost:<11.2f}")

        print(f"{'='*80}\n")

    def delete_key(self, name: str) -> bool:
        """删除密钥"""
        if name not in self.keys:
            print(f"❌ 密钥不存在: {name}")
            return False

        del self.keys[name]
        self._save_keys()
        self._audit_log("DELETE", name)
        print(f"✅ 已删除密钥: {name}")
        return True

    def rotate_key(self, name: str, new_key_value: str) -> bool:
        """密钥轮换"""
        if name not in self.keys:
            print(f"❌ 密钥不存在: {name}")
            return False

        old_data = self.keys[name]

        # 创建新密钥（保留旧数据）
        old_data["encrypted_key"] = self._fernet.encrypt(new_key_value.encode()).decode()
        old_data["key_hash"] = hashlib.sha256(new_key_value.encode()).hexdigest()
        old_data["last_rotated_at"] = datetime.now().isoformat()

        self._save_keys()
        self._audit_log("ROTATE", name)
        print(f"✅ 密钥已轮换: {name}")
        return True

    def update_usage(self, name: str, cost_usd: float):
        """更新使用成本"""
        if name not in self.keys:
            return

        self.keys[name]["usage"]["total_cost_usd"] += cost_usd
        self.keys[name]["usage"]["current_month_cost"] += cost_usd
        self._save_keys()

    def show_audit_log(self, limit: int = 20):
        """显示审计日志"""
        if not self.audit_file.exists():
            print("   暂无审计日志")
            return

        with open(self.audit_file, encoding="utf-8") as f:
            lines = f.readlines()[-limit:]

        print(f"\n📋 最近 {len(lines)} 条审计记录:")
        for line in lines:
            print(f"   {line.strip()}")
        print()

    def check_expiring_soon(self, days: int = 7) -> List[str]:
        """检查即将过期的密钥"""
        soon = []
        for name, key_data in self.keys.items():
            if key_data["expires_at"]:
                expires_at = datetime.fromisoformat(key_data["expires_at"])
                days_left = (expires_at - datetime.now()).days
                if 0 <= days_left <= days:
                    soon.append(name)
                    print(f"⚠️ {name} 将在 {days_left} 天后过期")

        return soon


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="OpenClaw API Key 安全管理器")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # list 命令
    subparsers.add_parser("list", help="列出所有密钥")

    # add 命令
    add_parser = subparsers.add_parser("add", help="添加新密钥")
    add_parser.add_argument("name", help="密钥名称")
    add_parser.add_argument("key_value", help="API Key 值")
    add_parser.add_argument("--provider", default="openai", help="提供商")
    add_parser.add_argument("--expires", type=int, default=90, help="过期天数")
    add_parser.add_argument("--limit", type=float, help="月度限额 USD")

    # get 命令
    get_parser = subparsers.add_parser("get", help="获取密钥")
    get_parser.add_argument("name", help="密钥名称")

    # delete 命令
    delete_parser = subparsers.add_parser("delete", help="删除密钥")
    delete_parser.add_argument("name", help="密钥名称")

    # rotate 命令
    rotate_parser = subparsers.add_parser("rotate", help="轮换密钥")
    rotate_parser.add_argument("name", help="密钥名称")
    rotate_parser.add_argument("new_key", help="新的密钥值")

    # audit 命令
    audit_parser = subparsers.add_parser("audit", help="查看审计日志")
    audit_parser.add_argument("--limit", type=int, default=20, help="显示条数")

    args = parser.parse_args()

    km = APIKeyManager()

    if args.command == "list" or args.command is None:
        km.list_keys()

    elif args.command == "add":
        km.add_key(
            args.name, args.key_value,
            provider=args.provider,
            expires_days=args.expires,
            monthly_limit=args.limit
        )

    elif args.command == "get":
        key = km.get_key(args.name)
        if key:
            print(f"\n🔑 {args.name}: {key[:10]}...{key[-4:]}")

    elif args.command == "delete":
        km.delete_key(args.name)

    elif args.command == "rotate":
        km.rotate_key(args.name, args.new_key)

    elif args.command == "audit":
        km.show_audit_log(args.limit)


if __name__ == "__main__":
    main()
