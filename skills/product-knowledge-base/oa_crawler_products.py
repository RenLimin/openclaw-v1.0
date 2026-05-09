#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OA产品价格表抓取模块
路径：产品研发管理系统 - 产品基本信息管理 - 梆梆_产品价格查询
"""
import asyncio
import os
import json
import pandas as pd
from datetime import datetime
from playwright.async_api import async_playwright

import os
KB_PATH = os.environ.get('KB_PATH', '/Users/bangcle/.openclaw/workspace/training-data/product-kb')

async def crawl_product_prices():
    """
    抓取"梆梆_产品价格查询"界面中的全部产品记录
    """
    from oa_login_module import login_oab
    
    playwright, browser, context, page = await login_oab()
    
    print("[INFO] 开始抓取产品价格表")
    
    try:
        # 导航到产品管理
        # 1. 点击"产品研发管理系统"
        await page.click("text=产品研发管理系统")
        await asyncio.sleep(3)
        
        # 2. 点击"产品基本信息管理"
        await page.click("text=产品基本信息管理")
        await asyncio.sleep(3)
        
        # 3. 找到右侧"梆梆_产品价格查询"iframe
        # 等待iframe加载
        await asyncio.sleep(5)
        
        # 尝试定位iframe
        frames = page.frames
        print(f"[INFO] 当前页面有 {len(frames)} 个iframe")
        
        price_frame = None
        for f in frames:
            if "产品价格" in f.name or "price" in f.name.lower() or "product" in f.name.lower():
                price_frame = f
                break
        
        if not price_frame:
            # 尝试最后一个iframe（通常内容在最后）
            price_frame = frames[-1] if frames else None
        
        if not price_frame:
            print("[ERROR] 未找到产品价格查询iframe")
            return []
        
        print("[INFO] 已定位产品价格查询界面")
        await asyncio.sleep(3)
        
        # 等待表格加载
        await price_frame.wait_for_selector("table")
        await asyncio.sleep(2)
        
        # 获取表格所有行
        rows = await price_frame.query_selector_all("table tbody tr")
        print(f"[INFO] 找到 {len(rows)} 条产品记录")
        
        # 获取表头
        headers = []
        header_row = await price_frame.query_selector("table thead tr")
        if header_row:
            header_cells = await header_row.query_selector_all("th")
            headers = [await h.inner_text() for h in header_cells]
            print(f"[INFO] 表头: {headers}")
        
        # 提取数据
        products = []
        for row in rows:
            cells = await row.query_selector_all("td")
            if len(cells) < len(headers):
                continue
                
            product = {}
            for i, header in enumerate(headers):
                if i < len(cells):
                    product[header] = await cells[i].inner_text()
            products.append(product)
        
        print(f"[INFO] 成功提取 {len(products)} 条产品记录")
        
        # 保存为JSON
        output_file = os.path.join(KB_PATH, "product_prices_latest.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        print(f"[INFO] 产品价格表已保存: {output_file}")
        
        # 保存为Excel
        excel_file = os.path.join(KB_PATH, "产品价格清单.xlsx")
        df = pd.DataFrame(products)
        df.to_excel(excel_file, index=False)
        print(f"[INFO] Excel版本已保存: {excel_file}")
        
        return products
        
    except Exception as e:
        print(f"[ERROR] 产品价格抓取失败: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        await browser.close()
        await playwright.stop()


if __name__ == '__main__':
    asyncio.run(crawl_product_prices())
