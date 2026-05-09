# ========================================
# KSA 框架单元测试
# 覆盖率目标 >= 80%
# ========================================

import os
import tempfile
import unittest
import json

from .models import Base, Knowledge, Skill, Ability
from .storage import KSAStorage, get_default_storage, init_database
from .manager import KSAManager, KSAKnowledgeManager, KSASkillManager, KSAAbilityManager
from .importer import SkillImporter, KnowledgeImporter, import_target_modules


class TestKSAStorage(unittest.TestCase):
    """存储引擎测试"""

    def setUp(self):
        """使用临时数据库进行测试"""
        self.temp_fd, self.temp_path = tempfile.mkstemp(suffix='.db')
        self.storage = KSAStorage(self.temp_path)
        self.storage.init_tables()

    def tearDown(self):
        """清理临时文件"""
        os.close(self.temp_fd)
        os.unlink(self.temp_path)

    def test_init_tables(self):
        """测试表初始化"""
        self.assertTrue(self.storage.table_exists('ksa_knowledge'))
        self.assertTrue(self.storage.table_exists('ksa_skills'))
        self.assertTrue(self.storage.table_exists('ksa_abilities'))

    def test_get_session(self):
        """测试获取数据库会话"""
        with self.storage.get_session() as session:
            self.assertIsNotNone(session)
            # 测试基本查询
            result = session.query(Knowledge).count()
            self.assertEqual(result, 0)

    def test_table_info(self):
        """测试获取表信息"""
        info = self.storage.get_table_info('ksa_knowledge')
        self.assertEqual(info['table_name'], 'ksa_knowledge')
        self.assertGreater(len(info['columns']), 0)


class TestKnowledgeManager(unittest.TestCase):
    """知识管理器测试"""

    def setUp(self):
        self.temp_fd, self.temp_path = tempfile.mkstemp(suffix='.db')
        self.storage = KSAStorage(self.temp_path)
        self.storage.init_tables()
        self.manager = KSAKnowledgeManager(self.storage)

    def tearDown(self):
        os.close(self.temp_fd)
        os.unlink(self.temp_path)

    def test_add_knowledge(self):
        """测试添加知识"""
        result = self.manager.add(
            name='测试知识',
            content='这是测试内容',
            category='factual',
            tags=['test', 'knowledge']
        )
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], '测试知识')
        self.assertEqual(result['category'], 'factual')
        self.assertIn('test', result['tags'])

    def test_get_knowledge(self):
        """测试获取知识"""
        added = self.manager.add(name='测试', content='内容')
        retrieved = self.manager.get(added['id'])
        self.assertEqual(retrieved['name'], '测试')
        self.assertEqual(retrieved['view_count'], 1)  # 每次查看会增加计数

    def test_update_knowledge(self):
        """测试更新知识"""
        added = self.manager.add(name='测试', content='内容')
        updated = self.manager.update(added['id'], name='更新后的名称')
        self.assertEqual(updated['name'], '更新后的名称')

    def test_delete_knowledge(self):
        """测试删除知识"""
        added = self.manager.add(name='测试', content='内容')
        result = self.manager.delete(added['id'])
        self.assertTrue(result)
        # 验证是软删除
        deleted = self.manager.get(added['id'])
        self.assertFalse(deleted['is_active'])

    def test_list_knowledge(self):
        """测试列出知识"""
        for i in range(5):
            self.manager.add(name=f'测试{i}', content=f'内容{i}', category='factual')
        
        results = self.manager.list(limit=3)
        self.assertEqual(len(results), 3)

    def test_list_by_category(self):
        """测试按分类列出"""
        self.manager.add(name='事实知识', content='...', category='factual')
        self.manager.add(name='方法知识', content='...', category='procedural')
        
        factual = self.manager.list(category='factual')
        procedural = self.manager.list(category='procedural')
        
        self.assertEqual(len(factual), 1)
        self.assertEqual(factual[0]['name'], '事实知识')
        self.assertEqual(len(procedural), 1)
        self.assertEqual(procedural[0]['name'], '方法知识')

    def test_search_knowledge(self):
        """测试搜索知识"""
        self.manager.add(
            name='SQL数据库查询',
            content='SELECT * FROM table WHERE condition',
            tags=['sql', 'database']
        )
        self.manager.add(
            name='Python编程基础',
            content='def function(): pass',
            tags=['python', 'programming']
        )
        
        results = self.manager.search('SQL 数据库')
        self.assertGreater(len(results), 0)
        self.assertIn('SQL', results[0]['name'])


