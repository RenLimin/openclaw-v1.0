# 🧪 多 Agent 团队技能测试方案 v1.0

> **版本**: v1.0  
> **创建日期**: 2026-04-23  
> **测试范围**: 5 个业务技能 + 系统安全规则  
> **预计测试周期**: 3 个工作日

---

## 🎯 一、测试目标

1. ✅ 验证所有 5 个业务技能的基础功能可用性
2. ✅ 验证安全规则的有效性（风控、限流、延迟、凭证安全）
3. ✅ 验证 Provider 智能路由逻辑
4. ✅ 验证 Agent 间任务分发与协作流程
5. ✅ 验证 Cron 提醒 + 用户确认执行流程

---

## 📋 二、测试范围

| 测试阶段 | 测试内容 | 优先级 | 预计耗时 |
|---------|---------|--------|---------|
| **第一阶段** | 单技能功能测试（5个技能） | 🔴 高 | 1 天 |
| **第二阶段** | 集成测试（Agent协作 + Provider路由） | 🟡 中 | 1 天 |
| **第三阶段** | 边界测试 + 安全规则验证 | 🟡 中 | 0.5 天 |

---

## 🔧 三、测试环境准备

### 3.1 软件环境

| 项 | 要求 | 状态 |
|----|-----|------|
| Python 版本 | ≥ 3.8 | ⬜ 待确认 |
| OpenClaw 版本 | ≥ 2026.4.x | ⬜ 待确认 |
| 浏览器 | Chromium（Playwright 自动安装） | ⬜ 待准备 |

### 3.2 依赖包检查清单

运行以下命令验证依赖：

```bash
# 基础依赖
pip install playwright beautifulsoup4 python-docx pypdf pdfplumber
pip install pandas openpyxl matplotlib jinja2 numpy
pip install imaplib2 chardet pytz

# Playwright 浏览器安装
playwright install chromium
```

| 包名 | 用途 | 检查状态 |
|------|-----|---------|
| playwright | 浏览器自动化 | ⬜ |
| beautifulsoup4 | HTML 解析 | ⬜ |
| python-docx | Word 处理 | ⬜ |
| pypdf / pdfplumber | PDF 处理 | ⬜ |
| pandas | 数据处理 | ⬜ |
| openpyxl | Excel 处理 | ⬜ |
| matplotlib | 图表生成 | ⬜ |
| jinja2 | 模板渲染 | ⬜ |
| imaplib2 | IMAP 邮件协议 | ⬜ |

### 3.3 配置文件准备

所有技能配置文件路径：

```
~/.openclaw/workspace/skills/
├── ones-data-download/config/ones-config.json
├── oa-approval/config/oa-config.json
├── contract-clause-split/config/contract-split-config.json
├── email-management/config/email-config.json
└── business-report-generator/config/report-config.json
```

每个配置从 `.template` 复制后填写实际参数。

### 3.4 凭证准备（macOS Keychain）

| 服务名 | 账号 | 用途 | 配置状态 |
|--------|-----|------|---------|
| `openclaw-browser-oliver-ones-username` | ONES 账号密码 | Oliver 下载 ONES 数据 | ⬜ |
| `openclaw-browser-ella-oa-username` | OA 账号密码 | Ella OA 审批 | ⬜ |
| `openclaw-email-iris-password` | 邮箱密码 | Iris 邮件管理 | ⬜ |

配置命令示例：
```bash
security add-generic-password -a "your-account" -s "openclaw-email-iris-password" -w "your-password"
```

---

## 📦 四、需要 Rex 提供的测试数据

请准备以下测试数据（可提供真实或脱敏数据）：

| # | 数据名称 | 用途 | 技能 | 优先级 |
|---|---------|-----|------|--------|
| 1 | **测试合同 PDF** (1-2 份) | 条款拆分、风险识别 | contract-clause-split | 🔴 高 |
| 2 | **测试合同 Word** (1-2 份) | 条款拆分、风险识别 | contract-clause-split | 🔴 高 |
| 3 | **经营数据 Excel** | 周报/月报生成、KPI计算 | business-report-generator | 🔴 高 |
| 4 | **邮箱账号配置** | 邮件收发测试 | email-management | 🔴 高 |
| 5 | **OA 系统访问地址** | OA 审批流程测试 | oa-approval | 🟡 中 |
| 6 | **ONES 系统访问地址** | 项目数据下载测试 | ones-data-download | 🟡 中 |
| 7 | **测试邮箱附件** | 附件导出功能测试 | email-management | 🟡 低 |

---

