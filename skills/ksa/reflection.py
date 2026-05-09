# ========================================
# KSA v1.1 - 反思成长引擎（Reflection Growth Engine）
# 核心：自动复盘 → 经验提取 → 举一反三 → 主动优化
# ========================================

import json
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from enum import Enum
from difflib import SequenceMatcher

from sqlalchemy import and_, or_, func, Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship

from .models import Base, Knowledge, Skill, Ability
from .storage import get_default_storage


# ========================================
# Enums
# ========================================

class FailureReason(str, Enum):
    """失败归因分类"""
    KNOWLEDGE_GAP = "knowledge_gap"      # 知识缺失
    SKILL_DEFECT = "skill_defect"      # 技能缺陷
    RESOURCE_LIMIT = "resource_limit"  # 资源不足
    COORDINATION_ISSUE = "coordination_issue"  # 协作问题
    UNKNOWN = "unknown"              # 未知原因


class OptimizationType(str, Enum):
    """经验类型"""
    BEST_PRACTICE = "best_practice"    # 最佳实践
    LESSON_LEARNED = "lesson_learned"  # 经验教训
    PATTERN = "pattern"              # 模式识别
    IMPROVEMENT = "improvement"      # 改进建议


# ========================================
# 任务复盘记录模型
# ========================================

class TaskRetrospective(Base):
    """任务复盘记录
    
    记录每个任务的执行结果、分析、经验提取
    """
    __tablename__ = 'task_retrospectives'

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(100), nullable=False, index=True)
    task_name = Column(String(200))
    agent_id = Column(String(100))  # 执行 Agent
    skill_id = Column(Integer, ForeignKey('ksa_skills.id'), nullable=True)
    ability_id = Column(Integer, ForeignKey('ksa_abilities.id'), nullable=True)
    success = Column(Boolean, nullable=False)
    execution_time = Column(Float)  # 执行时间（秒）
    error_message = Column(Text)
    output_quality = Column(Float)  # 产出质量评分 0-1
    root_cause = Column(String(100))  # 根因分类
    root_cause_detail = Column(Text)  # 根因详情
    improvement_suggestions = Column(JSON)  # 改进建议列表
    experience_extracted = Column(Boolean, default=False)  # 是否已提取经验
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'task_id': self.task_id,
            'task_name': self.task_name,
            'agent_id': self.agent_id,
            'skill_id': self.skill_id,
            'ability_id': self.ability_id,
            'success': self.success,
            'execution_time': self.execution_time,
            'error_message': self.error_message,
            'output_quality': self.output_quality,
            'root_cause': self.root_cause,
            'root_cause_detail': self.root_cause_detail,
            'improvement_suggestions': self.improvement_suggestions or [],
            'experience_extracted': self.experience_extracted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# ========================================
# 跨技能优化建议模型
# ========================================

class CrossSkillOptimization(Base):
    """跨技能优化建议
    
    记录从一个技能提取的经验，迁移到其他相似技能
    """
    __tablename__ = 'cross_skill_optimizations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_skill_id = Column(Integer, ForeignKey('ksa_skills.id'))
    target_skill_id = Column(Integer, ForeignKey('ksa_skills.id'))
    optimization_type = Column(String(100))
    title = Column(String(200))
    description = Column(Text)
    priority = Column(Integer, default=0)  # 优先级
    applied = Column(Boolean, default=False)  # 是否已应用
    applied_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'source_skill_id': self.source_skill_id,
            'target_skill_id': self.target_skill_id,
            'optimization_type': self.optimization_type,
            'title': self.title,
            'priority': self.priority,
            'applied': self.applied,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ========================================
# 反思成长引擎
# ========================================

