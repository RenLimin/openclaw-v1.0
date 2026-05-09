---
name: knowledge-base
description: >
  合同业务知识库 - 法规+标准产品双知识库系统
  包含《民法典》合同编核心法条结构化数据 + 355个标准产品/服务定义清单
  支持多维度法规查询、产品智能匹配、偏差自动识别，与业务逻辑完全解耦
metadata:
  openclaw:
    requires:
      bins: [python3]
      pip: [pyyaml, pandas, openpyxl]
---

# 合同业务知识库 📚

独立固化的法规+产品双知识库系统，与业务逻辑完全解耦，可被所有智能体引用。

## 📦 两大核心模块

| 模块 | 数据规模 | 核心功能 | 应用场景 |
|------|---------|---------|---------|
| 🔍 **合同法规知识库** | 58条核心法条 | 法规查询、合规审查、风险识别 | 合同审核、条款校验 |
| 📋 **标准产品/服务库** | 355个产品 | 产品匹配、偏差识别、履约义务提取 | 履约义务拆分、合同审核 |

## 功能特点

- ✅ **结构化法条数据**：民法典合同编核心法条完整结构化存储
- ✅ **多维度查询**：支持按ID、分类、关键词多维度查询
- ✅ **智能审查**：合同条款合规性自动审查，含评分、风险提示、法条依据
- ✅ **解耦设计**：与业务逻辑完全分离，可独立升级维护
- ✅ **统一接口**：所有智能体通过统一接口访问

## 数据范围（第一阶段）

### 《民法典》合同编通则
- 第一章 一般规定
- 第二章 合同的订立
- 第三章 合同的效力
- 第四章 合同的履行
- 第五章 合同的保全
- 第六章 合同的变更和转让
- 第七章 合同的权利义务终止
- 第八章 违约责任 ⭐ （重点）

### 《民法典》合同编 - 买卖合同
- 第九章 买卖合同核心条款

共计约 **50-60条** 核心法条。

---

## 查询接口使用文档

### 1. 按ID查询单条法条

```python
from skills.knowledge-base.scripts.law_query import LawQuery

query = LawQuery()
article = query.get_by_id("CC-577")
print(article['name'])          # 违约责任基本形态
print(article['original_text']) # 法条原文
```

### 2. 按分类查询法条列表

```python
# 违约责任分类
articles = query.get_by_category("违约责任")
for article in articles:
    print(f"{article['id']}: {article['title']}")

# 合同解除分类
articles = query.get_by_category("合同解除")
```

### 3. 关键词语义查询

```python
# 单关键词
results = query.query_by_keywords("违约金")
for result in results:
    print(f"{result['id']} - 匹配度: {result['match_score']}")

# 多关键词
results = query.query_by_keywords(["解除", "违约"])
```

### 4. 合同条款合规性审查

```python
clause_text = """
第七条 违约责任
1. 任何一方违反本合同约定，应向守约方支付合同总金额30%的违约金。
2. 违约金不足以弥补损失的，违约方还应赔偿全部损失。
"""

review = query.review_clause(clause_text)
print(f"合规评分: {review['score']}/100")
print(f"风险等级: {review['risk_level']}")
for risk in review['risks']:
    print(f"⚠️  {risk['type']}: {risk['description']}")
    print(f"   法条依据: {risk['law_basis']['id']} - {risk['law_basis']['name']}")
```

**审查返回结构:**
```python
{
    "score": 85,                    # 合规评分 (0-100)
    "risk_level": "中",              # 风险等级 (高/中/低)
    "risks": [                       # 风险列表
        {
            "type": "违约金过高",
            "description": "违约金约定超过损失的30%，可能被法院调低",
            "severity": "中",
            "law_basis": {           # 法条依据
                "id": "CC-585",
                "name": "违约金调整规则",
                "title": "约定的违约金低于或过分高于造成的损失的，人民法院或者仲裁机构可以根据当事人的请求予以调整"
            },
            "suggestion": "建议将违约金调整至合理范围，或明确损失计算方式"
        }
    ],
    "matched_articles": ["CC-577", "CC-585"],  # 匹配的法条ID
    "summary": "条款整体合规，但存在违约金过高的风险"
}
```

---

## 命令行使用

```bash
# 按ID查询
python3 skills/knowledge-base/scripts/law_query.py --id CC-577

# 按分类查询
python3 skills/knowledge-base/scripts/law_query.py --category "违约责任"

# 关键词查询
python3 skills/knowledge-base/scripts/law_query.py --keyword "违约金"

# 审查合同条款（从文件）
python3 skills/knowledge-base/scripts/law_query.py --review clause.txt
```

---

## 法条数据结构说明

每条款结构化包含以下字段：

