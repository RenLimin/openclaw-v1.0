# ========================================
# KSA v1.1 - Ontology 本体层（知识图谱 + 推理引擎）
# 核心：实体-关系-规则 三元组模型
# ========================================

import json
import re
from enum import Enum
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from difflib import SequenceMatcher
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy import and_, or_

from .models import Base, Knowledge, Skill, Ability
from .storage import get_default_storage


# ========================================
# Enums
# ========================================

class EntityType(str, Enum):
    """实体类型"""
    AGENT = "agent"
    SKILL = "skill"
    KNOWLEDGE = "knowledge"
    ABILITY = "ability"
    TASK = "task"
    DOMAIN = "domain"


class RelationType(str, Enum):
    """关系类型"""
    REQUIRES = "requires"        # A 需要 B
    DEPENDS_ON = "depends_on"    # A 依赖 B
    OWNS = "owns"                # A 拥有 B
    BELONGS_TO = "belongs_to"    # A 属于 B
    SIMILAR_TO = "similar_to"    # A 与 B 相似
    IMPROVES = "improves"        # A 改进 B
    DERIVED_FROM = "derived_from"  # A 源自 B
    PERFORMS = "performs"        # A 执行 B（Agent -> Task）
    CONTAINS = "contains"        # A 包含 B（Domain -> Skill）


class RuleType(str, Enum):
    """规则类型"""
    CASCADE_WARNING = "cascade_warning"      # 级联预警规则
    INHERITANCE = "inheritance"             # 继承规则
    SIMILARITY_PROPAGATION = "similarity_propagation"  # 相似度传播规则


# ========================================
# Ontology 数据模型
# ========================================

class OntologyEntity(Base):
    """本体实体
    
    代表知识图谱中的节点，可以是 Agent, Skill, Knowledge, Ability, Task, Domain
    """
    __tablename__ = 'ontology_entities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String(50), nullable=False, index=True)  # agent/skill/knowledge/ability/task/domain
    entity_id = Column(String(100), nullable=False, index=True)   # 外部实体 ID 或唯一标识
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    attributes = Column(JSON)  # 实体属性的 JSON 存储
    tags = Column(JSON)  # 标签数组
    embedding = Column(JSON)  # 向量嵌入，用于相似度计算
    confidence = Column(Float, default=1.0)  # 置信度
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(String(100))

    # 关系：作为源的关系
    outgoing_relations = relationship(
        'OntologyRelation',
        foreign_keys='OntologyRelation.source_id',
        back_populates='source_entity',
        cascade='all, delete-orphan'
    )

    # 关系：作为目标的关系
    incoming_relations = relationship(
        'OntologyRelation',
        foreign_keys='OntologyRelation.target_id',
        back_populates='target_entity',
        cascade='all, delete-orphan'
    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'name': self.name,
            'description': self.description,
            'attributes': self.attributes or {},
            'tags': self.tags or [],
            'confidence': self.confidence,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }


class OntologyRelation(Base):
    """本体关系
    
    代表知识图谱中的边，连接两个实体
    """
    __tablename__ = 'ontology_relations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey('ontology_entities.id', ondelete='CASCADE'), nullable=False)
    target_id = Column(Integer, ForeignKey('ontology_entities.id', ondelete='CASCADE'), nullable=False)
    relation_type = Column(String(50), nullable=False, index=True)  # requires/depends_on/owns/belongs_to/...
    weight = Column(Float, default=1.0)  # 关系权重/强度
    attributes = Column(JSON)  # 关系属性
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(String(100))

    # 关联的源实体和目标实体
    source_entity = relationship(
        'OntologyEntity',
        foreign_keys=[source_id],
        back_populates='outgoing_relations'
    )
    target_entity = relationship(
        'OntologyEntity',
        foreign_keys=[target_id],
        back_populates='incoming_relations'
    )

    def to_dict(self, include_entities: bool = False) -> dict:
        result = {
            'id': self.id,
            'source_id': self.source_id,
            'target_id': self.target_id,
            'relation_type': self.relation_type,
            'weight': self.weight,
            'attributes': self.attributes or {},
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }
        if include_entities:
            result['source'] = self.source_entity.to_dict() if self.source_entity else None
            result['target'] = self.target_entity.to_dict() if self.target_entity else None
        return result