## 🚀 五、第一阶段：单技能功能测试

> **目标**: 验证每个技能独立运行正常

---

### 🧪 测试 1: email-management（邮件管理）

**负责 Agent**: Iris 🐦‍⬛  
**优先级**: 🔴 高  
**预计时间**: 30 分钟

| 测试用例 ID | 测试步骤 | 预期结果 | 测试状态 |
|------------|---------|---------|---------|
| **EM-001** | 运行 `python scripts/email_manager.py --action test-connection` | ✅ IMAP 连接成功，无报错 | ⬜ 待测试 |
| **EM-002** | 运行 `python scripts/email_manager.py --action check --limit 5` | ✅ 获取最新 5 封邮件列表<br>✅ 显示发件人、主题、日期 | ⬜ 待测试 |
| **EM-003** | 运行分类规则测试：`python scripts/email_manager.py --action test-classification --sample "【OA审批提醒】合同待审批"` | ✅ 正确分类为 P0 审批提醒 | ⬜ 待测试 |
| **EM-004** | 运行分类规则测试：`python scripts/email_manager.py --action test-classification --sample "项目进度周报"` | ✅ 正确分类为 P1 工作邮件 | ⬜ 待测试 |
| **EM-005** | 检查邮件获取时的人类延迟 | ✅ 每封邮件分析间隔 1-3 秒<br>✅ 不是立即返回 | ⬜ 待测试 |
| **EM-006** | 发送邮件功能（可选） | ✅ 弹出用户确认提示<br>✅ 确认后邮件发送成功 | ⬜ 待测试 |

**安全规则验证点**:
- ✅ 必须用户主动发起，无自动调用
- ✅ 读取邮件有人类延迟模拟
- ✅ 配置中无明文密码，全部走 Keychain

---

### 🧪 测试 2: business-report-generator（经营报告）

**负责 Agent**: Aaron 🦉  
**优先级**: 🔴 高  
**预计时间**: 30 分钟

| 测试用例 ID | 测试步骤 | 预期结果 | 测试状态 |
|------------|---------|---------|---------|
| **BR-001** | 运行模板系统测试：`python scripts/generate_report.py --test-template` | ✅ 配置加载成功，无报错 | ⬜ 待测试 |
| **BR-002** | 使用模拟数据生成周报预览：`python scripts/generate_report.py --type weekly --sample --preview` | ✅ 生成完整 Markdown 报告结构<br>✅ 包含：执行摘要、数据分析、项目进度、风险、计划 | ⬜ 待测试 |
| **BR-003** | 使用真实 Excel 数据生成数据报告：`python scripts/generate_report.py --type data --data 测试数据.xlsx --preview` | ✅ 数据加载成功<br>✅ KPI 计算正确<br>✅ 报告内容与数据一致 | ⬜ 待测试 |
| **BR-004** | 导出 Word 格式报告：`python scripts/generate_report.py --type weekly --sample` | ✅ 生成 .docx 文件<br>✅ Word 可正常打开<br>✅ 包含基本格式（标题、段落、列表） | ⬜ 待测试 |
| **BR-005** | 检查报告生成时的人类延迟 | ✅ 每个章节生成间隔 3-10 秒<br>✅ 不是瞬间完成 | ⬜ 待测试 |

**安全规则验证点**:
- ✅ 必须用户主动发起
- ✅ 数据本地处理，不上传第三方
- ✅ 生成过程有人类思考延迟模拟

---

### 🧪 测试 3: contract-clause-split（合同条款拆分）

**负责 Agent**: Ella 🦊  
**优先级**: 🔴 高  
**预计时间**: 30 分钟

| 测试用例 ID | 测试步骤 | 预期结果 | 测试状态 |
|------------|---------|---------|---------|
| **CC-001** | 解析 PDF 合同：`python scripts/split_contract.py --file 测试合同.pdf --preview` | ✅ PDF 解析成功<br>✅ 文本内容正确提取 | ⬜ 待测试 |
| **CC-002** | 解析 Word 合同：`python scripts/split_contract.py --file 测试合同.docx --preview` | ✅ Word 解析成功<br>✅ 文本内容正确提取 | ⬜ 待测试 |
| **CC-003** | 条款拆分功能验证 | ✅ 合同被拆分为多个独立条款<br>✅ 条款边界识别正确 | ⬜ 待测试 |
| **CC-004** | 条款分类功能验证 | ✅ 每个条款被正确分类（基本信息/双方权利义务/违约责任等） | ⬜ 待测试 |
| **CC-005** | 关键信息提取验证 | ✅ 正确提取合同金额<br>✅ 正确提取合同日期<br>✅ 正确提取甲乙双方 | ⬜ 待测试 |
| **CC-006** | 风险条款识别验证（可选） | ✅ 标注高风险条款并说明原因 | ⬜ 待测试 |
| **CC-007** | JSON 格式导出验证 | ✅ 导出结构化 JSON，格式正确可解析 | ⬜ 待测试 |
| **CC-008** | 检查条款分析时的人类延迟 | ✅ 每条分析间隔 3-8 秒 | ⬜ 待测试 |

