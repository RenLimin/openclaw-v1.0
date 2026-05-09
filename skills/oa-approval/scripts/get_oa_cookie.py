#!/usr/bin/env python3
"""
OA Cookie 一键获取脚本
=====================

## 功能说明
只需手动完成一次验证码，即可永久保存登录状态：
1. 自动打开浏览器并填写用户名密码
2. 等待用户手动完成验证码（图片/滑块/点选等）
3. 自动完成 IAM → OA SSO 登录
4. 保存完整 Cookie 和会话状态

## 使用方法
1. 运行脚本：`python3 get_oa_cookie.py`
2. 浏览器自动打开，自动填写用户名密码
3. ⚠️ 手动完成验证码（图片点击、滑块拖动等）
4. 点击"登录"按钮
5. 脚本自动完成后续所有步骤
6. 看到 "✅ Cookie 保存成功" 即可关闭浏览器

## 保存位置
- Cookie 文件: ~/.openclaw/cache/oa_cookies.json
- 会话状态: ~/.openclaw/cache/oa_storage_state.json
- 完整状态: ~/.openclaw/cache/oa_full_state.json

## 有效期
- IAM Token: 约 2 小时
- OA Session: 约 24 小时
- 过期后重新运行本脚本即可

作者: Ella 🦊
创建时间: 2026-04-29
"""

import json
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# 配置
CONFIG = {
    'iam_url': 'https://iam.bangcle.com',
    'username': 'limin.ren',
    'keychain_service': 'oa-password',
    'jump_api': '/api/application/apps/jumpSystem?appid=9',
    'appid': '9',
}

# 保存路径
CACHE_DIR = Path.home() / '.openclaw' / 'cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

COOKIES_PATH = CACHE_DIR / 'oa_cookies.json'
STORAGE_STATE_PATH = CACHE_DIR / 'oa_storage_state.json'
FULL_STATE_PATH = CACHE_DIR / 'oa_full_state.json'


def get_password_from_keychain() -> str:
    """从 macOS Keychain 获取密码"""
    import subprocess
    result = subprocess.run([
        'security', 'find-generic-password',
        '-s', CONFIG['keychain_service'],
        '-w'
    ], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"\n❌ 无法从 Keychain 获取密码")
        print(f"   Service: {CONFIG['keychain_service']}")
        print(f"\n📝 请先添加密码到 Keychain:")
        print(f"   security add-generic-password -s '{CONFIG['keychain_service']}' -a 'oa' -w '你的密码'")
        sys.exit(1)
    return result.stdout.strip()


