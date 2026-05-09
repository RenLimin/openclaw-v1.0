#!/usr/bin/env python3
# ========================================
# 数据库初始化脚本
# 功能：创建 SQLite 数据库及所有表
# 使用方法：python init_db.py
# ========================================

import os
import sys
from pathlib import Path

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from sqlalchemy import create_engine, text
from models import Base

# 数据库文件路径
DB_PATH = current_dir / 'delivery_management.db'


def init_database():
    """
    初始化交付管理系统数据库
    
    功能说明：
    1. 检查数据库是否已存在，提示用户是否重建
    2. 创建 SQLite 数据库引擎
    3. 启用外键约束和 WAL 日志模式
    4. 创建所有 18 张业务表
    5. 验证并统计表创建结果
    
    Returns:
        bool: 初始化成功返回 True，失败返回 False
    """

    # 如果数据库已存在，先删除（可选）
    if DB_PATH.exists():
        print(f"⚠️  数据库已存在: {DB_PATH}")
        response = input("是否删除并重建？(y/N): ").strip().lower()
        if response == 'y':
            DB_PATH.unlink()
            print("✅ 已删除旧数据库")
        else:
            print("❌ 初始化已取消")
            return False

    # 创建 SQLite 引擎
    engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)

    print(f"🔧 开始创建数据库: {DB_PATH}")

    # 启用外键约束和 WAL 模式
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys = ON"))
        conn.execute(text("PRAGMA journal_mode = WAL"))
        conn.commit()

    # 创建所有表
    Base.metadata.create_all(engine)

    print("✅ 数据库表创建完成！")

    # 统计创建的表
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ))
        tables = [row[0] for row in result if not row[0].startswith('sqlite_')]

    print(f"\n📊 共创建 {len(tables)} 张表:")
    for i, table in enumerate(tables, 1):
        print(f"   {i:2d}. {table}")

    # 检查表数量是否为 18 张
    expected_tables = [
        'contract_contracts', 'contract_items', 'contract_risk', 'contract_fulfillment',
        'projects', 'project_tasks', 'project_costs', 'requirements', 'work_hours', 'test_cases',
        'business_reports', 'finance_data',
        'rag_collections', 'rag_documents', 'rag_chunks', 'rag_vectors',
        'prompt_templates', 'llm_call_logs'
    ]

    missing_tables = set(expected_tables) - set(tables)
    if missing_tables:
        print(f"\n❌ 缺少表: {missing_tables}")
        return False
    else:
        print(f"\n✅ 所有 18 张核心表已成功创建！")

    print(f"\n📁 数据库文件位置: {DB_PATH.resolve()}")
    return True


if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)
