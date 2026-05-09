#!/usr/bin/env python3
"""
调试脚本v2：检查登录细节 - 验证码、网络请求、密码
"""
import json
import time
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

CONFIG_PATH = Path(__file__).parent.parent / 'config' / 'oa-config.json'

def main():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("=" * 60)
    print("🔍 登录页面详细调试检查 v2")
    print("=" * 60)
    
    # 获取密码
    result = subprocess.run(
        ['security', 'find-generic-password', '-s', 'openclaw-oa', '-a', config['auth']['username'], '-w'],
        capture_output=True, text=True
    )
    password = result.stdout.strip()
    print(f"\n🔑 密码长度: {len(password)} 字符")
    if password:
        print(f"   密码前3位: *** (已脱敏)")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()
        
        # 监听网络请求
        def log_request(request):
            if 'login' in request.url.lower() or 'auth' in request.url.lower():
                print(f"\n🌐 请求: {request.method} {request.url}")
        
        page.on('request', log_request)
        
        print(f"\n📍 访问登录页: {config['iam_url']}")
        page.goto(config['iam_url'])
        time.sleep(3)
        
        # 检查是否有验证码
        print("\n🔍 检查验证码元素...")
        captcha_selectors = ['#captchaImg', '.captcha-image', '[alt=captcha]', 'img[src*=captcha]']
        for sel in captcha_selectors:
            elem = page.query_selector(sel)
            print(f"   {sel}: {'存在' if elem else '不存在'}")
        
        # 检查错误提示
        error_elem = page.query_selector('.error, .error-msg, .alert-danger')
        if error_elem:
            print(f"\n❌ 错误信息: {error_elem.inner_text()}")
        
        print(f"\n📝 填写用户名: {config['auth']['username']}")
        page.fill('input[type=text]', config['auth']['username'])
        time.sleep(2)
        
        print("🔑 填写密码...")
        page.fill('input[type=password]', password)
        time.sleep(2)
        
        # 截图填写后的状态
        page.screenshot(path='/Users/bangcle/output/oa-screenshots/debug_before_login.png')
        print("📸 登录前截图已保存")
        
        print("🖱️  点击登录按钮...")
        page.click('.login-btn')
        
        # 等待并检查页面状态
        print("\n" + "=" * 60)
        print("⏳ 等待页面响应（20秒...")
        for i in range(20):
            time.sleep(1)
            current_url = page.url
            has_password = page.query_selector('input[type=password]') is not None
            has_login_btn = page.query_selector('.login-btn') is not None
            
            # 检查错误信息
            error_elem = page.query_selector('.error, .error-msg, .alert-danger, .el-message')
            error_text = error_elem.inner_text() if error_elem else "无"
            
            if (i + 1) % 5 == 0:
                print(f"\n[{i+1}s] URL: {current_url}")
                print(f"    密码框: {has_password}, 登录按钮: {has_login_btn}")
                print(f"    错误信息: {error_text}")
                
                page.screenshot(path=f'/Users/bangcle/output/oa-screenshots/debug_login_{i+1}s.png')
            
            if not has_password and not has_login_btn:
                print(f"\n✅ [{i+1}s 密码框和登录按钮已消失！登录成功！")
                break
        
        print("\n" + "=" * 60)
        print("📸 最终截图已保存")
        page.screenshot(path='/Users/bangcle/output/oa-screenshots/debug_login_final.png')
        
        time.sleep(3)
        browser.close()

if __name__ == '__main__':
    main()