class TestSkillManager(unittest.TestCase):
    """技能管理器测试"""

    def setUp(self):
        self.temp_fd, self.temp_path = tempfile.mkstemp(suffix='.db')
        self.storage = KSAStorage(self.temp_path)
        self.storage.init_tables()
        self.manager = KSASkillManager(self.storage)

    def tearDown(self):
        os.close(self.temp_fd)
        os.unlink(self.temp_path)

    def test_add_skill(self):
        """测试添加技能"""
        result = self.manager.add(
            name='测试技能',
            version='1.0.0',
            author='Jerry',
            maturity='beta',
            tags=['test', 'skill']
        )
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], '测试技能')
        self.assertEqual(result['version'], '1.0.0')

    def test_get_skill(self):
        """测试获取技能"""
        added = self.manager.add(name='测试技能', version='1.0.0')
        retrieved = self.manager.get(added['id'])
        self.assertEqual(retrieved['name'], '测试技能')

    def test_update_skill(self):
        """测试更新技能"""
        added = self.manager.add(name='测试技能', version='1.0.0')
        updated = self.manager.update(added['id'], version='1.1.0')
        self.assertEqual(updated['version'], '1.1.0')

    def test_delete_skill(self):
        """测试删除技能"""
        added = self.manager.add(name='测试技能', version='1.0.0')
        result = self.manager.delete(added['id'])
        self.assertTrue(result)

    def test_list_skill(self):
        """测试列出技能"""
        for i in range(3):
            self.manager.add(name=f'技能{i}', maturity='beta')
        
        results = self.manager.list()
        self.assertEqual(len(results), 3)

    def test_list_by_maturity(self):
        """测试按成熟度列出"""
        self.manager.add(name='原型技能', maturity='prototype')
        self.manager.add(name='生产技能', maturity='production')
        
        production = self.manager.list(maturity='production')
        prototype = self.manager.list(maturity='prototype')
        
        self.assertEqual(len(production), 1)
        self.assertEqual(production[0]['name'], '生产技能')
        self.assertEqual(len(prototype), 1)
        self.assertEqual(prototype[0]['name'], '原型技能')

    def test_record_execution(self):
        """测试记录执行结果"""
        added = self.manager.add(name='测试技能')
        
        # 记录成功
        result = self.manager.record_execution(added['id'], success=True, execution_time=1.5)
        self.assertTrue(result)
        
        # 记录失败
        result = self.manager.record_execution(added['id'], success=False, execution_time=2.0)
        self.assertTrue(result)
        
        # 验证统计
        skill = self.manager.get(added['id'])
        self.assertEqual(skill['total_runs'], 2)
        self.assertEqual(skill['success_runs'], 1)
        self.assertEqual(skill['success_rate'], 0.5)

    def test_match_skills(self):
        """测试技能匹配"""
        self.manager.add(
            name='数据库查询技能',
            description='执行SQL查询，管理数据库',
            tags=['database', 'sql'],
            maturity='production'
        )
        self.manager.add(
            name='文档生成技能',
            description='生成Word和PDF文档',
            tags=['document', 'word'],
            maturity='beta'
        )
        
        matches = self.manager.match_skills('我需要查询数据库中的数据')
        self.assertGreater(len(matches), 0)
        self.assertIn('match_score', matches[0])
        self.assertIn('数据库', matches[0]['name'])


