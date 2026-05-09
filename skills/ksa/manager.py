# ========================================
# KSA 管理器类
# CRUD + 查询 + 搜索 + 版本管理 + 三大引擎
# ========================================

import json
import re
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from difflib import SequenceMatcher

from sqlalchemy import or_, and_, func
from sqlalchemy.orm import Session

from .models import Knowledge, Skill, Ability
from .storage import get_default_storage
from .ontology import OntologyManager
from .reflection import ReflectionEngine


class KSAKnowledgeManager:
    """知识管理器"""

    def __init__(self, storage=None):
        self.storage = storage or get_default_storage()

    def add(self, name: str, content: str, category: str = 'factual',
            description: str = '', tags: List[str] = None, source: str = '',
            confidence: float = 1.0, references: List[str] = None,
            created_by: str = '') -> Knowledge:
        """添加知识"""
        with self.storage.get_session() as session:
            knowledge = Knowledge(
                name=name,
                description=description,
                category=category,
                tags=tags or [],
                content=content,
                source=source,
                confidence=confidence,
                references=references or [],
                created_by=created_by
            )
            session.add(knowledge)
            session.flush()
            return knowledge.to_dict()

    def get(self, knowledge_id: int) -> Optional[Dict]:
        """获取知识"""
        with self.storage.get_session() as session:
            knowledge = session.query(Knowledge).filter(
                Knowledge.id == knowledge_id
            ).first()
            if knowledge:
                knowledge.view_count += 1
                session.flush()
                return knowledge.to_dict()
            return None

    def update(self, knowledge_id: int, **kwargs) -> Optional[Dict]:
        """更新知识"""
        with self.storage.get_session() as session:
            knowledge = session.query(Knowledge).filter(
                Knowledge.id == knowledge_id
            ).first()
            if not knowledge:
                return None
            
            for key, value in kwargs.items():
                if hasattr(knowledge, key):
                    setattr(knowledge, key, value)
            
            knowledge.updated_at = datetime.now()
            session.flush()
            return knowledge.to_dict()

    def delete(self, knowledge_id: int) -> bool:
        """删除知识（软删除）"""
        return self.update(knowledge_id, is_active=False) is not None

    def list(self, category: str = None, tag: str = None,
             active_only: bool = True, limit: int = 100, offset: int = 0) -> List[Dict]:
        """列出知识"""
        with self.storage.get_session() as session:
            query = session.query(Knowledge)
            
            if active_only:
                query = query.filter(Knowledge.is_active == True)
            if category:
                query = query.filter(Knowledge.category == category)
            if tag:
                query = query.filter(Knowledge.tags.contains(json.dumps([tag])))
            
            query = query.order_by(Knowledge.updated_at.desc())
            query = query.offset(offset).limit(limit)
            
            return [k.to_dict() for k in query.all()]

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        知识检索引擎：标签搜索 + 全文搜索 + 相似度推荐
        
        搜索策略：
        1. 名称和描述的关键词匹配
        2. 内容关键词匹配
        3. 按相似度排序
        """
        with self.storage.get_session() as session:
            all_knowledge = session.query(Knowledge).filter(
                Knowledge.is_active == True
            ).all()
            
            if not all_knowledge:
                return []
            
            scored_results = []
            query_lower = query.lower()
            keywords = self._extract_keywords(query)
            
            for k in all_knowledge:
                score = 0.0
                text_to_match = (k.name + ' ' + (k.description or '') + ' ' + k.content).lower()
                
                # 关键词匹配
                for kw in keywords:
                    if kw in text_to_match:
                        score += 0.3
                
                # 名称包含整个查询
                if query_lower in k.name.lower():
                    score += 0.5
                
                # 文本相似度
                similarity = self._calculate_similarity(query, k.name + ' ' + (k.description or ''))
                score += similarity
                
                if score > 0:
                    scored_results.append((k, score))
            
            # 排序：得分高的在前
            scored_results.sort(key=lambda x: x[1], reverse=True)
            
            return [r[0].to_dict() for r in scored_results[:limit]]

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        words = re.findall(r'\b\w+\b', text.lower())
        return [w for w in words if len(w) >= 2]

    def _calculate_similarity(self, a: str, b: str) -> float:
        """计算文本相似度"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()


