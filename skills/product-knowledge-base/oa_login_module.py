#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OA自动登录模块
支持Cookie持久化，避免重复登录
"""
import asyncio
from playwright.async_api import async_playwright
import json
import os

import os
COOKIE_FILE = os.environ.get('OA_COOKIE_FILE', '/Users/bangcle/.openclaw/workspace/config/oa_cookies.json')

async def login_oab():
    """
    自动登录OA系统
    返回：browser, context, page
    """
    playwright = await async_playwright().start()
    
    browser = await playwright.chromium.launch(
        headless=False,  # 设为True后台运行，False显示浏览器
        slow_mo=1000
    )
    
    context = await browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    
    # 尝试加载已保存的Cookie
    if os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
            await context.add_cookies(cookies)
        print("[INFO] 已加载Cookie")
    
    page = await context.new_page()
    
    # 访问OA
    await page.goto("https://oa.bangcle.com/")
    await asyncio.sleep(3)
    
    # 检查是否需要登录
    if "登录" in await page.title() or "login" in await page.title().lower():
        print("[INFO] 需要登录，请在浏览器中手动完成登录...")
        print("[INFO] 登录完成后按回车继续，脚本将自动保存Cookie")
        input()
        
        # 保存Cookie
        cookies = await context.cookies()
        os.makedirs(os.path.dirname(COOKIE_FILE), exist_ok=True)
        with open(COOKIE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
        print("[INFO] Cookie已保存")
    else:
        print("[INFO] Cookie有效，已自动登录")
    
    return playwright, browser, context, page


async def test_login():
    """测试登录功能"""
    playwright, browser, context, page = await login_oab()
    print(f"当前页面: {await page.title()}")
    await asyncio.sleep(5)
    await browser.close()
    await playwright.stop()


if __name__ == '__main__':
    asyncio.run(test_login())
