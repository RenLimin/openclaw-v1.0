#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品知识库功能验证测试
"""

import subprocess
import sys

def run_test(test_name, cmd_args):
    """运行测试"""
    print(f"\n{'='*60}")
    print(f"测试: {test_name}")
    print(f"命令: python main.py {' '.join(cmd_args)}")
    print('='*60)
    
    result = subprocess.run(
        [sys.executable, 'main.py'] + cmd_args,
        capture_output=True,
        text=True,
        cwd='/Users/bangcle/.openclaw/workspace/skills/product-knowledge-base'
    )
    
    if result.stdout:
        print(result.stdout[:2000])  # 限制输出长度
    if result.stderr:
        print("STDERR:", result.stderr)
    
    success = result.returncode == 0 and "未找到" not in result.stdout
    print(f"\n结果: {'✓ 通过' if success else '✗ 未找到数据或出错'}")
    return success

def main():
    print("🧪 产品知识库功能验证测试")
    
    tests = [
        ("按产品查询功能清单", ['func', 'API安全平台']),
        ("按产品查询部署安装说明", ['deploy', '全渠道应用安全监测']),
        ("按产品查询售后问题处理", ['support', '应用安全测评']),
        ("按应用场景查询跨产品方案", ['scene', '金融APP安全防护']),
        ("按产品线查看所有产品", ['line', '安全保护线']),
        ("查看产品实施步骤", ['step']),
        ("搜索移动应用安全监测产品", ['product', '移动应用安全监测']),
        ("搜索鸿蒙相关产品", ['product', '鸿蒙']),
    ]
    
    passed = 0
    for test_name, args in tests:
        if run_test(test_name, args):
            passed += 1
    
    print(f"\n{'='*60}")
    print(f"测试完成: {passed}/{len(tests)} 项通过")
    print('='*60)
    
    if passed == len(tests):
        print("\n✅ 所有功能验证通过！产品知识库已就绪。")
    else:
        print(f"\n⚠️  有 {len(tests) - passed} 项测试未通过，请检查。")

if __name__ == '__main__':
    main()