class ReflectionEngine:
    """反思成长引擎
    
    核心能力：
    1. 任务复盘分析 - 自动提取关键指标和根因
    2. 经验提取与沉淀 - 成功/失败案例入库
    3. 举一反三迁移 - 相似技能经验
    4. 主动优化触发 - 连续失败触发优化任务
    """

    def __init__(self, storage=None):
        self.storage = storage or get_default_storage()
        self._init_reflection_tables()

    def _init_reflection_tables(self):
        """初始化反思引擎表"""
        tables_to_create = [
            TaskRetrospective.__table__,
            CrossSkillOptimization.__table__
        ]

        with self.storage.engine.connect() as conn:
            for table in tables_to_create:
                if not self.storage.engine.dialect.has_table(conn, table.name):
                    table.create(self.storage.engine)

    # ========================================
    # 任务复盘分析器
    # ========================================

    def analyze_task_result(self, task_id: str, task_name: str, success: bool,
                           execution_time: float = None, error_message: str = None,
                           output_quality: float = None, skill_id: int = None,
                           ability_id: int = None, agent_id: str = None) -> Dict:
        """
        自动分析任务执行结果，提取关键指标和根因
        
        分析维度：
        1. 耗时分析 - 与历史对比、同类任务对比
        2. 成功率分析 - 历史趋势
        3. 根因分析 - 自动分类
        4. 改进建议 - 基于根因匹配建议
        """
        with self.storage.get_session() as session:
            # 创建复盘记录
            retrospective = TaskRetrospective(
                task_id=task_id,
                task_name=task_name,
                agent_id=agent_id,
                skill_id=skill_id,
                ability_id=ability_id,
                success=success,
                execution_time=execution_time,
                error_message=error_message,
                output_quality=output_quality
            )

            # 执行根因分析
            root_cause, details, suggestions = self._analyze_root_cause(
                success, error_message, execution_time, output_quality, skill_id
            )

            retrospective.root_cause = root_cause
            retrospective.root_cause_detail = details
            retrospective.improvement_suggestions = suggestions

            session.add(retrospective)
            session.flush()

            result = retrospective.to_dict()

            # 提取经验并沉淀
            if success:
                experience_result = self._extract_success_experience(retrospective, session)
                result['experience_extracted'] = True
                result['experience_result'] = experience_result
            else:
                failure_result = self._process_failure(retrospective, session)
                result['failure_analysis'] = failure_result

            # 更新技能指标
            if skill_id:
                self._update_skill_metrics(skill_id, success, execution_time, session)

            # 更新能力指标
            if ability_id:
                self._update_ability_metrics(ability_id, success, session)

            # 检查主动优化触发器
            triggers = self._check_optimization_triggers(skill_id, ability_id, session)
            if triggers:
                result['optimization_triggers'] = triggers

            session.flush()
            return result

    def _analyze_root_cause(self, success: bool, error_message: str = None,
                             execution_time: float = None, output_quality: float = None,
                             skill_id: int = None) -> Tuple[str, str, List[str]]:
        """分析任务失败或成功的根因"""
        suggestions = []

        if success:
            # 成功案例分析
            root_cause = "success_pattern"
            details = "任务成功执行"

            if execution_time and execution_time < 60:
                suggestions.append("执行效率高，可作为最佳实践案例")
            if output_quality and output_quality > 0.8:
                suggestions.append("产出质量优秀，建议提取为标准流程")

            return root_cause, details, suggestions

        # 失败案例分析
        root_cause = FailureReason.UNKNOWN
        details = "未知原因"

        if error_message:
            error_lower = error_message.lower()

            # 知识缺失类错误
            knowledge_keywords = ['not found', 'unknown', 'missing', '权限', '无法找到', '不存在', '缺失']
            if any(kw in error_lower for kw in knowledge_keywords):
                root_cause = FailureReason.KNOWLEDGE_GAP
                details = f"知识或信息缺失导致失败"
                suggestions.append("补充相关领域知识")
                suggestions.append("建立知识检查清单")

            # 技能缺陷类错误
            skill_keywords = ['error', 'exception', 'failed', 'bug', '错误', '异常', '失败']
            if any(kw in error_lower for kw in skill_keywords):
                root_cause = FailureReason.SKILL_DEFECT
                details = "技能执行过程中发生错误"
                suggestions.append("检查技能实现逻辑")
                suggestions.append("增加异常处理机制")

        # 资源限制
        if execution_time and execution_time > 300:  # 超过5分钟
            root_cause = FailureReason.RESOURCE_LIMIT
            details = f"执行时间过长 ({execution_time}s) 超出预期"
            suggestions.append("优化执行流程，减少不必要的步骤")
            suggestions.append("考虑并行执行或分步执行")

        return root_cause, details, suggestions

    # ========================================
    # 经验提取与沉淀
    # ========================================

    def _extract_success_experience(self, retrospective: TaskRetrospective, session) -> Dict:
        """从成功案例中提取经验，沉淀为知识"""
        # 构建经验知识
        experience_content = f"""
# 任务成功经验：{retrospective.task_name}

## 执行情况
- 任务ID: {retrospective.task_id}
- 执行时间: {retrospective.execution_time}秒
- 产出质量: {retrospective.output_quality}

## 成功要素
{retrospective.root_cause_detail}

## 改进建议
{chr(10).join('- ' + s for s in (retrospective.improvement_suggestions or []))}
        """

        # 创建 experiential 类型知识
        knowledge = Knowledge(
            name=f"成功经验：{retrospective.task_name}",
            description=f"从任务执行中提取的经验",
            category="experiential",
            tags=["经验", "最佳实践", retrospective.root_cause],
            content=experience_content.strip(),
            source=f"task:{retrospective.task_id}",
            confidence=0.8
        )
        session.add(knowledge)
        session.flush()

        # 关联到技能（如果有）
        if retrospective.skill_id:
            skill = session.query(Skill).filter(Skill.id == retrospective.skill_id).first()
            if skill:
                # 更新技能成功率（已在 record_execution 中处理）
                pass

        return {
            'knowledge_id': knowledge.id,
            'knowledge_name': knowledge.name,
            'category': 'experiential'
        }

    def _process_failure(self, retrospective: TaskRetrospective, session) -> Dict:
        """处理失败案例，更新技能限制和成功率"""
        result = {}

        if retrospective.skill_id:
            skill = session.query(Skill).filter(Skill.id == retrospective.skill_id).first()
            if skill:
                # 更新技能 limitations 字段
                failure_note = f"\n[{datetime.now().strftime('%Y-%m-%d')}] 失败记录: {retrospective.root_cause} - {retrospective.error_message or '无错误信息'}"
                if skill.limitations:
                    skill.limitations += failure_note
                else:
                    skill.limitations = failure_note

                result['skill_updated'] = {
                        'skill_id': skill.id,
                        'skill_name': skill.name,
                        'limitations_updated': True
                    }

        return result

    def _update_skill_metrics(self, skill_id: int, success: bool, execution_time: float, session):
        """更新技能执行指标（滑动平均）"""
        skill = session.query(Skill).filter(Skill.id == skill_id).first()
        if skill:
            skill.record_execution(success, execution_time or 0)

    def _update_ability_metrics(self, ability_id: int, success: bool, session):
        """更新能力指标（滑动平均）"""
        ability = session.query(Ability).filter(Ability.id == ability_id).first()
        if ability:
            ability.record_task(success)

    # ========================================
    # 举一反三迁移引擎
    # ========================================

    def migrate_experience(self, source_skill_id: int, session=None) -> List[Dict]:
        """
        识别相似技能，把经验自动迁移
        
        算法：
        1. 找到源技能的所有标签
        2. 找到有相似标签的其他技能
        3. 生成跨技能优化建议
        """
        if session is None:
            with self.storage.get_session() as s:
                return self.migrate_experience(source_skill_id, s)

        optimizations = []

        source_skill = session.query(Skill).filter(Skill.id == source_skill_id).first()
        if not source_skill:
            return []

        source_tags = set(source_skill.tags or [])

        # 找到相似技能
        all_skills = session.query(Skill).filter(
            and_(
                Skill.is_active == True,
                Skill.id != source_skill_id
            )
        ).all()

        for target_skill in all_skills:
            target_tags = set(target_skill.tags or [])
            similarity = len(source_tags & target_tags)

            if similarity >= 2:  # 至少2个共同标签
                # 生成优化建议
                optimization = CrossSkillOptimization(
                    source_skill_id=source_skill_id,
                    target_skill_id=target_skill.id,
                    optimization_type='experience_migration',
                    title=f"从 {source_skill.name} 迁移经验到 {target_skill.name}",
                    description=f"两个技能有 {similarity} 个共同标签: {', '.join(source_tags & target_tags)}",
                    priority=similarity
                )
                session.add(optimization)
                optimizations.append(optimization.to_dict())

        return optimizations

    def find_redundant_skills(self, session=None) -> List[Dict]:
        """发现技能之间的冗余和可复用部分"""
        if session is None:
            with self.storage.get_session() as s:
                return self.find_redundant_skills(s)

        redundancies = []
        all_skills = session.query(Skill).filter(Skill.is_active == True).all()

        for i, skill1 in enumerate(all_skills):
            for skill2 in all_skills[i + 1:]:
                # 计算名称和描述相似度
                text1 = skill1.name + ' ' + (skill1.description or '')
                text2 = skill2.name + ' ' + (skill2.description or '')
                similarity = self._calculate_similarity(text1, text2)

                if similarity > 0.6:  # 相似度超过60%
                    redundancies.append({
                        'skill1': {'id': skill1.id, 'name': skill1.name},
                        'skill2': {'id': skill2.id, 'name': skill2.name},
                        'similarity': similarity,
                        'recommendation': '考虑合并或提取共同逻辑'
                    })

        return redundancies

    # ========================================
    # 主动优化触发器
    # ========================================

    def _check_optimization_triggers(self, skill_id: int = None, ability_id: int = None,
                                      session=None) -> List[Dict]:
        """
        检查是否触发主动优化
        
        触发条件：
        1. 技能连续3次成功率低于阈值 → 触发优化任务
        2. 知识被引用超过10次 → 升级为核心知识
        3. Agent能力指标连续提升 → 扩大职责范围
        """
        triggers = []

        if skill_id:
            skill_triggers = self._check_skill_triggers(skill_id, session)
            triggers.extend(skill_triggers)

        if ability_id:
            ability_triggers = self._check_ability_triggers(ability_id, session)
            triggers.extend(ability_triggers)

        # 检查知识引用
        knowledge_triggers = self._check_knowledge_triggers(session)
        triggers.extend(knowledge_triggers)

        return triggers

    def _check_skill_triggers(self, skill_id: int, session) -> List[Dict]:
        """检查技能优化触发器"""
        triggers = []

        skill = session.query(Skill).filter(Skill.id == skill_id).first()
        if not skill:
            return triggers

        # 连续失败检查（简化版：检查最近执行记录）
        if skill.total_runs >= 3 and skill.success_rate < 0.5:
            triggers.append({
                'type': 'skill_optimization_required',
                'severity': 'high',
                'skill_id': skill_id,
                'skill_name': skill.name,
                'message': f"技能成功率 {skill.success_rate:.2f} 低于阈值 0.5",
                'action': '建议发起技能优化任务',
                'current_metrics': {
                    'total_runs': skill.total_runs,
                    'success_rate': skill.success_rate
                }
            })

        return triggers

    def _check_ability_triggers(self, ability_id: int, session) -> List[Dict]:
        """检查能力优化触发器"""
        triggers = []

        ability = session.query(Ability).filter(Ability.id == ability_id).first()
        if not ability:
            return triggers

        # 能力连续提升检查
        if ability.total_tasks >= 5 and ability.overall_success_rate > 0.8:
            triggers.append({
                'type': 'ability_expansion_recommended',
                'severity': 'low',
                'ability_id': ability_id,
                'ability_name': ability.name,
                'message': f"能力成功率 {ability.overall_success_rate:.2f} 表现优秀",
                'action': '建议扩大该能力的职责范围',
                'current_metrics': {
                    'total_tasks': ability.total_tasks,
                    'success_rate': ability.overall_success_rate
                }
            })

        return triggers

    def _check_knowledge_triggers(self, session) -> List[Dict]:
        """检查知识升级触发器"""
        triggers = []

        # 查找高引用知识
        knowledge_list = session.query(Knowledge).filter(
            and_(
                Knowledge.is_active == True,
                Knowledge.use_count >= 10
            )
        ).all()

        for knowledge in knowledge_list:
            # 检查是否已是核心知识（通过标签判断）
            tags = knowledge.tags or []
            if '核心知识' not in tags:
                triggers.append({
                    'type': 'knowledge_promotion',
                    'severity': 'low',
                    'knowledge_id': knowledge.id,
                    'knowledge_name': knowledge.name,
                    'message': f"知识被引用 {knowledge.use_count} 次",
                    'action': '建议升级为核心知识'
                })

        return triggers

    # ========================================
    # 复盘记录管理
    # ========================================

    def get_retrospective(self, retro_id: int) -> Optional[Dict]:
        """获取复盘记录"""
        with self.storage.get_session() as session:
            retro = session.query(TaskRetrospective).filter(
                TaskRetrospective.id == retro_id
            ).first()
            return retro.to_dict() if retro else None

    def list_retrospectives(self, task_id: str = None, success: bool = None,
                            limit: int = 100, offset: int = 0) -> List[Dict]:
        """列出复盘记录"""
        with self.storage.get_session() as session:
            query = session.query(TaskRetrospective)

            if task_id:
                query = query.filter(TaskRetrospective.task_id == task_id)
            if success is not None:
                query = query.filter(TaskRetrospective.success == success)

            query = query.order_by(TaskRetrospective.created_at.desc())
            query = query.offset(offset).limit(limit)

            return [r.to_dict() for r in query.all()]

    # ========================================
    # 统计信息
    # ========================================

    def get_stats(self) -> Dict:
        """获取反思引擎统计"""
        with self.storage.get_session() as session:
            total_retros = session.query(TaskRetrospective).count()
            success_retros = session.query(TaskRetrospective).filter(
                TaskRetrospective.success == True
            ).count()
            failure_retros = total_retros - success_retros

            # 根因分布
            root_cause_stats = {}
            for reason in ['knowledge_gap', 'skill_defect', 'resource_limit', 'coordination_issue', 'unknown', 'success_pattern']:
                count = session.query(TaskRetrospective).filter(
                    TaskRetrospective.root_cause == reason
                ).count()
                if count > 0:
                    root_cause_stats[reason] = count

            return {
                'total_retrospectives': total_retros,
                'success_count': success_retros,
                'failure_count': failure_retros,
                'success_rate': success_retros / total_retros if total_retros > 0 else 0,
                'root_cause_distribution': root_cause_stats,
                'pending_optimizations': session.query(CrossSkillOptimization).filter(
                    CrossSkillOptimization.applied == False
                ).count()
            }

    def _calculate_similarity(self, a: str, b: str) -> float:
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
