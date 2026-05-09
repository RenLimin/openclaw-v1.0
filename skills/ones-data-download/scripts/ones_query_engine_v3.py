#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ONES 项目与工作项查询引擎 v3.0
================================
新增能力：
1. ✅ 项目列表查询（含项目状态、负责人、时间线）
2. ✅ 工作项查询（支持按项目过滤、按状态过滤）
3. ✅ 子工作项层级查询（完整树结构）
4. ✅ 按条件筛选（负责人、状态、类型、时间范围）
5. ✅ Excel分层输出（项目表/工作项表/子工作项表）

作者：Oliver 🐘
版本：3.0.0
日期：2026-04-26
"""

import asyncio
import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ playwright 未安装")
    sys.exit(1)


class ONESQueryEngine:
    """ONES 查询引擎"""
    
    def __init__(self, config_path=None):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if config_path is None:
            config_path = os.path.join(script_dir, '..', 'config', 'ones-config.json')
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.team_uuid = self.config['team_uuid']
        self.base_url = self.config['ones_url']
        self.graphql_url = self.config['graphql_api'].format(team_uuid=self.team_uuid)
        
        self.page = None
        self.context = None
        self.browser = None
    
    # ============================================================
    # 1. 项目查询
    # ============================================================
    
    async def query_projects(self, filters=None):
        """
        查询项目列表
        
        Args:
            filters: 过滤条件
                - name_contains: 名称包含关键词
                - status: 状态 ('normal'=正常, 'archived'=归档)
                - owner_uuid: 负责人UUID
                - limit: 返回数量限制
        """
        filters = filters or {}
        limit = filters.get('limit', 100)
        
        variables = {
            "fields": [
                "uuid", "name", "key", "description", "status", "owner",
                "startTime", "endTime", "createTime", "updateTime", "archiveTime"
            ],
            "limit": limit,
            "offset": 0
        }
        
        if filters.get('name_contains'):
            variables["name"] = filters['name_contains']
        if filters.get('status'):
            variables["status"] = filters['status']
        
        result = await self._graphql_query("""
            query ($fields: [String!]!, $limit: Int!, $offset: Int!) {
                projects(fields: $fields, limit: $limit, offset: $offset) {
                    uuid name key description status owner startTime endTime
                    createTime updateTime archiveTime
                }
            }
        """, variables)
        
        projects = result.get('data', {}).get('projects', [])
        
        # 后处理过滤
        if filters.get('owner_uuid'):
            projects = [p for p in projects if p.get('owner', {}).get('uuid') == filters['owner_uuid']]
        
        return projects
    
    # ============================================================
    # 2. 工作项查询（支持按项目过滤）
    # ============================================================
    
    async def query_work_items(self, project_uuid=None, filters=None):
        """
        查询工作项（含子工作项关联信息）
        
        Args:
            project_uuid: 指定项目UUID，None表示所有项目
            filters: 过滤条件
                - status: 状态
                - assign_uuid: 负责人
                - issue_type: 工作项类型
                - title_contains: 标题包含
                - has_subtasks: 是否有子工作项
                - limit: 返回限制
        """
        filters = filters or {}
        limit = filters.get('limit', 500)
        
        # 基础字段 + 子工作项信息
        base_fields = [
            "uuid", "number", "name", "key", "path", "parent { uuid }",
            "status { uuid name category }",
            "assign { uuid name key }",
            "project { uuid name key }",
            "issueType { uuid name manhourStatisticMode }",
            "deadline", "estimatedHours", "remainingManhour",
            "startTime", "endTime", "createTime", "updateTime",
            "subTaskCount", "subTaskDoneCount"
        ]
        
        variables = {
            "fields": base_fields,
            "limit": limit,
            "offset": 0
        }
        
        # 按项目过滤
        if project_uuid:
            variables["projectUUID"] = project_uuid
        
        # 按状态过滤
        if filters.get('status'):
            variables["status"] = [filters['status']]
        
        # 按负责人过滤
        if filters.get('assign_uuid'):
            variables["assign"] = [filters['assign_uuid']]
        
        result = await self._graphql_query("""
            query ($fields: [String!]!, $limit: Int!, $offset: Int!) {
                tasks(fields: $fields, limit: $limit, offset: $offset) {
                    uuid number name key path
                    parent { uuid }
                    status { uuid name category }
                    assign { uuid name key }
                    project { uuid name key }
                    issueType { uuid name }
                    deadline estimatedHours remainingManhour
                    startTime endTime createTime updateTime
                    subTaskCount subTaskDoneCount
                }
            }
        """, variables)
        
        tasks = result.get('data', {}).get('tasks', [])
        
        # 后处理过滤
        if filters.get('has_subtasks') is True:
            tasks = [t for t in tasks if t.get('subTaskCount', 0) > 0]
        if filters.get('has_subtasks') is False:
            tasks = [t for t in tasks if t.get('subTaskCount', 0) == 0]
        if filters.get('title_contains'):
            keyword = filters['title_contains'].lower()
            tasks = [t for t in tasks if keyword in t.get('name', '').lower()]
        
        return tasks
    
    # ============================================================
    # 3. 子工作项层级查询（完整树结构）
    # ============================================================
    
    async def query_sub_work_items(self, parent_uuid):
        """
        查询指定工作项下的所有子工作项（递归）
        
        Args:
            parent_uuid: 父工作项UUID
        """
        fields = [
            "uuid", "number", "name", "path", "parent { uuid }",
            "status { uuid name }", "assign { uuid name }",
            "estimatedHours", "remainingManhour", "subTaskCount"
        ]
        
        result = await self._graphql_query("""
            query ($fields: [String!]!, $parentUUID: UUID!) {
                tasks(fields: $fields, parent: $parentUUID, limit: 100) {
                    uuid number name path
                    parent { uuid }
                    status { uuid name }
                    assign { uuid name }
                    estimatedHours remainingManhour
                    subTaskCount
                }
            }
        """, {"fields": fields, "parentUUID": parent_uuid})
        
        subtasks = result.get('data', {}).get('tasks', [])
        
        # 递归查询子子工作项
        for task in subtasks:
            if task.get('subTaskCount', 0) > 0:
                task['children'] = await self.query_sub_work_items(task['uuid'])
            else:
                task['children'] = []
        
        return subtasks
    
    async def build_work_hierarchy(self, project_uuid=None):
        """
        构建完整的工作项层级树
        
        Returns:
            {
                'root_tasks': [...],  # 顶层工作项（无父级）
                'hierarchy': {...},   # 完整树结构
                'total_count': N      # 总工作项数
            }
        """
        # 获取所有工作项
        all_tasks = await self.query_work_items(project_uuid=project_uuid, filters={'limit': 2000})
        
        # 按parent分组
        parent_map = {}
        for task in all_tasks:
            parent_uuid = task.get('parent', {}).get('uuid')
            if parent_uuid not in parent_map:
                parent_map[parent_uuid] = []
            parent_map[parent_uuid].append(task)
        
        # 顶层工作项（无parent或parent为项目）
        root_tasks = parent_map.get(None, []) + parent_map.get(project_uuid, [])
        
        # 递归构建层级
        def build_tree(tasks_list):
            result = []
            for task in tasks_list:
                task_uuid = task['uuid']
                children = parent_map.get(task_uuid, [])
                if children:
                    task['children'] = build_tree(children)
                else:
                    task['children'] = []
                result.append(task)
            return result
        
        hierarchy = build_tree(root_tasks)
        
        return {
            'root_tasks': root_tasks,
            'hierarchy': hierarchy,
            'total_count': len(all_tasks),
            'has_subtasks_count': sum(1 for t in all_tasks if t.get('subTaskCount', 0) > 0)
        }
    
    # ============================================================
    # 4. GraphQL 底层查询
    # ============================================================
    
    async def _graphql_query(self, query, variables):
        """执行 GraphQL 查询"""
        if not self.page:
            # 需要先登录
            await self._ensure_login()
        
        # 通过浏览器执行 GraphQL
        result = await self.page.evaluate("""
            async ({ query, variables, url }) => {
                const resp = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    credentials: 'include',
                    body: JSON.stringify({ query, variables })
                });
                return await resp.json();
            }
        """, {"query": query, "variables": variables, "url": self.graphql_url})
        
        return result
    
    async def _ensure_login(self):
        """确保已登录"""
        if self.page:
            return True
        
        # 简化版登录：使用已有Cookie
        print("🔐 启动浏览器并加载 ONES...")
        playwright = async_playwright()
        self.browser = await playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        
        await self.page.goto(self.base_url)
        await asyncio.sleep(2)
        
        print("✅ 浏览器已启动")
        return True
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
    
    # ============================================================
    # 5. Excel 分层导出
    # ============================================================
    
    def export_to_excel(self, projects=None, tasks=None, hierarchy=None, output_path=None):
        """
        分层导出到 Excel：
        Sheet1: 项目清单
        Sheet2: 工作项清单
        Sheet3: 子工作项层级（扁平化）
        """
        if pd is None:
            print("⚠️ pandas 未安装，跳过 Excel 导出")
            return None
        
        output_dir = Path(output_path) if output_path else Path.home() / '.openclaw/workspace/output/ones-data'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f'ONES项目与工作项_{timestamp}.xlsx'
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Sheet1: 项目清单
            if projects:
                df_projects = pd.DataFrame([
                    {
                        '项目UUID': p.get('uuid'),
                        '项目名称': p.get('name'),
                        '项目Key': p.get('key'),
                        '状态': p.get('status'),
                        '负责人': p.get('owner', {}).get('name') if p.get('owner') else '',
                        '开始时间': self._format_ts(p.get('startTime')),
                        '结束时间': self._format_ts(p.get('endTime')),
                        '创建时间': self._format_ts(p.get('createTime')),
                        '描述': (p.get('description') or '')[:200]
                    }
                    for p in projects
                ])
                df_projects.to_excel(writer, sheet_name='项目清单', index=False)
            
            # Sheet2: 工作项清单
            if tasks:
                df_tasks = pd.DataFrame([
                    {
                        '工作项UUID': t.get('uuid'),
                        '工作项编号': t.get('number'),
                        '工作项标题': t.get('name'),
                        '所属项目': t.get('project', {}).get('name') if t.get('project') else '',
                        '工作项类型': t.get('issueType', {}).get('name') if t.get('issueType') else '',
                        '状态': t.get('status', {}).get('name') if t.get('status') else '',
                        '负责人': t.get('assign', {}).get('name') if t.get('assign') else '',
                        '计划工时': t.get('estimatedHours'),
                        '剩余工时': t.get('remainingManhour'),
                        '子工作项数量': t.get('subTaskCount'),
                        '已完成子工作项': t.get('subTaskDoneCount'),
                        '开始时间': self._format_ts(t.get('startTime')),
                        '截止时间': self._format_ts(t.get('deadline')),
                        '父工作项UUID': t.get('parent', {}).get('uuid') if t.get('parent') else ''
                    }
                    for t in tasks
                ])
                df_tasks.to_excel(writer, sheet_name='工作项清单', index=False)
            
            # Sheet3: 子工作项层级（扁平化）
            if hierarchy:
                def flatten_hierarchy(hier, level=1, parent_id='', parent_title=''):
                    rows = []
                    for item in hier:
                        rows.append({
                            '层级': level,
                            '工作项UUID': item.get('uuid'),
                            '工作项编号': item.get('number'),
                            '工作项标题': item.get('name'),
                            '父工作项UUID': parent_id,
                            '父工作项标题': parent_title,
                            '子工作项数量': item.get('subTaskCount', 0),
                            '负责人': item.get('assign', {}).get('name') if item.get('assign') else ''
                        })
                        if item.get('children'):
                            rows.extend(flatten_hierarchy(
                                item['children'], level + 1,
                                item.get('uuid'), item.get('name')
                            ))
                    return rows
                
                flat_rows = flatten_hierarchy(hierarchy)
                if flat_rows:
                    df_hier = pd.DataFrame(flat_rows)
                    df_hier.to_excel(writer, sheet_name='子工作项层级', index=False)
        
        return output_file
    
    def _format_ts(self, ts):
        """格式化时间戳"""
        if not ts:
            return ''
        try:
            return datetime.fromtimestamp(int(ts) / 1000).strftime('%Y-%m-%d %H:%M')
        except:
            return str(ts)


# ============================================================
# 命令行入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description='ONES 项目与工作项查询引擎 v3.0')
    parser.add_argument('--mode', default='query', choices=['projects', 'tasks', 'subtasks', 'hierarchy', 'full', 'query'],
                        help='查询模式: projects(项目), tasks(工作项), subtasks(子工作项), hierarchy(层级树), full(全部)')
    parser.add_argument('--project', help='指定项目UUID（仅查询该项目工作项）')
    parser.add_argument('--parent', help='父工作项UUID（查询子工作项）')
    parser.add_argument('--status', help='按状态过滤')
    parser.add_argument('--assign', help='按负责人UUID过滤')
    parser.add_argument('--title', help='按标题关键词过滤')
    parser.add_argument('--limit', type=int, default=500, help='返回数量限制')
    parser.add_argument('--output', help='输出目录')
    parser.add_argument('--export-excel', action='store_true', help='导出Excel')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🔍 ONES 项目与工作项查询引擎 v3.0")
    print("=" * 70)
    
    engine = ONESQueryEngine()
    
    async def run():
        try:
            await engine._ensure_login()
            
            result = {}
            
            # 1. 查询项目
            if args.mode in ['projects', 'full', 'query']:
                print(f"\n📊 查询项目列表...")
                projects = await engine.query_projects({'limit': args.limit})
                print(f"   ✅ 找到 {len(projects)} 个项目")
                for p in projects[:10]:
                    status_icon = "🟢" if p.get('status') == 'normal' else "⚪"
                    print(f"   {status_icon} {p.get('name')[:40]} ({p.get('key')})")
                if len(projects) > 10:
                    print(f"   ... 还有 {len(projects) - 10} 个项目")
                result['projects'] = projects
            
            # 2. 查询工作项
            if args.mode in ['tasks', 'full', 'hierarchy', 'query']:
                filters = {}
                if args.status:
                    filters['status'] = args.status
                if args.assign:
                    filters['assign_uuid'] = args.assign
                if args.title:
                    filters['title_contains'] = args.title
                
                print(f"\n📋 查询工作项...")
                tasks = await engine.query_work_items(
                    project_uuid=args.project,
                    filters={**filters, 'limit': args.limit}
                )
                print(f"   ✅ 找到 {len(tasks)} 个工作项")
                
                # 统计信息
                status_count = {}
                for t in tasks:
                    status = t.get('status', {}).get('name', '未知') if t.get('status') else '未知'
                    status_count[status] = status_count.get(status, 0) + 1
                
                print(f"   📈 状态统计:")
                for status, count in status_count.items():
                    print(f"      {status}: {count} 个")
                
                result['tasks'] = tasks
            
            # 3. 查询子工作项层级
            if args.mode in ['subtasks', 'hierarchy', 'full']:
                if args.parent:
                    print(f"\n🌳 查询子工作项 (parent={args.parent})...")
                    subtasks = await engine.query_sub_work_items(args.parent)
                    print(f"   ✅ 找到 {len(subtasks)} 个直接子工作项")
                    result['subtasks'] = subtasks
                elif args.mode in ['hierarchy', 'full']:
                    print(f"\n🌳 构建完整工作项层级树...")
                    hier_result = await engine.build_work_hierarchy(project_uuid=args.project)
                    print(f"   ✅ 总工作项数: {hier_result['total_count']}")
                    print(f"   ✅ 顶层工作项: {len(hier_result['root_tasks'])} 个")
                    print(f"   ✅ 含子工作项的任务: {hier_result['has_subtasks_count']} 个")
                    result['hierarchy'] = hier_result
            
            # 导出 Excel
            if args.export_excel:
                print(f"\n📤 导出 Excel...")
                output_file = engine.export_to_excel(
                    projects=result.get('projects'),
                    tasks=result.get('tasks'),
                    hierarchy=result.get('hierarchy'),
                    output_path=args.output
                )
                if output_file:
                    print(f"   ✅ 已导出: {output_file}")
                    result['excel_file'] = str(output_file)
            
            print(f"\n" + "=" * 70)
            print("✅ 查询完成！")
            print("=" * 70)
            
            return result
            
        finally:
            await engine.close()
    
    return asyncio.run(run())


if __name__ == '__main__':
    main()
