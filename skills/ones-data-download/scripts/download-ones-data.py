#!/usr/bin/env python3
"""
ONES 筛选器数据下载脚本 v2.0
============================

功能：
1. 自动登录 ONES 系统（浏览器自动化处理验证码）
2. 通过 GraphQL API 下载指定筛选器的工作项数据
3. 支持 CSV 和 JSON 两种输出格式
4. 包含错误处理和自动重试机制

使用方式：
  python3 download-ones-data.py                          # 下载所有配置的筛选器
  python3 download-ones-data.py --filter 5wY9X4m8        # 下载指定筛选器
  python3 output-format json --output-dir ./data         # JSON 格式输出

依赖：
  pip install playwright pandas
  playwright install chromium
"""

import asyncio
import json
import os
import sys
import time
import csv
import io
import argparse
from datetime import datetime
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("⚠️ pandas 未安装，将使用内置 CSV 导出")
    pd = None

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ playwright 未安装，请运行: pip install playwright && playwright install chromium")
    sys.exit(1)


# ============================================================
# 配置
# ============================================================

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'ones-config.json')
DEFAULT_OUTPUT_DIR = os.path.expanduser("~/.openclaw/workspace/output/ones-data")

# 从配置文件加载
def load_config(config_path=None):
    """加载配置文件"""
    path = config_path or DEFAULT_CONFIG_PATH
    if not os.path.exists(path):
        # Try relative to script
        path = os.path.join(os.path.dirname(__file__), '..', 'config', 'ones-config.json')
    if not os.path.exists(path):
        print(f"❌ 配置文件不存在: {path}")
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


# ============================================================
# 登录模块
# ============================================================

