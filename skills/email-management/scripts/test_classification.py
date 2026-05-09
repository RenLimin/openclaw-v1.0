#!/usr/bin/env python3
"""
邮件分类逻辑测试脚本
无需连接邮件服务器，使用模拟数据测试
"""

import sys
import json
from pathlib import Path

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent))
from email_manager import EmailManager


def test_classification():
    """测试分类逻辑"""
    print("=" * 60)
    print("🧪 邮件分类逻辑测试")
    print("=" * 60)
    
    # 初始化 EmailManager
    em = EmailManager()
    
    # 测试用例
    test_cases = [
        # P0 测试用例
        {
            "name": "P0 - OA 审批邮件",
            "subject": "【OA 审批提醒】采购合同 HT-2024-001 待审批",
            "from_addr": "oa@company.com",
            "to_addr": "",
            "expected": "P0"
        },
        {
            "name": "P0 - Workflow 审批邮件",
            "subject": "请审批：2024年度预算申请",
            "from_addr": "workflow@company.com",
            "to_addr": "",
            "expected": "P0"
        },
        # P1 测试用例
        {
            "name": "P1 - 直接发送给本人",
            "subject": "项目进度汇报",
            "from_addr": "manager@company.com",
            "to_addr": "limin.ren@bangcle.com",
            "expected": "P1"
        },
        # P2 测试用例
        {
            "name": "P2 - 普通外部邮件",
            "subject": "合作洽谈意向",
            "from_addr": "partner@external.com",
            "to_addr": "",
            "expected": "P2"
        },
        # P3 测试用例
        {
            "name": "P3 - 系统通知",
            "subject": "【系统通知】您的账号已登录",
            "from_addr": "noreply@company.com",
            "to_addr": "",
            "expected": "P3"
        },
        {
            "name": "P3 - 营销邮件",
            "subject": "【优惠活动】春季大促销！",
            "from_addr": "marketing@company.com",
            "to_addr": "",
            "expected": "P3"
        },
        {
            "name": "P3 - 订阅邮件",
            "subject": "【订阅】技术周刊第 100 期",
            "from_addr": "newsletter@tech.com",
            "to_addr": "",
            "expected": "P3"
        },
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        print(f"\n📋 测试: {test['name']}")
        print(f"   主题: {test['subject']}")
        print(f"   发件人: {test['from_addr']}")
        
        result = em._classify_email(
            test['subject'], 
            test['from_addr'],
            test['to_addr']
        )
        
        actual = result['level']
        expected = test['expected']
        
        status = "✅ PASS" if actual == expected else "❌ FAIL"
        print(f"   预期: {expected}, 实际: {actual} - {status}")
        print(f"   原因: {result['reason']}")
        
        if actual == expected:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    return failed == 0


def test_generate_report():
    """测试报告生成功能"""
    print("\n" + "=" * 60)
    print("📝 报告生成功能测试")
    print("=" * 60)
    
    em = EmailManager()
    
    # 模拟邮件数据
    mock_emails = [
        {
            "id": "1",
            "subject": "【OA 审批提醒】采购合同待审批",
            "from": "oa@company.com",
            "date": "2026-04-24 10:00",
            "body_summary": "请尽快审批采购合同...",
            "classification": {"level": "P0", "name": "审批提醒", "reason": "OA 系统审批邮件"}
        },
        {
            "id": "2",
            "subject": "项目周报 - 第 16 周",
            "from": "pm@company.com",
            "date": "2026-04-24 09:00",
            "body_summary": "本周项目进展顺利，完成了...",
            "classification": {"level": "P1", "name": "工作邮件", "reason": "直接发送给本人"}
        },
        {
            "id": "3",
            "subject": "合作咨询",
            "from": "client@external.com",
            "date": "2026-04-23 15:00",
            "body_summary": "您好，想咨询一下贵公司的产品...",
            "classification": {"level": "P2", "name": "普通邮件", "reason": "普通外部邮件"}
        },
        {
            "id": "4",
            "subject": "【订阅】技术新闻",
            "from": "newsletter@tech.com",
            "date": "2026-04-23 08:00",
            "body_summary": "本周技术头条...",
            "classification": {"level": "P3", "name": "通知广告", "reason": "订阅邮件"}
        },
    ]
    
    report = em.generate_report(mock_emails)
    print("\n✅ 报告生成成功！")
    
    # 验证报告内容
    checks = [
        ("报告标题", "# 📧 邮件检查报告" in report),
        ("统计汇总", "📊 统计汇总" in report),
        ("P0 分组", "🔴 P0 审批提醒" in report),
        ("P1 分组", "🟡 P1 工作邮件" in report),
        ("P2 分组", "🟢 P2 普通邮件" in report),
        ("P3 分组", "⚪ P3 通知广告" in report),
        ("总计统计", "总计检查: **4** 封" in report),
    ]
    
    print("\n📋 报告内容验证:")
    all_pass = True
    for name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"   {status} {name}")
        if not passed:
            all_pass = False
    
    return all_pass


def main():
    success1 = test_classification()
    success2 = test_generate_report()
    
    if success1 and success2:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n⚠️  部分测试失败")
        return 1


if __name__ == '__main__':
    sys.exit(main())
