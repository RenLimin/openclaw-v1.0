#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 记忆管理技能 - 记录Rex的新要求到 MEMORY.md
确保Rex提出的任何要求都在10分钟内记录到长期记忆
"""

import sys
import re
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / '.openclaw' / 'workspace'
MEMORY_MD = WORKSPACE / 'MEMORY.md'

GREEN = '\033[92m'
BOLD = '\033[1m'
RESET = '\033[0m'

def record_requirement(requirement_text: str) -> bool:
    """
    记录Rex的新要求到 MEMORY.md
    
    Args:
        requirement_text: Rex要求的原文（一字不差！）
    
    Returns:
        bool: 是否成功
    """
    if not MEMORY_MD.exists():
        print(f"❌ MEMORY.md 不存在")
        return False
    
    content = MEMORY_MD.read_text(encoding='utf-8')
    
    # 检查是否已经记录过（相似度检查）
    if requirement_text[:20] in content:
        print(f"⚠️  该要求似乎已经记录，跳过")
        return True
    
    # 找到 Rex的5条硬性要求 章节，在后面追加
    pattern = r'(\| 序号 \| 要求 \| 违反后果 \|\n\|------\|------\|---------\|\n([|].*?\n)*)'
    
    match = re.search(pattern, content)
    if not match:
        print(f"❌ 未找到硬性要求表格，请手动添加")
        return False
    
    # 计算新的序号
    existing_table = match.group(1)
    line_count = existing_table.count('\n') - 2  # 减去表头2行
    new_num = line_count + 1
    
    # 生成新行
    new_line = f"| {new_num} | **{requirement_text}** | 待补充 |\n"
    
    # 插入到表格最后
    insert_pos = match.end()
    new_content = content[:insert_pos] + new_line + content[insert_pos:]
    
    # 写入文件
    MEMORY_MD.write_text(new_content, encoding='utf-8')
    
    # 同时更新记忆同步时间
    timestamp_pattern = r'最近同步时间：\d{4}-\d{2}-\d{2} \d{2}:\d{2}'
    new_timestamp = f'最近同步时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}'
    new_content = re.sub(timestamp_pattern, new_timestamp, new_content)
    MEMORY_MD.write_text(new_content, encoding='utf-8')
    
    return True

def main():
    if len(sys.argv) < 2:
        print("用法: python3 record_requirement.py <Rex要求的原文>")
        print("⚠️  重要：必须一字不差地记录原文，不能 paraphrase！")
        sys.exit(1)
    
    requirement = ' '.join(sys.argv[1:])
    
    print(f"\n{BOLD}🧠 === 记录Rex的新要求 ==={RESET}\n")
    print(f"  要求原文: {requirement}")
    print()
    
    success = record_requirement(requirement)
    
    if success:
        print(f"{GREEN}✅ 已成功记录到 MEMORY.md 的硬性要求章节！{RESET}\n")
        print(f"  📌 接下来请：")
        print(f"     1. 更新该要求的\"违反后果\"列")
        print(f"     2. 严格执行此要求\n")
        return 0
    else:
        print(f"❌ 记录失败\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
