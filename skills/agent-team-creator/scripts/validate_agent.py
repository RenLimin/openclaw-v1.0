#!/usr/bin/env python3
"""
智能体质量验证器 - Quality Validator
对智能体团队进行安全、成本、性能、协作四重验证
"""

import json
import argparse
from typing import Dict, List, Tuple
from datetime import datetime

class Validator:
    def __init__(self):
        self.results = {
            "version": "1.0",
            "validated_at": datetime.now().isoformat(),
            "score": 0,
            "passed": [],
            "failed": [],
            "warnings": []
        }
    
    def validate_security(self, team: Dict) -> Tuple[int, List[str], List[str]]:
        """安全闸门验证"""
        score = 0
        passed = []
        failed = []
        
        # 检查1: 权限边界 - 最小权限原则
        all_agents = {}
        if "coordination_layer" in team:
            all_agents.update(team["coordination_layer"])
        if "business_layer" in team:
            all_agents.update(team["business_layer"])
        if "infrastructure_layer" in team:
            all_agents.update(team["infrastructure_layer"])
        
        has_privilege_boundary = True
        for name, agent in all_agents.items():
            if "所有权限" in str(agent.get("tools", "")):
                has_privilege_boundary = False
                break
        
        if has_privilege_boundary:
            score += 25
            passed.append("✅ 权限边界 - 遵循最小权限原则")
        else:
            failed.append("❌ 权限边界 - 存在越权风险")
        
        # 检查2: 数据安全
        if "communication_protocol" in team:
            score += 25
            passed.append("✅ 通信协议 - 具备标准通信协议")
        else:
            failed.append("❌ 通信协议 - 缺少标准通信协议定义")
        
        # 检查3: 操作审批机制
        has_jerry = "jerry" in str(team.get("coordination_layer", {}))
        if has_jerry:
            score += 25
            passed.append("✅ 协调层 - 具备最终审批角色")
        else:
            failed.append("❌ 协调层 - 缺少最终审批角色")
        
        return score, passed, failed
    
    def validate_cost(self, team: Dict) -> Tuple[int, List[str], List[str]]:
        """成本控制验证"""
        score = 0
        passed = []
        failed = []
        
        # 检查1: Orion存在
        infra = team.get("infrastructure_layer", {})
        has_orion = "orion" in infra or "Orion" in str(infra)
        if has_orion:
            score += 35
            passed.append("✅ 成本调度 - 具备Orion模型调度角色")
        else:
            failed.append("❌ 成本调度 - 缺少成本优化角色")
        
        # 检查2: 技能层设计
        if "business_layer" in team and len(team["business_layer"]) > 0:
            score += 35
            passed.append("✅ 技能层 - 具备专业化技能分工")
        else:
            failed.append("❌ 技能层 - 缺少专业化技能分工")
        
        return score, passed, failed
    
    def validate_performance(self, team: Dict) -> Tuple[int, List[str], List[str]]:
        """性能指标验证"""
        score = 0
        passed = []
        failed = []
        
        # 检查1: Luna存在
        infra = team.get("infrastructure_layer", {})
        has_luna = "luna" in infra or "Luna" in str(infra)
        if has_luna:
            score += 35
            passed.append("✅ 监控运维 - 具备Luna监控角色")
        else:
            failed.append("❌ 监控运维 - 缺少监控运维角色")
        
        # 检查2: Nova存在
        has_nova = "nova" in infra or "Nova" in str(infra)
        if has_nova:
            score += 35
            passed.append("✅ 技能管理 - 具备Nova技能管理角色")
        else:
            failed.append("❌ 技能管理 - 缺少技能管理角色")
        
        return score, passed, failed
    
    def validate_collaboration(self, team: Dict) -> Tuple[int, List[str], List[str]]:
        """协作能力验证"""
        score = 0
        passed = []
        failed = []
        
        # 检查1: 三层架构完整
        has_coordination = "coordination_layer" in team
        has_business = "business_layer" in team
        has_infra = "infrastructure_layer" in team
        
        if has_coordination and has_business and has_infra:
            score += 30
            passed.append("✅ 架构完整 - 三层架构完整")
        else:
            failed.append("❌ 架构完整 - 三层架构不完整")
        
        # 检查2: 通信协议
        protocol = team.get("communication_protocol", {})
        if "message_types" in protocol and len(protocol["message_types"]) >= 5:
            score += 20
            passed.append("✅ 通信协议 - 消息类型完整")
        else:
            failed.append("❌ 通信协议 - 消息类型不完整")
        
        # 检查3: 协作模式
        if "collaboration_modes" in protocol and len(protocol["collaboration_modes"]) >= 3:
            score += 20
            passed.append("✅ 协作模式 - 协作模式完整")
        else:
            failed.append("❌ 协作模式 - 协作模式不完整")
        
        return score, passed, failed
    
    def validate(self, team: Dict) -> Dict:
        """执行完整验证"""
        # 安全验证
        sec_score, sec_pass, sec_fail = self.validate_security(team)
        self.results["passed"].extend(sec_pass)
        self.results["failed"].extend(sec_fail)
        
        # 成本验证
        cost_score, cost_pass, cost_fail = self.validate_cost(team)
        self.results["passed"].extend(cost_pass)
        self.results["failed"].extend(cost_fail)
        
        # 性能验证
        perf_score, perf_pass, perf_fail = self.validate_performance(team)
        self.results["passed"].extend(perf_pass)
        self.results["failed"].extend(perf_fail)
        
        # 协作验证
        collab_score, collab_pass, collab_fail = self.validate_collaboration(team)
        self.results["passed"].extend(collab_pass)
        self.results["failed"].extend(collab_fail)
        
        # 计算总分
        total_score = sec_score + cost_score + perf_score + collab_score
        self.results["score"] = total_score
        self.results["max_score"] = 300
        
        # 评级
        if total_score >= 270:
            self.results["grade"] = "S"
            self.results["recommendation"] = "✅ 完美！可以直接上线"
        elif total_score >= 240:
            self.results["grade"] = "A"
            self.results["recommendation"] = "✅ 优秀！可以上线"
        elif total_score >= 210:
            self.results["grade"] = "B"
            self.results["recommendation"] = "⚠️ 良好！建议修复问题后上线"
        elif total_score >= 180:
            self.results["grade"] = "C"
            self.results["recommendation"] = "⚠️ 及格！需要修复问题"
        else:
            self.results["grade"] = "D"
            self.results["recommendation"] = "❌ 不合格！需要重大改进"
        
        return self.results

