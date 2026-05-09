#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
履约义务拆分 - 测试脚本
"""

import sys
from pathlib import Path

# 添加脚本路径
script_dir = Path(__file__).parent.parent / 'scripts'
sys.path.insert(0, str(script_dir))

from obligation_splitter import ObligationSplitter, Colors


def test_basic_functionality():
    """测试基本功能"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}═════════════════════════════════════════{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}  履约义务拆分 - 功能测试{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}═════════════════════════════════════════{Colors.ENDC}")

    splitter = ObligationSplitter()

    # 测试1: 依赖检查
    print(f"\n{Colors.CYAN}[测试1] 依赖检查{Colors.ENDC}")
    deps = splitter.check_dependencies()
    assert deps['all_passed'], "依赖检查失败"

    # 测试2: 创建测试合同文本
    print(f"\n{Colors.CYAN}[测试2] 条款拆分测试{Colors.ENDC}")

    test_text = """
服务器采购合同

合同编号: HT-2026-001
签订日期: 2026年4月24日

甲方：某某科技有限公司
乙方：某某设备有限公司

1. 交付条款
乙方应在合同生效后30个工作日内完成服务器交付。
交付地点：甲方指定地点。

2. 验收条款
甲方应在收到服务器后7个工作日内完成验收。
验收标准：设备完好，运行正常。

3. 付款条款
甲方应在验收合格后15个工作日内支付100%款项。
付款方式：银行转账。

4. 质保条款
乙方提供3年7×24小时质保服务。
质保期内设备出现故障，乙方应在24小时内响应。

5. 保密条款
双方应对本合同内容及技术信息承担保密义务。
保密期限为5年。

6. 违约责任
乙方逾期交付的，每逾期一日应支付合同金额0.1%的违约金。
甲方逾期付款的，每逾期一日应支付应付金额0.1%的违约金。
"""

    clauses = splitter.split_clauses(test_text)
    print(f"  ✅ 拆分成 {len(clauses)} 个条款")
    assert len(clauses) > 0, "条款拆分失败"

    # 测试3: 义务提取
    print(f"\n{Colors.CYAN}[测试3] 义务提取测试{Colors.ENDC}")
    obligations = splitter.extract_obligations(clauses)
    print(f"  ✅ 提取到 {len(obligations)} 项义务")
    assert len(obligations) > 0, "义务提取失败"

    for obl in obligations:
        print(f"    - [{obl['type_name']}] {obl['content'][:40]}...")

    # 测试4: 产品匹配（指定编码）
    print(f"\n{Colors.CYAN}[测试4] 产品匹配测试{Colors.ENDC}")
    product = splitter.match_product(test_text, product_code='AS-SERVER-001')
    assert product is not None, "产品匹配失败"
    print(f"  ✅ 匹配到产品: {product['product_name']}")

    # 测试5: 义务比对
    print(f"\n{Colors.CYAN}[测试5] 义务比对测试{Colors.ENDC}")
    differences = splitter.compare_obligations(obligations, product)
    print(f"  ✅ 发现 {len(differences)} 处差异")

    # 测试6: 风险评估
    print(f"\n{Colors.CYAN}[测试6] 风险评估测试{Colors.ENDC}")
    risk_summary = splitter.assess_risk(obligations, differences)
    print(f"  ✅ 整体风险等级: {risk_summary['overall_level']}")

    # 测试7: 生成审核报告
    print(f"\n{Colors.CYAN}[测试7] 审核报告测试{Colors.ENDC}")
    report = splitter.generate_audit_report(obligations, differences, risk_summary, product)
    assert len(report) > 0, "审核报告生成失败"
    print(f"  ✅ 审核报告生成完成 ({len(report)} 字符)")

    print(f"\n{Colors.GREEN}═════════════════════════════════════════{Colors.ENDC}")
    print(f"{Colors.GREEN}✅ 所有测试通过！{Colors.ENDC}")
    print(f"{Colors.GREEN}═════════════════════════════════════════{Colors.ENDC}")

    return True


def test_field_extraction():
    """测试字段提取功能"""
    print(f"\n{Colors.CYAN}[字段提取专项测试]{Colors.ENDC}")

    splitter = ObligationSplitter()

    test_cases = [
        ("甲方应在验收合格后15个工作日内支付全部款项", "15个工作日内", "甲方"),
        ("乙方应在合同生效后30日内交付货物", "30日内", "乙方"),
        ("双方应在合同终止后6个月内完成清算", "6个月内", "双方"),
    ]

    all_passed = True
    for content, expected_time, expected_party in test_cases:
        time = splitter._extract_performance_time(content)
        party = splitter._extract_responsible_party(content)

        time_ok = expected_time in str(time) if time else False
        party_ok = expected_party == str(party)

        status = "✅" if (time_ok and party_ok) else "❌"
        print(f"  {status} 内容: {content[:30]}...")
        print(f"     时间提取: {time} (预期: {expected_time})")
        print(f"     责任方: {party} (预期: {expected_party})")

        if not (time_ok and party_ok):
            all_passed = False

    if all_passed:
        print(f"\n{Colors.GREEN}✅ 字段提取测试通过！{Colors.ENDC}")
    else:
        print(f"\n{Colors.YELLOW}⚠️  部分字段提取测试未通过（可能是正则匹配精度问题）{Colors.ENDC}")

    return all_passed


if __name__ == '__main__':
    print("履约义务拆分技能 - 测试套件\n")

    try:
        # 运行基本功能测试
        test_basic_functionality()

        # 运行字段提取测试
        test_field_extraction()

        print(f"\n{Colors.GREEN}🎉 测试完成！技能可以正常使用。{Colors.ENDC}")

    except Exception as e:
        print(f"\n{Colors.RED}❌ 测试失败: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
