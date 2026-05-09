---
# ===== 必选元数据（10个，必须完整填写） =====
skill_id: business.contract.management      # 唯一ID：层级.领域.子领域.名称
name: 合同全生命周期管理能力                 # 技能名称
description: 从合同审批到履约归档的全流程自动化管理  # 一句话描述核心价值
version: 1.0.0                              # 语义化版本号 MAJOR.MINOR.PATCH
author: Ella 🦊                             # 负责人 + emoji
category: business                          # core/integration/business/knowledge
maturity: production                        # prototype/beta/production/deprecated
success_rate: 0.92                          # 历史成功率（KSA自动计算，首次发布填1.0）
avg_execution_time: 45s                     # 平均执行时间
tags: [contract, approval, parsing, lifecycle]  # 标签，便于搜索和分类

# ===== 可选元数据（5个，建议填写） =====
related_knowledge:                          # 关联的 KSA Knowledge ID
  - business.contract_taxonomy
  - integration.oa_api_spec
related_skills:                             # 依赖的其他技能 ID
  - core.orion
  - core.iris
security_level: internal                    # public/internal/restricted
permissions:                                # 需要的权限声明
  - oa:read_write
  - db:contract_write
fallback_strategy: manual_review            # fail_silent/retry_3x/manual_review
error_codes:                                # 错误码映射
  E001: OA连接失败
  E002: 合同解析失败
  E003: 审批流创建失败
---

# {{技能名称}}

## 🚀 第一层：快速开始（渐进式披露 - 第1层）
> **目标用户**: 第一次使用这个技能的新用户
> **阅读时间**: 5分钟
> **核心目标**: 能跑起来就行，快速验证功能

### 功能简介（3句话以内）
> 一句话说明这个技能能做什么，核心价值是什么，解决什么问题。

**示例：**
本技能提供合同全生命周期的自动化管理能力，支持从合同审批、结构化字段提取、履约义务拆分到归档的全流程自动化，将合同处理时间从平均4小时缩短到15分钟。

### 30秒示例
> 最常用的调用方式，复制粘贴就能跑，包含输入输出示例。

```bash
# 最常用的调用方式 - 单个合同审批
python -m skills.business.contract approve --file contract.pdf

# 最基本的输入输出
输入: PDF合同文件路径
输出:
{
  "success": true,
  "contract_id": "CT20260506001",
  "approval_flow_id": "FLOW_12345",
  "extracted_fields": {...}
}
```

### 输入输出概览
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | string | ✅ | 合同PDF文件路径 |
| auto_submit | boolean | ❌ | 是否自动提交审批，默认false |

### 常见问题 Top 3
1. **Q: 支持哪些文件格式？** → A: 目前支持 PDF/Word/Excel，扫描件PDF需要 OCR 增强模式。
2. **Q: 审批失败怎么办？** → A: 系统会自动回滚所有变更，返回详细错误信息，可手动重试。
3. **Q: 支持批量处理吗？** → A: 支持，使用 `--batch` 参数指定目录，详见第二层文档。

---

## 📖 第二层：详细文档（渐进式披露 - 第2层）
> **目标用户**: 日常使用这个技能的业务人员/开发者
> **阅读时间**: 30分钟
> **核心目标**: 能用好，知道所有功能和限制

### 核心能力清单
- ✅ **合同审批流程** - 自动创建OA审批流，支持自定义审批节点
- ✅ **结构化字段提取** - 自动提取50+个合同关键字段，准确率95%+
- ✅ **履约义务拆分** - 自动识别并拆分履约义务，生成任务计划
- ✅ **合同全生命周期台账** - 自动生成完整的合同台账，支持导出Excel
- ✅ **风险智能识别** - 自动识别20+类合同风险条款
- ❌ **不包含**: 合同模板生成、电子签章集成（需单独购买扩展技能）

### 完整使用方法
```bash
# 单个合同审批
python -m skills.business.contract approve --file contract.pdf

# 批量合同审批
python -m skills.business.contract approve --batch ./contracts/

# 仅解析字段，不提交审批
python -m skills.business.contract parse --file contract.pdf

# 生成合同台账
python -m skills.business.contract ledger --output contract_ledger.xlsx

# 查看技能状态
python -m skills.business.contract status
```

### 输入输出完整规范
> **JSON Schema 定义（必须提供！）**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "file": {
      "type": "string",
      "description": "合同文件路径"
    },
    "batch": {
      "type": "string",
      "description": "批量处理目录路径"
    },
    "auto_submit": {
      "type": "boolean",
      "default": false,
      "description": "是否自动提交审批"
    }
  },
  "required": ["file"]
}
```

### 边界条件与限制
- **最大支持文件大小**: 单文件 50MB
- **最大批量处理数量**: 单次最多100个文件
- **性能指标**: 正常响应时间 30-60秒/文件，峰值响应时间 120秒/文件
- **不支持的场景**: 手写体合同、图片格式合同（需OCR增强扩展）、多语言混合合同

---

## 🔧 第三层：高级特性（渐进式披露 - 第3层）
> **目标用户**: 深度用户/需要定制开发的开发者
> **阅读时间**: 2小时
> **核心目标**: 能定制、能调优、能排查问题

### 容错与重试机制
```
┌─────────────────────────────────────────────────────────────┐
│  错误处理策略                                             │
├─────────────────────────────────────────────────────────────┤
│  ✅ 可重试错误：                                         │
│     - 网络超时 → 自动重试3次，指数退避（1s/3s/7s）       │
│     - OA系统繁忙 → 自动重试2次                            │
│                                                             │
│  ❌ 不可重试错误：                                       │
│     - 参数错误 → 立即返回，详细错误信息                    │
│     - 文件格式错误 → 立即返回                              │
│     - 权限错误 → 立即返回                                  │
│                                                             │
│  🛡️ 降级策略：                                           │
│     - LLM字段提取失败 → 规则引擎兜底提取核心字段         │
│     - OCR识别失败 → 返回人工处理标记                      │
└─────────────────────────────────────────────────────────────┘
```

### 配置与调优
**环境变量：**
```bash
# OA系统配置
export OA_API_ENDPOINT="https://oa.example.com/api"
export OA_API_TOKEN="your-token"

