# ========================================
# SQLAlchemy ORM 模型定义
# 交付管理系统 - 18张核心表
# ========================================

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, Text,
    Boolean, ForeignKey, DECIMAL, BLOB
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


# ========================================
# 合同域 (4张表)
# ========================================

class Contract(Base):
    """合同主表"""
    __tablename__ = 'contract_contracts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_no = Column(String(50), unique=True, nullable=False)
    contract_name = Column(String(200), nullable=False)
    contract_type = Column(String(50), nullable=False)  # 销售合同/采购合同/服务合同等
    party_a = Column(String(200), nullable=False)
    party_b = Column(String(200), nullable=False)
    sign_date = Column(Date)
    start_date = Column(Date)
    end_date = Column(Date)
    total_amount = Column(DECIMAL(15, 2), default=0.00)
    currency = Column(String(10), default='CNY')
    status = Column(String(50), default='draft')  # draft/active/expired/terminated
    owner = Column(String(100))
    department = Column(String(100))
    description = Column(Text)
    attachment_url = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(String(100))

    # 关系
    items = relationship('ContractItem', back_populates='contract', cascade='all, delete-orphan')
    risks = relationship('ContractRisk', back_populates='contract', cascade='all, delete-orphan')
    fulfillments = relationship('ContractFulfillment', back_populates='contract', cascade='all, delete-orphan')
    projects = relationship('Project', back_populates='contract')


class ContractItem(Base):
    """合同明细/行项目表"""
    __tablename__ = 'contract_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_id = Column(Integer, ForeignKey('contract_contracts.id', ondelete='CASCADE'), nullable=False)
    item_no = Column(String(50))
    item_name = Column(String(200), nullable=False)
    item_type = Column(String(50))
    quantity = Column(DECIMAL(15, 4), default=1)
    unit_price = Column(DECIMAL(15, 2), default=0.00)
    total_price = Column(DECIMAL(15, 2), default=0.00)
    unit = Column(String(50))
    delivery_date = Column(Date)
    status = Column(String(50), default='pending')
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    contract = relationship('Contract', back_populates='items')


class ContractRisk(Base):
    """合同风险表"""
    __tablename__ = 'contract_risk'

    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_id = Column(Integer, ForeignKey('contract_contracts.id', ondelete='CASCADE'), nullable=False)
    risk_type = Column(String(50), nullable=False)  # financial/legal/operational/compliance
    risk_level = Column(String(50), default='medium')  # low/medium/high/critical
    risk_title = Column(String(200), nullable=False)
    risk_description = Column(Text)
    identified_date = Column(Date)
    mitigation_measures = Column(Text)
    responsible_person = Column(String(100))
    due_date = Column(Date)
    status = Column(String(50), default='open')  # open/mitigated/closed/monitored
    resolution = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    contract = relationship('Contract', back_populates='risks')


class ContractFulfillment(Base):
    """合同履行/回款计划表"""
    __tablename__ = 'contract_fulfillment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_id = Column(Integer, ForeignKey('contract_contracts.id', ondelete='CASCADE'), nullable=False)
    milestone = Column(String(200), nullable=False)
    milestone_type = Column(String(50))  # delivery/payment/acceptance
    planned_date = Column(Date)
    actual_date = Column(Date)
    amount = Column(DECIMAL(15, 2), default=0.00)
    status = Column(String(50), default='pending')  # pending/in_progress/completed/delayed
    responsible_person = Column(String(100))
    deliverables = Column(Text)
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    contract = relationship('Contract', back_populates='fulfillments')


# ========================================
# 项目域 (6张表)
# ========================================

class Project(Base):
    """项目主表"""
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_code = Column(String(50), unique=True, nullable=False)
    project_name = Column(String(200), nullable=False)
    project_type = Column(String(50))  # development/implementation/consulting/maintenance
    contract_id = Column(Integer, ForeignKey('contract_contracts.id', ondelete='SET NULL'))
    client_name = Column(String(200))
    pm_name = Column(String(100))
    department = Column(String(100))
    start_date = Column(Date)
    end_date = Column(Date)
    planned_budget = Column(DECIMAL(15, 2), default=0.00)
    actual_budget = Column(DECIMAL(15, 2), default=0.00)
    status = Column(String(50), default='init')  # init/planning/in_progress/testing/delivered/closed
    priority = Column(String(50), default='medium')
    progress = Column(Integer, default=0)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(String(100))

    # 关系
    contract = relationship('Contract', back_populates='projects')
    tasks = relationship('ProjectTask', back_populates='project', cascade='all, delete-orphan')
    costs = relationship('ProjectCost', back_populates='project', cascade='all, delete-orphan')
    requirements = relationship('Requirement', back_populates='project', cascade='all, delete-orphan')
    work_hours = relationship('WorkHour', back_populates='project', cascade='all, delete-orphan')
    test_cases = relationship('TestCase', back_populates='project', cascade='all, delete-orphan')
    finance_data = relationship('FinanceData', back_populates='project')


