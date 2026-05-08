# 浏览器自动化优化方案（v2.0 升级）

> **背景**: v1.0 时浏览器自动化遇到重大挑战，需要针对以下场景进行优化：
> 1. 独立 Chromium 环境、账号隔离（默认读取 keychain 记录并自动登录）
> 2. Vue 与 JavaScript 处理能力，视觉识别能力

---

## 一、问题分析（v1.0 教训）

### 1.1 v1.0 遇到的挑战

| 挑战 | 影响 | 根本原因 |
|------|------|---------|
| 多 Agent 共享浏览器 | 账号冲突、状态污染 | 无独立环境隔离 |
| 登录状态丢失 | 每次重新登录 | 无持久化 Cookie 管理 |
| Vue SPA 页面识别失败 | 元素未渲染就操作 | 未等待 Vue 挂载完成 |
| 动态内容抓取不完整 | 数据缺失 | 未等待异步加载完成 |
| 复杂页面理解困难 | 误操作 | 缺乏视觉识别能力 |

### 1.2 v1.0 经验教训

- **必须**为每个 Agent 创建独立的浏览器环境
- **必须**持久化登录状态（Cookie/LocalStorage）
- **必须**等待 Vue/React 框架挂载完成
- **必须**结合视觉识别理解页面，不仅依赖 DOM

---

## 二、解决方案架构

### 2.1 独立 Chromium 环境

```
Chromium 主实例
├── BrowserContext: jerry-context (Jerry 专属)
│   ├── userDataDir: ~/.openclaw/browser-data/jerry/
│   ├── Cookies: 持久化
│   ├── LocalStorage: 持久化
│   └── 自动登录: 从 Keychain 读取凭证
│
├── BrowserContext: ella-context (Ella 专属)
│   ├── userDataDir: ~/.openclaw/browser-data/ella/
│   └── ...
│
├── BrowserContext: oliver-context (Oliver 专属)
│   └── ...
│
├── BrowserContext: aaron-context (Aaron 专属)
│   └── ...
│
└── BrowserContext: iris-context (Iris 专属)
    └── ...
```

### 2.2 Keychain 集成

```
Keychain (macOS)
├── openclaw-browser-{agent}-{site}-username
├── openclaw-browser-{agent}-{site}-password
└── openclaw-browser-{agent}-{site}-cookie (可选)

示例:
├── openclaw-browser-ella-oa-username → ella@company.com
├── openclaw-browser-ella-oa-password → (加密存储)
├── openclaw-browser-oliver-ones-username → oliver@company.com
└── ...
```

### 2.3 Vue/SPA 处理策略

```javascript
// Vue 应用等待策略
async function waitForVue(page, timeout = 10000) {
  await page.waitForFunction(() => {
    // 检测 Vue 3
    if (window.__VUE__) return true;
    // 检测 Vue 2
    if (window.__VUE_DEVTOOLS_GLOBAL_HOOK__) return true;
    // 检测 nuxt
    if (window.__NUXT__) return true;
    // 检测常见 Vue 应用根节点
    const app = document.querySelector('#app');
    return app && app.children.length > 0;
  }, { timeout });
}

// React 应用等待策略
async function waitForReact(page, timeout = 10000) {
  await page.waitForFunction(() => {
    // 检测 React
    const root = document.querySelector('#root');
    return root && root.children.length > 0;
  }, { timeout });
}

// 通用 SPA 等待
async function waitForSPA(page, framework = 'auto', timeout = 15000) {
  if (framework === 'vue' || framework === 'auto') {
    try { await waitForVue(page, timeout); return 'vue'; } catch {}
  }
  if (framework === 'react' || framework === 'auto') {
    try { await waitForReact(page, timeout); return 'react'; } catch {}
  }
  // Fallback: wait for network idle
  await page.waitForLoadState('networkidle');
  return 'unknown';
}
```

### 2.4 视觉识别能力

```
页面理解流程:
1. Playwright 截图 → 保存为 PNG
2. 调用百炼视觉模型 (kimi-k2.5) → 识别页面内容
3. 结合 DOM 信息 → 完整理解页面
4. 决定下一步操作

适用场景:
- 复杂布局识别
- 验证码识别（简单）
- 图表/图形理解
- 动态元素定位
- 页面状态确认
```

---

## 三、实现方案

### 3.1 浏览器环境管理脚本

