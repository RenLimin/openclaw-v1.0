# OA 合同审批技能

> 通过浏览器自动化操作泛微 OA 系统，完成合同审批流程。
> ⚠️ **安全规则**: 必须由用户主动触发，禁止任何自动化/定时调用！

---

## 👤 负责 Agent

**Ella 🦊** (合同管理专家)

---

## 🚀 触发条件

当用户需要：
- 查看 OA 待审批合同列表
- 审批/驳回指定合同
- 查看合同审批详情
- 查询合同审批进度

---

## ⚠️ 大模型使用安全规则

| 规则 | 要求 |
|------|------|
| **触发方式** | ✅ **必须用户主动发起**，禁止自动触发 |
| **推荐 Provider** | 🟢 **DeepSeek**（浏览器自动化场景） |
| **并发控制** | 同时最多处理 1 个审批 |
| **调用间隔** | 每次页面操作间隔 2-5 秒（模拟人类操作） |
| **错误重试** | 最多重试 2 次，每次间隔 5-10 秒 |
| **工作时间** | 建议 9:00-18:00 执行，符合人类办公规律 |

---

## 📋 功能清单

| 功能 | 说明 |
|------|------|
| 🔍 **待审批列表** | 获取当前用户的待审批合同清单 |
| ✅ **合同审批** | 审批通过指定合同 |
| ❌ **合同驳回** | 驳回指定合同并填写原因 |
| 📄 **详情查看** | 查看合同完整信息和审批历史 |
| 🔗 **跳转审批** | 从邮件链接直接跳转到审批页面 |
| 📥 **合同附件下载** | 自动下载合同相关附件（PDF/Word/Excel等） |

---

## 🔧 使用方法

### 合同审批功能

#### 1. 获取待审批列表

```bash
python3 scripts/oa_approval.py --action list
```

### 2. 审批合同

```bash
python3 scripts/oa_approval.py --action approve --id <合同ID> --comment "同意"
```

### 3. 驳回合同

```bash
python3 scripts/oa_approval.py --action reject --id <合同ID> --comment "原因：XXX"
```

### 4. 查看详情

```bash
python3 scripts/oa_approval.py --action detail --id <合同ID>
```

#### 5. 交互式模式（处理验证码）

```bash
python3 scripts/oa_approval.py --action list --interactive
```

---

### 合同附件下载功能

#### 1. 按合同编号下载

```bash
python3 scripts/oa_file_downloader.py --contract-code HT-2026-00123
```

#### 2. 按审批流程ID下载

```bash
python3 scripts/oa_file_downloader.py --request-id 123456
```

#### 3. 按标题关键词搜索下载（首个匹配）

```bash
python3 scripts/oa_file_downloader.py --keyword "采购合同"
```

#### 4. 批量下载（从文件读取合同编号列表）

```bash
python3 scripts/oa_file_downloader.py --batch contracts.txt
```

文件格式（每行一个合同编号）：
```
HT-2026-001
HT-2026-002
HT-2026-003
```

#### 5. 指定保存目录

```bash
python3 scripts/oa_file_downloader.py --contract-code HT-2026-00123 --output-dir ./my-contracts/
```

#### 6. 仅提取元信息不下载文件

```bash
python3 scripts/oa_file_downloader.py --contract-code HT-2026-00123 --metadata-only
```

#### 7. 显示浏览器窗口（调试用）

```bash
python3 scripts/oa_file_downloader.py --contract-code HT-2026-00123 --show-browser
```

---

### 🍪 一键 Cookie 获取工具（推荐！）

**解决验证码痛点：只需手动完成一次，永久使用！**

#### 为什么需要？
- OA 登录有多种验证码（图片、滑块、文字点选）
- 自动化难以 100% 破解所有验证码类型
- 最优解：一次手动验证 + 永久会话恢复

#### 使用方法

```bash
python3 scripts/get_oa_cookie.py
```

#### 执行流程

```
1. 脚本自动打开浏览器
2. 自动填写用户名 + 密码
3. ⚠️ 用户手动完成验证码（图片/滑块/点选）
4. 用户点击"登录"按钮
5. 脚本自动调用 jumpSystem API 完成 SSO
6. 自动保存 Cookie + Storage State
7. 下次登录直接恢复，无需再输验证码！
```

#### 保存的文件

| 文件 | 路径 | 说明 |
|------|------|------|
| Storage State | `~/.openclaw/cache/oa_storage_state.json` | ✅ 推荐，一键恢复所有状态 |
| Cookie 文件 | `~/.openclaw/cache/oa_cookies.json` | 原始 Cookie 列表 |
| 完整状态 | `~/.openclaw/cache/oa_full_state.json` | Cookie + localStorage |

