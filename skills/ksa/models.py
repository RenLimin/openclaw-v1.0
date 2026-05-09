# ========================================
# KSA (Knowledge/Skill/Ability) 核心数据模型
# 作为整个交付系统的核心基础设施
# ========================================

from datetime import datetime
from enum import Enum
from typing import List, Optional, Any
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text,
    Boolean, ForeignKey, JSON, Table
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


# ========================================
# Enums
# ========================================

class KnowledgeCategory(str, Enum):
    """知识分类"""
    FACTUAL = "factual"      # 事实类知识
    PROCEDURAL = "procedural"  # 方法类知识
    EXPERIENTIAL = "experiential"  # 经验类知识


class SkillMaturity(str, Enum):
    """技能成熟度"""
    PROTOTYPE = "prototype"    # 原型阶段
    BETA = "beta"             # 测试阶段
    PRODUCTION = "production"  # 生产阶段
    DEPRECATED = "deprecated"  # 已废弃


# ========================================
# 关联表
# ========================================

# 技能-知识 依赖关联
skill_knowledge_association = Table(
    'ksa_skill_knowledge',
    Base.metadata,
    Column('skill_id', Integer, ForeignKey('ksa_skills.id', ondelete='CASCADE'), primary_key=True),
    Column('knowledge_id', Integer, ForeignKey('ksa_knowledge.id', ondelete='CASCADE'), primary_key=True)
)

# 技能-技能 依赖关联
skill_skill_association = Table(
    'ksa_skill_skill',
    Base.metadata,
    Column('skill_id', Integer, ForeignKey('ksa_skills.id', ondelete='CASCADE'), primary_key=True),
    Column('required_skill_id', Integer, ForeignKey('ksa_skills.id', ondelete='CASCADE'), primary_key=True)
)

# 能力-知识 组成关联
ability_knowledge_association = Table(
    'ksa_ability_knowledge',
    Base.metadata,
    Column('ability_id', Integer, ForeignKey('ksa_abilities.id', ondelete='CASCADE'), primary_key=True),
    Column('knowledge_id', Integer, ForeignKey('ksa_knowledge.id', ondelete='CASCADE'), primary_key=True)
)

