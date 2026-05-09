#!/usr/bin/env python3
# ========================================
# Orion LLM调度框架 - 单元测试
# 功能：验证模板、验证器等核心功能
# ========================================

import sys
import unittest
from pathlib import Path

# 添加父目录到Python路径，支持skills包导入
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(current_dir))

# 导入待测试模块（使用绝对导入）
from orion.templates import (
    get_template,
    get_all_templates,
    build_prompt,
    TEMPLATE_REGISTRY,
)
from orion.templates_base import PromptTemplate, OutputFormat, PROMPT_TEMPLATES_TABLE_SCHEMA
from orion.templates_s11_s15 import TEMPLATES_S11_S15
from orion.templates_s16_s20 import TEMPLATES_S16_S20


class TestTemplates(unittest.TestCase):
    """模板加载测试"""

    def test_get_template_exists(self):
        """测试获取存在的模板"""
        for template_id in ["S11", "S12", "S13", "S14", "S15", "S16", "S17", "S18", "S19", "S20"]:
            with self.subTest(template_id=template_id):
                template = get_template(template_id)
                self.assertIsNotNone(template)
                self.assertIsInstance(template, PromptTemplate)
                self.assertEqual(template.template_id, template_id)

    def test_get_template_not_exists(self):
        """测试获取不存在的模板"""
        template = get_template("INVALID_ID")
        self.assertIsNone(template)

    def test_get_all_templates(self):
        """测试获取所有模板"""
        templates = get_all_templates()
        self.assertIsInstance(templates, dict)
        self.assertEqual(len(templates), 10)

    def test_template_structure(self):
        """测试模板结构完整性"""
        template = get_template("S11")
        self.assertIsNotNone(template.template_id)
        self.assertIsNotNone(template.scenario_name)
        self.assertIsNotNone(template.system_prompt)
        self.assertIsInstance(template.output_format, OutputFormat)
        self.assertIsInstance(template.output_schema, dict)
        self.assertIsInstance(template.input_params, list)
        self.assertIsInstance(template.example_input, dict)
        self.assertIsInstance(template.example_output, dict)
        self.assertIsInstance(template.tags, list)


class TestTemplateSplitting(unittest.TestCase):
    """模板文件拆分测试"""

    def test_s11_s15_templates(self):
        """测试S11-S15模板文件"""
        self.assertEqual(len(TEMPLATES_S11_S15), 5)
        self.assertIn("S11", TEMPLATES_S11_S15)
        self.assertIn("S15", TEMPLATES_S11_S15)

    def test_s16_s20_templates(self):
        """测试S16-S20模板文件"""
        self.assertEqual(len(TEMPLATES_S16_S20), 5)
        self.assertIn("S16", TEMPLATES_S16_S20)
        self.assertIn("S20", TEMPLATES_S16_S20)

    def test_full_registry_merges_both(self):
        """测试完整注册表包含所有模板"""
        self.assertEqual(len(TEMPLATE_REGISTRY), 10)


class TestBuildPrompt(unittest.TestCase):
    """Prompt构建测试"""

    def test_build_prompt_valid_template(self):
        """测试使用有效模板构建Prompt"""
        data = {
            "project_data": {"name": "测试项目"},
            "task_statuses": [],
            "week_range": "2024-W01"
        }
        prompt = build_prompt("S15", data)
        self.assertIsNotNone(prompt)
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)

    def test_build_prompt_invalid_template(self):
        """测试使用无效模板构建Prompt"""
        prompt = build_prompt("INVALID_ID", {})
        self.assertIsNone(prompt)

    def test_build_prompt_contains_system_prompt(self):
        """测试构建的Prompt包含系统提示词"""
        template = get_template("S11")
        data = {"test": "data"}
        prompt = build_prompt("S11", data)
        self.assertIn(template.system_prompt[:100], prompt)


class TestTemplatesBase(unittest.TestCase):
    """模板基类测试"""

    def test_output_format_enum(self):
        """测试输出格式枚举"""
        self.assertIsNotNone(OutputFormat.JSON)
        self.assertIsNotNone(OutputFormat.MARKDOWN)
        self.assertIsNotNone(OutputFormat.TEXT)
        self.assertIsNotNone(OutputFormat.XML)

    def test_prompt_template_dataclass(self):
        """测试PromptTemplate数据类结构"""
        template = PromptTemplate(
            template_id="TEST",
            scenario_name="测试场景",
            system_prompt="测试系统提示",
            output_format=OutputFormat.JSON,
            output_schema={"type": "object"},
            input_params=[],
            example_input={},
            example_output={}
        )
        self.assertEqual(template.template_id, "TEST")
        self.assertEqual(template.scenario_name, "测试场景")

    def test_table_schema_exists(self):
        """测试表结构定义存在"""
        self.assertIsInstance(PROMPT_TEMPLATES_TABLE_SCHEMA, str)
        self.assertIn("CREATE TABLE", PROMPT_TEMPLATES_TABLE_SCHEMA)


class TestTemplateCoverage(unittest.TestCase):
    """模板覆盖率测试"""

    def test_all_templates_have_tags(self):
        """测试所有模板都有标签"""
        for template_id, template in TEMPLATE_REGISTRY.items():
            with self.subTest(template_id=template_id):
                self.assertGreater(len(template.tags), 0)

    def test_all_templates_have_input_params(self):
        """测试所有模板都有输入参数定义"""
        for template_id, template in TEMPLATE_REGISTRY.items():
            with self.subTest(template_id=template_id):
                self.assertGreater(len(template.input_params), 0)

    def test_template_scenario_names_unique(self):
        """测试所有模板场景名称唯一"""
        scenario_names = set()
        for template in TEMPLATE_REGISTRY.values():
            self.assertNotIn(template.scenario_name, scenario_names)
            scenario_names.add(template.scenario_name)


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("🧪 开始运行 Orion 单元测试")
    print("=" * 60)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestTemplates))
    suite.addTests(loader.loadTestsFromTestCase(TestTemplateSplitting))
    suite.addTests(loader.loadTestsFromTestCase(TestBuildPrompt))
    suite.addTests(loader.loadTestsFromTestCase(TestTemplatesBase))
    suite.addTests(loader.loadTestsFromTestCase(TestTemplateCoverage))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ 所有测试通过！")
    else:
        print(f"❌ 测试失败: {len(result.failures)} 个失败, {len(result.errors)} 个错误")
    print("=" * 60)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
