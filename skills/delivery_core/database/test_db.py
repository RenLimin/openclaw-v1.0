#!/usr/bin/env python3
# ========================================
# 数据库测试脚本
# 功能：验证数据库可正常初始化并写入测试数据
# 使用方法：python test_db.py
# ========================================

import os
import sys
from pathlib import Path
from datetime import date, datetime

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import (
    Base, Contract, ContractItem, ContractRisk, ContractFulfillment,
    Project, ProjectTask, ProjectCost, Requirement, WorkHour, TestCase,
    BusinessReport, FinanceData,
    RagCollection, RagDocument, RagChunk, RagVector,
    PromptTemplate, LLMCallLog
)

# 测试数据库路径
TEST_DB_PATH = current_dir / 'test_delivery.db'


def setup_test_database():
    """
    初始化测试数据库环境
    
    创建干净的测试数据库和会话对象
    
    Returns:
        tuple: (engine, session) - 数据库引擎和会话对象
    """
    # 清理旧测试数据库
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    engine = create_engine(f'sqlite:///{TEST_DB_PATH}', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return engine, session


def test_contract_domain(session):
    """
    测试合同域数据写入功能
    
    测试内容：
    - 创建合同主记录
    - 创建合同明细
    - 创建合同风险记录
    - 创建合同履行计划
    
    Args:
        session: 数据库会话对象
    
    Returns:
        Contract: 创建的测试合同对象
    """
    test_contract = Contract(
        contract_no='HT-2026-001',
        contract_name='智能交付系统开发合同',
        contract_type='服务合同',
        party_a='客户公司',
        party_b='我们公司',
        sign_date=date(2026, 5, 1),
        start_date=date(2026, 5, 10),
        end_date=date(2026, 12, 31),
        total_amount=500000.00,
        status='active',
        owner='张三',
        department='技术部',
        created_by='admin'
    )
    session.add(test_contract)
    session.flush()

    # 合同明细
    test_item = ContractItem(
        contract_id=test_contract.id,
        item_name='系统开发服务',
        item_type='service',
        quantity=1,
        unit_price=500000.00,
        total_price=500000.00,
        status='active'
    )
    session.add(test_item)

    # 合同风险
    test_risk = ContractRisk(
        contract_id=test_contract.id,
        risk_type='schedule',
        risk_level='medium',
        risk_title='交付时间紧张',
        risk_description='项目周期较短，需注意进度管控',
        status='open'
    )
    session.add(test_risk)

    # 合同履行
    test_fulfillment = ContractFulfillment(
        contract_id=test_contract.id,
        milestone='需求调研完成',
        milestone_type='delivery',
        planned_date=date(2026, 5, 31),
        status='pending'
    )
    session.add(test_fulfillment)

    return test_contract


def test_project_domain(session, contract_id):
    """
    测试项目域数据写入功能
    
    测试内容：
    - 创建项目主记录
    - 创建项目任务
    - 创建项目成本记录
    - 创建需求记录
    - 创建工时记录
    - 创建测试用例
    
    Args:
        session: 数据库会话对象
        contract_id: 关联的合同ID
    
    Returns:
        Project: 创建的测试项目对象
    """
    test_project = Project(
        project_code='PRJ-2026-001',
        project_name='智能交付系统开发',
        project_type='development',
        contract_id=contract_id,
        client_name='客户公司',
        pm_name='李四',
        department='技术部',
        start_date=date(2026, 5, 10),
        end_date=date(2026, 12, 31),
        planned_budget=400000.00,
        status='in_progress',
        priority='high',
        progress=15,
        created_by='admin'
    )
    session.add(test_project)
    session.flush()

    # 任务
    test_task = ProjectTask(
        project_id=test_project.id,
        task_code='TASK-001',
        task_name='需求分析与调研',
        assignee='王五',
        start_date=date(2026, 5, 10),
        end_date=date(2026, 5, 25),
        planned_hours=40,
        status='in_progress',
        progress=60
    )
    session.add(test_task)
    session.flush()

    # 成本
    test_cost = ProjectCost(
        project_id=test_project.id,
        cost_type='labor',
        cost_name='人力成本-研发',
        planned_amount=200000.00,
        actual_amount=50000.00
    )
    session.add(test_cost)

    # 需求
    test_req = Requirement(
        project_id=test_project.id,
        req_code='REQ-001',
        req_name='数据库设计功能',
        req_type='functional',
        priority='high',
        status='approved',
        owner='王五'
    )
    session.add(test_req)
    session.flush()

    # 工时
    test_workhour = WorkHour(
        task_id=test_task.id,
        project_id=test_project.id,
        user_name='王五',
        work_date=date(2026, 5, 15),
        hours=8,
        work_type='development',
        description='数据库Schema设计'
    )
    session.add(test_workhour)

    # 测试用例
    test_case = TestCase(
        project_id=test_project.id,
        requirement_id=test_req.id,
        case_code='CASE-001',
        case_name='验证数据库创建功能',
        case_type='functional',
        priority='high',
        status='ready'
    )
    session.add(test_case)

    return test_project


def test_business_domain(session, project_id):
    """
    测试经营域数据写入功能
    
    测试内容：
    - 创建经营报告
    - 创建财务数据记录
    
    Args:
        session: 数据库会话对象
        project_id: 关联的项目ID
    """
    test_report = BusinessReport(
        report_period='2026-05',
        report_type='monthly',
        total_revenue=1000000.00,
        total_cost=600000.00,
        gross_profit=400000.00,
        gross_margin=40.00,
        project_count=5,
        completed_projects=2,
        status='final'
    )
    session.add(test_report)

    test_finance = FinanceData(
        fiscal_period='2026-05',
        data_type='revenue',
        category='项目收入',
        amount=500000.00,
        project_id=project_id,
        client='客户公司'
    )
    session.add(test_finance)


def test_rag_domain(session):
    """
    测试RAG知识域数据写入功能
    
    测试内容：
    - 创建知识库集合
    - 创建文档记录
    - 创建文档分块
    - 创建向量数据
    
    Returns:
        RagCollection: 创建的测试知识库集合对象
    """
    test_collection = RagCollection(
        collection_name='项目管理知识库',
        collection_code='KNOW-PM-001',
        description='包含项目管理相关的所有文档',
        embedding_model='text-embedding-v2',
        dimension=1536,
        owner='admin'
    )
    session.add(test_collection)
    session.flush()

    test_doc = RagDocument(
        collection_id=test_collection.id,
        doc_title='项目管理规范V1.0',
        doc_type='pdf',
        status='indexed',
        chunk_count=10
    )
    session.add(test_doc)
    session.flush()

    test_chunk = RagChunk(
        document_id=test_doc.id,
        chunk_index=1,
        chunk_text='这是测试文档分块内容，用于验证RAG功能...',
        token_count=50
    )
    session.add(test_chunk)
    session.flush()

    test_vector = RagVector(
        chunk_id=test_chunk.id,
        vector=b'test_vector_data',
        embedding_model='text-embedding-v2',
        dimension=1536
    )
    session.add(test_vector)
    return test_collection


def test_infrastructure_domain(session):
    """
    测试基础设施数据写入功能
    
    测试内容：
    - 创建Prompt模板
    - 创建LLM调用日志
    """
    test_prompt = PromptTemplate(
        template_code='PROMPT-001',
        template_name='项目风险分析',
        template_type='chat',
        category='项目管理',
        prompt_text='你是一个项目管理专家，请分析以下项目情况...',
        created_by='admin'
    )
    session.add(test_prompt)

    test_llmlog = LLMCallLog(
        request_id='req-20260506-0001',
        model='gpt-4',
        provider='openai',
        prompt_tokens=1000,
        completion_tokens=500,
        total_tokens=1500,
        cost=0.045,
        latency_ms=1200,
        status_code=200,
        status='success',
        user_id='admin'
    )
    session.add(test_llmlog)


def verify_data_integrity(session):
    """
    验证数据完整性和关联关系
    
    验证内容：
    - 合同数据读取正确性
    - 项目数据读取正确性
    - 任务与项目关联正确性
    - 外键关联数量正确性
    
    Args:
        session: 数据库会话对象
    """
    # 验证合同
    contract = session.query(Contract).filter_by(contract_no='HT-2026-001').first()
    assert contract is not None, "合同读取失败"
    assert contract.contract_name == '智能交付系统开发合同', "合同名称不符"
    print(f"   ✅ 合同读取: {contract.contract_no} - {contract.contract_name}")

    # 验证项目
    project = session.query(Project).filter_by(project_code='PRJ-2026-001').first()
    assert project is not None, "项目读取失败"
    assert project.pm_name == '李四', "项目经理不符"
    print(f"   ✅ 项目读取: {project.project_code} - {project.project_name}")

    # 验证任务关联
    task = session.query(ProjectTask).filter_by(task_code='TASK-001').first()
    assert task.project is not None, "任务关联项目失败"
    print(f"   ✅ 任务关联: {task.task_name} -> {task.project.project_name}")

    # 验证关联数量
    assert len(contract.items) == 1, "合同明细数量不符"
    assert len(contract.risks) == 1, "合同风险数量不符"
    assert len(project.tasks) == 1, "项目任务数量不符"
    print("   ✅ 外键关联关系验证通过")


def print_data_statistics(session):
    """
    打印各表数据统计信息
    
    Args:
        session: 数据库会话对象
    """
    print("\n📊 各表数据统计:")
    tables = [
        ('合同', Contract),
        ('项目', Project),
        ('任务', ProjectTask),
        ('需求', Requirement),
        ('工时', WorkHour),
        ('财务数据', FinanceData),
        ('RAG文档', RagDocument),
        ('Prompt模板', PromptTemplate),
        ('LLM日志', LLMCallLog),
    ]
    for name, model in tables:
        count = session.query(model).count()
        print(f"   {name}: {count} 条")


def run_tests():
    """
    运行所有数据库测试用例
    
    测试流程：
    1. 初始化干净的测试数据库
    2. 测试合同域数据写入
    3. 测试项目域数据写入
    4. 测试经营域数据写入
    5. 测试RAG知识域数据写入
    6. 测试基础设施数据写入
    7. 提交事务
    8. 验证数据完整性
    9. 输出统计信息
    
    Returns:
        bool: 所有测试通过返回 True，失败返回 False
    """
    print("=" * 60)
    print("🧪 开始数据库测试")
    print("=" * 60)

    # 清理旧测试数据库
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    # 创建引擎和会话
    engine = create_engine(f'sqlite:///{TEST_DB_PATH}', echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 1. 创建所有表
        print("\n📝 测试 1: 创建数据库表...")
        Base.metadata.create_all(engine)
        print("   ✅ 所有表创建成功")

        # 2. 测试合同域
        print("\n📝 测试 2: 合同域数据写入...")
        test_contract = test_contract_domain(session)
        print("   ✅ 合同域数据写入成功")

        # 3. 测试项目域
        print("\n📝 测试 3: 项目域数据写入...")
        test_project = test_project_domain(session, test_contract.id)
        print("   ✅ 项目域数据写入成功")

        # 4. 测试经营域
        print("\n📝 测试 4: 经营域数据写入...")
        test_business_domain(session, test_project.id)
        print("   ✅ 经营域数据写入成功")

        # 5. 测试 RAG 知识域
        print("\n📝 测试 5: RAG 知识域数据写入...")
        test_rag_domain(session)
        print("   ✅ RAG 知识域数据写入成功")

        # 6. 测试基础设施
        print("\n📝 测试 6: 基础设施数据写入...")
        test_infrastructure_domain(session)
        print("   ✅ 基础设施数据写入成功")

        # 提交所有数据
        session.commit()
        print("\n💾 所有数据已提交到数据库")

        # 7. 验证数据读取
        print("\n📝 测试 7: 验证数据读取...")
        verify_data_integrity(session)

        # 8. 统计表数据
        print_data_statistics(session)

        print("\n" + "=" * 60)
        print("🎉 所有测试通过！数据库功能正常！")
        print("=" * 60)
        print(f"\n📁 测试数据库位置: {TEST_DB_PATH.resolve()}")

        return True

    except Exception as e:
        session.rollback()
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        session.close()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