def main():
    print("\n" + "=" * 70)
    print("🦊 OA Cookie 一键获取工具")
    print("=" * 70)
    print("\n📋 执行步骤:")
    print("   1. 自动打开浏览器并填写用户名密码")
    print("   2. ⚠️ 手动完成验证码（图片/滑块/点选）")
    print("   3. 点击'登录'按钮")
    print("   4. 脚本自动完成后续所有步骤")
    print("   5. 保存 Cookie 和会话状态")
    print("\n" + "-" * 70 + "\n")

    password = get_password_from_keychain()
    print("✅ 从 Keychain 获取密码成功")

    with sync_playwright() as p:
        print("🚀 启动浏览器...")
        browser = p.chromium.launch(
            headless=False,  # 必须显示浏览器，方便手动完成验证码
            args=['--disable-blink-features=AutomationControlled'],
            slow_mo=500,  # 减慢操作速度，更像人类
        )

        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        page = context.new_page()

        # Step 1: 访问 IAM 登录页面
        print(f"\n📄 Step 1/5: 访问 IAM 登录页面")
        page.goto(CONFIG['iam_url'], wait_until='networkidle', timeout=30000)
        time.sleep(2)

        # Step 2: 自动填写用户名和密码
        print(f"\n✍️  Step 2/5: 自动填写用户名密码")

        # 填写用户名 - 尝试多种选择器
        username_selectors = ['#username', '[name=username]', '.username-input', 'input[type=text]']
        username_filled = False
        for selector in username_selectors:
            try:
                page.wait_for_selector(selector, timeout=1000, state='visible')
                page.fill(selector, CONFIG['username'])
                print(f"   ✅ 用户名已填写: {CONFIG['username']}")
                username_filled = True
                break
            except Exception:
                continue

        if not username_filled:
            print("   ⚠️  未能自动填写用户名，请手动填写")

        time.sleep(0.5)

        # 填写密码 - 尝试多种选择器
        password_selectors = ['#password', '[name=password]', '.password-input', 'input[type=password]']
        password_filled = False
        for selector in password_selectors:
            try:
                page.wait_for_selector(selector, timeout=1000, state='visible')
                page.fill(selector, password)
                print(f"   ✅ 密码已填写")
                password_filled = True
                break
            except Exception:
                continue

        if not password_filled:
            print("   ⚠️  未能自动填写密码，请手动填写")

        # Step 3: 等待用户完成验证码并登录
        print(f"\n⏳ Step 3/5: 等待手动完成验证码...")
        print("   ┌─────────────────────────────────────────────────┐")
        print("   │  ⚠️  请在浏览器中:                               │")
        print("   │     1. 完成验证码（图片点击/滑块拖动等）         │")
        print("   │     2. 点击'登录'按钮                           │")
        print("   │     3. 等待页面跳转到 IAM 主页                   │")
        print("   └─────────────────────────────────────────────────┘")
        print("\n   脚本会自动检测登录成功...\n")

        # 等待登录成功 - 检测 IAM 主页
        login_success = False
        start_time = time.time()
        timeout = 120  # 2 分钟超时

        while time.time() - start_time < timeout:
            current_url = page.url
            # 检测是否已进入主页
            if ('home' in current_url or 'index' in current_url) and 'login' not in current_url.lower():
                # 再验证一下页面内容
                try:
                    page.wait_for_selector('.app-list, [class*=card], [class*=application]', timeout=3000, state='visible')
                    login_success = True
                    print(f"   ✅ 检测到登录成功！")
                    print(f"   📍 当前页面: {current_url}")
                    break
                except Exception:
                    pass
            time.sleep(1)

        if not login_success:
            print(f"\n❌ 登录超时，请检查网络或重试")
            browser.close()
            sys.exit(1)

        time.sleep(3)  # 等待页面完全加载

        # Step 4: 调用 jumpSystem API 获取 OA SSO URL
        print(f"\n🔗 Step 4/5: 获取 OA SSO 跳转链接")

        jump_result = page.evaluate("""
        async () => {
            try {
                const state = JSON.parse(localStorage.getItem('GlobalState') || '{}');
                const token = state.token;
                if (!token) {
                    return {success: false, error: '未在 localStorage 找到 token'};
                }

                const resp = await fetch('/api/application/apps/jumpSystem?appid=9', {
                    method: 'GET',
                    headers: {
                        'x-access-token': token,
                        'noLoading': 'true'
                    }
                });
                const data = await resp.json();
                return {success: true, data: data};
            } catch(e) {
                return {success: false, error: e.message};
            }
        }
        """)

        if not jump_result.get('success'):
            print(f"   ❌ 获取跳转链接失败: {jump_result.get('error')}")
            browser.close()
            sys.exit(1)

        oa_url = jump_result.get('data', {}).get('data', '')
        if not oa_url:
            print(f"   ❌ 跳转链接为空")
            print(f"   完整响应: {jump_result}")
            browser.close()
            sys.exit(1)

        print(f"   ✅ 获取 OA 跳转 URL 成功")
        print(f"   🔗 URL: {oa_url[:80]}...")

        # Step 5: 访问 OA SSO URL，完成登录
        print(f"\n🌐 Step 5/5: 访问 OA，完成 SSO 登录")

        page.goto(oa_url, wait_until='networkidle', timeout=60000)
        time.sleep(5)

        # 验证是否成功进入 OA
        current_url = page.url
        if 'oa.bangcle.com' in current_url and 'login' not in current_url.lower():
            print(f"   ✅ 成功进入 OA 系统！")
            print(f"   📍 当前页面: {current_url}")
        else:
            print(f"   ⚠️  可能未成功进入 OA")
            print(f"   📍 当前页面: {current_url}")
            print(f"   请检查浏览器中的页面状态")

        time.sleep(3)

        # ============================================
        # 保存 Cookie 和会话状态
        # ============================================
        print("\n" + "-" * 70)
        print("💾 保存 Cookie 和会话状态...")

        # 方案 B: 获取完整 Cookie
        cookies = context.cookies()
        with open(COOKIES_PATH, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)
        print(f"   ✅ 完整 Cookie 已保存 ({len(cookies)} 个)")
        print(f"      📄 {COOKIES_PATH}")

        # 方案 C: Storage State 持久化（推荐！）
        context.storage_state(path=str(STORAGE_STATE_PATH))
        print(f"   ✅ Storage State 已保存")
        print(f"      📄 {STORAGE_STATE_PATH}")

        # 方案 A: 从 localStorage 提取 token（额外保存）
        local_storage_data = page.evaluate("() => { return JSON.stringify(localStorage); }")
        full_state = {
            'timestamp': time.time(),
            'cookies': cookies,
            'localStorage': json.loads(local_storage_data),
            'url': page.url
        }
        with open(FULL_STATE_PATH, 'w', encoding='utf-8') as f:
            json.dump(full_state, f, indent=2, ensure_ascii=False)
        print(f"   ✅ 完整状态已保存")
        print(f"      📄 {FULL_STATE_PATH}")

        # 显示关键 Cookie 信息
        print("\n" + "-" * 70)
        print("📋 关键 Cookie 信息:")
        for c in cookies:
            domain = c.get('domain', '')
            if 'bangcle' in domain:
                print(f"   • {c['name']:25s} domain={domain:20s} httpOnly={c.get('httpOnly', False)}")

        print("\n" + "=" * 70)
        print("✅ Cookie 获取完成！")
        print("=" * 70)
        print("\n📝 使用说明:")
        print("   其他脚本可以直接加载以下文件恢复会话:")
        print(f"   - {STORAGE_STATE_PATH}")
        print(f"   - {COOKIES_PATH}")
        print("\n⏰ 有效期提示:")
        print("   - IAM Token: 约 2 小时")
        print("   - OA Session: 约 24 小时")
        print("   - 过期后重新运行本脚本即可")
        print("\n👋 可以关闭浏览器了\n")

        # 等待用户确认后关闭
        input("按回车键退出...")
        browser.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，退出")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