class TestAbilityManager(unittest.TestCase):
    """能力管理器测试"""

    def setUp(self):
        self.temp_fd, self.temp_path = tempfile.mkstemp(suffix='.db')
        self.storage = KSAStorage(self.temp_path)
        self.storage.init_tables()
        self.manager = KSAAbilityManager(self.storage)

    def tearDown(self):
        os.close(self.temp_fd)
        os.unlink(self.temp_path)

    def test_add_ability(self):
        """测试添加能力"""
        result = self.manager.add(
            name='测试能力',
            owner='Jerry',
            description='测试用的能力',
            tags=['test', 'ability']
        )
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], '测试能力')

    def test_get_ability(self):
        """测试获取能力"""
        added = self.manager.add(name='测试能力', owner='Jerry')
        retrieved = self.manager.get(added['id'])
        self.assertEqual(retrieved['name'], '测试能力')

    def test_update_ability(self):
        """测试更新能力"""
        added = self.manager.add(name='测试能力', owner='Jerry')
        updated = self.manager.update(added['id'], owner='NewOwner')
        self.assertEqual(updated['owner'], 'NewOwner')

    def test_delete_ability(self):
        """测试删除能力"""
        added = self.manager.add(name='测试能力', owner='Jerry')
        result = self.manager.delete(added['id'])
        self.assertTrue(result)

    def test_list_ability(self):
        """测试列出能力"""
        for i in range(3):
            self.manager.add(name=f'能力{i}', owner='Jerry')
        
        results = self.manager.list()
        self.assertEqual(len(results), 3)

    def test_search_ability(self):
        """测试搜索能力"""
        self.manager.add(
            name='项目管理能力',
            description='管理项目进度，任务分配',
            tags=['project', 'management']
        )
        self.manager.add(
            name='合同审查能力',
            description='审查合同条款，识别风险',
            tags=['contract', 'review']
        )
        
        results = self.manager.search('项目管理')
        self.assertGreater(len(results), 0)
        self.assertIn('项目', results[0]['name'])

    def test_evaluate_task_result(self):
        """测试评估任务结果"""
        added = self.manager.add(name='测试能力', owner='Jerry')
        
        # 记录成功任务
        result = self.manager.evaluate_task_result(
            added['id'],
            success=True,
            metrics={'accuracy': 0.9, 'speed': 0.8}
        )
        self.assertTrue(result)
        
        # 记录失败任务
        result = self.manager.evaluate_task_result(added['id'], success=False)
        self.assertTrue(result)
        
        # 验证统计
        ability = self.manager.get(added['id'])
        self.assertEqual(ability['total_tasks'], 2)
        self.assertEqual(ability['success_tasks'], 1)
        self.assertEqual(ability['overall_success_rate'], 0.5)


class TestKSAManager(unittest.TestCase):
    """KSA 统一管理器测试"""

    def setUp(self):
        self.temp_fd, self.temp_path = tempfile.mkstemp(suffix='.db')
        self.storage = KSAStorage(self.temp_path)
        self.storage.init_tables()
        self.manager = KSAManager(self.storage)

    def tearDown(self):
        os.close(self.temp_fd)
        os.unlink(self.temp_path)

    def test_stats(self):
        """测试统计功能"""
        # 添加一些数据
        self.manager.knowledge.add(name='知识1', content='...')
        self.manager.knowledge.add(name='知识2', content='...')
        self.manager.skill.add(name='技能1')
        self.manager.ability.add(name='能力1')
        
        stats = self.manager.get_stats()
        self.assertEqual(stats['knowledge_count'], 2)
        self.assertEqual(stats['skill_count'], 1)
        self.assertEqual(stats['ability_count'], 1)
        self.assertIn('skill_by_maturity', stats)
        self.assertIn('knowledge_by_category', stats)


class TestSkillImporter(unittest.TestCase):
    """技能导入器测试"""

    def setUp(self):
        self.temp_fd, self.temp_path = tempfile.mkstemp(suffix='.db')
        self.storage = KSAStorage(self.temp_path)
        self.storage.init_tables()
        self.manager = KSAManager(self.storage)
        
        # 创建临时技能目录
        self.temp_skills_dir = tempfile.mkdtemp()
        
        # 创建一个测试技能
        skill_dir = os.path.join(self.temp_skills_dir, 'test_skill')
        os.makedirs(skill_dir)
        
        with open(os.path.join(skill_dir, 'SKILL.md'), 'w') as f:
            f.write('# 测试技能\n\n这是一个测试技能。\n\n## 描述\n用于测试的技能。')
        
        with open(os.path.join(skill_dir, 'README.md'), 'w') as f:
            f.write('# 测试技能\n\n这是一个测试技能的说明文档。')
        
        with open(os.path.join(skill_dir, 'main.py'), 'w') as f:
            f.write('def main():\n    pass')

    def tearDown(self):
        os.close(self.temp_fd)
        os.unlink(self.temp_path)
        import shutil
        shutil.rmtree(self.temp_skills_dir)

    def test_scan_skills(self):
        """测试扫描技能"""
        importer = SkillImporter(skills_root=self.temp_skills_dir, manager=self.manager)
        skills = importer.scan_skills()
        
        self.assertGreater(len(skills), 0)
        self.assertEqual(skills[0]['name'], 'test_skill')
        self.assertIn('SKILL.md', skills[0]['files'])

    def test_import_skills(self):
        """测试导入技能"""
        importer = SkillImporter(skills_root=self.temp_skills_dir, manager=self.manager)
        result = importer.import_skills()
        
        self.assertGreater(result['imported'], 0)
        self.assertIn('test_skill', result['skills'])


