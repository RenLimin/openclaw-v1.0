#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔒 OpenClaw 安全检查 - 简化兼容版

保证任何 Python 环境都可运行
功能：提交前强制用户批准确认

创建时间：2026-05-08
"""

import sys
import os

def main():
    print ""
    print "🔒" + "=" * 58
    print "🔒 OpenClaw 安全卫士 - 提交前强制检查"
    print "🔒" + "=" * 58
    print ""
    
    print "⚠️  即将执行 Git 提交操作！"
    print "⚠️  请确认：本次提交是否已获得用户明确批准？"
    print ""
    print "   请输入完整批准指令以继续："
    print "   批准提交github"
    print ""
    
    try:
        confirm = raw_input("👉 请输入: ").strip()
    except:
        confirm = input("👉 请输入: ").strip()
    
    if confirm != "批准提交github":
        print ""
        print "❌" + "=" * 58
        print "❌ 提交已终止！未获得用户批准，禁止提交！"
        print "❌" + "=" * 58
        print ""
        sys.exit(1)
    
    print ""
    print "✅" + "=" * 58
    print "✅ 已获得用户批准，允许提交！"
    print "✅" + "=" * 58
    print ""
    
    sys.exit(0)

if __name__ == "__main__":
    main()