# 性能调优
export MAX_CONCURRENT_JOBS=5      # 最大并发数
export OCR_TIMEOUT=120             # OCR超时时间（秒）
export ENABLE_LLM_ENHANCEMENT=true # 是否启用LLM增强
```

**自定义扩展点：**
- 自定义字段提取规则
- 自定义审批节点配置
- 自定义风险识别规则
- 自定义输出格式

### 监控与可观测性
**关键指标：**
| 指标名 | 告警阈值 | 说明 |
|--------|---------|------|
| 成功率 | < 90% | 低于此值触发告警 |
| P95 耗时 | > 120s | 性能告警 |
| 错误率 | > 10% | 错误告警 |

**日志格式：**
```json
{
  "timestamp": "2026-05-06T12:00:00Z",
  "skill_id": "business.contract.management",
  "version": "1.0.0",
  "trace_id": "trace_12345",
  "operation": "approve",
  "latency_ms": 45000,
  "success": true,
  "error_code": null,
  "error_message": null
}
```

---

## 🔬 第四层：内部实现（渐进式披露 - 第4层）
> **目标用户**: 需要修改和维护这个技能的开发人员/维护者
> **阅读时间**: 1天+
> **核心目标**: 能修改、能维护、能扩展

### 架构设计
**模块划分与依赖关系：**
```
business.contract.management
├── contract_parser.py     # 合同解析引擎
│   ├── pdf_extractor.py  # PDF文本提取
│   ├── ocr_engine.py     # OCR引擎封装
│   └── field_matcher.py  # 字段匹配规则引擎
├── approval_flow.py       # 审批流程管理
├── obligation_splitter.py # 履约义务拆分
├── ledger_generator.py    # 台账生成器
├── risk_detector.py       # 风险识别引擎
└── cli.py                 # CLI入口
```

**核心算法说明：**
- 字段提取：基于规则引擎 + 正则表达式 + LLM 兜底，三层校验
- 风险识别：关键词匹配 + 语义相似度 + 规则引擎，三层识别
- 履约拆分：基于合同条款的语义分类 + 任务模板映射

**数据流程图：**
```
输入文件 → 格式校验 → 文本提取 → 字段匹配 → 风险识别 → 
履约拆分 → 创建审批流 → 生成台账 → 输出结果
```

### 测试策略
**单元测试覆盖范围（目标：≥ 80%）：**
- ✅ 格式校验逻辑：100% 覆盖
- ✅ 字段匹配规则：100% 覆盖
- ✅ 风险识别规则：95% 覆盖
- ✅ 审批流程逻辑：90% 覆盖
- ✅ CLI 命令解析：85% 覆盖

**集成测试场景：**
1. 正常合同全流程处理
2. 扫描件合同处理
3. 批量合同处理
4. 网络异常场景
5. 权限异常场景

**边界测试用例：**
- 空文件 / 损坏文件 / 超大文件
- 异常参数 / 缺失参数 / 错误类型参数
- 并发场景 / 限流场景 / 超时场景

### 已知技术债务
**TODO 列表：**
- [ ] 支持多语言合同（中/英/日）
- [ ] 支持合同模板生成功能
- [ ] 优化大文件解析性能（>20MB）
- [ ] 增加增量解析能力，避免重复解析相同文件

**已知问题与限制：**
1. 扫描件合同的字段识别率约 80%，需要人工复核
2. 复杂的嵌套表格结构解析准确率较低
3. 部分老版本的 Word 文件可能解析失败

**未来优化方向：**
1. 引入更先进的文档解析模型（如 LayoutLM）
2. 增加用户反馈闭环，自动优化规则引擎
3. 支持合同版本对比功能

---

## 📚 参考与依赖

### 关联知识（KSA Knowledge）
- `business.contract_taxonomy` - 合同分类体系与标准
- `integration.oa_api_spec` - OA系统API接口规范
- `business.risk_management` - 合同风险管理规范

### 依赖技能
- `core.orion` - LLM调度框架，用于增强字段提取和风险识别
- `core.iris` - RAG知识库，用于合同条款检索和参考

### 外部参考
- 《企业合同管理规范》GB/T 36074-2018
- OA系统API文档 v2.5
- PDFBox 文档解析引擎官方文档

### 设计文档链接
- 合同管理系统架构设计文档 v1.0
- 字段提取规则引擎设计文档
- 风险识别规则库 v2.0

---

## 📝 变更历史

| 版本 | 日期 | 变更人 | 变更内容 |
|------|------|--------|---------|
| 1.0.0 | 2026-05-06 | Ella 🦊 | 初始版本发布，包含完整的合同全生命周期管理能力 |

---

**模板版本**: v1.0 | **适用规范**: SKILL_SPECIFICATION_v1.0.md
