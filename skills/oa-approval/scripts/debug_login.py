#!/usr/bin/env python3
"""
调试脚本：检查登录后页面实际状态
"""
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

CONFIG_PATH = Path(__file__).parent.parent / 'config' / 'oa-config.json'

def main():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("=" * 60)
    print("🔍 登录页面调试检查")
    print("=" * 60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print(f"\n📍 访问登录页: {config['iam_url']}")
        page.goto(config['iam_url'])
        time.sleep(3)
        
        print(f"\n📝 填写用户名: {config['auth']['username']}")
        page.fill('input[type=text]', config['auth']['username'])
        time.sleep(1)
        
        print("🔑 填写密码...")
        # 从keychain获取密码
        import subprocess
        result = subprocess.run(
            ['security', 'find-generic-password', '-s', 'openclaw-oa', '-a', config['auth']['username'], '-w'],
            capture_output=True, text=True
        )
        password = result.stdout.strip()
        page.fill('input[type=password]', password)
        time.sleep(1)
        
        print("🖱️  点击登录按钮...")
        page.click('.login-btn')
        
        # 等待并检查页面状态
        print("\n" + "=" * 60)
        print("⏳ 等待页面响应...")
        for i in range(10):
            time.sleep(1)
            current_url = page.url
            has_password = page.query_selector('input[type=password]') is not None
            has_login_btn = page.query_selector('.login-btn') is not None
            
            # 检查是否有门户页面元素
            has_oa_text = page.query_selector(':has-text("OA协同办公")') is not None
            has_app_text = page.query_selector(':has-text("应用")') is not None
            all_text = page.inner_text('body')[:500]
            
            print(f"\n[{i+1}s] URL: {current_url}")
            print(f"    密码框: {has_password}, 登录按钮: {has_login_btn}")
            print(f"    OA文本: {has_oa_text}, 应用文本: {has_app_text}")
            print(f"    页面内容预览: {all_text[:100]}...")
            
            if not has_password and not has_login_btn:
                print("✅ 密码框和登录按钮已消失！登录应该成功了")
                break
        
        print("\n" + "=" * 60)
        print("📸 截图已保存，按回车关闭浏览器...")
        page.screenshot(path='/Users/bangcle/output/oa-screenshots/debug_login_check.png')
        input()
        
        browser.close()

if __name__ == '__main__':
    main()
