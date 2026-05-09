# KSA 框架技能说明

## 技能信息

- **名称**: KSA (Knowledge/Skill/Ability) 管理框架
- **版本**: 1.0.0
- **作者**: Jerry
- **成熟度**: production
- **标签**: core, infrastructure, knowledge-management, skill-management, ability-management

## 技能描述

KSA 框架是整个交付系统的核心基础设施，提供了统一的知识、技能、能力管理能力。

### 核心功能

1. **知识管理**
   - 支持事实、方法、经验三类知识分类
   - 全文搜索 + 相似度推荐引擎
   - 置信度管理和来源追踪

2. **技能管理**
   - 四级成熟度管理
   - 自动成功率统计
   - 依赖关系管理
   - 智能技能匹配引擎

3. **能力管理**
   - 知识+技能组合能力
   - 成长历史追踪
   - 自动能力评估引擎
   - 并发执行控制

4. **自动迁移**
   - 扫描现有 skills 目录自动生成技能卡片
   - 从 memory 目录提取自动生成知识卡片

## 输入输出

### 输入
- 任务描述（用于技能匹配）
- 知识内容、元数据
- 技能定义、依赖关系
- 能力配置、组合关系

### 输出
- 匹配的技能列表（带匹配得分）
- 知识搜索结果（按相似度排序）
- 能力评估报告
- 统计概览

## 使用限制

- 需要 SQLite 数据库支持
- 向量嵌入功能依赖外部模型实现（当前使用文本相似度）
- 批量导入时注意内存使用

## 典型用例

```python
from skills.ksa import KSAManager

# 初始化
ksa = KSAManager()

# 搜索匹配技能
skills = ksa.skill.match_skills("需要对合同进行审查")

# 搜索知识
knowledge = ksa.knowledge.search("SQL查询优化")

# 记录技能执行
ksa.skill.record_execution(skill_id=1, success=True, execution_time=2.5)

# 评估能力
ksa.ability.evaluate_task_result(ability_id=1, success=True, metrics={"accuracy": 0.95})
```

## CLI 示例

```bash
# 导入指定模块技能
python -m skills.ksa import modules database,orion,nova,luna,vet

# 根据任务描述匹配技能
python -m skills.ksa skill search "数据库查询和项目管理"

# 查看统计
python -m skills.ksa stats
```
