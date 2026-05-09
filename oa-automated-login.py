#!/usr/bin/env python3
"""
OA 完全自动化登录脚本 - 无需验证码
基于研究结论: 正常登录下 IAM 不触发验证码
"""
import asyncio
import random
import json
import os
from playwright.async_api import async_playwright

class OAAutoLogin:
    def __init__(self, cookie_path='output/oa-cookies-latest.json'):
        self.cookie_path = cookie_path
        self.username = 'limin.ren'
        self.password = 'June-123'
        
    async def human_type(self, element, text, delay_range=(50, 150)):
        """模拟人类打字速度，避免被检测"""
        for char in text:
            await element.type(char, delay=random.randint(*delay_range))
            await asyncio.sleep(random.uniform(0.05, 0.15))
    
    async def create_browser_context(self, playwright):
        """创建带反检测的浏览器上下文"""
        browser = await playwright.chromium.launch(
            headless=False,
            slow_mo=500,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-infobars',
                '--no-sandbox',
                '--start-maximized',
            ]
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            viewport={'width': 1440, 'height': 900},
            locale='zh-CN',
            timezone_id='Asia/Shanghai'
        )
        
        # 注入 stealth 脚本
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});
            window.chrome = {runtime: {}};
        """)
        
        return browser, context
    
    async def check_captcha(self, page):
        """检查是否出现验证码"""
        captcha_indicators = [
            'iframe[src*="captcha"]',
            '.geetest_slider_button',
            '.slider-verify',
            '[class*="captcha"]',
            'canvas',
            'text=/拖动|滑块|验证码/'
        ]
        
        for selector in captcha_indicators:
            try:
                if await page.locator(selector).count() > 0:
                    print(f"⚠️  检测到验证码元素: {selector}")
                    return True
            except:
                pass
        return False
    
    async def login(self):
        """执行完整 IAM -> OA 登录流程"""
        print("=" * 60)
        print("🚀 启动 OA 自动化登录")
        print("=" * 60)
        
        async with async_playwright() as p:
            browser, context = await self.create_browser_context(p)
            page = await context.new_page()
            
            try:
                # ========== 步骤 1: IAM 登录 ==========
                print("\n📝 步骤 1: 访问 IAM 登录页面")
                await page.goto('https://iam.bangcle.com/')
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(2)
                
                print("   ✅ 页面加载完成")
                
                # 填写用户名
                username_input = page.locator('input[type="text"]').first
                print(f"   输入用户名: {self.username}")
                await self.human_type(username_input, self.username)
                await asyncio.sleep(random.uniform(0.3, 0.8))
                
                # 填写密码
                password_input = page.locator('input[type="password"]').first
                print("   输入密码: ******")
                await self.human_type(password_input, self.password)
                await asyncio.sleep(random.uniform(0.5, 1.2))
                
                # 检查验证码
                has_captcha = await self.check_captcha(page)
                if has_captcha:
                    print("⚠️  检测到验证码触发! 请人工完成验证")
                    print("   验证完成后脚本将继续...")
                    # 等待人工处理或集成滑块破解
                    await asyncio.sleep(60)
                
                # 点击登录
                print("\n🔘 步骤 2: 点击登录按钮")
                login_btn = page.locator('button:has-text("登录")').first
                await login_btn.click()
                
                # 等待登录完成
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(3)
                
                if 'home' in page.url or 'index' in page.url:
                    print("   ✅ IAM 登录成功!")
                    print(f"   📍 当前 URL: {page.url}")
                else:
                    print(f"   ⚠️  登录后 URL: {page.url}")
                    # 再次检查验证码
                    has_captcha = await self.check_captcha(page)
                    if has_captcha:
                        print("   ❌ 登录触发了验证码，需要手动处理")
                        return False, None
                
                # ========== 步骤 3: 跳转 OA ==========
                print("\n🌐 步骤 3: 跳转 OA 系统")
                await page.goto('https://oa.bangcle.com/')
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(5)
                
                print(f"   📍 OA URL: {page.url}")
                
                # 检查是否成功进入 OA
                page_text = await page.locator('body').text_content()
                if 'wui' in page.url or '待办' in page_text or '流程' in page_text:
                    print("   ✅ OA SSO 登录成功!")
                else:
                    print("   ⚠️  OA 可能需要额外认证")
                
                # ========== 步骤 4: 保存 Cookie ==========
                print("\n🍪 步骤 4: 保存浏览器 Cookie")
                cookies = await context.cookies()
                print(f"   共获取 {len(cookies)} 个 Cookie")
                
                os.makedirs(os.path.dirname(self.cookie_path), exist_ok=True)
                with open(self.cookie_path, 'w') as f:
                    json.dump(cookies, f, indent=2, ensure_ascii=False)
                
                print(f"   ✅ Cookie 已保存到: {self.cookie_path}")
                
                # ========== 完成 ==========
                print("\n" + "=" * 60)
                print("🎉 登录流程完成!")
                print("=" * 60)
                
                # 保持浏览器打开 10 秒供检查
                await asyncio.sleep(10)
                
                return True, cookies
                
            except Exception as e:
                print(f"\n❌ 登录过程出错: {e}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(10)
                return False, None
            
            finally:
                await browser.close()
    
    async def verify_cookie(self, cookies):
        """验证 Cookie 是否有效"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            await context.add_cookies(cookies)
            
            page = await context.new_page()
            await page.goto('https://oa.bangcle.com/')
            await asyncio.sleep(5)
            
            url = page.url
            await browser.close()
            
            return 'wui' in url or '待办' in await page.locator('body').text_content()

async def main():
    login = OAAutoLogin()
    success, cookies = await login.login()
    
    if success and cookies:
        print("\n✅ 登录成功，后续任务可以继续使用保存的 Cookie")
    else:
        print("\n❌ 登录失败，请检查日志")

if __name__ == '__main__':
    asyncio.run(main())
