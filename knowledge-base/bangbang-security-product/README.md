# 🏢 梆梆安全产品知识库 v2.0

**生成时间**: 2026-04-28 10:20:35
**数据来源**: ONES知识库 + 本地产品文档

## 📊 知识库统计

| 指标 | 数值 |
|------|------|
| 总文档数 | 44 |
| 总字数 | 9,326,736 |
| 文档分类 | 10 个 |

### 按来源分布
- **ONES知识库**: 3 个文档
- **本地产品文档**: 41 个文档

### 按分类分布
- **产品文档**: 41 个文档
- **Excel**: 17 个文档
- **PDF**: 10 个文档
- **PowerPoint**: 8 个文档
- **Word**: 6 个文档
- **产品技术**: 2 个文档
- **应用安全**: 1 个文档
- **威胁感知**: 1 个文档
- **服务交付**: 1 个文档
- **咨询服务**: 1 个文档

## 📁 文件结构

```
bangbang-security-product/
├── README.md                    # 本文件
├── product_knowledge_base.json  # 完整知识库（含所有文档内容）
├── search_index.json            # 搜索索引（快速检索）
├── category_index.json          # 分类索引
├── ones_documents.json          # ONES来源文档
├── local_documents.json         # 本地来源文档
├── scenario7_report.json        # 场景7执行报告
├── scenario8_report.json        # 场景8执行报告
└── merge_report.json            # 整合报告
```

## 🔍 检索方式

### 1. 关键词搜索
```python
import json

with open('search_index.json') as f:
    index = json.load(f)

# 搜索关键词
results = index['term_index'].get('安全加固', [])
for doc_id in results:
    doc_info = index['documents'][doc_id]
    print(f"{doc_info['title']} ({doc_info['source']})")
```

### 2. 按分类浏览
查看 `category_index.json` 获取所有分类及其文档列表

## 📝 说明

- 文档内容已做长度限制（单篇5万字），完整内容请参考原始文件
- 搜索索引为简单的词项匹配，如需高级搜索可接入Elasticsearch等引擎
- 建议定期（每周）更新知识库，保持内容时效性
