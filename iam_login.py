import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=['--no-sandbox', '--disable-extensions'])
        page = await browser.new_page()
        await page.goto('https://iam.bangcle.com')
        print("✅ 全新独立Chrome已启动，IAM登录页已打开")
        print("ℹ️  请手动验证登录，验证完成后可以关闭浏览器")
        await asyncio.sleep(180)  # 等待3分钟
        await browser.close()

asyncio.run(main())