#### 有效期
| 组件 | 有效期 | 过期处理 |
|------|--------|---------|
| IAM Token | ~ 2 小时 | 自动重新获取 |
| OA Session | ~ 24 小时 | 重新运行脚本 |

#### 与审批脚本无缝集成

`oa_approval_v2.py` 启动时会自动检测并加载已保存的会话状态：

```python
# 自动恢复会话
if storage_state_path.exists():
    context = browser.new_context(storage_state=storage_state_path)
    logger.info("🔄 恢复已保存的会话状态")
```

---

## ⚙️ 配置说明

### 配置文件位置

`config/oa-config.json`

| 配置项 | 说明 |
|--------|------|
| `oa_url` | OA 系统登录地址 |
| `auth.username` | 登录用户名 |
| `selectors` | 页面元素选择器配置 |
| `timeout.page_load` | 页面加载超时时间（秒） |
| `timeout.element_wait` | 元素等待超时时间（秒） |

### 下载配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `download.save_dir` | 文件保存目录 | `~/Downloads/OA_Contracts/` |
| `download.auto_rename` | 是否自动重命名文件 | `true` |
| `download.naming_pattern` | 文件命名模板 | `{contract_code}_{filename}_{timestamp}` |
| `download.retry_count` | 下载失败重试次数 | `3` |
| `download.retry_delay` | 重试间隔（秒） | `5` |
| `download.max_file_size` | 文件大小告警阈值（MB） | `100` |

### 凭证管理

密码存储在 macOS Keychain 中：

```bash
# 服务名: openclaw-browser-ella-oa-username
# 读取密码
security find-generic-password -s "openclaw-browser-ella-oa-username" -w
```

---

## 📝 标准操作流程 (SOP)

### 合同审批流程

```
1. 用户发起审批请求
   │
   ▼
2. 打开 OA 系统并登录
   │  └── 如遇验证码 → 提示用户手动处理
   │
   ▼
3. 进入待审批列表页面
   │  └── 等待 2-3 秒（模拟人类查看）
   │
   ▼
4. 获取待审批合同清单并展示给用户确认
   │  └── 用户确认后才继续
   │
   ▼
5. 点击进入具体合同详情页
   │  └── 等待 3-5 秒（模拟人类阅读）
   │
   ▼
6. 填写审批意见
   │  └── 打字间隔 0.1-0.3 秒/字符
   │
   ▼
7. 点击审批/驳回按钮
   │
   ▼
8. 确认操作结果并反馈给用户
```

---

## ⚠️ 注意事项

1. **必须用户确认**: 执行任何审批操作前，必须展示合同详情并获得用户明确确认
2. **验证码处理**: 遇到图形/短信验证码时，自动切换到交互式模式并提示用户
3. **操作可追溯**: 所有操作记录完整日志（时间、操作人、合同ID、结果）
4. **异常回滚**: 操作失败时自动截图并保存当前页面状态
5. **不批量操作**: 每次只处理一个合同审批，不支持批量操作

---

## 📦 依赖

- Python 3.8+
- `playwright` (浏览器自动化)
- `beautifulsoup4` (HTML 解析)
- `pyobjc` (macOS Keychain 访问)

```bash
pip install playwright beautifulsoup4 pyobjc
playwright install chromium
```

---

## 🧪 测试命令

```bash
# 测试登录功能
python3 scripts/oa_approval.py --action test-login --interactive

# 测试获取待审批列表
python3 scripts/oa_approval.py --action list --interactive
```

---

---

## 📊 输出文件说明

下载完成后自动生成以下报告文件：

| 文件名 | 说明 |
|--------|------|
| `download_report_YYYYMMDD_HHMMSS.json` | 下载报告，包含成功/失败统计、文件列表、错误信息 |
| `contract_metadata_YYYYMMDD_HHMMSS.json` | 合同元信息，包含合同名称、甲乙双方、金额、状态等 |

### 下载报告示例

```json
{
  "start_time": "2026-04-24T15:30:00",
  "end_time": "2026-04-24T15:32:00",
  "total_files": 5,
  "success_files": 4,
  "failed_files": 1,
  "files": [...],
  "errors": [...]
}
```

---

## 📦 依赖

- Python 3.8+
- `playwright` (浏览器自动化)

```bash
pip install playwright
playwright install chromium
```

---

_创建时间: 2026-04-23 | 更新时间: 2026-04-24 | 版本: v1.1 | 作者: Ella 🦊_