class ProjectTask(Base):
    """项目任务表"""
    __tablename__ = 'project_tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    parent_id = Column(Integer, ForeignKey('project_tasks.id', ondelete='SET NULL'))
    task_code = Column(String(50))
    task_name = Column(String(200), nullable=False)
    task_type = Column(String(50))
    assignee = Column(String(100))
    start_date = Column(Date)
    end_date = Column(Date)
    planned_hours = Column(DECIMAL(10, 2), default=0)
    actual_hours = Column(DECIMAL(10, 2), default=0)
    priority = Column(String(50), default='medium')
    status = Column(String(50), default='todo')  # todo/in_progress/review/done/blocked
    progress = Column(Integer, default=0)
    description = Column(Text)
    tags = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    project = relationship('Project', back_populates='tasks')
    parent = relationship('ProjectTask', remote_side=[id], back_populates='children')
    children = relationship('ProjectTask', back_populates='parent', cascade='all')
    work_hours = relationship('WorkHour', back_populates='task')


class ProjectCost(Base):
    """项目成本表"""
    __tablename__ = 'project_costs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    cost_type = Column(String(50), nullable=False)  # labor/material/travel/software/outsourcing/other
    cost_category = Column(String(100))
    cost_name = Column(String(200), nullable=False)
    planned_amount = Column(DECIMAL(15, 2), default=0.00)
    actual_amount = Column(DECIMAL(15, 2), default=0.00)
    occurrence_date = Column(Date)
    vendor = Column(String(200))
    invoice_no = Column(String(100))
    approver = Column(String(100))
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    project = relationship('Project', back_populates='costs')


class Requirement(Base):
    """需求表"""
    __tablename__ = 'requirements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    req_code = Column(String(50), unique=True, nullable=False)
    req_name = Column(String(200), nullable=False)
    req_type = Column(String(50))  # functional/non_functional/business/user
    source = Column(String(100))
    priority = Column(String(50), default='medium')
    severity = Column(String(50), default='normal')
    status = Column(String(50), default='draft')  # draft/review/approved/in_dev/tested/delivered/rejected
    description = Column(Text)
    acceptance_criteria = Column(Text)
    owner = Column(String(100))
    estimated_effort = Column(DECIMAL(10, 2))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(String(100))

    # 关系
    project = relationship('Project', back_populates='requirements')
    test_cases = relationship('TestCase', back_populates='requirement')


class WorkHour(Base):
    """工时记录表"""
    __tablename__ = 'work_hours'

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey('project_tasks.id', ondelete='SET NULL'))
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    user_name = Column(String(100), nullable=False)
    work_date = Column(Date, nullable=False)
    hours = Column(DECIMAL(4, 2), nullable=False)
    work_type = Column(String(50))  # development/testing/review/meeting/training
    description = Column(Text)
    is_overtime = Column(Boolean, default=False)
    approver = Column(String(100))
    status = Column(String(50), default='submitted')  # submitted/approved/rejected
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    task = relationship('ProjectTask', back_populates='work_hours')
    project = relationship('Project', back_populates='work_hours')


class TestCase(Base):
    """测试用例表"""
    __tablename__ = 'test_cases'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    requirement_id = Column(Integer, ForeignKey('requirements.id', ondelete='SET NULL'))
    case_code = Column(String(50), unique=True, nullable=False)
    case_name = Column(String(200), nullable=False)
    case_type = Column(String(50))  # functional/performance/security/regression
    module = Column(String(100))
    priority = Column(String(50), default='medium')
    preconditions = Column(Text)
    test_steps = Column(Text)
    expected_results = Column(Text)
    actual_results = Column(Text)
    status = Column(String(50), default='draft')  # draft/ready/pass/fail/blocked
    executor = Column(String(100))
    execution_date = Column(Date)
    defects_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    project = relationship('Project', back_populates='test_cases')
    requirement = relationship('Requirement', back_populates='test_cases')


# ========================================
# 经营域 (2张表)
# ========================================

class BusinessReport(Base):
    """经营报告表"""
    __tablename__ = 'business_reports'

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_period = Column(String(50), nullable=False)  # YYYY-MM / YYYY-Q / YYYY
    report_type = Column(String(50), nullable=False)  # monthly/quarterly/annual
    department = Column(String(100))
    total_revenue = Column(DECIMAL(15, 2), default=0.00)
    total_cost = Column(DECIMAL(15, 2), default=0.00)
    gross_profit = Column(DECIMAL(15, 2), default=0.00)
    gross_margin = Column(DECIMAL(5, 2), default=0.00)
    project_count = Column(Integer, default=0)
    completed_projects = Column(Integer, default=0)
    new_clients = Column(Integer, default=0)
    employee_count = Column(Integer, default=0)
    kpi_scores = Column(Text)
    highlights = Column(Text)
    risks = Column(Text)
    recommendations = Column(Text)
    status = Column(String(50), default='draft')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(String(100))


