---
name: Nova Skill Vetting Toolchain
description: 技能质量评估和版本管理框架
author: Nova 🌟
version: 1.0.0
---

## 功能概述

Nova 是一套完整的技能质量检查工具链，提供以下功能：

### 四件套检查工具

| 检查项 | 说明 | 权重 |
|--------|------|------|
| 依赖检查 | requirements.txt、setup.py、未声明/未使用依赖 | 20% |
| 文档检查 | README.md、SKILL.md、代码注释、示例代码 | 30% |
| 颗粒度检查 | 文件行数、函数数量、圈复杂度、单一职责 | 25% |
| 测试检查 | 测试覆盖率、断言质量、边界测试 | 25% |

### 版本管理框架

- 语义化版本号管理 (major/minor/patch)
- 变更日志自动生成
- 版本检查点与回滚机制
- 技能元数据持久化

## 使用方式

```bash
# 运行所有检查
python -m skills.nova.vet /path/to/skill

# 单独运行检查
python -m skills.nova.vet /path/to/skill --check-deps
python -m skills.nova.vet /path/to/skill --check-docs
python -m skills.nova.vet /path/to/skill --check-size
python -m skills.nova.vet /path/to/skill --check-tests

# 输出格式
python -m skills.nova.vet /path/to/skill --json
python -m skills.nova.vet /path/to/skill --output report.json

# 版本管理
python -m skills.nova.vet /path/to/skill --bump-version patch
python -m skills.nova.vet /path/to/skill --checkpoint "描述"
python -m skills.nova.vet /path/to/skill --list-checkpoints
python -m skills.nova.vet /path/to/skill --rollback <checkpoint_id>
```

## 输出格式

- 人类可读的彩色报告
- 结构化 JSON 输出
- 评分等级 (S/A/B/C/D/F)
- 自动改进建议

## 评分标准

| 分数 | 等级 | 说明 |
|------|------|------|
| 90+ | S | 优秀 |
| 80-89 | A | 良好 |
| 70-79 | B | 中等 |
| 60-69 | C | 及格 |
| 50-59 | D | 需改进 |
| <50 | F | 不及格 |
