#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛒 智能体团队模板管理器 v1.0

功能：
1. 列出可用团队模板
2. 查看模板详情
3. 使用模板快速创建团队
4. 搜索和筛选模板
5. 导出/导入自定义模板

创建时间：2026-05-08
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class TemplateManager:
    """智能体团队模板管理器"""

    def __init__(self, templates_dir: str = None):
        if templates_dir is None:
            templates_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "..", "templates"
            )

        self.templates_dir = Path(templates_dir).resolve()
        self.index_file = self.templates_dir / "index.json"

        print("🛒 智能体团队模板管理器 v1.0")
        print(f"   模板目录: {self.templates_dir}")

        # 加载模板索引
        with open(self.index_file, encoding="utf-8") as f:
            self.index = json.load(f)

        print(f"   已加载 {self.index['total_templates']} 个模板")

    def list_templates(self, category: str = None, search: str = None) -> List[Dict]:
        """列出所有模板"""
        all_templates = []

        for cat_name, cat_data in self.index["categories"].items():
            if category and cat_name != category:
                continue

            for template in cat_data["templates"]:
                if search:
                    if search.lower() in template["name"].lower() or \
                       any(search.lower() in tag.lower() for tag in template.get("tags", [])):
                        all_templates.append(template)
                else:
                    all_templates.append(template)

        return all_templates

    def show_templates_table(self, templates: List[Dict] = None):
        """以表格形式显示模板列表"""
        if templates is None:
            templates = self.list_templates()

        print("\n" + "=" * 90)
        print(f"{'模板ID':<45} {'名称':<25} {'分类':<10} {'难度':<10}")
        print("-" * 90)

        for template in templates:
            difficulty = template.get("difficulty", "unknown")
            category = template.get("id", "").split("-")[0]
            print(f"{template['id']:<45} {template['name']:<25} {category:<10} {difficulty:<10}")

        print("=" * 90)
        print(f"共 {len(templates)} 个模板\n")

    def get_template_detail(self, template_id: str) -> Optional[Dict]:
        """获取模板详情"""
        for category in self.index["categories"].values():
            for template in category["templates"]:
                if template["id"] == template_id:
                    template_path = self.templates_dir / template["path"]
                    with open(template_path, encoding="utf-8") as f:
                        return json.load(f)
        return None

    def show_template_detail(self, template_id: str):
        """显示模板详细信息"""
        detail = self.get_template_detail(template_id)
        if not detail:
            print(f"❌ 模板不存在: {template_id}")
            return

        print(f"\n{'='*80}")
        print(f"📋 模板详情: {detail['template_name']}")
        print(f"{'='*80}")
        print(f"\n📌 基本信息:")
        print(f"   模板ID: {detail['template_id']}")
        print(f"   版本: {detail['version']}")
        print(f"   分类: {detail['template_category']}")
        print(f"   描述: {detail['description']}")
        print(f"\n⏱️ 部署估算:")
        print(f"   预估成本: ${detail['estimated_cost_usd_per_month']}/月")
        print(f"   预估部署时间: {detail['estimated_setup_time_minutes']} 分钟")

        print(f"\n👥 团队架构 ({len(detail['team_structure'])} 个角色):")
        for agent_id, agent_info in detail["team_structure"].items():
            print(f"   - {agent_info['role']}")
            print(f"     目标: {agent_info['goal']}")
            print(f"     技能: {', '.join(agent_info['skills'][:3])}")

        print(f"\n📊 工作流程 ({len(detail.get('workflow', {}))} 个):")
        for workflow_name, workflow_info in detail.get("workflow", {}).items():
            print(f"   - {workflow_info['name']}")

        print(f"\n🏷️ 标签: {', '.join(detail.get('tags', []))}")
        print(f"\n{'='*80}\n")

    def create_team_from_template(self, template_id: str, team_name: str, output_dir: str = None) -> bool:
        """从模板创建团队配置"""
        detail = self.get_template_detail(template_id)
        if not detail:
            print(f"❌ 模板不存在: {template_id}")
            return False

        if output_dir is None:
            output_dir = self.templates_dir.parent / "generated_teams" / team_name

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n🚀 从模板创建团队: {template_id} → {team_name}")

        # 保存团队配置
        team_config = {
            "team_name": team_name,
            "created_from_template": template_id,
            "created_at": datetime.now().isoformat(),
            "template_version": detail["version"],
            "team_structure": detail["team_structure"],
            "workflow": detail.get("workflow", {}),
            "slas": detail.get("slas", {}),
            "metrics": detail.get("metrics", {})
        }

        config_file = output_dir / "team_config.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(team_config, f, indent=2, ensure_ascii=False)

        # 为每个Agent生成独立配置文件
        agents_dir = output_dir / "agents"
        agents_dir.mkdir(exist_ok=True)

        for agent_id, agent_config in detail["team_structure"].items():
            agent_file = agents_dir / f"{agent_id}.json"
            with open(agent_file, "w", encoding="utf-8") as f:
                json.dump(agent_config, f, indent=2, ensure_ascii=False)

        # 创建README
        readme_content = f"""# {team_name}

此团队由模板自动生成

## 模板信息
- 模板ID: {template_id}
- 模板版本: {detail['version']}
- 创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 团队规模
- 角色数: {len(detail['team_structure'])}
"""
        with open(output_dir / "README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)

        print(f"✅ 团队创建成功!")
        print(f"   输出目录: {output_dir}")
        print(f"   包含角色: {len(detail['team_structure'])} 个")

        return True

    def search_templates(self, keyword: str):
        """搜索模板"""
        results = self.list_templates(search=keyword)
        print(f"\n🔍 搜索 '{keyword}' 找到 {len(results)} 个模板:")
        self.show_templates_table(results)

    def list_categories(self):
        """列出模板分类"""
        print("\n📁 模板分类列表:")
        for cat_name, cat_data in self.index["categories"].items():
            print(f"   - {cat_name}: {cat_data['name']} ({cat_data['count']} 个模板)")
            print(f"     {cat_data['description']}\n")

    def export_template(self, template_id: str, output_file: str) -> bool:
        """导出模板"""
        detail = self.get_template_detail(template_id)
        if not detail:
            print(f"❌ 模板不存在: {template_id}")
            return False

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(detail, f, indent=2, ensure_ascii=False)

        print(f"✅ 模板已导出到: {output_file}")
        return True


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="智能体团队模板管理器")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # list 命令
    list_parser = subparsers.add_parser("list", help="列出所有模板")
    list_parser.add_argument("--category", help="按分类筛选")

    # show 命令
    show_parser = subparsers.add_parser("show", help="显示模板详情")
    show_parser.add_argument("template_id", help="模板ID")

    # create 命令
    create_parser = subparsers.add_parser("create", help="从模板创建团队")
    create_parser.add_argument("template_id", help="模板ID")
    create_parser.add_argument("team_name", help="团队名称")
    create_parser.add_argument("--output", help="输出目录")

    # search 命令
    search_parser = subparsers.add_parser("search", help="搜索模板")
    search_parser.add_argument("keyword", help="搜索关键词")

    # categories 命令
    subparsers.add_parser("categories", help="列出所有分类")

    args = parser.parse_args()

    tm = TemplateManager()

    if args.command == "list" or args.command is None:
        templates = tm.list_templates(category=args.category if hasattr(args, 'category') else None)
        tm.show_templates_table(templates)

    elif args.command == "show":
        tm.show_template_detail(args.template_id)

    elif args.command == "create":
        tm.create_team_from_template(args.template_id, args.team_name, args.output)

    elif args.command == "search":
        tm.search_templates(args.keyword)

    elif args.command == "categories":
        tm.list_categories()


if __name__ == "__main__":
    main()