```python
# scripts/browser-env-manager.py
import os
import subprocess
import json
from playwright.sync_api import sync_playwright

class BrowserEnvironment:
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.user_data_dir = os.path.expanduser(
            f"~/.openclaw/browser-data/{agent_name}/"
        )
        self.browser = None
        self.context = None
        self.page = None
    
    def launch(self, headless=True):
        """启动独立浏览器环境"""
        os.makedirs(self.user_data_dir, exist_ok=True)
        
        p = sync_playwright().start()
        self.browser = p.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox'
            ]
        )
        self.context = self.browser
        self.page = self.context.new_page()
        return self
    
    def load_keychain_credentials(self, site):
        """从 Keychain 加载凭证并自动登录"""
        try:
            # macOS Keychain 读取
            cmd = f'security find-generic-password -s "openclaw-browser-{self.agent_name}-{site}-username" -w'
            username = subprocess.check_output(cmd, shell=True, text=True).strip()
            
            cmd = f'security find-generic-password -s "openclaw-browser-{self.agent_name}-{site}-password" -w'
            password = subprocess.check_output(cmd, shell=True, text=True).strip()
            
            return {"username": username, "password": password}
        except subprocess.CalledProcessError:
            return None
    
    def auto_login(self, site, login_url, username_field, password_field, submit_selector):
        """自动登录流程"""
        creds = self.load_keychain_credentials(site)
        if not creds:
            print(f"⚠️ 未找到 {site} 的 Keychain 凭证")
            return False
        
        self.page.goto(login_url, wait_until="networkidle")
        self.page.fill(username_field, creds["username"])
        self.page.fill(password_field, creds["password"])
        self.page.click(submit_selector)
        self.page.wait_for_load_state("networkidle")
        
        # 保存 Cookie
        cookies = self.context.cookies()
        with open(f"{self.user_data_dir}/{site}-cookies.json", "w") as f:
            json.dump(cookies, f)
        
        print(f"✅ {site} 登录成功，Cookie 已保存")
        return True
    
    def wait_for_vue(self, timeout=10000):
        """等待 Vue 应用挂载"""
        self.page.wait_for_function("""
            () => {
                // Vue 3
                if (window.__VUE__) return true;
                // Vue 2
                if (window.__VUE_DEVTOOLS_GLOBAL_HOOK__) return true;
                // Nuxt
                if (window.__NUXT__) return true;
                // Common Vue root
                const app = document.querySelector('#app');
                return app && app.children.length > 0;
            }
        """, timeout=timeout)
    
    def wait_for_react(self, timeout=10000):
        """等待 React 应用挂载"""
        self.page.wait_for_function("""
            () => {
                const root = document.querySelector('#root');
                return root && root.children.length > 0;
            }
        """, timeout=timeout)
    
    def wait_for_spa(self, framework='auto', timeout=15000):
        """通用 SPA 等待"""
        try:
            if framework in ('vue', 'auto'):
                self.wait_for_vue(timeout)
                return 'vue'
        except:
            pass
        
        try:
            if framework in ('react', 'auto'):
                self.wait_for_react(timeout)
                return 'react'
        except:
            pass
        
        # Fallback
        self.page.wait_for_load_state('networkidle')
        return 'unknown'
    
    def visual_analyze(self, prompt="请描述这个页面的内容和布局。"):
        """视觉识别分析"""
        import base64
        import requests
        
        # 截图
        screenshot_path = f"/tmp/{self.agent_name}-screenshot.png"
        self.page.screenshot(path=screenshot_path, full_page=True)
        
        # 读取图片
        with open(screenshot_path, "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        # 调用百炼视觉模型
        api_key = "sk-sp-a68df77f47f04e1ca871300f7afa41f1"
        url = "https://coding.dashscope.aliyuncs.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "kimi-k2.5",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
                ]
            }],
            "max_tokens": 1000
        }
        
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        return None
    
    def smart_click(self, text_or_description):
        """智能点击：结合 DOM 和视觉识别"""
        # 先尝试 DOM 查找
        try:
            self.page.get_by_text(text_or_description).click()
            return True
        except:
            pass
        
        # DOM 失败，使用视觉识别
        analysis = self.visual_analyze(f"请找出包含'{text_or_description}'的可点击元素位置。")
        if analysis:
            print(f"🔍 视觉识别结果: {analysis}")
            # 可以进一步结合坐标点击
        return False
    
    def close(self):
        """关闭浏览器环境"""
        if self.context:
            self.context.close()
```

