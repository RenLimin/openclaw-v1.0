# SKILL.md - database 模块

## 技能概述

**技能名称**: delivery_core/database - 交付管理系统数据库模块
**技能版本**: 1.0.0
**技能类型**: 基础设施 - 数据持久化

## 功能描述

本技能提供交付管理系统的核心数据持久化能力，基于 SQLAlchemy ORM 实现。包含 18 张核心业务表，覆盖合同、项目、经营、知识库等全业务域。

## 核心能力

### 1. 数据模型定义
- 6 个业务域的完整数据模型
- 完善的外键关联与关系映射
- 类型安全的字段定义

### 2. 数据库初始化
- 一键创建所有数据表
- SQLite 数据库自动配置
- 外键约束与 WAL 模式启用

### 3. 数据操作支持
- 支持所有标准 CRUD 操作
- 级联删除与关联查询
- 事务管理支持

### 4. 测试验证
- 完整的功能测试套件
- 覆盖所有业务域的数据写入测试
- 关联关系验证

## 适用场景

- 项目管理系统数据持久化
- 合同管理与履行跟踪
- 经营数据统计与分析
- RAG 知识库数据存储
- LLM 调用日志记录

## 使用方法

### 作为模块导入
```python
from delivery_core.database.models import (
    Contract, Project, Requirement,
    WorkHour, FinanceData,
    RagCollection, RagDocument,
    PromptTemplate, LLMCallLog
)
```

### 初始化数据库
```bash
python -m delivery_core.database.init_db
```

### 运行测试
```bash
python -m delivery_core.database.test_db
```

## 依赖项

- `sqlalchemy>=2.0.0` - ORM 框架

## 维护与扩展

### 添加新表
1. 在 `models.py` 中定义新的模型类，继承自 `Base`
2. 在 `init_db.py` 中会自动创建新表
3. 在 `test_db.py` 中添加对应测试用例

### 迁移数据库
- 生产环境建议使用 Alembic 进行数据库迁移
- SQLite 不支持 ALTER TABLE，需特殊处理

## 版本历史

### v1.0.0 (2026-05-06)
- 初始版本发布
- 完成 18 张核心表定义
- 实现完整测试套件
