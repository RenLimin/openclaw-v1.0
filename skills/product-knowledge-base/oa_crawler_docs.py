#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OA知识中心文档抓取模块
路径：应用中心 - 知识 - 查询文档/知识类文件 - 产品中心
按日期增量抓取
"""
import asyncio
import os
import json
from datetime import datetime
from playwright.async_api import async_playwright

import os
KB_PATH = os.environ.get('KB_PATH', '/Users/bangcle/.openclaw/workspace/training-data/product-kb')
DOWNLOAD_PATH = os.path.join(KB_PATH, 'downloads')

async def crawl_knowledge_docs(cutoff_date="2026-01-01"):
    """
    抓取产品中心知识库文档
    
    Args:
        cutoff_date: 截止日期，只抓取此日期之后更新的文档
    """
    from oa_login_module import login_oab
    
    playwright, browser, context, page = await login_oab()
    
    print(f"[INFO] 开始抓取 {cutoff_date} 之后更新的知识文档")
    
    try:
        # 导航到知识中心
        # 1. 点击"应用中心"
        await page.click("text=应用中心")
        await asyncio.sleep(2)
        
        # 2. 点击"知识"
        await page.click("text=知识")
        await asyncio.sleep(2)
        
        # 3. 点击"查询文档/知识类文件"
        await page.click("text=查询文档")
        await asyncio.sleep(3)
        
        # 4. 进入"产品中心"分类
        await page.click("text=产品中心")
        await asyncio.sleep(3)
        
        # 5. 设置日期筛选
        # TODO: 根据实际页面元素定位日期筛选器
        # await page.fill("[placeholder='开始日期']", cutoff_date)
        
        # 6. 获取文档列表
        # 等待表格加载
        await page.wait_for_selector("table")
        await asyncio.sleep(2)
        
        # 获取所有文档行
        rows = await page.query_selector_all("table tbody tr")
        print(f"[INFO] 找到 {len(rows)} 个文档")
        
        # 创建下载目录
        os.makedirs(DOWNLOAD_PATH, exist_ok=True)
        
        downloaded = []
        
        # 遍历下载
        for i, row in enumerate(rows[:10]):  # 先抓10个测试
            cells = await row.query_selector_all("td")
            if len(cells) < 3:
                continue
                
            doc_name = await cells[0].inner_text()
            update_date = await cells[2].inner_text()
            
            print(f"[INFO] 下载 ({i+1}/10): {doc_name} ({update_date})")
            
            # 点击下载
            download_btn = await cells[-1].query_selector("a:has-text('下载')")
            if download_btn:
                async with page.expect_download() as download_info:
                    await download_btn.click()
                download = await download_info.value
                save_path = os.path.join(DOWNLOAD_PATH, download.suggested_filename)
                await download.save_as(save_path)
                
                downloaded.append({
                    "name": doc_name,
                    "update_date": update_date,
                    "file": save_path,
                    "download_time": datetime.now().isoformat()
                })
        
        print(f"[INFO] 完成下载 {len(downloaded)} 个文档")
        
        # 保存下载记录
        with open(os.path.join(KB_PATH, "download_record.json"), "w", encoding='utf-8') as f:
            json.dump(downloaded, f, ensure_ascii=False, indent=2)
        
        return downloaded
        
    except Exception as e:
        print(f"[ERROR] 抓取失败: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        await browser.close()
        await playwright.stop()


if __name__ == '__main__':
    asyncio.run(crawl_knowledge_docs())