### 3.2 Keychain 凭证管理

```bash
#!/bin/bash
# scripts/keychain-browser.sh

# 存储浏览器凭证
store_credential() {
    local agent=$1
    local site=$2
    local username=$3
    local password=$4
    
    security add-generic-password \
        -s "openclaw-browser-${agent}-${site}-username" \
        -a "${agent}" \
        -w "${username}" \
        -U
    
    security add-generic-password \
        -s "openclaw-browser-${agent}-${site}-password" \
        -a "${agent}" \
        -w "${password}" \
        -U
    
    echo "✅ 已存储 ${agent}/${site} 的凭证"
}

# 读取浏览器凭证
get_credential() {
    local agent=$1
    local site=$2
    
    local username=$(security find-generic-password \
        -s "openclaw-browser-${agent}-${site}-username" \
        -w 2>/dev/null)
    
    local password=$(security find-generic-password \
        -s "openclaw-browser-${agent}-${site}-password" \
        -w 2>/dev/null)
    
    if [ -n "$username" ] && [ -n "$password" ]; then
        echo "{\"username\":\"${username}\",\"password\":\"${password}\"}"
    else
        echo "null"
    fi
}

# 列出所有浏览器凭证
list_credentials() {
    security find-generic-password -l "openclaw-browser" 2>/dev/null | grep -o '"openclaw-browser-[^"]*"' | sort -u
}
```

### 3.3 Vue/SPA 专用测试脚本

```python
# scripts/browser-vue-test.py
"""测试 Vue/SPA 处理能力"""
from playwright.sync_api import sync_playwright

def test_vue_app():
    """测试 Vue 应用等待和交互"""
    print("🧪 测试 Vue 应用处理...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # 导航到 Vue 应用
        page.goto("https://vuejs.org/", wait_until="domcontentloaded")
        
        # 等待 Vue 挂载
        page.wait_for_function("""
            () => {
                return window.__VUE__ || 
                       (document.querySelector('#app') && 
                        document.querySelector('#app').children.length > 0);
            }
        """, timeout=10000)
        
        # 验证内容已渲染
        title = page.inner_text("h1")
        print(f"  页面标题: {title}")
        
        # 测试动态内容等待
        page.goto("https://example.com/", wait_until="networkidle")
        content = page.inner_text("body")[:100]
        print(f"  内容预览: {content}")
        
        browser.close()
        print("  ✅ Vue 应用测试通过")
        return True

def test_javascript_execution():
    """测试 JavaScript 执行能力"""
    print("\n📜 测试 JavaScript 执行...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto("https://example.com/")
        
        # 执行 JavaScript
        result = page.evaluate("""() => {
            return {
                title: document.title,
                url: window.location.href,
                hasVue: !!window.__VUE__,
                hasReact: !!window.__REACT_DEVTOOLS_GLOBAL_HOOK__,
                cookies: document.cookie
            };
        }""")
        
        print(f"  JavaScript 执行结果:")
        for k, v in result.items():
            print(f"    {k}: {v}")
        
        browser.close()
        print("  ✅ JavaScript 执行测试通过")
        return True

def test_visual_recognition():
    """测试视觉识别能力"""
    print("\n👁️ 测试视觉识别...")
    
    import base64
    import requests
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto("https://example.com/")
        
        # 截图
        screenshot_path = "/tmp/browser-vue-visual.png"
        page.screenshot(path=screenshot_path, full_page=True)
        
        # 读取图片
        with open(screenshot_path, "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        # 调用百炼视觉模型
        api_key = "sk-sp-a68df77f47f04e1ca871300f7afa41f1"
        url = "https://coding.dashscope.aliyuncs.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "kimi-k2.5",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": "请描述这个网页的内容和布局。"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
                ]
            }],
            "max_tokens": 500
        }
        
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            analysis = resp.json()["choices"][0]["message"]["content"]
            print(f"  视觉识别结果: {analysis[:200]}...")
            print("  ✅ 视觉识别测试通过")
            result = True
        else:
            print(f"  ❌ 视觉识别失败: {resp.status_code}")
            result = False
        
        browser.close()
        return result

if __name__ == "__main__":
    print("=" * 50)
    print("浏览器自动化 v2.0 优化测试")
    print("=" * 50)
    
    results = {}
    results["vue_app"] = "✅ 通过" if test_vue_app() else "❌ 失败"
    results["js_execution"] = "✅ 通过" if test_javascript_execution() else "❌ 失败"
    results["visual_recognition"] = "✅ 通过" if test_visual_recognition() else "❌ 失败"
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    for k, v in results.items():
        print(f"  {k}: {v}")
    print("=" * 50)
```