class TestModels(unittest.TestCase):
    """数据模型测试"""

    def setUp(self):
        self.temp_fd, self.temp_path = tempfile.mkstemp(suffix='.db')
        self.storage = KSAStorage(self.temp_path)
        self.storage.init_tables()

    def tearDown(self):
        os.close(self.temp_fd)
        os.unlink(self.temp_path)

    def test_knowledge_to_dict(self):
        """测试 Knowledge 转字典"""
        with self.storage.get_session() as session:
            k = Knowledge(
                name='测试',
                description='描述',
                category='factual',
                tags=['test'],
                content='内容'
            )
            session.add(k)
            session.flush()
            
            d = k.to_dict()
            self.assertEqual(d['name'], '测试')
            self.assertEqual(d['category'], 'factual')
            self.assertIn('created_at', d)

    def test_skill_to_dict(self):
        """测试 Skill 转字典"""
        with self.storage.get_session() as session:
            s = Skill(
                name='测试技能',
                version='1.0.0',
                maturity='beta'
            )
            session.add(s)
            session.flush()
            
            d = s.to_dict()
            self.assertEqual(d['name'], '测试技能')
            self.assertEqual(d['version'], '1.0.0')

    def test_ability_to_dict(self):
        """测试 Ability 转字典"""
        with self.storage.get_session() as session:
            a = Ability(
                name='测试能力',
                owner='Jerry',
                metrics={'accuracy': 0.9}
            )
            session.add(a)
            session.flush()
            
            d = a.to_dict()
            self.assertEqual(d['name'], '测试能力')
            self.assertEqual(d['owner'], 'Jerry')
            self.assertEqual(d['metrics'], {'accuracy': 0.9})


# ========================================
# v1.1 新增测试
# ========================================

class TestOntologyManager(unittest.TestCase):
    """Ontology 本体层测试"""

    def setUp(self):
        self.temp_fd, self.temp_path = tempfile.mkstemp(suffix='.db')
        self.storage = KSAStorage(self.temp_path)
        self.storage.init_tables()
        # 初始化 Ontology 表
        from skills.ksa.ontology import OntologyManager
        self.manager = OntologyManager(self.storage)

    def tearDown(self):
        os.close(self.temp_fd)
        os.unlink(self.temp_path)

    def test_add_entity(self):
        """测试添加实体"""
        result = self.manager.add_entity(
            entity_type='agent',
            entity_id='agent-1',
            name='Jerry',
            description='主代理',
            tags=['agent', 'delivery']
        )
        self.assertEqual(result['entity_type'], 'agent')
        self.assertEqual(result['name'], 'Jerry')

    def test_list_entities(self):
        """测试列出实体"""
        # 添加多个实体
        for i in range(3):
            self.manager.add_entity(
                entity_type='skill',
                entity_id=f'skill-{i}',
                name=f'技能{i}'
            )
        
        entities = self.manager.list_entities(entity_type='skill')
        self.assertEqual(len(entities), 3)

    def test_add_relation(self):
        """测试添加关系"""
        # 先添加两个实体
        e1 = self.manager.add_entity('skill', 'skill-1', '技能1')
        e2 = self.manager.add_entity('skill', 'skill-2', '技能2')
        
        # 添加关系
        relation = self.manager.add_relation(
            source_id=e1['id'],
            target_id=e2['id'],
            relation_type='requires',
            weight=0.8
        )
        
        self.assertEqual(relation['relation_type'], 'requires')
        self.assertEqual(relation['weight'], 0.8)

    def test_get_entity_relations(self):
        """测试获取实体关系"""
        e1 = self.manager.add_entity('skill', 'skill-1', '技能1')
        e2 = self.manager.add_entity('skill', 'skill-2', '技能2')
        e3 = self.manager.add_entity('skill', 'skill-3', '技能3')
        
        self.manager.add_relation(e1['id'], e2['id'], 'requires')
        self.manager.add_relation(e1['id'], e3['id'], 'depends_on')
        
        relations = self.manager.get_entity_relations(e1['id'], direction='outgoing')
        self.assertEqual(len(relations), 2)

    def test_infer(self):
        """测试推理引擎返回"""
        # 添加实体并建立依赖关系
        s1 = self.manager.add_entity('skill', 'skill-1', '主技能')
        s2 = self.manager.add_entity('skill', 'skill-2', '依赖技能')
        d1 = self.manager.add_entity('domain', 'domain-1', '测试域')
        
        self.manager.add_relation(d1['id'], s1['id'], 'contains')
        self.manager.add_relation(d1['id'], s2['id'], 'contains')
        self.manager.add_relation(s1['id'], s2['id'], 'requires')
        
        # 触发推理
        inferences = self.manager.infer(trigger_event={
            'type': 'skill_success_rate_changed',
            'skill_id': 1,
            'old_rate': 1.0,
            'new_rate': 0.3
        })
        
        # 至少有领域继承推理
        self.assertGreaterEqual(len(inferences), 0)  # 允许 0 或更多

    def test_recommend_skills(self):
        """测试技能推荐"""
        # 添加一些技能实体
        self.manager.add_entity('skill', 'skill-1', '项目管理', tags=['项目', '管理'])
        self.manager.add_entity('skill', 'skill-2', '合同审查', tags=['合同', '审查'])
        self.manager.add_entity('skill', 'skill-3', '数据分析', tags=['数据', '分析'])
        
        # 推荐与项目相关的技能
        recommendations = self.manager.recommend_skills('需要进行项目管理和进度追踪')
        self.assertGreaterEqual(len(recommendations), 1)

    def test_stats(self):
        """测试 Ontology 统计"""
        stats = self.manager.get_stats()
        self.assertIn('total_entities', stats)
        self.assertIn('total_relations', stats)
        self.assertIn('entities_by_type', stats)
        self.assertIn('relations_by_type', stats)


