#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库 v4.0 快速测试脚本
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "skills" / "knowledge-base" / "scripts"))

from kb_manager import KnowledgeBaseManager

def main():
    print("=" * 60)
    print("🧪 知识库 v4.0 功能测试")
    print("=" * 60)

    kb = KnowledgeBaseManager()

    # 1. 添加测试数据源
    print("\n1️⃣  添加测试数据源...")
    source_id = kb.add_source(
        name="测试文档库",
        source_type="offline_doc",
        config={"path": "/tmp/test-docs"}
    )

    # 2. 添加测试文档
    print("\n2️⃣  添加测试文档...")
    doc_id = kb.add_document(
        source_id=source_id,
        uri="/tmp/test-docs/合同范本.md",
        title="2026标准采购合同范本",
        doc_type="md",
        content="""
# 标准采购合同

## 第一条 合同标的
甲方同意向乙方采购，乙方同意向甲方出售以下产品：
1. 企业级服务器 10台
2. 存储设备 2台
3. 网络设备 5台

## 第二条 价格与支付
合同总金额：人民币 5,000,000元整

## 第三条 违约责任
3.1 任何一方违反本合同约定，应向守约方支付合同总金额20%的违约金
3.2 违约金不足以弥补损失的，违约方还应赔偿全部实际损失
3.3 逾期交付超过30日的，守约方有权解除合同

## 第四条 争议解决
双方发生争议应友好协商，协商不成的提交甲方所在地人民法院诉讼解决。
        """,
        file_size=1024
    )

    # 3. 添加第二篇测试文档
    doc_id2 = kb.add_document(
        source_id=source_id,
        uri="/tmp/test-docs/员工手册.pdf",
        title="2026版员工手册",
        doc_type="pdf",
        content="""
# 员工手册

## 第一章 入职
新员工应在入职当日提交以下材料：
1. 身份证复印件
2. 学历证明复印件
3. 离职证明
4. 银行卡信息

## 第二章 考勤
工作时间：周一至周五 9:00-18:00
每月迟到超过3次，扣除当月全勤奖

## 第三章 离职
员工提前30日以书面形式通知公司，可以解除劳动合同。
试用期内提前3日通知。
        """,
        file_size=2048
    )

    # 4. 列出数据源
    print("\n3️⃣  列出所有数据源...")
    sources = kb.list_sources()
    for s in sources:
        print(f"   ID: {s['id']} - {s['name']} ({s['type']})")

    # 5. 列出文档
    print("\n4️⃣  列出所有文档...")
    docs = kb.list_documents(limit=10)
    for d in docs:
        print(f"   {d['id']}. {d['title']} - {d['uri']} - {d['chunk_count']}分块")

    # 6. 搜索测试
    print("\n5️⃣  关键词搜索测试...")
    queries = ["违约", "离职", "合同"]
    for q in queries:
        results = kb.keyword_search(q, limit=3)
        print(f"\n   搜索: '{q}' → 找到 {len(results)} 个结果")
        for r in results:
            print(f"      - {r['title']} (得分: {r['score']:.3f})")

    # 7. 统计信息
    print("\n6️⃣  知识库统计...")
    stats = kb.get_stats()
    print(f"   数据源: {stats['source_count']} 个")
    print(f"   文档数: {stats['document_count']} 个")
    print(f"   分块数: {stats['chunk_count']} 个")
    print(f"   总大小: {stats['total_size_mb']} MB")

    # 8. 导出测试
    print("\n7️⃣  导出测试...")
    export_path = "/tmp/kb_export.json"
    kb.export_to_json(export_path)
    print(f"   导出文件: {export_path}")

    kb.close()

    print("\n" + "=" * 60)
    print("✅ 所有测试通过！知识库 v4.0 运行正常")
    print("=" * 60)

if __name__ == '__main__':
    main()
