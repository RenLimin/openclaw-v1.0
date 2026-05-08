#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 敏感操作前置检查快捷脚本

在执行敏感操作前调用，自动弹出对应检查清单

用法：
    python check_sensitive_op.py <operation_type>
    
支持的操作类型：
    - doc_change: 文档变更（修改带版本号的文档时）
    - github_push: GitHub 提交前
    - team_create: 创建智能体团队前
    - config_change: 修改核心配置前

创建时间：2026-05-08
"""

import sys
import os

# 添加脚本路径
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "skills", "agent-team-creator", "scripts"
))

try:
    from evolution_engine import EvolutionEngine
except ImportError:
    # 直接从绝对路径导入
    import sys
    sys.path.insert(0, "/Users/bangcle/.openclaw/workspace/skills/agent-team-creator/scripts")
    from evolution_engine import EvolutionEngine

def main():
    if len(sys.argv) < 2:
        print("🔍 敏感操作前置检查工具 v1.0")
        print("=" * 60)
        print("用法: python check_sensitive_op.py <operation_type>")
        print("")
        print("支持的操作类型：")
        print("  📝 doc_change    - 文档变更（修改带版本号的文档时）")
        print("  🐙 github_push   - GitHub 提交前")
        print("  👥 team_create   - 创建智能体团队前")
        print("  ⚙️  config_change  - 修改核心配置前")
        print("  📊 status        - 显示当前成熟度状态")
        print("")
        print("示例：")
        print("  python check_sensitive_op.py github_push")
        return
    
    operation_type = sys.argv[1]
    
    engine = EvolutionEngine()
    
    if operation_type == "status":
        engine.show_status()
    else:
        engine.monitor_sensitive_operation(operation_type)

if __name__ == "__main__":
    main()
