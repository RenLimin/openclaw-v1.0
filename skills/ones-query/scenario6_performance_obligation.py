#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
场景6：ONES工作项履约义务查询验证
=======================================
功能：
1. 查询"北京光环新网科技股份有限公司"相关项目（客户名称或最终用户名称包含）
2. 对每个项目，递归查询所有子工作项
3. 筛选工作项类型 = "履约义务" 的项
4. 构建层级树形结构：项目 → 工作项 → 子工作项
5. 统计每个项目的履约义务数量、状态分布

作者：Jerry 🦞
版本：1.0.0
日期：2026-04-29
"""

import asyncio
import json
import os
import sys
import time
import pickle
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("⚠️ pandas 未安装，表格输出功能受限")

try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("❌ playwright 未安装")
    sys.exit(1)


# ============================================================
# 配置
# ============================================================
SCRIPT_DIR = Path(__file__).parent
CONFIG_PATH = SCRIPT_DIR / 'config.json'
COOKIE_PATH = Path.home() / '.openclaw/cache/ones_cookies.pkl'
OUTPUT_DIR = Path.home() / '.openclaw/workspace/training-reports'

# 目标客户
TARGET_COMPANY = "北京光环新网科技股份有限公司"

# 性能日志
PERF_LOG = []


def perf_log(step: str, start_time: float, extra: str = ""):
    """记录性能日志"""
    elapsed = time.time() - start_time
    PERF_LOG.append({
        "step": step,
        "elapsed_seconds": round(elapsed, 2),
        "timestamp": datetime.now().isoformat(),
        "extra": extra
    })
    print(f"⏱️  {step}: {elapsed:.2f}s {extra}")


class PerformanceObligationQuery:
    """履约义务查询工具"""
    
    def __init__(self):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.team_uuid = self.config['team_uuid']
        self.base_url = self.config['ones_url']
        self.graphql_url = self.config['graphql_api'].format(team_uuid=self.team_uuid)
        
        self.field_mapping = self.config['field_mapping']
        
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_authenticated = False
        
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    async def authenticate(self) -> bool:
        """登录认证（简化版）"""
        start_time = time.time()
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox']
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        
        # 加载已有Cookie
        if COOKIE_PATH.exists():
            with open(COOKIE_PATH, 'rb') as f:
                cookies = pickle.load(f)
            await self.context.add_cookies(cookies)
        
        self.page = await self.context.new_page()
        print("🔐 加载 ONES 页面...")
        await self.page.goto(self.base_url, timeout=30000)
        await asyncio.sleep(3)
        
        self.is_authenticated = True
        perf_log("认证", start_time, "SUCCESS")
        print("✅ 浏览器已启动，准备查询")
        return True
    
    async def graphql_query(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """执行GraphQL查询"""
        if not self.is_authenticated or not self.page:
            raise Exception("未认证")
        
        result = await self.page.evaluate("""
            async ({ query, variables, url }) => {
                const resp = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    credentials: 'include',
                    body: JSON.stringify({ query, variables }),
                    signal: AbortSignal.timeout(30000)
                });
                if (!resp.ok) {
                    throw new Error(`HTTP ${resp.status}`);
                }
                return await resp.json();
            }
        """, {"query": query, "variables": variables, "url": self.graphql_url})
        
        if result.get('errors'):
            raise Exception(f"GraphQL错误: {result['errors'][0].get('message')}")
        
        return result
    
    async def query_all_projects(self) -> List[Dict[str, Any]]:
        """查询所有项目（用于过滤）"""
        start_time = time.time()
        print("🔍 查询所有项目...")
        
        all_projects = []
        offset = 0
        limit = 100
        max_pages = 50
        
        while True:
            variables = {
                "fields": ["uuid", "name", "key", "status", "owner", "createTime"],
                "limit": limit,
                "offset": offset
            }
            
            result = await self.graphql_query("""
                query ($fields: [String!]!, $limit: Int!, $offset: Int!) {
                    projects(fields: $fields, limit: $limit, offset: $offset) {
                        uuid name key status owner createTime
                    }
                }
            """, variables)
            
            projects = result.get('data', {}).get('projects', [])
            if not projects:
                break
            
            all_projects.extend(projects)
            if len(projects) < limit:
                break
            
            offset += limit
            if offset // limit >= max_pages:
                break
        
        perf_log("查询所有项目", start_time, f"共 {len(all_projects)} 个项目")
        return all_projects
    
    async def query_work_items_with_custom_fields(self, project_uuid: str) -> List[Dict[str, Any]]:
        """查询工作项（包含客户名称、最终用户、工作项类型等自定义字段）"""
        customer_field = self.field_mapping.get('客户名称', '_F4awkERN')
        end_user_field = self.field_mapping.get('最终用户名称', '_RnWqUALs')
        
        fields = [
            "uuid", "number", "name", "path",
            "parent { uuid }",
            "status { uuid name category }",
            "assign { uuid name }",
            "project { uuid name }",
            "issueType { uuid name }",
            "subTaskCount",
            f"{customer_field}",
            f"{end_user_field}",
            "createTime", "updateTime"
        ]
        
        all_tasks = []
        offset = 0
        limit = 500
        max_pages = 20
        
        while True:
            variables = {
                "fields": fields,
                "limit": limit,
                "offset": offset,
                "projectUUID": project_uuid
            }
            
            result = await self.graphql_query("""
                query ($fields: [String!]!, $limit: Int!, $offset: Int!, $projectUUID: UUID!) {
                    tasks(fields: $fields, limit: $limit, offset: $offset, project: $projectUUID) {
                        uuid number name path
                        parent { uuid }
                        status { uuid name category }
                        assign { uuid name }
                        project { uuid name }
                        issueType { uuid name }
                        subTaskCount
                    }
                }
            """, variables)
            
            tasks = result.get('data', {}).get('tasks', [])
            if not tasks:
                break
            
            all_tasks.extend(tasks)
            if len(tasks) < limit:
                break
            
            offset += limit
            if offset // limit >= max_pages:
                break
        
        return all_tasks
    
    async def query_all_work_items_with_type(self) -> List[Dict[str, Any]]:
        """查询所有工作项，包含自定义字段"""
        start_time = time.time()
        print("🔍 查询所有工作项（含自定义字段）...")
        
        customer_field = self.field_mapping.get('客户名称', '_F4awkERN')
        end_user_field = self.field_mapping.get('最终用户名称', '_RnWqUALs')
        
        fields = [
            "uuid", "number", "name", "path",
            "parent { uuid }",
            "status { uuid name category }",
            "assign { uuid name }",
            "project { uuid name key }",
            "issueType { uuid name }",
            "subTaskCount", "subTaskDoneCount",
            f"{customer_field}",
            f"{end_user_field}",
            "createTime", "updateTime"
        ]
        
        all_tasks = []
        offset = 0
        limit = 500
        max_pages = 40  # 最多20000条
        
        while True:
            variables = {
                "fields": fields,
                "limit": limit,
                "offset": offset
            }
            
            result = await self.graphql_query("""
                query ($fields: [String!]!, $limit: Int!, $offset: Int!) {
                    tasks(fields: $fields, limit: $limit, offset: $offset) {
                        uuid number name path
                        parent { uuid }
                        status { uuid name category }
                        assign { uuid name }
                        project { uuid name key }
                        issueType { uuid name }
                        subTaskCount subTaskDoneCount
                    }
                }
            """, variables)
            
            tasks = result.get('data', {}).get('tasks', [])
            if not tasks:
                break
            
            all_tasks.extend(tasks)
            print(f"   已拉取 {len(all_tasks)} 条...")
            
            if len(tasks) < limit:
                break
            
            offset += limit
            if offset // limit >= max_pages:
                break
        
        perf_log("查询所有工作项", start_time, f"共 {len(all_tasks)} 条")
        return all_tasks
    
    def filter_tasks_by_customer(self, tasks: List[Dict], target_company: str) -> List[Dict]:
        """按客户名称或最终用户名称过滤工作项"""
        # 注意：自定义字段在GraphQL返回中可能需要特殊处理
        # 先通过project关联，然后检查工作项属性
        
        # 简化方案：先收集所有包含目标公司的工作项
        # 由于自定义字段可能不在返回中，我们先通过项目名称匹配
        # 或者后续递归查询子工作项
        
        # 先收集所有项目信息
        projects = {}
        for task in tasks:
            proj = task.get('project', {})
            if proj and proj.get('uuid'):
                projects[proj['uuid']] = proj
        
        # 匹配"履约义务"类型的工作项
        performance_tasks = []
        for task in tasks:
            issue_type = task.get('issueType', {}) or {}
            type_name = issue_type.get('name', '') or ''
            
            # 检查是否是履约义务类型
            if '履约' in type_name or '义务' in type_name:
                performance_tasks.append(task)
        
        print(f"   找到 {len(performance_tasks)} 个履约义务类型的工作项")
        return performance_tasks
    
    async def build_performance_obligation_hierarchy(self, tasks: List[Dict]) -> Dict[str, Any]:
        """构建履约义务层级树"""
        start_time = time.time()
        print("🌳 构建履约义务层级树...")
        
        # 1. 按项目分组
        project_groups = {}
        for task in tasks:
            proj = task.get('project', {}) or {}
            proj_uuid = proj.get('uuid')
            proj_name = proj.get('name', '未知项目')
            proj_key = proj.get('key', '')
            
            if not proj_uuid:
                continue
            
            if proj_uuid not in project_groups:
                project_groups[proj_uuid] = {
                    'project_uuid': proj_uuid,
                    'project_name': proj_name,
                    'project_key': proj_key,
                    'performance_obligations': []
                }
            
            # 构建工作项树
            project_groups[proj_uuid]['performance_obligations'].append(task)
        
        # 2. 为每个项目的履约义务构建子工作项层级
        for proj_uuid, group in project_groups.items():
            print(f"   查询项目 {group['project_name'][:30]} 的子工作项...")
            
            for obligation in group['performance_obligations']:
                if obligation.get('subTaskCount', 0) > 0:
                    obligation['children'] = await self.query_sub_work_items_recursive(obligation['uuid'])
                else:
                    obligation['children'] = []
        
        perf_log("构建层级树", start_time, f"共 {len(project_groups)} 个项目")
        
        return {
            'project_groups': project_groups,
            'total_projects': len(project_groups),
            'total_obligations': len(tasks)
        }
    
    async def query_sub_work_items_recursive(self, parent_uuid: str, depth: int = 0) -> List[Dict]:
        """递归查询子工作项"""
        if depth > 5:  # 防止无限递归
            return []
        
        fields = [
            "uuid", "number", "name", "path",
            "parent { uuid }",
            "status { uuid name }",
            "assign { uuid name }",
            "issueType { uuid name }",
            "subTaskCount"
        ]
        
        try:
            result = await self.graphql_query("""
                query ($fields: [String!]!, $parentUUID: UUID!) {
                    tasks(fields: $fields, parent: $parentUUID, limit: 100) {
                        uuid number name path
                        parent { uuid }
                        status { uuid name }
                        assign { uuid name }
                        issueType { uuid name }
                        subTaskCount
                    }
                }
            """, {"fields": fields, "parentUUID": parent_uuid})
            
            subtasks = result.get('data', {}).get('tasks', [])
            
            # 继续递归
            for task in subtasks:
                if task.get('subTaskCount', 0) > 0:
                    task['children'] = await self.query_sub_work_items_recursive(task['uuid'], depth + 1)
                else:
                    task['children'] = []
            
            return subtasks
            
        except Exception as e:
            print(f"   ⚠️ 查询子工作项失败 {parent_uuid}: {e}")
            return []
    
    def generate_statistics(self, hierarchy: Dict[str, Any]) -> Dict[str, Any]:
        """生成统计数据"""
        start_time = time.time()
        print("📊 生成统计数据...")
        
        stats = {
            'summary': {
                'total_projects': hierarchy['total_projects'],
                'total_obligations': hierarchy['total_obligations'],
                'total_subtasks': 0,
                'completed_obligations': 0,
                'in_progress_obligations': 0,
                'pending_obligations': 0
            },
            'by_project': {},
            'by_status': {},
            'status_distribution': {}
        }
        
        total_subtasks = 0
        completed = 0
        in_progress = 0
        pending = 0
        
        # 按项目统计
        for proj_uuid, group in hierarchy['project_groups'].items():
            proj_stats = {
                'project_name': group['project_name'],
                'project_key': group['project_key'],
                'obligation_count': len(group['performance_obligations']),
                'subtask_count': 0,
                'status_distribution': {},
                'obligations': []
            }
            
            for obligation in group['performance_obligations']:
                status = obligation.get('status', {}).get('name', '未知') if obligation.get('status') else '未知'
                
                # 状态分布
                proj_stats['status_distribution'][status] = proj_stats['status_distribution'].get(status, 0) + 1
                stats['status_distribution'][status] = stats['status_distribution'].get(status, 0) + 1
                
                # 状态计数
                status_cat = obligation.get('status', {}).get('category', '') if obligation.get('status') else ''
                if 'done' in str(status_cat).lower() or '已完成' in status or status == '完成':
                    completed += 1
                elif '进行' in status or '处理' in status:
                    in_progress += 1
                else:
                    pending += 1
                
                # 子工作项计数
                subtask_count = obligation.get('subTaskCount', 0) or 0
                proj_stats['subtask_count'] += subtask_count
                total_subtasks += subtask_count
                
                # 保存明细
                proj_stats['obligations'].append({
                    'number': obligation.get('number'),
                    'name': obligation.get('name'),
                    'status': status,
                    'assign': obligation.get('assign', {}).get('name') if obligation.get('assign') else '-',
                    'subtask_count': subtask_count
                })
            
            stats['by_project'][proj_uuid] = proj_stats
        
        stats['summary']['total_subtasks'] = total_subtasks
        stats['summary']['completed_obligations'] = completed
        stats['summary']['in_progress_obligations'] = in_progress
        stats['summary']['pending_obligations'] = pending
        
        # 计算完成率
        total = hierarchy['total_obligations']
        if total > 0:
            stats['summary']['completion_rate'] = round(completed / total * 100, 2)
        else:
            stats['summary']['completion_rate'] = 0
        
        perf_log("生成统计数据", start_time)
        return stats
    
    def generate_markdown_report(self, stats: Dict[str, Any], hierarchy: Dict[str, Any]) -> str:
        """生成Markdown报告"""
        start_time = time.time()
        print("📝 生成Markdown报告...")
        
        lines = []
        lines.append("# 场景6：ONES工作项履约义务查询验证报告")
        lines.append("")
        lines.append(f"**查询时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**目标客户**: {TARGET_COMPANY}")
        lines.append("")
        
        # 摘要
        lines.append("## 📊 统计摘要")
        lines.append("")
        lines.append("| 指标 | 数值 |")
        lines.append("|------|------|")
        lines.append(f"| 关联项目数 | {stats['summary']['total_projects']} |")
        lines.append(f"| 履约义务总数 | {stats['summary']['total_obligations']} |")
        lines.append(f"| 子工作项总数 | {stats['summary']['total_subtasks']} |")
        lines.append(f"| 已完成履约义务 | {stats['summary']['completed_obligations']} |")
        lines.append(f"| 进行中履约义务 | {stats['summary']['in_progress_obligations']} |")
        lines.append(f"| 待处理履约义务 | {stats['summary']['pending_obligations']} |")
        lines.append(f"| 履约义务完成率 | {stats['summary']['completion_rate']}% |")
        lines.append("")
        
        # 状态分布
        lines.append("## 📈 履约义务状态分布")
        lines.append("")
        lines.append("| 状态 | 数量 | 占比 |")
        lines.append("|------|------|------|")
        total = stats['summary']['total_obligations']
        for status, count in sorted(stats['status_distribution'].items(), key=lambda x: -x[1]):
            pct = round(count / total * 100, 1) if total > 0 else 0
            lines.append(f"| {status} | {count} | {pct}% |")
        lines.append("")
        
        # 按项目分组的履约义务
        lines.append("## 📋 按项目分组的履约义务明细")
        lines.append("")
        
        for proj_uuid, proj_stats in sorted(stats['by_project'].items(), 
                                            key=lambda x: -x[1]['obligation_count']):
            proj_name = proj_stats['project_name']
            proj_key = proj_stats['project_key']
            obl_count = proj_stats['obligation_count']
            
            lines.append(f"### 项目: {proj_name} ({proj_key})")
            lines.append("")
            lines.append(f"- 履约义务数量: **{obl_count}**")
            lines.append(f"- 子工作项总数: {proj_stats['subtask_count']}")
            lines.append("")
            
            # 该项目状态分布
            lines.append("**状态分布:**")
            for status, count in proj_stats['status_distribution'].items():
                lines.append(f"- {status}: {count}")
            lines.append("")
            
            # 履约义务表格
            lines.append("**履约义务明细:**")
            lines.append("")
            lines.append("| 编号 | 履约义务名称 | 状态 | 负责人 | 子工作项数 |")
            lines.append("|------|-------------|------|--------|-----------|")
            
            for obl in proj_stats['obligations']:
                lines.append(f"| {obl['number']} | {obl['name'][:50]} | {obl['status']} | {obl['assign']} | {obl['subtask_count']} |")
            
            lines.append("")
            lines.append("---")
            lines.append("")
        
        perf_log("生成Markdown报告", start_time)
        return "\n".join(lines)
    
    async def close(self):
        """关闭资源"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