**安全规则验证点**:
- ✅ 必须用户主动发起
- ✅ 敏感合同数据本地处理
- ✅ 条款分析有人类阅读延迟

---

### 🧪 测试 4: oa-approval（OA 审批）

**负责 Agent**: Ella 🦊  
**优先级**: 🟡 中  
**预计时间**: 40 分钟

| 测试用例 ID | 测试步骤 | 预期结果 | 测试状态 |
|------------|---------|---------|---------|
| **OA-001** | 运行登录测试（无头模式）：`python scripts/oa_approval.py --action test-login` | ✅ 浏览器启动<br>✅ 成功加载 OA 登录页<br>✅ （如需验证码）提示交互式模式 | ⬜ 待测试 |
| **OA-002** | 运行交互式登录测试：`python scripts/oa_approval.py --action test-login --interactive` | ✅ 显示浏览器窗口<br>✅ 可手动输入验证码完成登录 | ⬜ 待测试 |
| **OA-003** | 登录后获取待审批列表：`python scripts/oa_approval.py --action list --interactive` | ✅ 成功进入待审批页面<br>✅ 获取待审批合同清单 | ⬜ 待测试 |
| **OA-004** | 查看单个合同详情 | ✅ 成功进入合同详情页<br>✅ 正确提取合同关键信息 | ⬜ 待测试 |
| **OA-005** | 审批操作测试（可选真实审批） | ✅ 弹出用户二次确认<br>✅ 确认后填写审批意见<br>✅ 点击审批按钮<br>✅ 验证审批成功 | ⬜ 待测试 |
| **OA-006** | 检查操作延迟 | ✅ 页面切换间隔 2-5 秒<br>✅ 打字有间隔（不是瞬间输入） | ⬜ 待测试 |

**安全规则验证点**:
- ✅ 必须用户主动发起
- ✅ 审批操作有二次确认
- ✅ 不支持批量审批（每次只能处理 1 个）
- ✅ 操作过程模拟人类速度

---

### 🧪 测试 5: ones-data-download（ONES 数据下载）

**负责 Agent**: Oliver 🐘  
**优先级**: 🟡 中  
**预计时间**: 40 分钟

| 测试用例 ID | 测试步骤 | 预期结果 | 测试状态 |
|------------|---------|---------|---------|
| **ONES-001** | 配置文件验证 | ✅ 配置文件存在且格式正确<br>✅ 筛选器配置正确 | ⬜ 待测试 |
| **ONES-002** | 登录测试（交互式）：`python scripts/download_ones_data.py --interactive-login` | ✅ 浏览器启动并加载 ONES 登录页<br>✅ 登录成功 | ⬜ 待测试 |
| **ONES-003** | 下载单个筛选器数据 | ✅ 成功进入筛选器页面<br>✅ 数据正确提取<br>✅ 生成 CSV/Excel 文件<br>✅ 文件内容与页面一致 | ⬜ 待测试 |
| **ONES-004** | JSON 格式导出 | ✅ 生成结构化 JSON 文件<br>✅ 格式正确可解析 | ⬜ 待测试 |
| **ONES-005** | 检查操作延迟 | ✅ 页面操作有合理延迟<br>✅ 不是瞬间完成 | ⬜ 待测试 |

**安全规则验证点**:
- ✅ 必须用户主动发起
- ✅ 操作过程模拟人类速度

---

## 🔗 六、第二阶段：集成测试

> **目标**: 验证系统级流程和协作机制

