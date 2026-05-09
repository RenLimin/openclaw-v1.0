-- ========================================
-- 核心数据库 Schema - SQLite 语法
-- 交付管理系统 - 18张核心表
-- ========================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- ========================================
-- 合同域 (4张表)
-- ========================================

-- 合同主表
CREATE TABLE IF NOT EXISTS contract_contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_no VARCHAR(50) UNIQUE NOT NULL,
    contract_name VARCHAR(200) NOT NULL,
    contract_type VARCHAR(50) NOT NULL, -- 销售合同/采购合同/服务合同等
    party_a VARCHAR(200) NOT NULL,
    party_b VARCHAR(200) NOT NULL,
    sign_date DATE,
    start_date DATE,
    end_date DATE,
    total_amount DECIMAL(15, 2) DEFAULT 0.00,
    currency VARCHAR(10) DEFAULT 'CNY',
    status VARCHAR(50) DEFAULT 'draft', -- draft/active/expired/terminated
    owner VARCHAR(100),
    department VARCHAR(100),
    description TEXT,
    attachment_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100)
);

-- 合同明细/行项目表
CREATE TABLE IF NOT EXISTS contract_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    item_no VARCHAR(50),
    item_name VARCHAR(200) NOT NULL,
    item_type VARCHAR(50),
    quantity DECIMAL(15, 4) DEFAULT 1,
    unit_price DECIMAL(15, 2) DEFAULT 0.00,
    total_price DECIMAL(15, 2) DEFAULT 0.00,
    unit VARCHAR(50),
    delivery_date DATE,
    status VARCHAR(50) DEFAULT 'pending',
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contract_id) REFERENCES contract_contracts(id) ON DELETE CASCADE
);

-- 合同风险表
CREATE TABLE IF NOT EXISTS contract_risk (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    risk_type VARCHAR(50) NOT NULL, -- financial/legal/operational/compliance
    risk_level VARCHAR(50) DEFAULT 'medium', -- low/medium/high/critical
    risk_title VARCHAR(200) NOT NULL,
    risk_description TEXT,
    identified_date DATE,
    mitigation_measures TEXT,
    responsible_person VARCHAR(100),
    due_date DATE,
    status VARCHAR(50) DEFAULT 'open', -- open/mitigated/closed/monitored
    resolution TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contract_id) REFERENCES contract_contracts(id) ON DELETE CASCADE
);

-- 合同履行/回款计划表
CREATE TABLE IF NOT EXISTS contract_fulfillment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    milestone VARCHAR(200) NOT NULL,
    milestone_type VARCHAR(50), -- delivery/payment/acceptance
    planned_date DATE,
    actual_date DATE,
    amount DECIMAL(15, 2) DEFAULT 0.00,
    status VARCHAR(50) DEFAULT 'pending', -- pending/in_progress/completed/delayed
    responsible_person VARCHAR(100),
    deliverables TEXT,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contract_id) REFERENCES contract_contracts(id) ON DELETE CASCADE
);

-- ========================================
-- 项目域 (6张表)
-- ========================================

-- 项目主表
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_code VARCHAR(50) UNIQUE NOT NULL,
    project_name VARCHAR(200) NOT NULL,
    project_type VARCHAR(50), -- development/implementation/consulting/maintenance
    contract_id INTEGER,
    client_name VARCHAR(200),
    pm_name VARCHAR(100),
    department VARCHAR(100),
    start_date DATE,
    end_date DATE,
    planned_budget DECIMAL(15, 2) DEFAULT 0.00,
    actual_budget DECIMAL(15, 2) DEFAULT 0.00,
    status VARCHAR(50) DEFAULT 'init', -- init/planning/in_progress/testing/delivered/closed
    priority VARCHAR(50) DEFAULT 'medium',
    progress INTEGER DEFAULT 0,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    FOREIGN KEY (contract_id) REFERENCES contract_contracts(id) ON DELETE SET NULL
);

-- 项目任务表
CREATE TABLE IF NOT EXISTS project_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    parent_id INTEGER,
    task_code VARCHAR(50),
    task_name VARCHAR(200) NOT NULL,
    task_type VARCHAR(50),
    assignee VARCHAR(100),
    start_date DATE,
    end_date DATE,
    planned_hours DECIMAL(10, 2) DEFAULT 0,
    actual_hours DECIMAL(10, 2) DEFAULT 0,
    priority VARCHAR(50) DEFAULT 'medium',
    status VARCHAR(50) DEFAULT 'todo', -- todo/in_progress/review/done/blocked
    progress INTEGER DEFAULT 0,
    description TEXT,
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES project_tasks(id) ON DELETE SET NULL
);

