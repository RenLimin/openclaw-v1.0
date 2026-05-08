#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 安全钩子安装脚本

自动将安全卫士集成到 Git pre-commit 钩子中
实现提交前强制检查机制

创建时间：2026-05-08
"""

import os
import stat
from pathlib import Path

PRE_COMMIT_HOOK_CONTENT = '''#!/bin/bash
# ==============================================
# OpenClaw Git 预提交强制安全检查钩子
# ==============================================
# 此钩子由 install_security_hooks.py 自动安装
# 任何提交必须通过此检查！

echo "🔒"
echo "🔒 ============================================"
echo "🔒 OpenClaw 安全卫士 - 提交前强制检查"
echo "🔒 ============================================"
echo ""

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 python3"
    exit 1
fi

# 找到安全卫士脚本路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GUARD_SCRIPT="$SCRIPT_DIR/../../deploy-system/scripts/security_guard.py"

# 如果找不到，尝试在工作区查找
if [ ! -f "$GUARD_SCRIPT" ]; then
    GUARD_SCRIPT=$(find "$SCRIPT_DIR" -name "security_guard.py" -path "*/deploy-system/*" 2>/dev/null | head -1)
fi

if [ ! -f "$GUARD_SCRIPT" ]; then
    echo "⚠️  找不到安全卫士脚本，跳过强制检查（不推荐）"
    echo "💡 建议运行: python deploy-system/scripts/install_security_hooks.py"
    exit 0
fi

# 运行安全检查
echo "🚦 执行提交前安全检查..."
echo ""

python3 "$GUARD_SCRIPT" pre-commit

EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "❌ ============================================"
    echo "❌ 安全检查未通过，提交已终止！"
    echo "❌ ============================================"
    exit $EXIT_CODE
fi

echo ""
echo "✅ ============================================"
echo "✅ 所有安全检查通过，允许提交！"
echo "✅ ============================================"
echo ""
exit 0
'''


def install_pre_commit_hook():
    """安装 pre-commit 钩子"""
    git_dir = Path.cwd() / ".git"
    hooks_dir = git_dir / "hooks"
    pre_commit_file = hooks_dir / "pre-commit"

    if not git_dir.exists():
        print("❌ 未找到 .git 目录，请在 Git 仓库根目录运行此脚本")
        return False

    # 备份原有的钩子
    if pre_commit_file.exists():
        backup_file = hooks_dir / "pre-commit.backup_before_openclaw"
        import shutil
        shutil.copy2(pre_commit_file, backup_file)
        print(f"💾 已备份原有钩子到: {backup_file}")

    # 写入新钩子
    with open(pre_commit_file, 'w', encoding='utf-8') as f:
        f.write(PRE_COMMIT_HOOK_CONTENT)

    # 设置执行权限
    os.chmod(pre_commit_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
             stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

    print(f"✅ 安全钩子已安装到: {pre_commit_file}")
    print(f"✅ 从此刻起，所有 git commit 操作必须经过安全检查！")
    print()
    print("💡 提示：可以通过以下命令跳过钩子（仅限紧急情况）：")
    print("   git commit --no-verify")
    print()
    return True


def test_security_guard():
    """测试安全卫士脚本是否正常"""
    guard_script = Path.cwd() / "deploy-system" / "scripts" / "security_guard.py"
    if not guard_script.exists():
        print(f"❌ 找不到安全卫士脚本: {guard_script}")
        return False

    print(f"✅ 安全卫士脚本位置正确: {guard_script}")
    return True


def main():
    print("🔧" + "=" * 58)
    print("🔧 OpenClaw 安全钩子安装程序 v1.0")
    print("🔧" + "=" * 58)
    print()

    # 测试脚本
    if not test_security_guard():
        print("\n❌ 安全卫士检查未通过，请先确保脚本存在")
        return 1

    print()

    # 安装钩子
    if install_pre_commit_hook():
        print("🎉 安全机制安装完成！")
        print()
        print("📋 生效的安全机制：")
        print("   1. ✅ 提交前强制用户批准验证")
        print("   2. ✅ 版本依赖关系同步检查")
        print("   3. ✅ 敏感文件泄漏检测")
        print("   4. ✅ 违规行为审计日志")
        print()
        return 0
    else:
        print("\n❌ 安装失败")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