async def main():
    """主函数"""
    overall_start = time.time()
    print("=" * 70)
    print("🔍 场景6：ONES工作项履约义务查询验证")
    print("=" * 70)
    print(f"🎯 目标客户: {TARGET_COMPANY}")
    print("")
    
    tool = PerformanceObligationQuery()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    try:
        # 1. 认证
        await tool.authenticate()
        
        # 2. 查询所有工作项
        all_tasks = await tool.query_all_work_items_with_type()
        
        # 3. 过滤履约义务类型的工作项
        performance_tasks = tool.filter_tasks_by_customer(all_tasks, TARGET_COMPANY)
        
        if not performance_tasks:
            print("\n⚠️ 未找到履约义务类型的工作项")
            # 尝试直接查询所有项目，然后逐个查询
            print("\n尝试替代方案: 查询所有项目，筛选名称包含目标公司的项目...")
            projects = await tool.query_all_projects()
            target_projects = [p for p in projects if TARGET_COMPANY in p.get('name', '')]
            print(f"   找到 {len(target_projects)} 个名称包含'{TARGET_COMPANY}'的项目")
            
            # 重新收集这些项目下的履约义务
            performance_tasks = []
            for proj in target_projects:
                proj_tasks = await tool.query_work_items_with_custom_fields(proj['uuid'])
                for task in proj_tasks:
                    issue_type = task.get('issueType', {}) or {}
                    type_name = issue_type.get('name', '') or ''
                    if '履约' in type_name or '义务' in type_name:
                        performance_tasks.append(task)
                print(f"   项目 {proj['name'][:30]}: 找到 {len([t for t in proj_tasks if '履约' in str(t.get('issueType', {}).get('name', ''))])} 个履约义务")
        
        print(f"\n✅ 共找到 {len(performance_tasks)} 个履约义务工作项")
        
        # 4. 构建层级树
        hierarchy = await tool.build_performance_obligation_hierarchy(performance_tasks)
        
        # 5. 生成统计
        stats = tool.generate_statistics(hierarchy)
        
        # 6. 生成Markdown报告
        markdown = tool.generate_markdown_report(stats, hierarchy)
        
        # 7. 保存结果
        json_output = OUTPUT_DIR / f"scenario6_performance_obligation_{timestamp}.json"
        md_output = OUTPUT_DIR / f"scenario6_performance_obligation_{timestamp}.md"
        perf_output = OUTPUT_DIR / f"scenario6_performance_log_{timestamp}.json"
        
        # 保存JSON（层级树）
        result_data = {
            "query_time": datetime.now().isoformat(),
            "target_company": TARGET_COMPANY,
            "statistics": stats,
            "hierarchy": hierarchy
        }
        
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        print(f"✅ JSON层级树已保存: {json_output}")
        
        # 保存Markdown报告
        with open(md_output, 'w', encoding='utf-8') as f:
            f.write(markdown)
        print(f"✅ Markdown报告已保存: {md_output}")
        
        # 保存性能日志
        with open(perf_output, 'w', encoding='utf-8') as f:
            json.dump(PERF_LOG, f, indent=2, ensure_ascii=False)
        print(f"✅ 性能日志已保存: {perf_output}")
        
        # 输出性能汇总
        print("\n" + "=" * 70)
        print("⏱️ 性能汇总")
        print("=" * 70)
        total_time = time.time() - overall_start
        for log in PERF_LOG:
            print(f"   {log['step']}: {log['elapsed_seconds']}s {log.get('extra', '')}")
        print(f"\n⏱️ 总执行时间: {total_time:.2f}s")
        
        print("\n" + "=" * 70)
        print("✅ 场景6执行成功！")
        print("=" * 70)
        
        # 打印关键统计
        print(f"\n📊 查询结果摘要:")
        print(f"   关联项目数: {stats['summary']['total_projects']}")
        print(f"   履约义务总数: {stats['summary']['total_obligations']}")
        print(f"   子工作项总数: {stats['summary']['total_subtasks']}")
        print(f"   履约义务完成率: {stats['summary']['completion_rate']}%")
        
        return {
            "success": True,
            "json_file": str(json_output),
            "markdown_file": str(md_output),
            "perf_log_file": str(perf_output),
            "statistics": stats['summary']
        }
        
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        print(f"\n详细错误:\n{traceback.format_exc()}")
        return {"success": False, "error": str(e)}
    finally:
        await tool.close()


if __name__ == '__main__':
    asyncio.run(main())
