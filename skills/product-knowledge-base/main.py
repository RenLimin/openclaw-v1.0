#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品知识库查询主程序
支持：按产品查询功能、按产品查询部署说明、按产品查询售后、按场景跨产品查询
"""

import json
import os
import sys
from pathlib import Path

KB_PATH = os.environ.get('KB_PATH', '/Users/bangcle/.openclaw/workspace/training-data/product-kb')

# 产品线映射
PRODUCT_LINES = {
    '安全监测线': ['移动应用安全监测', 'API安全平台', '全渠道应用安全监测', '端到端安全监测'],
    '安全检测线': ['应用安全测评', '移动应用合规', '固件安全检测', 'SDK安全检测'],
    '安全保护线': ['Android应用加固', 'iOS应用加固', 'H5应用加固', '小程序加固', 'SDK加固', '安全键盘', '防界面劫持', '密钥白盒', '通信协议保护', '鸿蒙应用加固', '物联网应用加固', '智能手表加固'],
    '内容安全线': ['内容安全检测', '内容审核', '舆情监测'],
    '安全服务线': ['安全评估', '渗透测试', '等保咨询', '应急响应', '安全培训', '合规咨询', '移动威胁感知运营'],
    '物联网服务线': ['汽车信息安全测试', '物联网安全测评', '车载安全检测']
}

def load_json_file(filename):
    """加载JSON文件"""
    filepath = os.path.join(KB_PATH, filename)
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def search_product_by_name(keyword):
    """按产品名称搜索"""
    products = load_json_file('product_list.json')
    if not products:
        return []
    
    results = []
    for sheet_name, items in products.items():
        for item in items:
            # 搜索产品名称、描述等字段
            search_text = ' '.join([
                str(item.get('产品服务名称（浏览）', '')),
                str(item.get('服务描述', '')),
                str(item.get('货物或应税服务名称', '')),
                str(item.get('所属产品', ''))
            ])
            if keyword.lower() in search_text.lower():
                results.append({
                    '产品线': item.get('产品线类别', ''),
                    '产品名称': item.get('产品服务名称（浏览）', ''),
                    '型号': item.get('产品服务型号', ''),
                    '单价': item.get('产品服务单价（元）', ''),
                    '描述': item.get('服务描述', ''),
                    '状态': item.get('启用状态', '')
                })
    return results

def search_implementation_steps(keyword=''):
    """搜索实施步骤"""
    steps = load_json_file('implementation_steps.json')
    if not steps:
        return []
    
    results = []
    for sheet_name, items in steps.items():
        for item in items:
            if not keyword or keyword.lower() in str(item.get('步骤', '')).lower() or keyword.lower() in str(item.get('阶段', '')).lower():
                results.append({
                    '阶段': item.get('阶段', ''),
                    '步骤': item.get('步骤', ''),
                    '完成标准': item.get('完成标准', ''),
                    '输入': item.get('输入', ''),
                    '输出': item.get('输出', '')
                })
    return results

def search_document_content(line_name, keyword):
    """在产品线文档中搜索内容"""
    docs = load_json_file('product_service_docs.json')
    if not docs:
        return []
    
    results = []
    
    # 确定要搜索的产品线
    lines_to_search = []
    if line_name:
        for line in PRODUCT_LINES.keys():
            if line_name.lower() in line.lower():
                lines_to_search.append(line)
    else:
        lines_to_search = list(PRODUCT_LINES.keys())
    
    for line in lines_to_search:
        if line not in docs:
            continue
        for filename, doc_info in docs[line].items():
            content = doc_info.get('content', '')
            if keyword.lower() in content.lower():
                # 提取关键词前后的上下文
                idx = content.lower().find(keyword.lower())
                start = max(0, idx - 100)
                end = min(len(content), idx + 300)
                context = content[start:end].replace('\n', ' ')
                
                results.append({
                    '产品线': line,
                    '文档': filename,
                    '上下文': f'...{context}...'
                })
                if len(results) >= 10:  # 限制返回数量
                    return results
    
    return results

def get_product_list_by_line(line_name):
    """按产品线获取产品列表"""
    products = load_json_file('product_list.json')
    if not products:
        return []
    
    results = []
    for sheet_name, items in products.items():
        for item in items:
            if item.get('产品线类别', '') == line_name:
                results.append({
                    '产品名称': item.get('产品服务名称（浏览）', ''),
                    '型号': item.get('产品服务型号', ''),
                    '单价': item.get('产品服务单价（元）', ''),
                    '状态': item.get('启用状态', '')
                })
    return results

def format_results(results, title):
    """格式化输出结果"""
    if not results:
        return f"未找到「{title}」相关内容"
    
    output = [f"\n=== {title} ===\n"]
    for i, r in enumerate(results[:10], 1):
        output.append(f"\n{i}.")
        for k, v in r.items():
            if v:
                output.append(f"  {k}: {v}")
    
    if len(results) > 10:
        output.append(f"\n  ... 还有 {len(results) - 10} 条结果")
    
    return '\n'.join(output)

def main():
    if len(sys.argv) < 2:
        print("""
产品知识库查询工具
用法: python main.py <查询类型> [参数]

查询类型:
  product <关键词>     - 按产品名称搜索
  func <产品名>        - 查询产品功能清单
  deploy <产品名>      - 查询产品部署安装说明
  support <产品名>     - 查询产品售后问题处理
  scene <场景描述>     - 按应用场景跨产品查询方案
  line <产品线>        - 查看某产品线的所有产品
  step [关键词]        - 查看实施步骤
""")
        return
    
    query_type = sys.argv[1]
    
    if query_type == 'product':
        keyword = sys.argv[2] if len(sys.argv) > 2 else ''
        results = search_product_by_name(keyword)
        print(format_results(results, f"产品搜索: {keyword}"))
    
    elif query_type == 'line':
        line_name = sys.argv[2] if len(sys.argv) > 2 else ''
        results = get_product_list_by_line(line_name)
        print(format_results(results, f"产品线: {line_name}"))
    
    elif query_type == 'step':
        keyword = sys.argv[2] if len(sys.argv) > 2 else ''
        results = search_implementation_steps(keyword)
        print(format_results(results, "实施步骤"))
    
    elif query_type in ['func', 'deploy', 'support']:
        product = sys.argv[2] if len(sys.argv) > 2 else ''
        type_map = {
            'func': '功能清单',
            'deploy': '部署安装说明',
            'support': '售后问题处理'
        }
        
        # 先搜索产品基本信息
        product_results = search_product_by_name(product)
        
        # 再搜索文档中的相关内容
        doc_results = search_document_content('', product)
        
        if product_results:
            print(format_results(product_results, f"产品信息: {product}"))
        
        if doc_results:
            print(format_results(doc_results, f"{type_map[query_type]}相关文档"))
    
    elif query_type == 'scene':
        scene = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else ''
        results = search_document_content('', scene)
        print(format_results(results, f"场景方案: {scene}"))
    
    else:
        print(f"未知查询类型: {query_type}")

if __name__ == '__main__':
    main()