| 测试用例 ID | 测试场景 | 测试步骤 | 预期结果 | 测试状态 |
|------------|---------|---------|---------|---------|
| **INT-001** | Provider 智能路由 - 邮件场景 | 1. 触发邮件检查任务<br>2. 观察日志中使用的 Provider | ✅ 自动选择 DeepSeek<br>❌ 不使用 Volcengine/百炼 | ⬜ 待测试 |
| **INT-002** | Provider 智能路由 - 编程场景 | 1. 用户发起编程相关对话<br>2. 观察日志中使用的 Provider | ✅ 优先使用 Volcengine | ⬜ 待测试 |
| **INT-003** | Jerry 任务分发 | 1. 用户说"帮我拆分这份合同"<br>2. 观察任务流向 | ✅ Jerry 自动分发给 Ella<br>✅ Ella 正确执行 | ⬜ 待测试 |
| **INT-004** | Jerry 任务分发 2 | 1. 用户说"帮我生成周报"<br>2. 观察任务流向 | ✅ Jerry 自动分发给 Aaron<br>✅ Aaron 正确执行 | ⬜ 待测试 |
| **INT-005** | Cron 提醒不自动执行 | 1. 触发 Cron 提醒时间<br>2. 观察系统行为 | ✅ 只发送提醒消息<br>❌ 不实际执行任何操作<br>✅ 等用户回复确认后才执行 | ⬜ 待测试 |

---

## 🛡️ 七、第三阶段：安全规则验证

> **目标**: 验证所有风控和安全规则有效执行

| 测试用例 ID | 测试场景 | 测试步骤 | 预期结果 | 测试状态 |
|------------|---------|---------|---------|---------|
| **SEC-001** | 高风险 Provider 时间窗口限制（可选验证） | 1. 在非工作时间（22:00-09:00）尝试调用 Volcengine | ✅ 自动切换到 DeepSeek<br>❌ 不调用 Volcengine | ⬜ 待测试 |
| **SEC-002** | 凭证安全验证 | 1. 检查所有配置文件 | ✅ 配置文件中无明文密码<br>✅ 全部通过 Keychain 读取 | ⬜ 待测试 |
| **SEC-003** | 人类延迟一致性验证 | 1. 连续执行 5 次相同的模型调用<br>2. 记录每次耗时 | ✅ 每次调用间隔随机<br>✅ 不是固定间隔<br>✅ 不是零延迟 | ⬜ 待测试 |
| **SEC-004** | 百炼账号保护验证 | 1. 尝试触发自动化场景使用百炼 | ✅ 拒绝使用百炼<br>✅ 自动切换到 DeepSeek | ⬜ 待测试 |

---

## ✅ 八、测试通过标准

### 8.1 单技能通过标准

| 等级 | 通过标准 |
|------|---------|
| 🟢 **P0 功能全部通过** | 所有 🔴 高优先级测试用例全部通过 |
| 🟡 **P1 功能 ≥ 80% 通过** | 中优先级测试用例通过率 ≥ 80% |
| ⚪ **P2 功能无严重阻塞** | 低优先级用例可有不影响核心流程的问题 |

### 8.2 系统级通过标准

1. ✅ 所有安全规则验证通过
2. ✅ Agent 间任务分发准确无误
3. ✅ Provider 路由逻辑正确
4. ✅ 无明文密码泄露
5. ✅ 所有自动化场景正确使用 DeepSeek

---

## ⚠️ 九、风险与注意事项

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| **测试环境访问限制** | 无法访问内网 OA/ONES 系统 | 优先测试不需要内网的技能（合同拆分、报告生成） |
| **生产数据敏感性** | 真实合同/经营数据安全 | 使用脱敏测试数据，测试完成立即删除 |
| **验证码拦截** | OA/ONES 登录需要验证码 | 使用交互式模式，手动输入验证码 |
| **API 限流** | 大模型调用频繁被限流 | 降低测试频率，遵守调用间隔规则 |

---

## 📊 十、测试结果记录表模板

| 测试用例 ID | 测试日期 | 测试人员 | 测试结果 (✅/❌/⚠️) | 备注 / Bug 描述 |
|------------|---------|---------|-------------------|---------------|
| EM-001 | | | | |
| EM-002 | | | | |
| BR-001 | | | | |
| ... | | | | |

---

## 🎬 十一、测试启动检查清单

开始测试前，请确认：

| # | 检查项 | 状态 |
|---|-------|------|
| 1 | ✅ 所有 Python 依赖包已安装 | ⬜ |
| 2 | ✅ Playwright Chromium 已安装 | ⬜ |
| 3 | ✅ 所有配置文件从 template 复制并填写 | ⬜ |
| 4 | ✅ 所有密码已存入 Keychain | ⬜ |
| 5 | ✅ 测试数据文件已准备 | ⬜ |
| 6 | ✅ 所有 Provider API Key 配置正确且可用 | ⬜ |
| 7 | ✅ 网络可访问各业务系统（OA/ONES/邮箱） | ⬜ |

---

**文档版本**: v1.0  
**最后更新**: 2026-04-23