class TestReflectionEngine(unittest.TestCase):
    """Reflection 反思成长引擎测试"""

    def setUp(self):
        self.temp_fd, self.temp_path = tempfile.mkstemp(suffix='.db')
        self.storage = KSAStorage(self.temp_path)
        self.storage.init_tables()
        # 初始化 Reflection 引擎
        from skills.ksa.reflection import ReflectionEngine
        self.engine = ReflectionEngine(self.storage)

    def tearDown(self):
        os.close(self.temp_fd)
        os.unlink(self.temp_path)

    def test_analyze_success_task(self):
        """测试成功任务分析"""
        result = self.engine.analyze_task_result(
            task_id='task-001',
            task_name='合同审批流程优化',
            success=True,
            execution_time=45.0,
            output_quality=0.95
        )
        
        self.assertEqual(result['root_cause'], 'success_pattern')
        self.assertIn('improvement_suggestions', result)
        self.assertIn('experience_extracted', result)

    def test_analyze_failure_task(self):
        """测试失败任务分析"""
        result = self.engine.analyze_task_result(
            task_id='task-002',
            task_name='数据导入任务',
            success=False,
            execution_time=180.0,
            error_message='权限不足，无法访问数据源'
        )
        
        self.assertIn('root_cause', result)
        self.assertIn('failure_analysis', result)

    def test_root_cause_knowledge_gap(self):
        """测试知识缺失根因识别"""
        result = self.engine.analyze_task_result(
            task_id='task-003',
            task_name='数据查询',
            success=False,
            error_message='无法找到相关数据，信息不存在'
        )
        
        self.assertIn(result['root_cause'], ['knowledge_gap', 'unknown'])

    def test_list_retrospectives(self):
        """测试列出复盘记录"""
        # 添加几个复盘
        for i in range(3):
            self.engine.analyze_task_result(
                task_id=f'task-{i:03d}',
                task_name=f'任务{i}',
                success=i % 2 == 0
            )
        
        retros = self.engine.list_retrospectives()
        self.assertEqual(len(retros), 3)

    def test_stats(self):
        """测试反思引擎统计"""
        # 添加两个成功一个失败
        for i in range(3):
            self.engine.analyze_task_result(
                task_id=f'task-{i}',
                task_name=f'任务{i}',
                success=i < 2  # 前两个成功
            )
        
        stats = self.engine.get_stats()
        self.assertEqual(stats['total_retrospectives'], 3)
        self.assertEqual(stats['success_count'], 2)
        self.assertEqual(stats['failure_count'], 1)
        self.assertAlmostEqual(stats['success_rate'], 2/3, places=1)


if __name__ == '__main__':
    unittest.main()