-- 项目成本表
CREATE TABLE IF NOT EXISTS project_costs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    cost_type VARCHAR(50) NOT NULL, -- labor/material/travel/software/outsourcing/other
    cost_category VARCHAR(100),
    cost_name VARCHAR(200) NOT NULL,
    planned_amount DECIMAL(15, 2) DEFAULT 0.00,
    actual_amount DECIMAL(15, 2) DEFAULT 0.00,
    occurrence_date DATE,
    vendor VARCHAR(200),
    invoice_no VARCHAR(100),
    approver VARCHAR(100),
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- 需求表
CREATE TABLE IF NOT EXISTS requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    req_code VARCHAR(50) UNIQUE NOT NULL,
    req_name VARCHAR(200) NOT NULL,
    req_type VARCHAR(50), -- functional/non_functional/business/user
    source VARCHAR(100),
    priority VARCHAR(50) DEFAULT 'medium',
    severity VARCHAR(50) DEFAULT 'normal',
    status VARCHAR(50) DEFAULT 'draft', -- draft/review/approved/in_dev/tested/delivered/rejected
    description TEXT,
    acceptance_criteria TEXT,
    owner VARCHAR(100),
    estimated_effort DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- 工时记录表
CREATE TABLE IF NOT EXISTS work_hours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER,
    project_id INTEGER NOT NULL,
    user_name VARCHAR(100) NOT NULL,
    work_date DATE NOT NULL,
    hours DECIMAL(4, 2) NOT NULL,
    work_type VARCHAR(50), -- development/testing/review/meeting/training
    description TEXT,
    is_overtime BOOLEAN DEFAULT 0,
    approver VARCHAR(100),
    status VARCHAR(50) DEFAULT 'submitted', -- submitted/approved/rejected
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES project_tasks(id) ON DELETE SET NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- 测试用例表
CREATE TABLE IF NOT EXISTS test_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    requirement_id INTEGER,
    case_code VARCHAR(50) UNIQUE NOT NULL,
    case_name VARCHAR(200) NOT NULL,
    case_type VARCHAR(50), -- functional/performance/security/regression
    module VARCHAR(100),
    priority VARCHAR(50) DEFAULT 'medium',
    preconditions TEXT,
    test_steps TEXT,
    expected_results TEXT,
    actual_results TEXT,
    status VARCHAR(50) DEFAULT 'draft', -- draft/ready/pass/fail/blocked
    executor VARCHAR(100),
    execution_date DATE,
    defects_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (requirement_id) REFERENCES requirements(id) ON DELETE SET NULL
);

-- ========================================
-- 经营域 (2张表)
-- ========================================

-- 经营报告表
CREATE TABLE IF NOT EXISTS business_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_period VARCHAR(50) NOT NULL, -- YYYY-MM / YYYY-Q / YYYY
    report_type VARCHAR(50) NOT NULL, -- monthly/quarterly/annual
    department VARCHAR(100),
    total_revenue DECIMAL(15, 2) DEFAULT 0.00,
    total_cost DECIMAL(15, 2) DEFAULT 0.00,
    gross_profit DECIMAL(15, 2) DEFAULT 0.00,
    gross_margin DECIMAL(5, 2) DEFAULT 0.00,
    project_count INTEGER DEFAULT 0,
    completed_projects INTEGER DEFAULT 0,
    new_clients INTEGER DEFAULT 0,
    employee_count INTEGER DEFAULT 0,
    kpi_scores TEXT,
    highlights TEXT,
    risks TEXT,
    recommendations TEXT,
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100)
);

-- 财务数据表
CREATE TABLE IF NOT EXISTS finance_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fiscal_period VARCHAR(50) NOT NULL,
    data_type VARCHAR(50) NOT NULL, -- revenue/expense/asset/liability/cashflow
    category VARCHAR(100) NOT NULL,
    sub_category VARCHAR(100),
    amount DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    currency VARCHAR(10) DEFAULT 'CNY',
    department VARCHAR(100),
    project_id INTEGER,
    vendor VARCHAR(200),
    client VARCHAR(200),
    invoice_no VARCHAR(100),
    transaction_date DATE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
);