| 字段 | 说明 | 示例 |
|------|------|------|
| `id` | 法条唯一标识符 | `CC-577` |
| `name` | 法条名称 | 违约责任基本形态 |
| `category` | 分类 | 违约责任 |
| `title` | 条款核心要点 | 当事人一方不履行合同义务或者履行合同义务不符合约定的，应当承担继续履行、采取补救措施或者赔偿损失等违约责任 |
| `original_text` | 法规原文 | 完整法条原文 |
| `interpretation` | 要点解读 | 结构化解读对象 |
| `interpretation.core_principle` | 核心原则 | 违约必究原则 |
| `interpretation.key_points` | 关键要点列表 | 要点数组 |
| `contract_review_tips` | 合同审查提示 | 智能体审查时的提示语 |
| `risk_level` | 风险等级 | 高/中/低 |
| `keywords` | 匹配关键词 | 用于自动关联的关键词列表 |
| `version` | 版本号 | `v1.0` |
| `updated` | 更新日期 | `2026-04-24` |
| `source` | 法规来源 | 《中华人民共和国民法典》 |

---

## 配置文件说明

### `config/query-config.yaml`

```yaml
# 关键词匹配权重配置
keyword_weights:
  exact_match: 100       # 精确匹配权重
  partial_match: 50      # 部分匹配权重
  fuzzy_match: 30        # 模糊匹配权重

# 风险评分规则
risk_scoring:
  high_risk_threshold: 30    # 高风险阈值（低于此分）
  medium_risk_threshold: 60  # 中风险阈值（低于此分）

# 审查提示配置
review_tips:
  enable_auto_suggestion: true
  max_risk_items: 5
```

---

## 📋 模块二：标准产品/服务查询接口

### 功能特点

- ✅ **355个产品完整结构化**：6条产品线，59个产品类别
- ✅ **智能产品匹配**：从合同文本自动识别匹配对应标准产品
- ✅ **偏差自动识别**：6类偏差检测（价格/范围/交付/验收/维保/定制化）
- ✅ **多维度查询**：产品编码、ID、产品线、类别、关键词模糊搜索
- ✅ **风险自动分级**：高/中/低三级风险 + 自动审核建议

### 查询接口使用

```python
from skills.knowledge-base.scripts.product_query import ProductQueryEngine

engine = ProductQueryEngine()

# 1. 按产品编码精确查询
product = engine.get_by_code('AS-AIOTP-6.0-EA-SAP-021')

# 2. 从合同文本智能匹配产品（履约义务拆分用）
matches = engine.match_contract_product("""合同内容：全渠道应用安全监测软件V6.0采购...""")
for product, score in matches:
    print(f"匹配: {product['product_name']}, 置信度: {score:.2%}")

# 3. 偏差检查（合同审核用）
result = engine.check_deviation("合同约定价格为40000元...", product)
if result['has_deviation']:
    print(f"发现偏差，风险等级: {result['risk_level']}")
    print(f"审核建议: {result['review_advice']}")

# 4. 按产品线/类别查询
products = engine.get_by_product_line('安全监测线')
categories = engine.get_all_categories()
```

### 返回结构说明

```python
# 偏差检查返回结构
{
    'has_deviation': True,                    # 是否存在偏差
    'risk_level': '高风险',                    # 风险等级
    'risk_score': 15,                         # 风险评分
    'deviations': [                            # 详细偏差列表
        {
            'code': 'PRICE_DEVIATION',
            'name': '价格偏差',
            'risk_level': '高',
            'description': '合同价格与标准产品价格偏差超过阈值',
            'actual_value': 40000,
            'standard_value': 50000,
            'diff_percent': 20.0,
        }
    ],
    'review_advice': '【高风险】本项合同约定与标准产品/服务定义存在重大偏差...',
}
```

### 命令行使用

```bash
# 产品库统计
python3 skills/knowledge-base/scripts/product_query.py

# 搜索产品
python3 skills/knowledge-base/scripts/product_query.py --keyword "安全监测"

# 按编码查询
python3 skills/knowledge-base/scripts/product_query.py --code AS-AIOTP-6.0-EA-SAP-021
```

---

## 版本信息

| 项目 | 值 |
|------|-----|
| 版本 | v2.0（双知识库版） |
| 更新日期 | 2026-04-24 |
| 数据范围 | 民法典合同编（通则+买卖合同） + 355个标准产品 |
| 法条数量 | 58条 |
| 产品数量 | 355个（6条产品线） |
| 作者 | Jerry 🦞 |

---

## 扩展计划

### 第二阶段
- [ ] 民法典合同编其余典型合同（借款、租赁、承揽等）
- [ ] 公司法核心条款
- [ ] 劳动合同法核心条款

### 第三阶段
- [ ] 司法解释结构化录入
- [ ] 指导性案例库
- [ ] 裁判规则库

---

**注意：** 本知识库仅供智能体内部使用，不构成法律意见。
