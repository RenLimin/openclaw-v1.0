# SKILL 开发规范 v1.0 完整版

> **生效日期**: 2026-05-06
> **适用范围**: 所有交付管理系统的 SKILL 开发
> **强制执行**: 所有新建/修改的 SKILL 必须 100% 符合本规范

---

## 📋 目录

1. [🔴 规则一：标准格式与元数据](#规则一标准格式与元数据)
2. [🔴 规则二：质量门禁标准](#规则二质量门禁标准)
3. [🔴 规则三：三重自测机制](#规则三三重自测机制)
4. [🔴 规则四：版本管理规范](#规则四版本管理规范)
5. [🔴 规则五：数据埋点规范](#规则五数据埋点规范)
6. [🔴 规则六：商业化设计规范](#规则六商业化设计规范)
7. [🚀 实施计划](#实施计划)

---

## 🔴 规则一：标准格式与元数据

### 1.1 统一文件格式
**所有 SKILL 必须使用 YAML front matter + Markdown 内容格式**，文件名为 `SKILL.md`。

### 1.2 必选元数据字段（10个）
| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `skill_id` | string | 唯一ID，命名空间：`层级.领域.子领域.名称` | `business.contract.management` |
| `name` | string | 技能名称 | `合同全生命周期管理能力` |
| `description` | string | 一句话描述 | `从合同审批到履约归档的全流程自动化管理` |
| `version` | string | 语义化版本号 | `1.0.0` |
| `author` | string | 负责人 + emoji | `Ella 🦊` |
| `category` | string | 分类：`core`/`integration`/`business`/`knowledge` | `business` |
| `maturity` | string | 成熟度：`prototype`/`beta`/`production`/`deprecated` | `production` |
| `success_rate` | float | 历史成功率（KSA自动计算） | `0.92` |
| `avg_execution_time` | string | 平均执行时间 | `45s` |
| `tags` | array[string] | 标签列表 | `[contract, approval, parsing]` |

### 1.3 可选元数据字段（5个）
| 字段 | 类型 | 说明 |
|------|------|------|
| `related_knowledge` | array[string] | 关联的 KSA Knowledge ID |
| `related_skills` | array[string] | 依赖的其他技能 ID |
| `security_level` | string | 安全级别：`public`/`internal`/`restricted` |
| `permissions` | array[string] | 需要的权限声明 |
| `fallback_strategy` | string | 降级策略：`fail_silent`/`retry_3x`/`manual_review` |
| `error_codes` | object | 错误码映射表 |

### 1.4 四层渐进式披露设计
| 层级 | 名称 | 目标用户 | 阅读时间 | 核心内容 |
|------|------|---------|---------|---------|
| **第一层** | 快速开始 | 第一次用的用户 | 5分钟 | 3句话简介 + 30秒示例 + 输入输出概览 + Top3问题 |
| **第二层** | 详细文档 | 日常使用的用户 | 30分钟 | 核心能力清单 + 完整使用方法 + 完整输入输出规范 + 边界条件 |
| **第三层** | 高级特性 | 深度用户/开发者 | 2小时 | 容错与重试机制 + 配置与调优 + 监控与可观测性 |
| **第四层** | 内部实现 | 维护者 | 1天+ | 架构设计 + 测试策略 + 已知技术债务 |

### 1.5 标准模板示例
见附录 A - 完整 SKILL.md 模板。

---

## 🔴 规则二：质量门禁标准

### 2.1 skill-vetting 强制评分要求
| 检查项 | 权重 | 合格标准 |
|--------|------|---------|
| 依赖检查 | 20% | ≥ 80分 |
| 文档检查 | 30% | ≥ 80分 |
| 颗粒度检查 | 25% | ≥ 80分 |
| 测试检查 | 25% | ≥ 80分 |
| **总分** | 100% | **≥ 80分** |

### 2.2 测试覆盖率要求
| 测试类型 | 最低覆盖率 | 说明 |
|---------|-----------|------|
| 单元测试 | ≥ 80% | 核心业务逻辑必须 100% 覆盖 |
| 集成测试 | ≥ 60% | 与外部系统交互的场景 |
| 端到端测试 | ≥ 50% | 核心用户场景 |

### 2.3 门禁熔断机制
- ❌ skill-vetting < 80分 → 禁止合入主线，自动打回
- ❌ 测试覆盖率 < 80% → 禁止合入主线，自动打回
- ❌ 有 P0/P1 级 Bug 未修复 → 禁止发布

---

## 🔴 规则三：三重自测机制

### 3.1 第一重：代码级自测（开发人员执行）
| 检查项 | 要求 |
|--------|------|
| 单元测试 | 全部通过，覆盖率报告生成 |
| 边界测试 | 极端输入、空输入、异常输入全部覆盖 |
| 代码风格 | 符合项目编码规范 |
| 文档同步 | 代码变更同步更新文档 |

### 3.2 第二重：技能级自测（Nova 自动执行）
**提交后自动触发 Nova skill-vetting 4件套检查：**
1. ✅ 依赖检查：requirements.txt 完整，版本正确
2. ✅ 文档检查：README.md + SKILL.md 完整，有示例
3. ✅ 颗粒度检查：单一职责，无上帝类，圈复杂度合规
4. ✅ 测试检查：覆盖率达标，断言质量合格

### 3.3 第三重：能力级自测（KSA 自动执行）
**合并到主线后自动触发：**
1. ✅ 端到端测试 ≥ 3 次，100% 成功
2. ✅ 成功率指标自动计算并写入 KSA 能力卡
3. ✅ 失败根因自动识别（如有问题）
4. ✅ 自动生成改进建议

---

## 🔴 规则四：版本管理规范

### 4.1 语义化版本号（强制执行）
```
MAJOR.MINOR.PATCH
│     │     │
│     │     └─ 补丁版本：向下兼容的 Bug 修复
│     └─────── 次版本：向下兼容的功能新增
└───────────── 主版本：不兼容的 API 变更
```

**示例：**
```
1.0.0   - 首个稳定版本
1.0.1   - 修复了合同解析的一个 Bug
1.1.0   - 新增了批量审批功能
2.0.0   - 接口重构，不兼容 1.x 版本
```

### 4.2 Git 提交规范（Conventional Commits）
```
<type>(<skill-id>): <subject>

<body>

<footer>
```

**Type 类型：**
| 类型 | 说明 | 版本影响 |
|------|------|---------|
| feat | 新功能 | MINOR |
| fix | Bug 修复 | PATCH |
| docs | 文档变更 | PATCH |
| style | 代码格式调整 | PATCH |
| refactor | 重构 | PATCH/MINOR |
| perf | 性能优化 | PATCH |
| test | 测试相关 | PATCH |
| chore | 构建/工具变动 | PATCH |
| BREAKING CHANGE | 不兼容的 API 变更 | MAJOR |

### 4.3 版本检查点与快速回滚
**Nova 工具链原生支持：**
```bash
# 创建版本检查点
python -m skills.nova.vet <skill-path> --checkpoint "v1.0.0 正式发布"

# 列出所有检查点
python -m skills.nova.vet <skill-path> --list-checkpoints

# 快速回滚到指定版本
python -m skills.nova.vet <skill-path> --rollback <checkpoint-id>

# 自动版本升级
python -m skills.nova.vet <skill-path> --bump-version patch|minor|major
```

### 4.4 CHANGELOG 自动生成
每个 SKILL 根目录必须包含 `CHANGELOG.md`，自动从 Git 提交记录生成。

格式要求：
```markdown
# CHANGELOG - 合同管理技能

## [1.1.0] - 2026-05-06
### ✨ Features
- 新增批量审批功能
- 新增批量导出Excel功能

### 🐛 Bug Fixes
- 修复了合同编号重复的问题

## [1.0.0] - 2026-05-01
### 🎉 Initial Release
- 合同审批流程
- 结构化字段提取
- 履约义务拆分
```

---

## 🔴 规则五：数据埋点规范

### 5.1 统一埋点 SDK
**所有 SKILL 必须集成标准埋点 SDK，一行代码完成埋点：**

```python
from skills.core.metrics import SkillMetrics

# 初始化（每个 SKILL 只需一次）
metrics = SkillMetrics(
    skill_id="business.contract.management",
    version="1.0.0"
)

def parse_contract(file_path):
    # 开始计时
    span = metrics.start_span("parse_contract")
    
    try:
        # 业务逻辑
        result = do_parse(file_path)
        
        # 成功埋点
        metrics.record_success(span, metadata={
            "file_size": len(file_path),
            "file_type": "pdf"
        })
        return result
        
    except Exception as e:
        # 失败埋点
        metrics.record_failure(
            span,
            error_code="E002",
            error_message=str(e),
            metadata={"file_path": file_path}
        )
        raise
```

### 5.2 必须采集的核心指标
| 指标名 | 说明 | 采集方式 |
|--------|------|---------|
| `call_count` | 调用次数 | 自动 +1 |
| `success_count` | 成功次数 | 调用 record_success |
| `failure_count` | 失败次数 | 调用 record_failure |
| `avg_latency` | 平均耗时 | 自动计算 span 时长 |
| `p50_latency` | P50 耗时 | 百分位统计 |
| `p95_latency` | P95 耗时 | 百分位统计 |
| `p99_latency` | P99 耗时 | 百分位统计 |
| `error_distribution` | 错误码分布 | 按 error_code 分组统计 |
| `user_distribution` | 用户分布 | 按调用者统计 |

### 5.3 数据存储与查询
**统一存储到 `delivery_management.db` 的 `skill_metrics` 表：**

```bash
# 查询技能指标
python -m skills.core.metrics query <skill-id> --time 7d

# 输出报表
python -m skills.core.metrics report <skill-id> --format html

# 实时监控面板
python -m skills.core.metrics dashboard
```

### 5.4 自动优化建议
**KSA 反思引擎自动基于指标数据生成优化建议：**

```
📊 合同管理技能 - 周度分析报告

🔴 需要优化：
- 成功率：82%（低于90%阈值）
- 主要错误：E002 合同解析失败（占比65%）
- 建议：优化PDF解析引擎，增加扫描件预处理

🟡 关注：
- P95 耗时：120s（略高于100s阈值）
- 建议：增加缓存机制，常见合同模板预解析

✅ 优秀：
- 调用量：周增25%，使用频率持续上升
```

---

## 🔴 规则六：商业化设计规范

### 6.1 商业化核心原则
| 原则 | 说明 | 硬性要求 |
|------|------|---------|
| **完全独立** | 不依赖其他业务 SKILL | 最多只能依赖 `core.*` 层基础技能 |
| **零外部依赖** | 不需要外部系统账号 | 所有依赖可配置、可替换 |
| **开箱即用** | 购买后5分钟内能跑起来 | 完整的示例数据、配置向导 |
| **可授权** | 支持 License 授权机制 | 内置授权校验 |
| **知识产权清晰** | 所有代码自有 | 第三方依赖必须是 MIT/BSD/Apache 等宽松协议 |

### 6.2 商业化 SKILL 标准目录结构
```
skill-package/
├── skill/                    # 技能核心代码
│   ├── __init__.py
│   ├── main.py
│   ├── utils.py
│   └── config.py
├── data/                     # 示例数据（开箱即用）
│   ├── sample_contract.pdf
│   ├── sample_project.xlsx
│   └── demo_data.db
├── docs/                     # 商业化文档
│   ├── QUICKSTART.md         # 5分钟快速上手
│   ├── USER_GUIDE.md         # 完整用户手册
│   ├── API_REFERENCE.md      # API参考
│   └── DEPLOYMENT_GUIDE.md   # 部署指南
├── tests/                    # 完整测试套件
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── config/                   # 配置模板
│   ├── config.example.yaml
│   └── license.example.json
├── LICENSE                   # 商业授权协议
├── README.md                 # 商业化介绍（卖点、价值、客户案例）
├── SKILL.md                  # 标准技能文档
├── CHANGELOG.md              # 变更历史
└── requirements.txt          # 严格版本锁定的依赖声明
```

### 6.3 授权与定价机制
**内置标准授权系统：**
```json
{
  "license_id": "lic_123456",
  "skill_id": "business.contract.management",
  "tier": "professional",
  "expires_at": "2027-05-06",
  "max_users": 50,
  "max_calls_per_month": 10000,
  "features": [
    "batch_processing",
    "custom_templates",
    "api_access",
    "priority_support"
  ],
  "signature": "..."
}
```

**标准定价层级（参考）：**

| 层级 | 价格（月付） | 限制 | 包含功能 |
|------|-------------|------|---------|
| **Basic** | ¥99 | 10用户 / 1000次/月 | 核心功能 |
| **Professional** | ¥499 | 50用户 / 10000次/月 | 批量处理 + API访问 |
| **Enterprise** | ¥1999 | 无限用户 / 无限调用 | 所有功能 + 定制开发 + 专属支持 |

### 6.4 商业化包装清单
**每个商业化 SKILL 必须包含：**

1. ✅ **一分钟介绍视频**（展示核心价值）
2. ✅ **产品介绍页**（卖点、客户痛点、解决方案、客户案例）
3. ✅ **5分钟快速上手教程**（图文 + 视频）
4. ✅ **完整的 API 文档**（OpenAPI 规范）
5. ✅ **演示环境**（沙箱环境，客户可以直接体验）
6. ✅ **售后支持 SLA**（响应时间、问题处理流程）

---

## 🚀 实施计划

| 阶段 | 任务 | 负责人 | 预计时间 | 依赖 | 状态 |
|------|------|--------|---------|------|------|
| **Phase 1** | 版本管理工具链实现（Nova 集成） | Nova 🌟 | 2小时 | Nova 现有工具链 | ⏳ 待启动 |
| **Phase 2** | 统一埋点 SDK 实现（core.metrics 模块） | Jerry 🦞 | 3小时 | 数据库表结构 | ⏳ 待启动 |
| **Phase 3** | 商业化授权系统实现 | Jerry 🦞 | 4小时 | 加密模块 | ⏳ 待启动 |
| **Phase 4** | 标准 SKILL 模板完善 + 文档补充 | Jerry 🦞 | 2小时 | 全部完成 | ⏳ 待启动 |
| **Phase 5** | 给已完成的 6 个技能补齐六大能力 | Nova 🌟 | 1天 | 前四阶段完成 | ⏳ 待启动 |
| **Phase 6** | 后续新技能强制执行六大标准 | 所有Agent | 永久 | 全部完成 | ⏳ 待启动 |

---

## 📌 附录 A - 完整 SKILL.md 模板

完整模板文件位置：`/Users/bangcle/.openclaw/workspace/skills/SKILL_TEMPLATE_v1.0.md`

---

**版本**: v1.0 | **状态**: 🔒 已固化，待实施 | **生效日期**: 2026-05-06