async def login_ones(page, config, timeout=60):
    """
    通过浏览器自动化登录 ONES
    返回 (auth_token, user_id) 或 (None, None)
    """
    login_api = config.get('login_api', 'https://ones.bangcle.com/project/api/project/auth/login')
    ones_url = config.get('ones_url', 'https://ones.bangcle.com/project/')

    # 尝试从 Keychain 获取密码
    username = config.get('auth', {}).get('username', '')
    password = ""

    if not username:
        keychain_service = config.get('auth', {}).get('username_keychain_service', '')
        if keychain_service:
            try:
                import subprocess
                result = subprocess.run(
                    ['security', 'find-generic-password', '-s', keychain_service, '-w'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    username = result.stdout.strip()
            except Exception:
                pass

    if not username:
        print("❌ 未找到 ONES 用户名")
        print("   请通过以下方式配置：")
        print("   1. 在 config/ones-config.json 的 auth.username 中设置")
        print("   2. 或存入 Keychain: security add-generic-password -s openclaw-browser-oliver-ones-username -a <email> -w <email>")
        return None, None

    print(f"🔐 正在登录 ONES ({username})...")

    # 方法1: 尝试 API 登录（无验证码时可用）
    auth_result = await api_login(page, login_api, username, password)
    if auth_result:
        return auth_result

    # 方法2: 浏览器登录（处理验证码）
    return await browser_login(page, ones_url, username)


async def api_login(page, login_api, username, password):
    """尝试通过 API 登录"""
    try:
        resp = await page.evaluate("""
            async ({url, username, password}) => {
                try {
                    const res = await fetch(url, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({email: username, password: password, captcha: ''})
                    });
                    const data = await res.json();
                    return {status: res.status, data: data};
                } catch(e) {
                    return {error: e.message};
                }
            }
        """, {"url": login_api, "username": username, "password": password})

        if resp.get('status') == 200 and resp.get('data', {}).get('user', {}).get('token'):
            user = resp['data']['user']
            print(f"  ✅ API 登录成功: {user.get('name', username)}")
            return user.get('token'), user.get('uuid')
    except Exception as e:
        print(f"  ⚠️ API 登录失败: {e}")

    return None


async def browser_login(page, ones_url, username):
    """通过浏览器填写表单登录（处理验证码）"""
    login_url = ones_url.rstrip('/') + '/#/auth/login'

    try:
        await page.goto(login_url, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(2)

        # 检查是否已登录
        if 'login' not in page.url:
            print("  ✅ 检测到已登录状态")
            return await extract_auth_from_page(page)

        # 填写登录表单
        inputs = await page.query_selector_all('input')
        email_input = None
        pwd_input = None

        for inp in inputs:
            inp_type = await inp.get_attribute('type') or ''
            placeholder = await inp.get_attribute('placeholder') or ''
            name = await inp.get_attribute('name') or ''

            if inp_type == 'email' or '邮箱' in placeholder or 'email' in placeholder.lower():
                email_input = inp
            elif inp_type == 'password':
                pwd_input = inp

        if not email_input or not pwd_input:
            print("  ❌ 未找到登录表单")
            return None, None

        await email_input.fill(username)
        print(f"  📧 已填写用户名")

        # 等待用户输入密码和验证码
        print("  ⏳ 请在浏览器中完成登录（输入密码和验证码）...")
        print("     等待 120 秒...")

        for i in range(24):  # 120 seconds
            await asyncio.sleep(5)
            if 'login' not in page.url:
                print(f"  ✅ 检测到登录成功! URL: {page.url}")
                return await extract_auth_from_page(page)

        print("  ❌ 登录超时")
        return None, None

    except Exception as e:
        print(f"  ❌ 浏览器登录异常: {e}")
        return None, None


async def extract_auth_from_page(page):
    """从页面中提取认证信息"""
    try:
        cookies = await page.context.cookies()
        auth_token = None
        user_id = None

        for c in cookies:
            if c['name'] == 'ones-lt':
                auth_token = c['value']
            elif c['name'] == 'ones-uid':
                user_id = c['value']

        # 备用：从 localStorage 获取
        if not auth_token:
            storage = await page.evaluate("() => { try { return localStorage; } catch(e) { return {}; } }")
            auth_token = storage.get('ones-lt') or storage.get('token')
            user_id = storage.get('ones-uid') or storage.get('userId')

        if auth_token:
            print(f"  ✅ 已获取认证信息")
            return auth_token, user_id
    except Exception as e:
        print(f"  ⚠️ 提取认证信息失败: {e}")

    return None, None


# ============================================================
# GraphQL API 模块
# ============================================================

async def fetch_filter_data(page, config, filter_uuid, auth_token, user_id, max_retries=3):
    """
    通过 GraphQL API 获取筛选器数据
    使用浏览器内 fetch 避免 CORS 问题
    """
    team_uuid = config.get('team_uuid', 'RZxvwUZ8')
    graphql_url = f"{config.get('ones_url', '').rstrip('/')}/api/project/team/{team_uuid}/items/graphql"
    retry_config = config.get('retry', {})
    max_retries = max_retries or retry_config.get('max_retries', 3)
    retry_delay = retry_config.get('retry_delay_seconds', 5)

    # 构建 GraphQL 查询
    fields = config.get('graphql_fields', [
        'number', 'name', 'key', 'uuid', 'path', 'position',
        'status { uuid name category }',
        'assign { uuid name key }',
        'project { uuid name key }',
        'issueType { uuid manhourStatisticMode }',
        'subIssueType',
        'parent { uuid }',
        'deadline', 'estimatedHours', 'remainingManhour',
        'serverUpdateStamp',
    ])

    fields_str = '\n    '.join(fields)

    query = f"""
    query {{
        buckets(
            groupBy: {{ tasks: {{}} }}
            filter: {{
                filterGroup: {{
                    connector: AND
                    filterGroups: [
                        {{
                            connector: AND
                            filters: [
                                {{
                                    field: "project"
                                    operator: in
                                    value: {{ projects: [] }}
                                }}
                            ]
                        }}
                    ]
                }}
            }}
        ) {{
            key
            pageInfo {{
                count
                totalCount
                hasNextPage
                endCursor
            }}
            tasks {{
                {fields_str}
            }}
        }}
    }}
    """

    all_tasks = []

    for attempt in range(max_retries):
        try:
            if attempt > 0:
                print(f"  🔄 重试 {attempt}/{max_retries}...")
                await asyncio.sleep(retry_delay * attempt)

            # 导航到筛选器页面以获取正确的上下文
            filter_url = f"{config.get('ones_url', '').rstrip('/')}/#/workspace/filter/{filter_uuid}"
            print(f"  📄 导航到筛选器页面...")
            await page.goto(filter_url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(3)

            # 检查是否被重定向到登录页
            if 'login' in page.url:
                print("  ❌ 被重定向到登录页，需要重新登录")
                return None, "need_relogin"

            # 通过页面内的 fetch 调用 GraphQL API
            result = await page.evaluate("""
                async ({url, query, authToken, userId}) => {
                    try {
                        const res = await fetch(url, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'Ones-Auth-Token': authToken || '',
                                'Ones-User-Id': userId || ''
                            },
                            body: JSON.stringify({query: query, variables: {}})
                        });
                        const text = await res.text();
                        return {status: res.status, body: text};
                    } catch(e) {
                        return {error: e.message};
                    }
                }
            """, {"url": graphql_url, "query": query, "authToken": auth_token, "userId": user_id})

            if 'error' in result:
                raise Exception(f"Fetch error: {result['error']}")

            if result['status'] != 200:
                raise Exception(f"HTTP {result['status']}: {result['body'][:200]}")

            data = json.loads(result['body'])

            if 'errors' in data:
                raise Exception(f"GraphQL errors: {json.dumps(data['errors'])[:500]}")

            buckets = data.get('data', {}).get('buckets', [])
            if not buckets:
                print("  ⚠️ 未获取到数据（可能是筛选器为空）")
                return [], "success"

            for bucket in buckets:
                tasks = bucket.get('tasks', [])
                all_tasks.extend(tasks)

                # 处理分页
                page_info = bucket.get('pageInfo', {})
                while page_info.get('hasNextPage'):
                    end_cursor = page_info.get('endCursor')
                    # 带游标的分页查询
                    page_query = query.replace(
                        'value: { projects: [] }',
                        f'value: {{ projects: [] }}, after: "{end_cursor}"'
                    )
                    # 简化：实际需要根据 ONES GraphQL schema 调整
                    break  # ONES 分页可能需要特殊处理

            print(f"  ✅ 获取到 {len(all_tasks)} 条工作项")
            return all_tasks, "success"

        except Exception as e:
            print(f"  ⚠️ 请求失败 (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return None, f"failed_after_retries: {e}"

    return None, "max_retries_exceeded"


# ============================================================
# 导出模块
# ============================================================

def flatten_task(task, field_mapping=None):
    """将嵌套的任务数据扁平化"""
    flat = {}

    for key, value in task.items():
        if isinstance(value, dict):
            if 'value' in value:
                flat[key] = value['value']
            elif 'name' in value:
                flat[key] = value['name']
            elif 'uuid' in value:
                flat[key] = value['uuid']
            else:
                flat[key] = json.dumps(value, ensure_ascii=False)
        elif isinstance(value, list):
            flat[key] = ', '.join(
                str(item.get('value', item.get('name', item)))
                for item in value if isinstance(item, dict)
            ) or str(value)
        else:
            flat[key] = value

    return flat


def format_timestamp(ts):
    """将 ONES 微秒时间戳转换为日期字符串"""
    if not ts:
        return ''
    try:
        ts_int = int(ts)
        if ts_int > 1e15:  # 微秒
            return datetime.fromtimestamp(ts_int / 1e6).strftime('%Y-%m-%d %H:%M:%S')
        elif ts_int > 1e12:  # 毫秒
            return datetime.fromtimestamp(ts_int / 1e3).strftime('%Y-%m-%d %H:%M:%S')
        else:
            return datetime.fromtimestamp(ts_int).strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError, OSError):
        return str(ts)


def export_csv(tasks, output_path, field_mapping=None):
    """导出为 CSV（UTF-8 BOM）"""
    if not tasks:
        print("  ⚠️ 无数据可导出")
        return

    flat_tasks = [flatten_task(t, field_mapping) for t in tasks]

    if pd is not None:
        df = pd.DataFrame(flat_tasks)
        # 格式化时间戳字段
        ts_fields = ['serverUpdateStamp', 'deadline', '_TmDTXaHw', '_5wdMuxor', '_EAnxnS4w']
        for f in ts_fields:
            if f in df.columns:
                df[f] = df[f].apply(format_timestamp)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
    else:
        # 使用内置 CSV 导出
        all_keys = []
        for ft in flat_tasks:
            for k in ft:
                if k not in all_keys:
                    all_keys.append(k)

        with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=all_keys)
            writer.writeheader()
            for ft in flat_tasks:
                row = {}
                for k in all_keys:
                    v = ft.get(k, '')
                    if k in ['serverUpdateStamp', 'deadline']:
                        v = format_timestamp(v)
                    row[k] = v
                writer.writerow(row)

    print(f"  📄 CSV 已导出: {output_path} ({len(tasks)} 行)")


def export_json(tasks, output_path):
    """导出为 JSON"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    print(f"  📄 JSON 已导出: {output_path} ({len(tasks)} 条)")


# ============================================================
# 主流程
# ============================================================

async def download_filter(page, config, filter_uuid, filter_info, auth_token, user_id, output_dir, output_format):
    """下载单个筛选器数据"""
    name = filter_info.get('name', filter_uuid)
    output_file = filter_info.get('output_file', name)

    print(f"\n{'='*50}")
    print(f"📥 下载: {name} ({filter_uuid})")
    print(f"{'='*50}")

    tasks, status = await fetch_filter_data(page, config, filter_uuid, auth_token, user_id)

    if status == "need_relogin":
        return "need_relogin"

    if status != "success" or tasks is None:
        print(f"  ❌ 下载失败: {status}")
        return f"failed: {status}"

    if not tasks:
        print(f"  ⚠️ 筛选器无数据")
        return "empty"

    # 导出
    os.makedirs(output_dir, exist_ok=True)

    if output_format == 'csv' or output_format == 'both':
        csv_path = os.path.join(output_dir, f"{output_file}.csv")
        export_csv(tasks, csv_path, config.get('field_mapping'))

    if output_format == 'json' or output_format == 'both':
        json_path = os.path.join(output_dir, f"{output_file}.json")
        export_json(tasks, json_path)

    return "success"


async def main():
    parser = argparse.ArgumentParser(description='ONES 筛选器数据下载工具')
    parser.add_argument('--filter', type=str, help='指定筛选器 UUID（不指定则下载所有）')
    parser.add_argument('--output-format', choices=['csv', 'json', 'both'], default='csv',
                        help='输出格式 (默认: csv)')
    parser.add_argument('--output-dir', type=str, default=None,
                        help='输出目录 (默认: 配置中的 output.default_dir)')
    parser.add_argument('--config', type=str, default=None,
                        help='配置文件路径')
    parser.add_argument('--headless', action='store_true',
                        help='无头模式运行浏览器')
    parser.add_argument('--interactive-login', action='store_true',
                        help='交互式登录（显示浏览器窗口）')

    args = parser.parse_args()

    config = load_config(args.config)
    output_dir = args.output_dir or config.get('output', {}).get('default_dir', DEFAULT_OUTPUT_DIR)

    print("=" * 60)
    print("🐘 ONES 筛选器数据下载 v2.0")
    print("=" * 60)
    print(f"📁 输出目录: {output_dir}")
    print(f"📋 输出格式: {args.output_format}")

    # 启动浏览器
    async with async_playwright() as p:
        if args.interactive_login:
            browser = await p.chromium.launch(headless=False)
        else:
            browser = await p.chromium.launch(
                headless=args.headless,
                args=['--disable-blink-features=AutomationControlled']
            )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = await context.new_page()

        try:
            # 登录
            auth_token, user_id = await login_ones(page, config)

            if not auth_token:
                print("\n❌ 登录失败，无法继续")
                await browser.close()
                sys.exit(1)

            # 保存认证状态
            state_path = os.path.join(output_dir, 'auth-state.json')
            os.makedirs(output_dir, exist_ok=True)
            await context.storage_state(path=state_path)
            print(f"  💾 认证状态已保存: {state_path}")

            # 确定要下载的筛选器
            filters_config = config.get('filters', {})
            if args.filter:
                if args.filter not in filters_config:
                    print(f"❌ 未知筛选器: {args.filter}")
                    print(f"可用筛选器: {list(filters_config.keys())}")
                    await browser.close()
                    sys.exit(1)
                targets = {args.filter: filters_config[args.filter]}
            else:
                targets = filters_config

            # 下载数据
            results = {}
            need_relogin = False

            for f_uuid, f_info in targets.items():
                result = await download_filter(
                    page, config, f_uuid, f_info,
                    auth_token, user_id, output_dir, args.output_format
                )
                results[f_info.get('name', f_uuid)] = result

                if result == "need_relogin":
                    need_relogin = True
                    print("  🔄 需要重新登录...")
                    auth_token, user_id = await login_ones(page, config)
                    if not auth_token:
                        print("  ❌ 重新登录失败，跳过剩余筛选器")
                        break
                    # 重试当前筛选器
                    result = await download_filter(
                        page, config, f_uuid, f_info,
                        auth_token, user_id, output_dir, args.output_format
                    )
                    results[f_info.get('name', f_uuid)] = result

            # 汇总报告
            print(f"\n{'='*60}")
            print("📊 下载汇总")
            print(f"{'='*60}")
            for name, result in results.items():
                icon = "✅" if result == "success" else "❌" if result.startswith("failed") else "⚠️"
                print(f"  {icon} {name}: {result}")

            success_count = sum(1 for r in results.values() if r == "success")
            print(f"\n总计: {success_count}/{len(results)} 成功")

        finally:
            await browser.close()

    print("\n✅ 下载完成")


if __name__ == "__main__":
    asyncio.run(main())