class FinanceData(Base):
    """财务数据表"""
    __tablename__ = 'finance_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fiscal_period = Column(String(50), nullable=False)
    data_type = Column(String(50), nullable=False)  # revenue/expense/asset/liability/cashflow
    category = Column(String(100), nullable=False)
    sub_category = Column(String(100))
    amount = Column(DECIMAL(15, 2), nullable=False, default=0.00)
    currency = Column(String(10), default='CNY')
    department = Column(String(100))
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='SET NULL'))
    vendor = Column(String(200))
    client = Column(String(200))
    invoice_no = Column(String(100))
    transaction_date = Column(Date)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    project = relationship('Project', back_populates='finance_data')


# ========================================
# RAG知识域 (4张表)
# ========================================

class RagCollection(Base):
    """知识库集合表"""
    __tablename__ = 'rag_collections'

    id = Column(Integer, primary_key=True, autoincrement=True)
    collection_name = Column(String(200), nullable=False)
    collection_code = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    embedding_model = Column(String(100), nullable=False)
    dimension = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    permission = Column(String(50), default='private')  # private/public/team
    owner = Column(String(100))
    tags = Column(Text)
    document_count = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    documents = relationship('RagDocument', back_populates='collection', cascade='all, delete-orphan')


class RagDocument(Base):
    """文档表"""
    __tablename__ = 'rag_documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    collection_id = Column(Integer, ForeignKey('rag_collections.id', ondelete='CASCADE'), nullable=False)
    doc_title = Column(String(500), nullable=False)
    doc_type = Column(String(50))  # pdf/docx/pptx/txt/markdown/html
    source_url = Column(Text)
    file_path = Column(Text)
    file_size = Column(Integer)
    content_hash = Column(String(100))
    status = Column(String(50), default='uploaded')  # uploaded/processing/indexed/failed
    chunk_count = Column(Integer, default=0)
    token_count = Column(Integer, default=0)
    metadata_json = Column(Text)  # JSON 格式的元数据
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(String(100))

    # 关系
    collection = relationship('RagCollection', back_populates='documents')
    chunks = relationship('RagChunk', back_populates='document', cascade='all, delete-orphan')


class RagChunk(Base):
    """文档分块表"""
    __tablename__ = 'rag_chunks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey('rag_documents.id', ondelete='CASCADE'), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)
    start_pos = Column(Integer)
    end_pos = Column(Integer)
    section_title = Column(String(500))
    metadata_json = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    # 关系
    document = relationship('RagDocument', back_populates='chunks')
    vectors = relationship('RagVector', back_populates='chunk', cascade='all, delete-orphan')


class RagVector(Base):
    """向量表"""
    __tablename__ = 'rag_vectors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chunk_id = Column(Integer, ForeignKey('rag_chunks.id', ondelete='CASCADE'), nullable=False)
    vector = Column(BLOB, nullable=False)
    embedding_model = Column(String(100), nullable=False)
    dimension = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # 关系
    chunk = relationship('RagChunk', back_populates='vectors')


# ========================================
# 基础设施 (2张表)
# ========================================

class PromptTemplate(Base):
    """Prompt 模板表"""
    __tablename__ = 'prompt_templates'

    id = Column(Integer, primary_key=True, autoincrement=True)
    template_code = Column(String(100), unique=True, nullable=False)
    template_name = Column(String(200), nullable=False)
    template_type = Column(String(50))  # chat/completion/system/function
    category = Column(String(100))
    version = Column(String(50), default='1.0')
    prompt_text = Column(Text, nullable=False)
    input_variables = Column(Text)  # JSON 数组
    output_format = Column(Text)
    model_config = Column(Text)  # JSON 对象
    description = Column(Text)
    tags = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(String(100))


class LLMCallLog(Base):
    """LLM 调用日志表"""
    __tablename__ = 'llm_call_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String(100), unique=True, nullable=False)
    model = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False)
    endpoint = Column(String(200))
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost = Column(DECIMAL(15, 6), default=0.00)
    currency = Column(String(10), default='CNY')
    latency_ms = Column(Integer)
    status_code = Column(Integer)
    status = Column(String(50))  # success/failed/timeout/canceled
    error_message = Column(Text)
    user_id = Column(String(100))
    session_id = Column(String(100))
    features = Column(Text)  # JSON 功能标签
    created_at = Column(DateTime, default=datetime.now)
