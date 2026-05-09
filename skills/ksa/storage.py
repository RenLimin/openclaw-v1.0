# ========================================
# KSA 存储引擎
# SQLite 数据库存储，接入 delivery_management.db
# ========================================

import os
from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .models import Base

# 默认数据库路径 - 接入 delivery_management.db
DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'delivery_core', 'database', 'delivery_management.db'
)


class KSAStorage:
    """KSA 存储引擎"""

    def __init__(self, db_path: Optional[str] = None):
        """
        初始化存储引擎
        
        Args:
            db_path: SQLite 数据库文件路径，默认使用 delivery_management.db
        """
        self.db_path = db_path or DEFAULT_DB_PATH
        self._ensure_db_directory()
        
        # 使用 SQLite 特定配置
        self.engine = create_engine(
            f'sqlite:///{self.db_path}',
            connect_args={'check_same_thread': False},
            poolclass=StaticPool,
            echo=False
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def _ensure_db_directory(self):
        """确保数据库目录存在"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    def init_tables(self):
        """初始化 KSA 相关表"""
        # 只创建 KSA 模块的表，不影响已有表
        from .models import (
            Knowledge, Skill, Ability,
            skill_knowledge_association, skill_skill_association,
            ability_knowledge_association, ability_skill_association
        )
        tables_to_create = [
            skill_knowledge_association, skill_skill_association,
            ability_knowledge_association, ability_skill_association,
            Knowledge.__table__, Skill.__table__, Ability.__table__
        ]
        
        # 检查表是否已存在，不存在则创建
        with self.engine.connect() as conn:
            for table in tables_to_create:
                if not self.engine.dialect.has_table(conn, table.name):
                    table.create(self.engine)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """获取数据库会话"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def execute_raw(self, sql: str, params: dict = None):
        """执行原生 SQL"""
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), params or {})
            conn.commit()
            return result

    def table_exists(self, table_name: str) -> bool:
        """检查表是否存在"""
        with self.engine.connect() as conn:
            return self.engine.dialect.has_table(conn, table_name)

    def get_table_info(self, table_name: str) -> dict:
        """获取表信息"""
        with self.engine.connect() as conn:
            result = conn.execute(text(f"PRAGMA table_info({table_name})"))
            columns = []
            for row in result:
                columns.append({
                    'cid': row[0],
                    'name': row[1],
                    'type': row[2],
                    'notnull': row[3],
                    'default': row[4],
                    'pk': row[5]
                })
            return {
                'table_name': table_name,
                'columns': columns
            }


# 全局单例
_default_storage: Optional[KSAStorage] = None


def get_default_storage() -> KSAStorage:
    """获取默认存储引擎实例"""
    global _default_storage
    if _default_storage is None:
        _default_storage = KSAStorage()
        _default_storage.init_tables()
    return _default_storage


def init_database(db_path: Optional[str] = None) -> KSAStorage:
    """初始化数据库"""
    storage = KSAStorage(db_path)
    storage.init_tables()
    return storage