class KSASkillManager:
    """技能管理器"""

    def __init__(self, storage=None):
        self.storage = storage or get_default_storage()

    def add(self, name: str, version: str = '1.0.0', author: str = '',
            description: str = '', tags: List[str] = None, maturity: str = 'prototype',
            inputs: Dict = None, outputs: Dict = None, limitations: str = '',
            entry_point: str = '', skill_path: str = '',
            requires_knowledge: List[int] = None, requires_skill: List[int] = None,
            created_by: str = '') -> Dict:
        """添加技能"""
        with self.storage.get_session() as session:
            skill = Skill(
                name=name,
                version=version,
                author=author,
                description=description,
                tags=tags or [],
                maturity=maturity,
                inputs=inputs or {},
                outputs=outputs or {},
                limitations=limitations,
                entry_point=entry_point,
                skill_path=skill_path,
                created_by=created_by
            )
            
            # 添加知识依赖
            if requires_knowledge:
                for kid in requires_knowledge:
                    k = session.query(Knowledge).filter(Knowledge.id == kid).first()
                    if k:
                        skill.requires_knowledge.append(k)
            
            # 添加技能依赖
            if requires_skill:
                for sid in requires_skill:
                    s = session.query(Skill).filter(Skill.id == sid).first()
                    if s:
                        skill.requires_skill.append(s)
            
            session.add(skill)
            session.flush()
            return skill.to_dict(include_dependencies=True)

    def get(self, skill_id: int, include_dependencies: bool = False) -> Optional[Dict]:
        """获取技能"""
        with self.storage.get_session() as session:
            skill = session.query(Skill).filter(Skill.id == skill_id).first()
            if skill:
                return skill.to_dict(include_dependencies=include_dependencies)
            return None

    def update(self, skill_id: int, **kwargs) -> Optional[Dict]:
        """更新技能"""
        with self.storage.get_session() as session:
            skill = session.query(Skill).filter(Skill.id == skill_id).first()
            if not skill:
                return None
            
            for key, value in kwargs.items():
                if hasattr(skill, key):
                    setattr(skill, key, value)
            
            skill.updated_at = datetime.now()
            session.flush()
            return skill.to_dict()

    def delete(self, skill_id: int) -> bool:
        """删除技能（软删除）"""
        return self.update(skill_id, is_active=False) is not None

    def list(self, maturity: str = None, tag: str = None,
             active_only: bool = True, limit: int = 100, offset: int = 0) -> List[Dict]:
        """列出技能"""
        with self.storage.get_session() as session:
            query = session.query(Skill)
            
            if active_only:
                query = query.filter(Skill.is_active == True)
            if maturity:
                query = query.filter(Skill.maturity == maturity)
            if tag:
                query = query.filter(Skill.tags.contains(json.dumps([tag])))
            
            query = query.order_by(Skill.updated_at.desc())
            query = query.offset(offset).limit(limit)
            
            return [s.to_dict() for s in query.all()]

    def record_execution(self, skill_id: int, success: bool, execution_time: float) -> bool:
        """记录执行结果"""
        with self.storage.get_session() as session:
            skill = session.query(Skill).filter(Skill.id == skill_id).first()
            if not skill:
                return False
            skill.record_execution(success, execution_time)
            return True

    def match_skills(self, task_description: str, limit: int = 5) -> List[Dict]:
        """
        技能匹配引擎：根据任务描述，自动推荐最合适的技能
        
        匹配策略：
        1. 标签匹配
        2. 名称和描述相似度匹配
        3. 成熟度和成功率加权
        """
        with self.storage.get_session() as session:
            all_skills = session.query(Skill).filter(
                Skill.is_active == True
            ).all()
            
            if not all_skills:
                return []
            
            scored_skills = []
            keywords = self._extract_keywords(task_description)
            
            for skill in all_skills:
                score = 0.0
                
                # 标签匹配得分
                for tag in (skill.tags or []):
                    if any(k in tag.lower() for k in keywords):
                        score += 0.3
                
                # 名称和描述相似度
                name_similarity = self._calculate_similarity(
                    task_description, skill.name + ' ' + (skill.description or '')
                )
                score += name_similarity * 0.5
                
                # 成熟度和成功率加权
                maturity_weights = {
                    'production': 1.0,
                    'beta': 0.7,
                    'prototype': 0.4,
                    'deprecated': 0.1
                }
                score *= maturity_weights.get(skill.maturity, 0.3)
                score += skill.success_rate * 0.2
                
                scored_skills.append((skill, score))
            
            # 按得分排序
            scored_skills.sort(key=lambda x: x[1], reverse=True)
            
            return [
                {**s[0].to_dict(), 'match_score': s[1]}
                for s in scored_skills[:limit] if s[1] > 0.1
            ]

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        words = re.findall(r'\b\w+\b', text.lower())
        return [w for w in words if len(w) >= 2]

    def _calculate_similarity(self, a: str, b: str) -> float:
        """计算文本相似度"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()


class KSAAbilityManager:
    """能力管理器"""

    def __init__(self, storage=None):
        self.storage = storage or get_default_storage()

    def add(self, name: str, owner: str = '', description: str = '',
            tags: List[str] = None, metrics: Dict = None,
            max_concurrent: int = 1, composed_of_knowledge: List[int] = None,
            composed_of_skill: List[int] = None, created_by: str = '') -> Dict:
        """添加能力"""
        with self.storage.get_session() as session:
            ability = Ability(
                name=name,
                owner=owner,
                description=description,
                tags=tags or [],
                metrics=metrics or {},
                growth_history=[],
                max_concurrent=max_concurrent,
                created_by=created_by
            )
            
            # 添加知识组成
            if composed_of_knowledge:
                for kid in composed_of_knowledge:
                    k = session.query(Knowledge).filter(Knowledge.id == kid).first()
                    if k:
                        ability.composed_of_knowledge.append(k)
            
            # 添加技能组成
            if composed_of_skill:
                for sid in composed_of_skill:
                    s = session.query(Skill).filter(Skill.id == sid).first()
                    if s:
                        ability.composed_of_skill.append(s)
            
            session.add(ability)
            session.flush()
            return ability.to_dict(include_components=True)

    def get(self, ability_id: int, include_components: bool = False) -> Optional[Dict]:
        """获取能力"""
        with self.storage.get_session() as session:
            ability = session.query(Ability).filter(Ability.id == ability_id).first()
            if ability:
                return ability.to_dict(include_components=include_components)
            return None

    def update(self, ability_id: int, **kwargs) -> Optional[Dict]:
        """更新能力"""
        with self.storage.get_session() as session:
            ability = session.query(Ability).filter(Ability.id == ability_id).first()
            if not ability:
                return None
            
            for key, value in kwargs.items():
                if hasattr(ability, key):
                    setattr(ability, key, value)
            
            ability.updated_at = datetime.now()
            session.flush()
            return ability.to_dict()

    def delete(self, ability_id: int) -> bool:
        """删除能力（软删除）"""
        return self.update(ability_id, is_active=False) is not None

    def list(self, owner: str = None, tag: str = None,
             active_only: bool = True, limit: int = 100, offset: int = 0) -> List[Dict]:
        """列出能力"""
        with self.storage.get_session() as session:
            query = session.query(Ability)
            
            if active_only:
                query = query.filter(Ability.is_active == True)
            if owner:
                query = query.filter(Ability.owner == owner)
            if tag:
                query = query.filter(Ability.tags.contains(json.dumps([tag])))
            
            query = query.order_by(Ability.updated_at.desc())
            query = query.offset(offset).limit(limit)
            
            return [a.to_dict() for a in query.all()]

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """搜索能力"""
        with self.storage.get_session() as session:
            results = []
            
            # 名称和描述匹配
            name_match = session.query(Ability).filter(
                and_(
                    Ability.is_active == True,
                    or_(
                        Ability.name.like(f'%{query}%'),
                        Ability.description.like(f'%{query}%')
                    )
                )
            ).all()
            results.extend(name_match)
            
            # 标签匹配
            keywords = self._extract_keywords(query)
            for keyword in keywords:
                tag_match = session.query(Ability).filter(
                    and_(
                        Ability.is_active == True,
                        Ability.tags.contains(json.dumps([keyword]))
                    )
                ).all()
                results.extend(tag_match)
            
            # 去重并排序
            seen_ids = set()
            unique_results = []
            for r in results:
                if r.id not in seen_ids:
                    seen_ids.add(r.id)
                    similarity = self._calculate_similarity(query, r.name + ' ' + (r.description or ''))
                    unique_results.append((r, similarity))
            
            unique_results.sort(key=lambda x: x[1], reverse=True)
            
            return [r[0].to_dict() for r in unique_results[:limit]]

    def evaluate_task_result(self, ability_id: int, success: bool,
                             metrics: Dict = None) -> bool:
        """
        能力评估引擎：根据任务执行结果，自动更新技能成功率和能力指标
        """
        with self.storage.get_session() as session:
            ability = session.query(Ability).filter(Ability.id == ability_id).first()
            if not ability:
                return False
            
            # 记录任务结果
            ability.record_task(success)
            
            # 更新成长历史
            history_entry = {
                'timestamp': datetime.now().isoformat(),
                'success': success,
                'metrics': metrics or {}
            }
            
            if ability.growth_history is None:
                ability.growth_history = []
            ability.growth_history.append(history_entry)
            if len(ability.growth_history) > 100:  # 保留最近100条
                ability.growth_history = ability.growth_history[-100:]
            
            # 更新指标
            if metrics:
                current_metrics = ability.metrics or {}
                for key, value in metrics.items():
                    if key in current_metrics:
                        if isinstance(value, (int, float)):
                            # 滑动平均
                            current_metrics[key] = current_metrics[key] * 0.7 + value * 0.3
                    else:
                        current_metrics[key] = value
                ability.metrics = current_metrics
            
            return True

    def _extract_keywords(self, text: str) -> List[str]:
        words = re.findall(r'\b\w+\b', text.lower())
        return [w for w in words if len(w) >= 2]

    def _calculate_similarity(self, a: str, b: str) -> float:
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()


class KSAManager:
    """KSA 统一管理器"""

    def __init__(self, storage=None):
        self.storage = storage or get_default_storage()
        self.knowledge = KSAKnowledgeManager(self.storage)
        self.skill = KSASkillManager(self.storage)
        self.ability = KSAAbilityManager(self.storage)
        # v1.1 新增引擎
        self.ontology = OntologyManager(self.storage)
        self.reflection = ReflectionEngine(self.storage)

    def get_stats(self) -> Dict:
        """获取 KSA 统计信息"""
        with self.storage.get_session() as session:
            base_stats = {
                'version': '1.1',
                'knowledge_count': session.query(Knowledge).filter(Knowledge.is_active == True).count(),
                'skill_count': session.query(Skill).filter(Skill.is_active == True).count(),
                'ability_count': session.query(Ability).filter(Ability.is_active == True).count(),
                'skill_by_maturity': {
                    'prototype': session.query(Skill).filter(Skill.maturity == 'prototype', Skill.is_active == True).count(),
                    'beta': session.query(Skill).filter(Skill.maturity == 'beta', Skill.is_active == True).count(),
                    'production': session.query(Skill).filter(Skill.maturity == 'production', Skill.is_active == True).count(),
                    'deprecated': session.query(Skill).filter(Skill.maturity == 'deprecated', Skill.is_active == True).count()
                },
                'knowledge_by_category': {
                    'factual': session.query(Knowledge).filter(Knowledge.category == 'factual', Knowledge.is_active == True).count(),
                    'procedural': session.query(Knowledge).filter(Knowledge.category == 'procedural', Knowledge.is_active == True).count(),
                    'experiential': session.query(Knowledge).filter(Knowledge.category == 'experiential', Knowledge.is_active == True).count()
                }
            }
            # v1.1 新增统计
            ontology_stats = self.ontology.get_stats()
            reflection_stats = self.reflection.get_stats()
            return {
                **base_stats,
                'ontology': ontology_stats,
                'reflection': reflection_stats
            }
