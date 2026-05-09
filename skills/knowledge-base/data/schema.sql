-- ============================================================
-- 知识库体系架构 v4.0.0 数据库 schema
-- ============================================================
-- SQLite 3.x 兼容
-- 支持全文检索 (FTS5)
-- ============================================================

-- 1. knowledge_sources - 数据源注册表
CREATE TABLE IF NOT EXISTS knowledge_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,           -- 数据源名称
    type TEXT NOT NULL,                 -- offline_doc / web_page / agent_memory
    config_json TEXT NOT NULL,          -- 完整配置 JSON
    status TEXT DEFAULT 'active',       -- active / inactive / error
    last_scan_at TIMESTAMP,              -- 上次扫描时间
    next_scan_at TIMESTAMP,              -- 下次计划扫描
    total_documents INTEGER DEFAULT 0,   -- 总文档数
    total_chunks INTEGER DEFAULT 0,       -- 总分块数
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. documents - 文档主表
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,         -- 关联数据源
    uri TEXT NOT NULL,                  -- 唯一资源标识（路径/URL）
    title TEXT,                         -- 文档标题
    doc_type TEXT NOT NULL,             -- 文档类型（扩展名/MIME）
    file_size INTEGER,                  -- 文件大小（字节）
    content_hash TEXT NOT NULL,         -- MD5/SHA256 内容哈希（用于增量检测）
    last_modified_at TIMESTAMP,         -- 源文件修改时间
    metadata_json TEXT,                 -- 扩展元数据
    chunk_count INTEGER DEFAULT 0,      -- 分块数量
    token_count INTEGER DEFAULT 0,      -- 总 Token 数
    status TEXT DEFAULT 'active',       -- active / archived / deleted
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (source_id) REFERENCES knowledge_sources(id),
    UNIQUE(source_id, uri)              -- 同一数据源内 URI 唯一
);

-- 文档表索引
CREATE INDEX IF NOT EXISTS idx_documents_source ON documents(source_id);
CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(doc_type);
CREATE INDEX IF NOT EXISTS idx_documents_hash ON documents(content_hash);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);

-- 3. document_chunks - 文档分块表
CREATE TABLE IF NOT EXISTS document_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,       -- 关联文档
    chunk_index INTEGER NOT NULL,       -- 分块序号（从0开始）
    chunk_title TEXT,                   -- 分块所属标题
    content TEXT NOT NULL,              -- 分块文本内容
    content_length INTEGER NOT NULL,    -- 文本长度
    token_count INTEGER,                -- Token 估算
    page_number INTEGER,                -- 页码（如适用）
    context_path TEXT,                  -- 上下文路径（标题层级）
    metadata_json TEXT,                 -- 分块级元数据

    FOREIGN KEY (document_id) REFERENCES documents(id),
    UNIQUE(document_id, chunk_index)
);

-- 分块表索引
CREATE INDEX IF NOT EXISTS idx_chunks_document ON document_chunks(document_id);

-- 4. 全文索引 FTS5 (SQLite 内置全文检索
-- 支持中文检索，支持高性全文查询
CREATE VIRTUAL TABLE IF NOT EXISTS chunk_fts USING fts5(
    content,
    chunk_title,
    context_path,
    tokenize = 'unicode61 remove_diacritics 0'
);

-- 5. chunk_vectors - 向量索引表（可选，用于 FAISS）
CREATE TABLE IF NOT EXISTS chunk_vectors (
    chunk_id INTEGER PRIMARY KEY,
    vector BLOB NOT NULL,                 -- 向量二进制数据（FAISS 格式）
    model_name TEXT NOT NULL,             -- Embedding 模型名称
    model_version TEXT,                   -- 模型版本
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (chunk_id) REFERENCES document_chunks(id)
);

-- 6. knowledge_tags - 知识标签体系
CREATE TABLE IF NOT EXISTS knowledge_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,            -- 标签名
    category TEXT,                        -- 分类（领域/优先级/类型）
    color TEXT DEFAULT '#808080',         -- 展示颜色
    description TEXT,                     -- 标签描述
    usage_count INTEGER DEFAULT 0,        -- 使用次数
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 文档-标签关联表
CREATE TABLE IF NOT EXISTS document_tags (
    document_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    confidence REAL DEFAULT 1.0,          -- 标签置信度
    tagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (document_id, tag_id),
    FOREIGN KEY (document_id) REFERENCES documents(id),
    FOREIGN KEY (tag_id) REFERENCES knowledge_tags(id)
);

-- 7. knowledge_relations - 知识关联关系
CREATE TABLE IF NOT EXISTS knowledge_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_doc_id INTEGER NOT NULL,
    to_doc_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL,          -- references / duplicate / related / supersedes
    strength REAL DEFAULT 0.5,            -- 关联强度 0-1
    description TEXT,                     -- 关系描述
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (from_doc_id) REFERENCES documents(id),
    FOREIGN KEY (to_doc_id) REFERENCES documents(id),
    UNIQUE(from_doc_id, to_doc_id, relation_type)
);

-- 8. query_logs - 查询日志（用于优化检索）
CREATE TABLE IF NOT EXISTS query_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_text TEXT NOT NULL,             -- 查询文本
    top_results TEXT,                     -- TOP 结果 ID 列表（JSON）
    clicked_result INTEGER,               -- 用户点击的结果（如可收集）
    feedback_score INTEGER,               -- -1/0/+1 用户反馈评分
    execution_time_ms INTEGER,            -- 执行耗时
    result_count INTEGER,                 -- 返回结果数
    queried_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    agent_name TEXT                       -- 哪个智能体发起的查询
);

-- ============================================================
-- 视图：方便统计
-- ============================================================

-- 文档统计视图
CREATE VIEW IF NOT EXISTS document_stats AS
SELECT
    s.name as source_name,
    s.type as source_type,
    COUNT(d.id) as document_count,
    SUM(d.chunk_count) as total_chunks,
    SUM(d.file_size) as total_size
FROM knowledge_sources s
LEFT JOIN documents d ON s.id = d.source_id
GROUP BY s.id;

-- ============================================================
-- 触发器：自动更新时间戳
-- ============================================================

CREATE TRIGGER IF NOT EXISTS update_sources_timestamp
AFTER UPDATE ON knowledge_sources
BEGIN
    UPDATE knowledge_sources SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_documents_timestamp
AFTER UPDATE ON documents
BEGIN
    UPDATE documents SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
