"""
Orion LLM调度框架 - 使用示例
演示各个模块的基本使用方法
"""

import sys
sys.path.insert(0, '..')

from orion import (
    LLMClient, 
    call_llm, 
    get_template, 
    get_cost_tracker,
    validate_output
)


def example_basic_call():
    """示例1: 基本调用（规则模式）"""
    print("=" * 60)
    print("示例1: 基本调用（规则模式 - enable_llm=False）")
    print("=" * 60)
    
    client = LLMClient()
    
    # S11: 需求结构化梳理 & PRD初稿生成
    result = client.call(
        scenario="S11",
        data={
            "raw_requirement": "我们需要做一个项目管理系统，支持创建项目、分配任务、跟踪进度",
            "business_context": "公司目前项目管理混乱，需要标准化流程",
            "project_data": {"name": "项目管理系统V1.0"}
        },
        enable_llm=False
    )
    
    print(f"场景: {result.scenario}")
    print(f"成功: {result.success}")
    print(f"是否模拟: {result.is_mock}")
    if result.success:
        print(f"业务目标: {result.data.get('business_objective')}")
        print(f"功能需求数量: {len(result.data.get('functional_requirements', []))}")
    print()


def example_all_scenarios():
    """示例2: 遍历所有10个场景"""
    print("=" * 60)
    print("示例2: 遍历所有10个项目管理场景")
    print("=" * 60)
    
    client = LLMClient()
    
    test_data = {
        "S11": {"raw_requirement": "OA系统升级", "project_data": {"name": "OA系统升级项目"}},
        "S12": {"requirement_doc": "系统需要支持百万级并发", "project_snapshot": {"name": "高并发系统"}},
        "S13": {"project_brief": "新建数据中台项目", "project_info": {"name": "数据中台项目"}},
        "S14": {"meeting_content": "张三：下周五完成需求文档", "meeting_metadata": {"title": "项目周会"}},
        "S15": {"project_data": {"name": "OA系统升级"}, "week_range": "2024-W20"},
        "S16": {"project_monthly_data": {"name": "OA系统升级"}, "report_month": "2024-05"},
        "S17": {"project_snapshot": {"name": "OA系统升级", "progress": 75}},
        "S18": {"project_info": {"name": "OA系统升级"}, "test_records": [{"item": "登录功能"}]},
        "S19": {"project_history": {"name": "OA系统升级", "duration": "6个月"}},
        "S20": {"current_project_profile": {"industry": "互联网", "tech_stack": ["Python", "React"]}},
    }
    
    for scenario_id in ["S11", "S12", "S13", "S14", "S15", "S16", "S17", "S18", "S19", "S20"]:
        template = get_template(scenario_id)
        result = client.call(
            scenario=scenario_id,
            data=test_data.get(scenario_id, {}),
            enable_llm=False
        )
        print(f"{scenario_id}: {template.scenario_name} -> {'成功' if result.success else '失败'}")
    
    print()


def example_cost_tracking():
    """示例3: 成本统计"""
    print("=" * 60)
    print("示例3: Token成本统计")
    print("=" * 60)
    
    client = LLMClient(model_name="gpt-3.5-turbo")
    
    # 估算S11的调用成本
    estimate = client.estimate_cost("S11", {"raw_requirement": "测试需求描述"})
    print(f"S11 预估成本:")
    print(f"  预估输入Token: {estimate['estimated_input_tokens']}")
    print(f"  预估输出Token: {estimate['estimated_output_tokens']}")
    print(f"  预估总成本: ¥{estimate['estimated_total_cost']:.4f}")
    
    # 获取全局统计
    tracker = get_cost_tracker()
    stats = tracker.get_overall_stats()
    print(f"\n全局统计:")
    print(f"  总请求数: {stats['total_requests']}")
    print(f"  总Token: {stats['total_tokens']}")
    print(f"  总成本: ¥{stats['total_cost']:.4f}")
    print()


def example_validation():
    """示例4: 输出校验"""
    print("=" * 60)
    print("示例4: 结构化输出校验")
    print("=" * 60)
    
    template = get_template("S11")
    
    # 正确的输出
    valid_data = {
        "business_objective": "测试目标",
        "functional_requirements": []
    }
    
    result = validate_output(valid_data, template.output_schema)
    print(f"合法数据校验结果: {'通过' if result.is_valid else '失败'}")
    
    # 有问题的输出
    invalid_data = {
        "business_objective": 123,  # 类型错误
        # 缺失必填字段
    }
    
    result2 = validate_output(invalid_data, template.output_schema)
    print(f"非法数据校验结果: {'通过' if result2.is_valid else '失败'}")
    if not result2.is_valid:
        for error in result2.errors[:2]:
            print(f"  - {error.field_path}: {error.message}")
    print()


def example_template_info():
    """示例5: 查看模板信息"""
    print("=" * 60)
    print("示例5: Prompt模板信息")
    print("=" * 60)
    
    for scenario_id in ["S11", "S12", "S13", "S14", "S15", "S16", "S17", "S18", "S19", "S20"]:
        template = get_template(scenario_id)
        print(f"{scenario_id}: {template.scenario_name}")
        print(f"  标签: {', '.join(template.tags)}")
        print(f"  输出格式: {template.output_format.value}")
        print(f"  输入参数: {len(template.input_params)}个")
        print()


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("Orion LLM调度框架 v1.0 - 使用示例")
    print("=" * 60 + "\n")
    
    example_basic_call()
    example_all_scenarios()
    example_cost_tracking()
    example_validation()
    example_template_info()
    
    print("=" * 60)
    print("所有示例运行完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
