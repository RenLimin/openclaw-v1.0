#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 配置管理器 v1.0

功能：
1. 多环境配置切换（dev/staging/prod）
2. 敏感信息加密/解密
3. 配置验证与校验

创建时间：2026-05-08
"""

import os
import sys
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("⚠️  cryptography 库未安装，加密功能不可用")
    print("   安装命令：pip install cryptography")


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "..", "config"
            )

        self.config_dir = Path(config_dir).resolve()
        self.current_env = os.getenv("OPENCLAW_ENV", "dev")
        self.config = None
        self.fernet = None

        print(f"🔧 配置管理器 v1.0")
        print(f"   配置目录：{self.config_dir}")
        print(f"   当前环境：{self.current_env}")

        # 初始化加密器
        self._init_crypto()

        # 加载配置
        self.load_config()

    def _init_crypto(self):
        """初始化加密器"""
        if not CRYPTO_AVAILABLE:
            return

        key = os.getenv("ENCRYPTION_KEY")
        if key:
            try:
                self.fernet = Fernet(key.encode())
                print("✅ 加密器初始化成功")
            except Exception as e:
                print(f"⚠️  加密器初始化失败：{e}")
        else:
            print("ℹ️  未设置 ENCRYPTION_KEY，加密功能不可用")

    def load_config(self, env: str = None) -> Dict[str, Any]:
        """加载指定环境的配置"""
        if env is None:
            env = self.current_env

        config_file = self.config_dir / f"config.{env}.yaml"

        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在：{config_file}")

        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        print(f"✅ 已加载 {env} 环境配置")
        return self.config

    def switch_env(self, env: str) -> bool:
        """切换环境"""
        valid_envs = ["dev", "staging", "prod"]

        if env not in valid_envs:
            print(f"❌ 无效环境：{env}，可选：{valid_envs}")
            return False

        try:
            self.load_config(env)
            self.current_env = env
            os.environ["OPENCLAW_ENV"] = env
            print(f"✅ 已切换到 {env} 环境")
            return True
        except Exception as e:
            print(f"❌ 切换环境失败：{e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        if self.config is None:
            return default

        # 支持嵌套键，如 "llm.provider"
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def encrypt_secret(self, plain_text: str) -> Optional[str]:
        """加密敏感信息"""
        if not self.fernet:
            print("⚠️  加密功能不可用")
            return None

        try:
            encrypted = self.fernet.encrypt(plain_text.encode())
            return encrypted.decode()
        except Exception as e:
            print(f"❌ 加密失败：{e}")
            return None

    def decrypt_secret(self, encrypted_text: str) -> Optional[str]:
        """解密敏感信息"""
        if not self.fernet:
            print("⚠️  解密功能不可用")
            return None

        try:
            decrypted = self.fernet.decrypt(encrypted_text.encode())
            return decrypted.decode()
        except Exception as e:
            print(f"❌ 解密失败：{e}")
            return None

    def validate_config(self) -> Dict[str, Any]:
        """验证配置完整性"""
        if self.config is None:
            return {"valid": False, "error": "未加载配置"}

        issues = []

        # 检查必需字段
        required_fields = ["env", "service", "llm"]
        for field in required_fields:
            if field not in self.config:
                issues.append(f"缺少必需字段：{field}")

        # 检查 LLM 配置
        llm_config = self.config.get("llm", {})
        if not llm_config.get("provider"):
            issues.append("未设置 LLM provider")

        result = {
            "valid": len(issues) == 0,
            "env": self.current_env,
            "issues": issues,
            "config_summary": {
                "env": self.get("env"),
                "service_name": self.get("service.name"),
                "llm_provider": self.get("llm.provider"),
                "llm_model": self.get("llm.model"),
                "auto_backup": self.get("features.auto_backup", False)
            }
        }

        if result["valid"]:
            print("✅ 配置验证通过")
        else:
            print(f"⚠️  配置发现 {len(issues)} 个问题：")
            for issue in issues:
                print(f"   - {issue}")

        return result

    @staticmethod
    def generate_encryption_key() -> str:
        """生成新的加密密钥"""
        if not CRYPTO_AVAILABLE:
            print("❌ 请先安装 cryptography 库")
            return ""

        key = Fernet.generate_key()
        print("✅ 已生成新的加密密钥：")
        print(f"   {key.decode()}")
        print("\n⚠️  请妥善保存此密钥，丢失将无法解密已加密的数据！")
        return key.decode()

    def list_envs(self) -> list:
        """列出所有可用的环境配置"""
        envs = []
        for file in self.config_dir.glob("config.*.yaml"):
            env_name = file.stem.replace("config.", "")
            envs.append(env_name)
        return sorted(envs)


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="OpenClaw 配置管理器")
    parser.add_argument(
        "action",
        choices=["list", "current", "switch", "validate", "gen-key"],
        help="执行操作"
    )
    parser.add_argument(
        "--env",
        choices=["dev", "staging", "prod"],
        help="目标环境（switch 命令使用）"
    )
    parser.add_argument(
        "--config-dir",
        help="配置文件目录"
    )

    args = parser.parse_args()

    cm = ConfigManager(config_dir=args.config_dir)

    if args.action == "list":
        print("\n📋 可用环境配置：")
        for env in cm.list_envs():
            current = " (当前)" if env == cm.current_env else ""
            print(f"   - {env}{current}")

    elif args.action == "current":
        print("\n📄 当前配置摘要：")
        result = cm.validate_config()
        print(json.dumps(result["config_summary"], indent=2, ensure_ascii=False))

    elif args.action == "switch":
        if not args.env:
            print("❌ 请使用 --env 指定目标环境")
            sys.exit(1)
        cm.switch_env(args.env)

    elif args.action == "validate":
        print("\n🔍 验证配置：")
        cm.validate_config()

    elif args.action == "gen-key":
        print("\n🔑 生成加密密钥：")
        ConfigManager.generate_encryption_key()


if __name__ == "__main__":
    main()
