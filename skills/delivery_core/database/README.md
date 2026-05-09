# delivery_core/database 模块

交付管理系统 - SQLAlchemy ORM 数据库核心模块，包含 18 张核心业务表。

## 功能说明

本模块提供交付管理系统的完整数据持久化方案，包含 6 个业务域：

| 业务域 | 表数量 | 说明 |
|--------|--------|------|
| 合同域 | 4 | 合同主表、合同明细、合同风险、合同履行 |
| 项目域 | 6 | 项目主表、任务、成本、需求、工时、测试用例 |
| 经营域 | 2 | 经营报告、财务数据 |
| RAG知识域 | 4 | 知识库集合、文档、分块、向量 |
| 基础设施 | 2 | Prompt模板、LLM调用日志 |

## 安装与依赖

### 环境要求
- Python 3.8+
- SQLAlchemy 2.0+

### 安装依赖
```bash
pip install -r requirements.txt
```

## 快速开始

### 1. 初始化数据库
```python
from pathlib import Path
from sqlalchemy import create_engine
from models import Base

# 创建数据库引擎
engine = create_engine('sqlite:///delivery_management.db', echo=False)

# 创建所有表
Base.metadata.create_all(engine)
```

或使用初始化脚本：
```bash
python init_db.py
```

### 2. 基本操作示例

#### 2.1 创建合同
```python
from sqlalchemy.orm import sessionmaker
from models import Contract
from datetime import date

Session = sessionmaker(bind=engine)
session = Session()

# 创建新合同
contract = Contract(
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
    department='技术部'
)

session.add(contract)
session.commit()
```

#### 2.2 创建项目并关联合同
```python
from models import Project

project = Project(
    project_code='PRJ-2026-001',
    project_name='智能交付系统开发',
    project_type='development',
    contract_id=contract.id,  # 关联合同
    client_name='客户公司',
    pm_name='李四',
    start_date=date(2026, 5, 10),
    end_date=date(2026, 12, 31),
    planned_budget=400000.00,
    status='in_progress'
)

session.add(project)
session.commit()
```

#### 2.3 查询数据
```python
# 查询所有进行中的项目
active_projects = session.query(Project).filter_by(status='in_progress').all()

# 查询合同及其关联的项目
contract = session.query(Contract).filter_by(contract_no='HT-2026-001').first()
print(f"合同: {contract.contract_name}")
print(f"关联项目数: {len(contract.projects)}")
for proj in contract.projects:
    print(f"  - {proj.project_name}")
```

## 目录结构

```
database/
├── models.py           # SQLAlchemy ORM 模型定义 (18张表)
├── init_db.py          # 数据库初始化脚本
├── test_db.py          # 数据库功能测试脚本
├── schema.sql          # 数据库 Schema 定义
├── requirements.txt    # 依赖声明
├── README.md           # 本文件
├── SKILL.md            # 技能描述文件
└── *.db                # SQLite 数据库文件 (运行时生成)
```

## 运行测试

```bash
# 运行完整测试套件
python test_db.py
```

测试内容包括：
- 数据库表创建验证
- 各业务域数据写入验证
- 数据读取与查询验证
- 外键关联关系验证

## 数据库 Schema

详见 `schema.sql` 文件，包含完整的表结构定义和索引。

## 注意事项

1. 生产环境建议使用 MySQL/PostgreSQL 替代 SQLite
2. 数据库连接配置建议通过环境变量管理
3. 敏感数据（如数据库密码）请勿硬编码
4. 定期备份数据库文件
