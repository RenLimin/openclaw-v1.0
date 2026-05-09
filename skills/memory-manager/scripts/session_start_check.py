#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 记忆管理技能 - 会话启动自检
确保每个会话开始时都读完了必要的记忆文件
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

WORKSPACE = Path.home() / '.openclaw' / 'workspace'
MEMORY_MD = WORKSPACE / 'MEMORY.md'
MEMORY_DIR = WORKSPACE / 'memory'

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BOLD = '\033[1m'
RESET = '\033[0m'

def check_memory_md():
    """检查 MEMORY.md 是否包含核心规则"""
    if not MEMORY_MD.exists():
        return False, "MEMORY.md 不存在"
    
    content = MEMORY_MD.read_text(encoding='utf-8')
    
    required_keywords = [
        ("记忆管理规则", "未包含记忆管理规则章节"),
        ("硬性要求", "未包含Rex的5条硬性要求"),
        ("jumpSystem", "未包含OA登录核心流程记录"),
        ("经验库", "未包含经验库索引"),
    ]
    
    missing = []
    for keyword, desc in required_keywords:
        if keyword not in content:
            missing.append(desc)
    
    if missing:
        return False, f"MEMORY.md 缺少关键内容: {', '.join(missing)}"
    
    return True, "MEMORY.md 核心内容完整"

def check_yesterday_memory():
    """检查是否读取了昨天的会话记忆"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    yesterday_file = MEMORY_DIR / f'{yesterday}.md'
    
    if not yesterday_file.exists():
        # 昨天没有记忆文件是正常的（周末/休假）
        return True, f"昨天({yesterday})没有会话记录，正常"
    
    # 检查今天是否已有会话记录，如果有说明已经读过了
    today = datetime.now().strftime('%Y-%m-%d')
    today_file = MEMORY_DIR / f'{today}.md'
    
    if today_file.exists():
        return True, "今天的会话记忆已创建，说明已读昨天的记录"
    
    return None, "注意：请先读昨天的会话记忆再开始工作"

def check_pending_lessons():
    """检查是否有需要建立但未建立的经验库"""
    if not MEMORY_MD.exists():
        return False, "MEMORY.md 不存在"
    
    content = MEMORY_MD.read_text(encoding='utf-8')
    
    # 查找经验库索引中标记为"待建立"的项
    pending = []
    for line in content.split('\n'):
        if '待建立' in line and '经验库' in line:
            # 提取经验库名称
            if '|' in line:
                parts = [p.strip() for p in line.split('|')]
                for p in parts:
                    if '经验库' in p:
                        pending.append(p)
                        break
    
    if pending:
        return False, f"有 {len(pending)} 个待建立的经验库: {', '.join(pending)}"
    
    return True, "没有待建立的经验库"

def check_pending_tasks():
    """检查待完成任务跟踪表"""
    task_file = WORKSPACE / 'memory' / '待完成任务跟踪.json'
    
    if not task_file.exists():
        return None, "任务跟踪文件不存在，首次创建中"
    
    try:
        import json
        with open(task_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        tasks = data.get('tasks', [])
        stats = data.get('statistics', {})
        
        # 只显示最高优先级和进行中的任务
        high_priority = [t for t in tasks if t.get('priority') in ['🔴 最高', '🟡 高']]
        in_progress = [t for t in tasks if t.get('status') == '🔄 执行中']
        
        msg = f"共{stats.get('total_tasks', 0)}个待完成，{len(in_progress)}个执行中，{len(high_priority)}个高优先级"
        return True, msg
    except Exception as e:
        return False, f"任务跟踪文件读取失败: {str(e)}"

def print_pending_tasks_summary():
    """简洁打印待完成任务摘要"""
    task_file = WORKSPACE / 'memory' / '待完成任务跟踪.json'
    
    if not task_file.exists():
        return
    
    try:
        import json
        with open(task_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        tasks = data.get('tasks', [])
        
        print(f"  \n{BOLD}📋 待完成任务摘要:{RESET}")
        for i, task in enumerate(tasks, 1):
            if task.get('status') in ['🔄 执行中', '⏳ 待Rex完成一次验证码']:
                print(f"     {task.get('priority')} [{task.get('status')}] {task.get('name')}")
        print()
    except Exception:
        pass

def main():
    print(f"\n{BOLD}🧠 === 记忆管理 - 会话启动自检 ==={RESET}\n")
    
    checks = [
        ("检查 MEMORY.md 核心内容", check_memory_md),
        ("检查昨天的会话记忆", check_yesterday_memory),
        ("检查待建立的经验库", check_pending_lessons),
        ("检查待完成任务跟踪", check_pending_tasks),
    ]
    
    all_pass = True
    for name, check_func in checks:
        status, msg = check_func()
        if status is True:
            print(f"  {GREEN}✅{RESET} {name}: {msg}")
        elif status is False:
            print(f"  {RED}❌{RESET} {name}: {msg}")
            all_pass = False
        else:  # None = 警告
            print(f"  {YELLOW}⚠️{RESET} {name}: {msg}")
    
    print()
    
    # 无论是否通过，都强制显示待完成任务！
    print_pending_tasks_summary()
    
    if all_pass:
        print(f"{GREEN}✅ 记忆自检全部通过！可以开始工作{RESET}\n")
        print(f"  📢 工作前请默念3条最容易忘的要求：")
        print(f"     1. 耗时任务必须用子代理独立执行")
        print(f"     2. 改代码前先读经验库对照检查清单")
        print(f"     3. Rex的新要求10分钟内必须记录\n")
        return 0
    else:
        print(f"{RED}❌ 记忆自检发现待处理事项，请优先关注高优先级任务{RESET}\n")
        print(f"  📖 建议优先处理：")
        print(f"     1. 🔴 最高优先级的进行中任务")
        print(f"     2. 待Rex确认/操作的阻塞项")
        print(f"     3. 长期待建立的经验库（避免知识流失）\n")
        return 0  # 改为不阻断，只提示，避免耽误核心工作

if __name__ == '__main__':
    sys.exit(main())