# 能力-技能 组成关联
ability_skill_association = Table(
    'ksa_ability_skill',
    Base.metadata,
    Column('ability_id', Integer, ForeignKey('ksa_abilities.id', ondelete='CASCADE'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('ksa_skills.id', ondelete='CASCADE'), primary_key=True)
)


# ========================================
# Knowledge 知识模型
# ========================================

class Knowledge(Base):
    """知识模型
    
    知识分类：
    - factual(事实): 客观事实、数据、规则等静态信息
    - procedural(方法): 流程、步骤、方法等过程性信息
    - experiential(经验): 教训、最佳实践、案例等经验性信息
    """
    __tablename__ = 'ksa_knowledge'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    category = Column(String(50), nullable=False, index=True)  # factual/procedural/experiential
    tags = Column(JSON)  # JSON 数组格式的标签
    content = Column(Text, nullable=False)
    source = Column(String(500))  # 知识来源：文件路径、URL、文档名等
    confidence = Column(Float, default=1.0)  # 置信度 0.0-1.0
    references = Column(JSON)  # JSON 数组格式的引用列表
    embedding = Column(JSON)  # 向量嵌入，用于相似度搜索
    is_active = Column(Boolean, default=True)
    view_count = Column(Integer, default=0)
    use_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(String(100))

    # 关系
    required_by_skills = relationship(
        'Skill',
        secondary=skill_knowledge_association,
        back_populates='requires_knowledge'
    )
    composed_in_abilities = relationship(
        'Ability',
        secondary=ability_knowledge_association,
        back_populates='composed_of_knowledge'
    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'tags': self.tags or [],
            'content': self.content,
            'source': self.source,
            'confidence': self.confidence,
            'references': self.references or [],
            'is_active': self.is_active,
            'view_count': self.view_count,
            'use_count': self.use_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }


# ========================================
# Skill 技能模型
# ========================================

class Skill(Base):
    """技能模型
    
    技能是可执行的能力单元，有明确的输入输出和成功率统计
    
    成熟度：
    - prototype(原型): 初步实现，待验证
    - beta(测试): 测试中，可试用
    - production(生产): 稳定可用，生产环境
    - deprecated(废弃): 不再维护，建议迁移
    """
    __tablename__ = 'ksa_skills'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    version = Column(String(50), default='1.0.0')
    author = Column(String(100))
    description = Column(Text)
    tags = Column(JSON)  # JSON 数组格式的标签
    maturity = Column(String(50), default='prototype', index=True)  # prototype/beta/production/deprecated
    success_rate = Column(Float, default=0.0)  # 成功率 0.0-1.0
    avg_time = Column(Float, default=0.0)  # 平均执行时间（秒）
    total_runs = Column(Integer, default=0)  # 总执行次数
    success_runs = Column(Integer, default=0)  # 成功次数
    inputs = Column(JSON)  # JSON 对象格式的输入定义
    outputs = Column(JSON)  # JSON 对象格式的输出定义
    limitations = Column(Text)  # 技能的局限性说明
    entry_point = Column(String(500))  # 技能入口点：模块路径或命令
    skill_path = Column(String(500))  # 技能在文件系统中的路径
    embedding = Column(JSON)  # 向量嵌入，用于技能匹配
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(String(100))

    # 关系
    requires_knowledge = relationship(
        'Knowledge',
        secondary=skill_knowledge_association,
        back_populates='required_by_skills'
    )
    requires_skill = relationship(
        'Skill',
        secondary=skill_skill_association,
        primaryjoin=id == skill_skill_association.c.skill_id,
        secondaryjoin=id == skill_skill_association.c.required_skill_id,
        backref='required_by_skills'
    )
    composed_in_abilities = relationship(
        'Ability',
        secondary=ability_skill_association,
        back_populates='composed_of_skill'
    )

    def record_execution(self, success: bool, execution_time: float):
        """记录执行结果"""
        self.total_runs += 1
        if success:
            self.success_runs += 1
        self.success_rate = self.success_runs / self.total_runs if self.total_runs > 0 else 0.0
        self.avg_time = ((self.avg_time * (self.total_runs - 1)) + execution_time) / self.total_runs

    def to_dict(self, include_dependencies: bool = False) -> dict:
        result = {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'author': self.author,
            'description': self.description,
            'tags': self.tags or [],
            'maturity': self.maturity,
            'success_rate': self.success_rate,
            'avg_time': self.avg_time,
            'total_runs': self.total_runs,
            'success_runs': self.success_runs,
            'inputs': self.inputs or {},
            'outputs': self.outputs or {},
            'limitations': self.limitations,
            'entry_point': self.entry_point,
            'skill_path': self.skill_path,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }
        if include_dependencies:
            result['requires_knowledge'] = [k.to_dict() for k in self.requires_knowledge]
            result['requires_skill'] = [s.to_dict() for s in self.requires_skill]
        return result


# ========================================
# Ability 能力模型
# ========================================

class Ability(Base):
    """能力模型
    
    能力是知识 + 技能的组合，表示完成某类任务的综合能力
    """
    __tablename__ = 'ksa_abilities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    owner = Column(String(100))  # 能力所有者：Agent 名称或人名
    description = Column(Text)
    tags = Column(JSON)  # JSON 数组格式的标签
    metrics = Column(JSON)  # JSON 对象格式的能力指标
    growth_history = Column(JSON)  # JSON 数组格式的成长历史
    max_concurrent = Column(Integer, default=1)  # 最大并发执行数
    current_concurrent = Column(Integer, default=0)  # 当前执行数
    total_tasks = Column(Integer, default=0)  # 总任务数
    success_tasks = Column(Integer, default=0)  # 成功任务数
    overall_success_rate = Column(Float, default=0.0)  # 总体成功率
    embedding = Column(JSON)  # 向量嵌入，用于能力搜索
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(String(100))

    # 关系
    composed_of_knowledge = relationship(
        'Knowledge',
        secondary=ability_knowledge_association,
        back_populates='composed_in_abilities'
    )
    composed_of_skill = relationship(
        'Skill',
        secondary=ability_skill_association,
        back_populates='composed_in_abilities'
    )

    def record_task(self, success: bool):
        """记录任务执行结果"""
        self.total_tasks += 1
        if success:
            self.success_tasks += 1
        self.overall_success_rate = self.success_tasks / self.total_tasks if self.total_tasks > 0 else 0.0

    def to_dict(self, include_components: bool = False) -> dict:
        result = {
            'id': self.id,
            'name': self.name,
            'owner': self.owner,
            'description': self.description,
            'tags': self.tags or [],
            'metrics': self.metrics or {},
            'growth_history': self.growth_history or [],
            'max_concurrent': self.max_concurrent,
            'current_concurrent': self.current_concurrent,
            'total_tasks': self.total_tasks,
            'success_tasks': self.success_tasks,
            'overall_success_rate': self.overall_success_rate,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }
        if include_components:
            result['composed_of_knowledge'] = [k.to_dict() for k in self.composed_of_knowledge]
            result['composed_of_skill'] = [s.to_dict() for s in self.composed_of_skill]
        return result
