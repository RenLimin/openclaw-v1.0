# ONES 项目/工作项/子工作项 查询工具

> 通过 GraphQL API 查询 ONES 系统的项目、工作项、子工作项数据，支持多维度筛选和结构化 Excel 导出。

## 功能概览

| 功能 | 状态 | 说明 |
|------|------|------|
| 🔐 登录认证 | ✅ | 自动登录，Cookie 持久化，支持交互式验证码处理 |
| 📊 项目查询 | ✅ | 按名称、状态、负责人筛选项目列表 |
| 📋 工作项查询 | ✅ | 按项目、状态、负责人、标题筛选工作项 |
| 🌳 子工作项层级 | ✅ | 递归查询，完整树结构展示 |
| 📤 Excel 导出 | ✅ | 多 Sheet 结构化导出（项目/工作项/子工作项） |
| ⚠️ 异常处理 | ✅ | 网络异常、登录失效、查询超时自动处理 |

## 快速使用

### 1. 完整查询（推荐）

```bash
cd /Users/bangcle/.openclaw/workspace/skills/ones-query

# 完整查询 + Excel 导出（首次登录建议用 --interactive）
python main.py --mode full --export-excel --interactive
```

### 2. 仅查询项目

```bash
# 查询所有项目
python main.py --mode projects

# 按名称关键词筛选
python main.py --mode projects --name "合同"

# 限制返回数量
python main.py --mode projects --limit 20
```

### 3. 查询工作项

```bash
# 查询所有工作项
python main.py --mode tasks

# 查询指定项目的工作项
python main.py --mode tasks --project <项目UUID>

# 按状态过滤
python main.py --mode tasks --status "进行中"

# 按标题关键词过滤
python main.py --mode tasks --title "优化"

# 按负责人过滤
python main.py --mode tasks --assign <负责人UUID>
```

### 4. 构建工作项层级树

```bash
# 构建完整层级树并导出 Excel
python main.py --mode hierarchy --export-excel

# 仅构建指定项目的层级树
python main.py --mode hierarchy --project <项目UUID>
```

### 5. 查询指定工作项的子工作项

```bash
python main.py --mode subtasks --parent <父工作项UUID>
```

## 参数说明

### 查询模式 (`--mode`)

| 模式 | 说明 |
|------|------|
| `projects` | 仅查询项目 |
| `tasks` | 仅查询工作项 |
| `subtasks` | 查询指定父工作项的子工作项 |
| `hierarchy` | 构建完整工作项层级树 |
| `full` | 完整查询（项目 + 工作项 + 层级树） |
| `query` | 默认模式（项目 + 工作项） |

### 过滤参数

| 参数 | 说明 |
|------|------|
| `--project <UUID>` | 指定项目 UUID |
| `--parent <UUID>` | 指定父工作项 UUID (subtasks 模式) |
| `--status <状态>` | 按工作项状态过滤 |
| `--assign <UUID>` | 按负责人 UUID 过滤 |
| `--name <关键词>` | 按项目名称关键词过滤 |
| `--title <关键词>` | 按工作项标题关键词过滤 |
| `--limit <数量>` | 返回数量限制 (默认 500) |

### 输出选项

| 参数 | 说明 |
|------|------|
| `--output <目录>` | 输出目录 |
| `--export-excel` | 导出为 Excel 文件 |
| `--interactive` | 交互式登录 (显示浏览器，用于验证码) |

## Excel 导出结构

| Sheet 名称 | 内容说明 |
|-----------|----------|
| 项目清单 | 项目基础信息（UUID、名称、Key、状态、负责人、时间等） |
| 工作项清单 | 工作项详细信息（含所属项目、类型、状态、负责人、工时等） |
| 子工作项层级 | 扁平化层级结构（显示层级、父子关系） |

## 配置文件

### `config.json`

自动从 `ones-data-download` 技能复制，无需手动配置。

主要配置项：
- `ones_url`: ONES 系统地址
- `graphql_api`: GraphQL API 地址模板
- `team_uuid`: 团队 UUID
- `auth`: 认证配置（用户名、Keychain 服务名）

## 认证说明

### Cookie 持久化

- 登录成功后 Cookie 保存到 `~/.openclaw/cache/ones_cookies.pkl`
- 后续运行自动加载 Cookie
- Cookie 过期时自动提示重新登录

### 首次登录（验证码处理）

首次使用或 Cookie 过期时：

```bash
# 使用 --interactive 参数，会显示浏览器窗口
python main.py --mode full --interactive

# 在浏览器中手动输入密码、完成验证码
# 登录成功后脚本会自动继续执行
```

### Keychain 凭证

用户名从 macOS Keychain 获取：
- Service: `openclaw-browser-oliver-ones-username`
- 可通过 `Keychain Access.app` 查看和修改

## 异常处理

| 异常类型 | 处理方式 |
|---------|---------|
| 登录失败 | 提示交互式登录 |
| 认证过期 | 自动清除失效 Cookie，提示重新登录 |
| 网络超时 | 自动重试 3 次（指数退避） |
| 查询超时 | 30 秒超时保护 |
| 其他异常 | 输出详细错误信息和堆栈 |

## 依赖要求

```bash
pip install playwright pandas openpyxl
playwright install chromium
```

## 输出示例

```
======================================================================
🔍 ONES 项目/工作项/子工作项 查询工具 v1.0
======================================================================
🔐 初始化浏览器...
📦 已加载保存的 Cookie，验证有效性...
🌐 访问 ONES: https://ones.bangcle.com/project/
✅ 认证成功，Cookie 已持久化
🔍 查询项目列表 (limit=500)...
   ✅ 找到 45 个项目

📊 项目列表 (前10个):
   🟢 2026-合同交付项目A | 负责人: 张三
   🟢 2026-POC实施项目B | 负责人: 李四
   ...

🔍 查询工作项 (all projects, limit=500)...
   ✅ 找到 328 个工作项

📈 工作项状态统计:
   进行中: 145 个
   待处理: 89 个
   已完成: 67 个
   已关闭: 27 个

🌳 构建完整工作项层级树...
   ✅ 总工作项数: 328
   ✅ 顶层工作项: 186 个
   ✅ 含子工作项的任务: 42 个

📤 导出 Excel: /Users/bangcle/.openclaw/workspace/training-reports/ONES_查询结果_20260427_093000.xlsx
   ✅ 项目清单: 45 条
   ✅ 工作项清单: 328 条
   ✅ 子工作项层级: 421 条
✅ Excel 导出完成
======================================================================
✅ 查询执行成功！
======================================================================
```

## 常见问题

### Q: 登录时出现验证码？
A: 使用 `--interactive` 参数，会显示浏览器窗口，手动完成验证码即可。

### Q: Cookie 过期了怎么办？
A: 脚本会自动检测并提示，重新运行 `--interactive` 登录即可。

### Q: 查询速度慢？
A: 工作项查询默认 limit=500，可通过 `--limit` 调整。大数量查询建议按项目拆分。

### Q: Excel 导出失败？
A: 检查是否安装了 pandas 和 openpyxl：`pip install pandas openpyxl`

## 版本信息

- **版本**: v1.0.0
- **日期**: 2026-04-27
- **作者**: Jerry 🦞
