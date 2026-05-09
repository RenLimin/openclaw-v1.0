# Nova Skill Vetting Toolchain v1.0

技能质量评估和版本管理框架

## 功能特性

### 四件套检查工具

1. **📦 依赖检查** (`--check-deps`)
   - 检查 requirements.txt、setup.py
   - 识别未声明依赖、未使用依赖
   - 版本冲突检测

2. **📚 文档检查** (`--check-docs`)
   - README.md 完整性检查
   - SKILL.md 技能描述检查
   - 代码注释比例统计
   - 文档字符串覆盖率
   - 示例代码检查

3. **📏 颗粒度检查** (`--check-size`)
   - 文件行数统计
   - 函数/类数量统计
   - 圈复杂度计算
   - 单一职责原则检查
   - 大函数/大文件检测

4. **🧪 测试覆盖检查** (`--check-tests`)
   - 测试文件识别
   - 测试用例数量统计
   - 断言质量评估
   - 边界条件测试检查
   - 函数测试覆盖率估算

### 版本管理框架

- 语义化版本号管理 (`--bump-version`)
- 变更日志自动生成
- 版本检查点与回滚机制 (`--checkpoint`, `--rollback`)
- 技能元数据持久化

## 安装使用

```bash
# 运行所有检查
python -m skills.nova.vet /path/to/skill

# 单独运行某项检查
python -m skills.nova.vet /path/to/skill --check-deps
python -m skills.nova.vet /path/to/skill --check-docs
python -m skills.nova.vet /path/to/skill --check-size
python -m skills.nova.vet /path/to/skill --check-tests

# 输出 JSON 格式
python -m skills.nova.vet /path/to/skill --json

# 保存到文件
python -m skills.nova.vet /path/to/skill --output report.json

# 版本管理
python -m skills.nova.vet /path/to/skill --bump-version patch
python -m skills.nova.vet /path/to/skill --checkpoint "重构前备份"
python -m skills.nova.vet /path/to/skill --list-checkpoints
python -m skills.nova.vet /path/to/skill --rollback 20240506_120000
```

## 评分机制

- 每项检查独立评分 (0-100)
- 综合评分采用加权平均:
  - 文档检查: 30%
  - 测试检查: 25%
  - 颗粒度检查: 25%
  - 依赖检查: 20%

## 输出示例

```
======================================================================
Nova Skill Vetting Report - my_skill
Generated: 2024-05-06 12:00:00
======================================================================

🏆 综合评分: 85.5 / 100 [A]
   版本: 1.0.0

----------------------------------------------------------------------

📦 依赖检查: 90 / 100 [A]
   建议:
   💡 考虑移除以下未使用的依赖: abc, xyz

📚 文档检查: 80 / 100 [B]
   问题:
   🟡 README 缺少 2 个关键章节
   建议:
   💡 在 README 中补充以下章节: 使用方法, API 说明
```

## 作者

Nova 🌟