---

## 四、Agent 浏览器配置

### 4.1 各 Agent 浏览器配置

| Agent | 网站 | Keychain 条目 | 用途 |
|-------|------|--------------|------|
| **Ella 🦊** | 泛微 OA | `openclaw-browser-ella-oa-*` | 合同审批 |
| **Ella 🦊** | 合同系统 | `openclaw-browser-ella-contract-*` | 合同管理 |
| **Oliver 🐘** | ONES | `openclaw-browser-oliver-ones-*` | 项目管理 |
| **Aaron 🦉** | 报表系统 | `openclaw-browser-aaron-report-*` | 经营分析 |
| **Iris 🐦‍⬛** | 邮箱 | `openclaw-browser-iris-email-*` | 邮件管理 |
| **Jerry 🦞** | 管理后台 | `openclaw-browser-jerry-admin-*` | 团队协调 |

### 4.2 配置写入

```bash
# 为每个 Agent 创建浏览器数据目录
mkdir -p ~/.openclaw/browser-data/{jerry,ella,oliver,aaron,iris}

# 示例：存储 Ella 的 OA 凭证
security add-generic-password \
    -s "openclaw-browser-ella-oa-username" \
    -a "ella" \
    -w "ella@company.com" \
    -U

security add-generic-password \
    -s "openclaw-browser-ella-oa-password" \
    -a "ella" \
    -w "password_here" \
    -U
```

---

## 五、执行计划

### 5.1 Phase A: 环境搭建

| 步骤 | 操作 | 预期输出 |
|------|------|---------|
| 1 | 创建浏览器数据目录 | `~/.openclaw/browser-data/{5 agents}/` |
| 2 | 安装 browser-env-manager.py | `scripts/browser-env-manager.py` |
| 3 | 安装 keychain-browser.sh | `scripts/keychain-browser.sh` |
| 4 | 测试独立环境启动 | 5 个独立浏览器上下文 |

### 5.2 Phase B: Vue/SPA 处理

| 步骤 | 操作 | 预期输出 |
|------|------|---------|
| 1 | 安装 browser-vue-test.py | `scripts/browser-vue-test.py` |
| 2 | 测试 Vue 应用等待 | 正确等待 Vue 挂载 |
| 3 | 测试 JavaScript 执行 | 正确执行 JS 并获取结果 |
| 4 | 测试视觉识别 | 百炼视觉模型识别页面 |

### 5.3 Phase C: 凭证管理

| 步骤 | 操作 | 预期输出 |
|------|------|---------|
| 1 | 创建 Keychain 条目 | 各 Agent 网站凭证 |
| 2 | 测试自动登录 | Cookie 持久化 |
| 3 | 测试 Cookie 恢复 | 无需重复登录 |

---

## 六、验收标准

| 能力 | 验收项 | 通过标准 |
|------|--------|---------|
| 环境隔离 | 5 个独立上下文 | 无状态交叉 |
| 凭证管理 | Keychain 读写 | 正确存取 |
| 自动登录 | Cookie 保存/恢复 | 无需重复输入 |
| Vue 处理 | 等待挂载完成 | 元素可交互 |
| JS 执行 | 执行并获取结果 | 结果正确 |
| 视觉识别 | 页面理解 | 准确描述内容 |

---

## 七、风险评估

| 风险 | 影响 | 可能性 | 应对 |
|------|------|--------|------|
| Keychain 访问权限 | 无法读取凭证 | 中 | 使用环境变量替代 |
| Vue 检测失败 | 等待超时 | 中 | 多种检测方式+Fallback |
| 视觉识别准确率低 | 误操作 | 中 | 结合 DOM + 视觉双重验证 |
| Cookie 过期 | 登录失效 | 高 | 定期刷新+异常检测 |

---

_创建时间: 2026-04-12 11:12 | 版本: v1.0 | 作者: Jerry 🦞_