def main():
    parser = argparse.ArgumentParser(description="智能体质量验证器")
    parser.add_argument("--input", type=str, required=True,
                       help="智能体团队JSON文件路径")
    parser.add_argument("--output", type=str, help="验证结果输出路径")
    
    args = parser.parse_args()
    
    # 读取智能体团队定义
    with open(args.input, 'r', encoding='utf-8') as f:
        team = json.load(f)
    
    # 执行验证
    validator = Validator()
    results = validator.validate(team)
    
    # 输出结果
    print("=" * 60)
    print("🦞 Jerry 智能体团队质量验证报告")
    print("=" * 60)
    print(f"\n📊 总分: {results['score']} / {results['max_score']}")
    print(f"🏆 评级: {results['grade']}")
    print(f"💡 建议: {results['recommendation']}")
    print(f"\n⏰ 验证时间: {results['validated_at']}")
    
    print("\n" + "=" * 60)
    print("✅ 通过项:")
    print("=" * 60)
    for item in results["passed"]:
        print(f"  {item}")
    
    if results["failed"]:
        print("\n" + "=" * 60)
        print("❌ 未通过项:")
        print("=" * 60)
        for item in results["failed"]:
            print(f"  {item}")
    
    print("\n" + "=" * 60)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n✅ 验证报告已保存到: {args.output}")

if __name__ == "__main__":
    main()