-- ========================================
-- RAG知识域 (4张表)
-- ========================================

-- 知识库集合表
CREATE TABLE IF NOT EXISTS rag_collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_name VARCHAR(200) NOT NULL,
    collection_code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    embedding_model VARCHAR(100) NOT NULL,
    dimension INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    permission VARCHAR(50) DEFAULT 'private', -- private/public/team
    owner VARCHAR(100),
    tags TEXT,
    document_count INTEGER DEFAULT 0,
    chunk_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 文档表
CREATE TABLE IF NOT EXISTS rag_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_id INTEGER NOT NULL,
    doc_title VARCHAR(500) NOT NULL,
    doc_type VARCHAR(50), -- pdf/docx/pptx/txt/markdown/html
    source_url TEXT,
    file_path TEXT,
    file_size INTEGER,
    content_hash VARCHAR(100),
    status VARCHAR(50) DEFAULT 'uploaded', -- uploaded/processing/indexed/failed
    chunk_count INTEGER DEFAULT 0,
    token_count INTEGER DEFAULT 0,
    metadata_json TEXT, -- JSON 格式的元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    FOREIGN KEY (collection_id) REFERENCES rag_collections(id) ON DELETE CASCADE
);

-- 文档分块表
CREATE TABLE IF NOT EXISTS rag_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    token_count INTEGER DEFAULT 0,
    start_pos INTEGER,
    end_pos INTEGER,
    section_title VARCHAR(500),
    metadata_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES rag_documents(id) ON DELETE CASCADE
);

-- 向量表
CREATE TABLE IF NOT EXISTS rag_vectors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id INTEGER NOT NULL,
    vector BLOB NOT NULL,
    embedding_model VARCHAR(100) NOT NULL,
    dimension INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chunk_id) REFERENCES rag_chunks(id) ON DELETE CASCADE
);

-- ========================================
-- 基础设施 (2张表)
-- ========================================

-- Prompt 模板表
CREATE TABLE IF NOT EXISTS prompt_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_code VARCHAR(100) UNIQUE NOT NULL,
    template_name VARCHAR(200) NOT NULL,
    template_type VARCHAR(50), -- chat/completion/system/function
    category VARCHAR(100),
    version VARCHAR(50) DEFAULT '1.0',
    prompt_text TEXT NOT NULL,
    input_variables TEXT, -- JSON 数组
    output_format TEXT,
    model_config TEXT, -- JSON 对象
    description TEXT,
    tags TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100)
);

-- LLM 调用日志表
CREATE TABLE IF NOT EXISTS llm_call_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id VARCHAR(100) UNIQUE NOT NULL,
    model VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    endpoint VARCHAR(200),
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    cost DECIMAL(15, 6) DEFAULT 0.00,
    currency VARCHAR(10) DEFAULT 'CNY',
    latency_ms INTEGER,
    status_code INTEGER,
    status VARCHAR(50), -- success/failed/timeout/canceled
    error_message TEXT,
    user_id VARCHAR(100),
    session_id VARCHAR(100),
    features TEXT, -- JSON 功能标签
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- 索引优化
-- ========================================

CREATE INDEX IF NOT EXISTS idx_contract_status ON contract_contracts(status);
CREATE INDEX IF NOT EXISTS idx_contract_date ON contract_contracts(sign_date);
CREATE INDEX IF NOT EXISTS idx_project_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_project_pm ON projects(pm_name);
CREATE INDEX IF NOT EXISTS idx_task_assignee ON project_tasks(assignee);
CREATE INDEX IF NOT EXISTS idx_task_status ON project_tasks(status);
CREATE INDEX IF NOT EXISTS idx_workhours_date ON work_hours(work_date);
CREATE INDEX IF NOT EXISTS idx_workhours_user ON work_hours(user_name);
CREATE INDEX IF NOT EXISTS idx_llmlog_date ON llm_call_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_llmlog_model ON llm_call_logs(model);
CREATE INDEX IF NOT EXISTS idx_ragdoc_collection ON rag_documents(collection_id);
CREATE INDEX IF NOT EXISTS idx_ragchunk_doc ON rag_chunks(document_id);
