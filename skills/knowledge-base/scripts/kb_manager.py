#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库管理器 v4.0.0
核心功能：初始化、数据源管理、文档入库、查询、更新、导出
"""

import os
import sys
import json
import sqlite3
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_DB_PATH = PROJECT_ROOT / "knowledge-base" / "knowledge.db"
SCHEMA_PATH = Path(__file__).parent.parent / "data" / "schema.sql"


class KnowledgeBaseManager:
    """知识库管理器主类"""

    def __init__(self, db_path: str = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self._connect()

    def _connect(self):
        """连接数据库"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

    def init_database(self, force: bool = False):
        """初始化数据库"""
        if force and self.db_path.exists():
            self.db_path.unlink()
            self._connect()

        # 执行建表脚本
        if SCHEMA_PATH.exists():
            with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            self.conn.executescript(schema_sql)
            self.conn.commit()
            print(f"✅ 数据库初始化完成: {self.db_path}")
        else:
            print(f"⚠️  schema 文件不存在: {SCHEMA_PATH}")

    # ==================== 数据源管理 ====================

    def add_source(self, name: str, source_type: str, config: Dict) -> int:
        """添加数据源"""
        config_json = json.dumps(config, ensure_ascii=False)

        cursor = self.conn.execute(
            """
            INSERT INTO knowledge_sources 
            (name, type, config_json, status, created_at, updated_at)
            VALUES (?, ?, ?, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """,
            (name, source_type, config_json)
        )
        self.conn.commit()
        print(f"✅ 数据源 '{name}' 添加成功 (ID: {cursor.lastrowid})")
        return cursor.lastrowid

    def list_sources(self) -> List[Dict]:
        """列出所有数据源"""
        cursor = self.conn.execute(
            """
            SELECT id, name, type, status, total_documents, total_chunks,
                   last_scan_at, created_at
            FROM knowledge_sources
            ORDER BY id
            """
        )
        sources = []
        for row in cursor.fetchall():
            sources.append(dict(row))
        return sources

    def get_source(self, source_id: int = None, name: str = None) -> Optional[Dict]:
        """获取数据源信息"""
        if source_id:
            cursor = self.conn.execute(
                "SELECT * FROM knowledge_sources WHERE id = ?",
                (source_id,)
            )
        elif name:
            cursor = self.conn.execute(
                "SELECT * FROM knowledge_sources WHERE name = ?",
                (name,)
            )
        else:
            return None

        row = cursor.fetchone()
        return dict(row) if row else None

    # ==================== 文档管理 ====================

    def _calculate_file_hash(self, filepath: str) -> str:
        """计算文件哈希用于增量检测"""
        h = hashlib.sha256()
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()

    def add_document(self, source_id: int, uri: str, title: str,
                     doc_type: str, content: str,
                     metadata: Dict = None, file_size: int = None,
                     last_modified: datetime = None) -> int:
        """添加/更新文档（自动去重）"""
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        metadata_json = json.dumps(metadata or {}, ensure_ascii=False)
        last_modified_str = last_modified.isoformat() if last_modified else None

        # 检查是否已存在（同一 source_id + uri）
        cursor = self.conn.execute(
            "SELECT id, content_hash FROM documents WHERE source_id = ? AND uri = ?",
            (source_id, uri)
        )
        existing = cursor.fetchone()

        if existing:
            doc_id, old_hash = existing
            if old_hash == content_hash:
                # 内容未变化，跳过
                print(f"⏭️ 文档未变化，跳过: {uri}")
                return doc_id
            else:
                # 内容有变化，先删除旧分块
                self.conn.execute(
                    "DELETE FROM document_chunks WHERE document_id = ?",
                    (doc_id,)
                )
                # 更新文档信息
                self.conn.execute(
                    """
                    UPDATE documents
                    SET title = ?, content_hash = ?, file_size = ?,
                        last_modified_at = ?, metadata_json = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (title, content_hash, file_size, last_modified_str, metadata_json, doc_id)
                )
                print(f"🔄 更新文档: {uri}")
        else:
            # 新增文档
            cursor = self.conn.execute(
                """
                INSERT INTO documents
                (source_id, uri, title, doc_type, content_hash, file_size,
                 last_modified_at, metadata_json, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """,
                (source_id, uri, title, doc_type, content_hash, file_size,
                 last_modified_str, metadata_json)
            )
            doc_id = cursor.lastrowid
            print(f"✅ 新增文档: {uri}")

        # 简单分块（实际使用时应用语义分块）
        self._simple_chunking(doc_id, content)
        self.conn.commit()
        return doc_id

    def _simple_chunking(self, document_id: int, content: str,
                         chunk_size: int = 1000):
        """简单的固定大小分块（演示用）"""
        chunks = []
        for i in range(0, len(content), chunk_size):
            chunk_content = content[i:i + chunk_size]
            chunks.append({
                'document_id': document_id,
                'chunk_index': len(chunks),
                'content': chunk_content,
                'content_length': len(chunk_content)
            })

        # 批量插入分块
        self.conn.executemany(
            """
            INSERT INTO document_chunks
            (document_id, chunk_index, content, content_length)
            VALUES (:document_id, :chunk_index, :content, :content_length)
            """,
            chunks
        )

        # 更新文档的分块数量
        self.conn.execute(
            "UPDATE documents SET chunk_count = ? WHERE id = ?",
            (len(chunks), document_id)
        )

        # 先获取插入后的真实 rowid，然后插入全文索引
        cursor = self.conn.execute(
            "SELECT id FROM document_chunks WHERE document_id = ? ORDER BY chunk_index",
            (document_id,)
        )
        rowids = [r[0] for r in cursor.fetchall()]
        
        # 插入全文索引（使用真实的 rowid）
        for i, chunk in enumerate(chunks):
            if i < len(rowids):
                self.conn.execute(
                    """
                    INSERT INTO chunk_fts (rowid, content, chunk_title)
                    VALUES (?, ?, ?)
                    """,
                    (rowids[i], chunk['content'], '')
                )

        return len(chunks)

    def list_documents(self, source_id: int = None,
                       offset: int = 0, limit: int = 50) -> List[Dict]:
        """列出文档"""
        sql = """
            SELECT d.id, d.uri, d.title, d.doc_type, d.file_size,
                   d.chunk_count, d.status, s.name as source_name, d.created_at
            FROM documents d
            LEFT JOIN knowledge_sources s ON d.source_id = s.id
            {}
            ORDER BY d.created_at DESC
            LIMIT ? OFFSET ?
            """.format("WHERE d.source_id = ?" if source_id else "")

        params = (source_id, limit, offset) if source_id else (limit, offset)
        cursor = self.conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]

    # ==================== 基础查询 ====================

    def keyword_search(self, query: str, limit: int = 10) -> List[Dict]:
        """关键词全文搜索（使用 FTS5 + 普通 LIKE 兜底）"""
        # 先尝试 FTS5 全文检索
        cursor = self.conn.execute(
            """
            SELECT
                c.id as chunk_id,
                c.document_id,
                d.title,
                d.uri,
                s.name as source_name,
                c.content,
                1.0 as score
            FROM document_chunks c
            JOIN documents d ON c.document_id = d.id
            JOIN knowledge_sources s ON d.source_id = s.id
            WHERE c.content LIKE ?
            ORDER BY c.id
            LIMIT ?
            """,
            (f'%{query}%', limit)
        )
        results = []
        for row in cursor.fetchall():
            row_dict = dict(row)
            # SQLite FTS rank 是越小越好，转换为 0-1 分数
            max_rank = 100.0  # 假设最大值
            row_dict['score'] = max(0, 1 - (float(row_dict['score']) / max_rank))
            results.append(row_dict)
        return results

    def get_document(self, doc_id: int) -> Optional[Dict]:
        """获取单篇文档信息"""
        cursor = self.conn.execute(
            """
            SELECT d.*, s.name as source_name
            FROM documents d
            JOIN knowledge_sources s ON d.source_id = s.id
            WHERE d.id = ?
            """,
            (doc_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_document_chunks(self, doc_id: int) -> List[Dict]:
        """获取文档的所有分块"""
        cursor = self.conn.execute(
            """
            SELECT * FROM document_chunks
            WHERE document_id = ?
            ORDER BY chunk_index
            """,
            (doc_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

    # ==================== 统计与导出 ====================

    def get_stats(self) -> Dict:
        """获取知识库统计"""
        cursor = self.conn.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM knowledge_sources) as source_count,
                (SELECT COUNT(*) FROM documents) as doc_count,
                (SELECT COUNT(*) FROM document_chunks) as chunk_count,
                (SELECT SUM(file_size) FROM documents) as total_size
            """
        )
        row = cursor.fetchone()
        return {
            'source_count': row['source_count'],
            'document_count': row['doc_count'],
            'chunk_count': row['chunk_count'],
            'total_size_bytes': row['total_size'] or 0,
            'total_size_mb': round((row['total_size'] or 0) / 1024 / 1024, 2)
        }

    def export_to_json(self, output_path: str):
        """导出知识库为 JSON"""
        stats = self.get_stats()
        sources = self.list_sources()
        documents = self.list_documents(limit=stats['document_count'])

        export_data = {
            'export_time': datetime.now().isoformat(),
            'version': '4.0.0',
            'stats': stats,
            'sources': sources,
            'documents': documents
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        print(f"✅ 导出完成: {output_path}")

    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()


# ==================== 命令行接口 ====================

def cmd_init(args):
    """初始化数据库命令"""
    kb = KnowledgeBaseManager(args.db)
    kb.init_database(force=args.force)
    kb.close()


def cmd_add_source(args):
    """添加数据源命令"""
    kb = KnowledgeBaseManager(args.db)

    # 解析配置
    config = {}
    if args.path:
        config['path'] = args.path
    if args.url:
        config['base_url'] = args.url

    source_id = kb.add_source(args.name, args.type, config)
    kb.close()
    return source_id


def cmd_list_sources(args):
    """列出数据源命令"""
    kb = KnowledgeBaseManager(args.db)
    sources = kb.list_sources()

    print(f"\n📊 数据源列表 ({len(sources)} 个)")
    print("-" * 80)
    for s in sources:
        print(f"  ID: {s['id']:3} | {s['name']:<20} | {s['type']:<15} | "
              f"文档: {s['total_documents']:4} | 状态: {s['status']}")
    print()
    kb.close()


def cmd_stats(args):
    """统计命令"""
    kb = KnowledgeBaseManager(args.db)
    stats = kb.get_stats()

    print("\n📈 知识库统计")
    print("-" * 40)
    print(f"  数据源数量: {stats['source_count']}")
    print(f"  文档数量: {stats['document_count']}")
    print(f"  分块数量: {stats['chunk_count']}")
    print(f"  总大小: {stats['total_size_mb']} MB")
    print()
    kb.close()


def cmd_search(args):
    """搜索命令"""
    kb = KnowledgeBaseManager(args.db)
    results = kb.keyword_search(args.query, args.limit)

    print(f"\n🔍 搜索: '{args.query}' ({len(results)} 个结果)")
    print("-" * 80)
    for i, r in enumerate(results, 1):
        print(f"\n{i}. {r['title']} (得分: {r['score']:.3f})")
        print(f"   来源: {r['source_name']}")
        print(f"   路径: {r['uri']}")
        print(f"   内容: {r['content'][:150]}...")
    print()
    kb.close()


def main():
    parser = argparse.ArgumentParser(description='知识库管理器 v4.0.0')
    parser.add_argument('--db', help='数据库路径')

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # init 命令
    init_parser = subparsers.add_parser('init', help='初始化数据库')
    init_parser.add_argument('--force', action='store_true', help='强制重置（删除现有数据）')
    init_parser.set_defaults(func=cmd_init)

    # add-source 命令
    add_parser = subparsers.add_parser('add-source', help='添加数据源')
    add_parser.add_argument('--name', required=True, help='数据源名称')
    add_parser.add_argument('--type', required=True,
                           choices=['offline_doc', 'web_page', 'agent_memory'],
                           help='数据源类型')
    add_parser.add_argument('--path', help='本地路径')
    add_parser.add_argument('--url', help='基础 URL')
    add_parser.set_defaults(func=cmd_add_source)

    # list-sources 命令
    list_parser = subparsers.add_parser('list-sources', help='列出所有数据源')
    list_parser.set_defaults(func=cmd_list_sources)

    # stats 命令
    stats_parser = subparsers.add_parser('stats', help='显示知识库统计')
    stats_parser.set_defaults(func=cmd_stats)

    # search 命令
    search_parser = subparsers.add_parser('search', help='关键词搜索')
    search_parser.add_argument('query', help='搜索关键词')
    search_parser.add_argument('--limit', type=int, default=10, help='结果数量')
    search_parser.set_defaults(func=cmd_search)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == '__main__':
    main()