class OntologyRule(Base):
    """本体推理规则
    
    定义图谱上的推理规则，支持级联预警、继承推理等
    """
    __tablename__ = 'ontology_rules'

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_type = Column(String(50), nullable=False, index=True)  # cascade_warning/inheritance/...
    name = Column(String(200), nullable=False)
    description = Column(Text)
    condition = Column(JSON)  # 条件表达式的 JSON 表示
    action = Column(JSON)  # 动作表达式的 JSON 表示
    priority = Column(Integer, default=0)  # 优先级，数字越大越高
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'rule_type': self.rule_type,
            'name': self.name,
            'description': self.description,
            'condition': self.condition or {},
            'action': self.action or {},
            'priority': self.priority,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# ========================================
# Ontology 管理器
# ========================================

class OntologyManager:
    """Ontology 本体管理器
    
    提供：
    - 实体 CRUD
    - 关系 CRUD
    - 图遍历查询
    - 路径查找
    - 推理引擎
    - 智能推荐
    """

    def __init__(self, storage=None):
        self.storage = storage or get_default_storage()
        self._init_ontology_tables()

    def _init_ontology_tables(self):
        """初始化 Ontology 表"""
        tables_to_create = [
            OntologyEntity.__table__,
            OntologyRelation.__table__,
            OntologyRule.__table__
        ]

        with self.storage.engine.connect() as conn:
            for table in tables_to_create:
                if not self.storage.engine.dialect.has_table(conn, table.name):
                    table.create(self.storage.engine)

    # ========================================
    # 实体管理
    # ========================================

    def add_entity(self, entity_type: str, entity_id: str, name: str,
                   description: str = '', attributes: Dict = None, tags: List[str] = None,
                   confidence: float = 1.0, created_by: str = '') -> Dict:
        """添加实体"""
        with self.storage.get_session() as session:
            # 检查是否已存在
            existing = session.query(OntologyEntity).filter(
                and_(
                    OntologyEntity.entity_type == entity_type,
                    OntologyEntity.entity_id == entity_id
                )
            ).first()

            if existing:
                # 更新现有实体
                existing.name = name
                existing.description = description
                existing.attributes = attributes or {}
                existing.tags = tags or []
                existing.confidence = confidence
                existing.updated_at = datetime.now()
                session.flush()
                return existing.to_dict()

            # 创建新实体
            entity = OntologyEntity(
                entity_type=entity_type,
                entity_id=entity_id,
                name=name,
                description=description,
                attributes=attributes or {},
                tags=tags or [],
                confidence=confidence,
                created_by=created_by
            )
            session.add(entity)
            session.flush()
            return entity.to_dict()

    def get_entity(self, entity_id: int) -> Optional[Dict]:
        """获取实体"""
        with self.storage.get_session() as session:
            entity = session.query(OntologyEntity).filter(
                OntologyEntity.id == entity_id
            ).first()
            return entity.to_dict() if entity else None

    def get_entity_by_external_id(self, entity_type: str, entity_id: str) -> Optional[Dict]:
        """根据外部 ID 获取实体"""
        with self.storage.get_session() as session:
            entity = session.query(OntologyEntity).filter(
                and_(
                    OntologyEntity.entity_type == entity_type,
                    OntologyEntity.entity_id == entity_id,
                    OntologyEntity.is_active == True
                )
            ).first()
            return entity.to_dict() if entity else None

    def list_entities(self, entity_type: str = None, tag: str = None,
                      active_only: bool = True, limit: int = 100, offset: int = 0) -> List[Dict]:
        """列出实体"""
        with self.storage.get_session() as session:
            query = session.query(OntologyEntity)

            if active_only:
                query = query.filter(OntologyEntity.is_active == True)
            if entity_type:
                query = query.filter(OntologyEntity.entity_type == entity_type)
            if tag:
                query = query.filter(OntologyEntity.tags.contains(json.dumps([tag])))

            query = query.order_by(OntologyEntity.updated_at.desc())
            query = query.offset(offset).limit(limit)

            return [e.to_dict() for e in query.all()]

    def update_entity(self, entity_id: int, **kwargs) -> Optional[Dict]:
        """更新实体"""
        with self.storage.get_session() as session:
            entity = session.query(OntologyEntity).filter(
                OntologyEntity.id == entity_id
            ).first()
            if not entity:
                return None

            for key, value in kwargs.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)

            entity.updated_at = datetime.now()
            session.flush()
            return entity.to_dict()

    def delete_entity(self, entity_id: int) -> bool:
        """删除实体（软删除）"""
        return self.update_entity(entity_id, is_active=False) is not None

    # ========================================
    # 关系管理
    # ========================================

    def add_relation(self, source_id: int, target_id: int, relation_type: str,
                     weight: float = 1.0, attributes: Dict = None,
                     created_by: str = '') -> Dict:
        """添加实体关系"""
        with self.storage.get_session() as session:
            # 检查是否已存在
            existing = session.query(OntologyRelation).filter(
                and_(
                    OntologyRelation.source_id == source_id,
                    OntologyRelation.target_id == target_id,
                    OntologyRelation.relation_type == relation_type
                )
            ).first()

            if existing:
                existing.weight = weight
                existing.attributes = attributes or {}
                existing.updated_at = datetime.now()
                session.flush()
                return existing.to_dict()

            relation = OntologyRelation(
                source_id=source_id,
                target_id=target_id,
                relation_type=relation_type,
                weight=weight,
                attributes=attributes or {},
                created_by=created_by
            )
            session.add(relation)
            session.flush()
            return relation.to_dict()

    def get_relation(self, relation_id: int) -> Optional[Dict]:
        """获取关系"""
        with self.storage.get_session() as session:
            relation = session.query(OntologyRelation).filter(
                OntologyRelation.id == relation_id
            ).first()
            return relation.to_dict(include_entities=True) if relation else None

    def get_entity_relations(self, entity_id: int, relation_type: str = None,
                             direction: str = 'both') -> List[Dict]:
        """获取实体的所有关系
        
        Args:
            entity_id: 实体 ID
            relation_type: 按关系类型过滤
            direction: 'outgoing' | 'incoming' | 'both'
        """
        with self.storage.get_session() as session:
            relations = []

            if direction in ['outgoing', 'both']:
                query = session.query(OntologyRelation).filter(
                    OntologyRelation.source_id == entity_id,
                    OntologyRelation.is_active == True
                )
                if relation_type:
                    query = query.filter(OntologyRelation.relation_type == relation_type)
                relations.extend(query.all())

            if direction in ['incoming', 'both']:
                query = session.query(OntologyRelation).filter(
                    OntologyRelation.target_id == entity_id,
                    OntologyRelation.is_active == True
                )
                if relation_type:
                    query = query.filter(OntologyRelation.relation_type == relation_type)
                relations.extend(query.all())

            return [r.to_dict(include_entities=True) for r in relations]

    def list_relations(self, relation_type: str = None,
                       active_only: bool = True, limit: int = 100, offset: int = 0) -> List[Dict]:
        """列出关系"""
        with self.storage.get_session() as session:
            query = session.query(OntologyRelation)

            if active_only:
                query = query.filter(OntologyRelation.is_active == True)
            if relation_type:
                query = query.filter(OntologyRelation.relation_type == relation_type)

            query = query.order_by(OntologyRelation.updated_at.desc())
            query = query.offset(offset).limit(limit)

            return [r.to_dict(include_entities=True) for r in query.all()]

    def delete_relation(self, relation_id: int) -> bool:
        """删除关系（软删除）"""
        with self.storage.get_session() as session:
            relation = session.query(OntologyRelation).filter(
                OntologyRelation.id == relation_id
            ).first()
            if not relation:
                return False
            relation.is_active = False
            relation.updated_at = datetime.now()
            return True

    # ========================================
    # 图遍历与路径查找
    # ========================================

    def find_path(self, start_entity_id: int, end_entity_id: int,
                  max_depth: int = 5, relation_types: List[str] = None) -> Optional[List[Dict]]:
        """查找两个实体之间的关联路径（BFS）"""
        with self.storage.get_session() as session:
            # BFS 搜索
            from collections import deque

            visited = set()
            queue = deque([(start_entity_id, [])])  # (current_id, path)

            while queue:
                current_id, path = queue.popleft()

                if current_id == end_entity_id:
                    return path

                if len(path) >= max_depth or current_id in visited:
                    continue

                visited.add(current_id)

                # 获取当前实体的所有出边
                query = session.query(OntologyRelation).filter(
                    and_(
                        OntologyRelation.source_id == current_id,
                        OntologyRelation.is_active == True
                    )
                )
                if relation_types:
                    query = query.filter(OntologyRelation.relation_type.in_(relation_types))

                for relation in query.all():
                    next_id = relation.target_id
                    if next_id not in visited:
                        queue.append((next_id, path + [relation.to_dict(include_entities=True)]))

            return None

    def get_neighbors(self, entity_id: int, relation_type: str = None,
                      depth: int = 1) -> List[Dict]:
        """获取实体的邻居节点"""
        with self.storage.get_session() as session:
            neighbors = set()
            to_visit = {entity_id}

            for _ in range(depth):
                next_level = set()
                for eid in to_visit:
                    query = session.query(OntologyRelation).filter(
                        and_(
                            OntologyRelation.source_id == eid,
                            OntologyRelation.is_active == True
                        )
                    )
                    if relation_type:
                        query = query.filter(OntologyRelation.relation_type == relation_type)

                    for r in query.all():
                        if r.target_id not in neighbors:
                            neighbors.add(r.target_id)
                            next_level.add(r.target_id)
                to_visit = next_level

            # 获取实体详情
            entities = session.query(OntologyEntity).filter(
                OntologyEntity.id.in_(list(neighbors))
            ).all()
            return [e.to_dict() for e in entities]

    # ========================================
    # 推理引擎
    # ========================================

    def infer(self, trigger_source: str = None, trigger_event: Dict = None) -> List[Dict]:
        """
        基于规则推理得到新知识
        
        支持的推理规则：
        1. 级联预警：如果 Skill A requires Skill B，且 B 成功率降低，则预警 A
        2. 继承推理：领域知识自动应用到该领域下的所有技能
        3. 相似度传播：相似技能自动推荐相似任务
        """
        inferences = []

        # 推理1: 级联预警规则 - 技能成功率变化影响依赖它的技能
        if trigger_event and trigger_event.get('type') == 'skill_success_rate_changed':
            skill_id = trigger_event.get('skill_id')
            old_rate = trigger_event.get('old_rate', 0)
            new_rate = trigger_event.get('new_rate', 0)

            if new_rate < old_rate * 0.8:  # 成功率下降超过 20%
                affected_skills = self._find_dependent_skills(skill_id)
                for skill in affected_skills:
                    inferences.append({
                        'type': 'cascade_warning',
                        'severity': 'high',
                        'message': f"技能 [{skill['name']}] 依赖的技能成功率从 {old_rate:.2f} 下降到 {new_rate:.2f}",
                        'affected_entity': skill,
                        'trigger': trigger_event,
                        'recommendation': '建议检查依赖技能的稳定性或寻找替代技能'
                    })

        # 推理2: 继承推理 - 查找领域知识并应用到下属技能
        domain_knowledge = self._infer_domain_knowledge()
        inferences.extend(domain_knowledge)

        # 推理3: 相似度推理 - 基于相似关系的技能推荐
        similarity_inferences = self._infer_similar_skills()
        inferences.extend(similarity_inferences)

        return inferences

    def _find_dependent_skills(self, skill_id: int) -> List[Dict]:
        """查找依赖指定技能的所有技能"""
        with self.storage.get_session() as session:
            # 找到 skill 对应的 ontology entity
            skill_entity = session.query(OntologyEntity).filter(
                and_(
                    OntologyEntity.entity_type == 'skill',
                    OntologyEntity.entity_id == str(skill_id)
                )
            ).first()

            if not skill_entity:
                return []

            # 查找所有 requires 该技能的实体
            relations = session.query(OntologyRelation).filter(
                and_(
                    OntologyRelation.target_id == skill_entity.id,
                    OntologyRelation.relation_type.in_(['requires', 'depends_on']),
                    OntologyRelation.is_active == True
                )
            ).all()

            # 获取技能详情
            skill_ids = []
            for r in relations:
                source_entity = session.query(OntologyEntity).filter(
                    OntologyEntity.id == r.source_id
                ).first()
                if source_entity and source_entity.entity_type == 'skill':
                    try:
                        external_id = int(source_entity.entity_id)
                        skill_ids.append(external_id)
                    except (ValueError, TypeError):
                        pass

            # 从 KSA skills 表获取详情
            from .models import Skill
            skills = session.query(Skill).filter(Skill.id.in_(skill_ids)).all()
            return [s.to_dict() for s in skills]

    def _infer_domain_knowledge(self) -> List[Dict]:
        """推理领域知识继承"""
        inferences = []
        with self.storage.get_session() as session:
            # 查找所有 domain 实体
            domains = session.query(OntologyEntity).filter(
                and_(
                    OntologyEntity.entity_type == 'domain',
                    OntologyEntity.is_active == True
                )
            ).all()

            for domain in domains:
                # 查找该领域包含的技能
                relations = session.query(OntologyRelation).filter(
                    and_(
                        OntologyRelation.source_id == domain.id,
                        OntologyRelation.relation_type == 'contains',
                        OntologyRelation.is_active == True
                    )
                ).all()

                skill_count = len(relations)
                if skill_count > 0:
                    inferences.append({
                        'type': 'domain_inheritance',
                        'domain': domain.name,
                        'message': f"领域 [{domain.name}] 包含 {skill_count} 个技能",
                        'skills_count': skill_count,
                        'recommendation': '该领域知识可应用于所有下属技能'
                    })

        return inferences

    def _infer_similar_skills(self) -> List[Dict]:
        """推理相似技能"""
        inferences = []
        # 简单的相似度推理 - 基于标签和名称匹配
        return inferences

    # ========================================
    # 智能推荐
    # ========================================

    def recommend_skills(self, task_description: str, limit: int = 5) -> List[Dict]:
        """基于任务描述和图谱智能推荐技能"""
        with self.storage.get_session() as session:
            # 首先获取所有 skill 实体
            skill_entities = session.query(OntologyEntity).filter(
                and_(
                    OntologyEntity.entity_type == 'skill',
                    OntologyEntity.is_active == True
                )
            ).all()

            if not skill_entities:
                return []

            scored_skills = []
            keywords = self._extract_keywords(task_description)

            for entity in skill_entities:
                score = 0.0

                # 1. 标签匹配
                for tag in (entity.tags or []):
                    if any(k in tag.lower() for k in keywords):
                        score += 0.3

                # 2. 名称和描述相似度
                name_similarity = self._calculate_similarity(
                    task_description, entity.name + ' ' + (entity.description or '')
                )
                score += name_similarity * 0.5

                # 3. 图谱权重增强 - 有更多关系的技能得分更高
                relation_count = session.query(OntologyRelation).filter(
                    or_(
                        OntologyRelation.source_id == entity.id,
                        OntologyRelation.target_id == entity.id
                    )
                ).count()
                score += min(relation_count * 0.05, 0.3)

                # 4. 置信度加权
                score *= entity.confidence

                if score > 0:
                    scored_skills.append((entity, score))

            # 排序
            scored_skills.sort(key=lambda x: x[1], reverse=True)

            return [
                {**e[0].to_dict(), 'recommendation_score': e[1]}
                for e in scored_skills[:limit]
            ]

    def _extract_keywords(self, text: str) -> List[str]:
        words = re.findall(r'\b\w+\b', text.lower())
        return [w for w in words if len(w) >= 2]

    def _calculate_similarity(self, a: str, b: str) -> float:
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    # ========================================
    # 统计信息
    # ========================================

    def get_stats(self) -> Dict:
        """获取 Ontology 统计信息"""
        with self.storage.get_session() as session:
            entity_counts = {}
            for et in ['agent', 'skill', 'knowledge', 'ability', 'task', 'domain']:
                count = session.query(OntologyEntity).filter(
                    and_(
                        OntologyEntity.entity_type == et,
                        OntologyEntity.is_active == True
                    )
                ).count()
                entity_counts[et] = count

            relation_counts = {}
            for rt in ['requires', 'depends_on', 'owns', 'belongs_to', 'similar_to', 'improves', 'derived_from', 'performs', 'contains']:
                count = session.query(OntologyRelation).filter(
                    and_(
                        OntologyRelation.relation_type == rt,
                        OntologyRelation.is_active == True
                    )
                ).count()
                relation_counts[rt] = count

            return {
                'total_entities': sum(entity_counts.values()),
                'entities_by_type': entity_counts,
                'total_relations': sum(relation_counts.values()),
                'relations_by_type': relation_counts,
                'rules_count': session.query(OntologyRule).filter(OntologyRule.is_active == True).count()
            }
