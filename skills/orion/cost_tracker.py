"""
Orion LLM调度框架 - Token成本统计机制
支持多模型、多维度的Token消耗统计和成本估算
"""

import json
import time
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime, date


class ModelProvider(Enum):
    """模型提供商"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    BAIDU = "baidu"  # 文心一言
    ALIBABA = "alibaba"  # 通义千问
    TENCENT = "tencent"  # 腾讯混元
    BYTEDANCE = "bytedance"  # 豆包
    DEEPSEEK = "deepseek"
    CUSTOM = "custom"


class TokenType(Enum):
    """Token类型"""
    INPUT = "input"      # 输入Token
    OUTPUT = "output"    # 输出Token
    TOTAL = "total"      # 总Token


@dataclass
class ModelPricing:
    """模型定价配置"""
    model_name: str
    provider: ModelProvider
    input_price_per_1k: float  # 每1k输入Token价格(元)
    output_price_per_1k: float  # 每1k输出Token价格(元)
    currency: str = "CNY"
    is_active: bool = True


@dataclass
class TokenUsage:
    """Token使用记录"""
    request_id: str
    scenario: str  # 使用场景: S11, S12等
    model_name: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    input_cost: float = 0.0
    output_cost: float = 0.0
    total_cost: float = 0.0
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "scenario": self.scenario,
            "model_name": self.model_name,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "input_cost": self.input_cost,
            "output_cost": self.output_cost,
            "total_cost": self.total_cost,
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "metadata": self.metadata
        }


# 预定义的模型定价表
DEFAULT_MODEL_PRICING: Dict[str, ModelPricing] = {
    # OpenAI系列
    "gpt-3.5-turbo": ModelPricing(
        model_name="gpt-3.5-turbo",
        provider=ModelProvider.OPENAI,
        input_price_per_1k=0.0015,
        output_price_per_1k=0.002
    ),
    "gpt-4": ModelPricing(
        model_name="gpt-4",
        provider=ModelProvider.OPENAI,
        input_price_per_1k=0.03,
        output_price_per_1k=0.06
    ),
    "gpt-4-turbo": ModelPricing(
        model_name="gpt-4-turbo",
        provider=ModelProvider.OPENAI,
        input_price_per_1k=0.01,
        output_price_per_1k=0.03
    ),
    
    # 阿里通义千问
    "qwen-turbo": ModelPricing(
        model_name="qwen-turbo",
        provider=ModelProvider.ALIBABA,
        input_price_per_1k=0.0008,
        output_price_per_1k=0.002
    ),
    "qwen-plus": ModelPricing(
        model_name="qwen-plus",
        provider=ModelProvider.ALIBABA,
        input_price_per_1k=0.002,
        output_price_per_1k=0.006
    ),
    
    # 字节豆包
    "doubao-pro": ModelPricing(
        model_name="doubao-pro",
        provider=ModelProvider.BYTEDANCE,
        input_price_per_1k=0.0015,
        output_price_per_1k=0.003
    ),
    
    # DeepSeek
    "deepseek-chat": ModelPricing(
        model_name="deepseek-chat",
        provider=ModelProvider.DEEPSEEK,
        input_price_per_1k=0.001,
        output_price_per_1k=0.002
    ),
}


class CostTracker:
    """Token成本追踪器"""
    
    def __init__(self):
        self.model_pricing = DEFAULT_MODEL_PRICING.copy()
        self.usage_history: List[TokenUsage] = []
        self.daily_budget: Dict[str, float] = {}  # 日期 -> 日预算
        self.scenario_budget: Dict[str, float] = {}  # 场景 -> 场景预算
    
    def register_model_pricing(self, pricing: ModelPricing):
        """注册模型定价"""
        self.model_pricing[pricing.model_name] = pricing
    
    def estimate_tokens(self, text: str) -> int:
        """
        粗略估算文本的Token数量
        中文: 约1.3字符 = 1Token
        英文: 约0.75单词 = 1Token
        混合: 约4字符 = 3Token
        """
        if not text:
            return 0
        
        # 统计中文字符数
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        # 非中文字符
        other_chars = len(text) - chinese_chars
        
        # 估算: 中文1.3字符/Token，其他字符2字符/Token
        chinese_tokens = chinese_chars / 1.3
        other_tokens = other_chars / 2
        
        return int(chinese_tokens + other_tokens) + 1
    
    def calculate_cost(self, model_name: str, prompt_tokens: int, completion_tokens: int) -> tuple[float, float, float]:
        """
        计算调用成本
        
        Returns:
            (input_cost, output_cost, total_cost)
        """
        pricing = self.model_pricing.get(model_name)
        
        if not pricing:
            # 使用默认定价
            input_cost = prompt_tokens * 0.002 / 1000
            output_cost = completion_tokens * 0.004 / 1000
        else:
            input_cost = prompt_tokens * pricing.input_price_per_1k / 1000
            output_cost = completion_tokens * pricing.output_price_per_1k / 1000
        
        total_cost = input_cost + output_cost
        
        return round(input_cost, 6), round(output_cost, 6), round(total_cost, 6)
    
    def record_usage(self, 
                     request_id: str,
                     scenario: str,
                     model_name: str,
                     prompt_tokens: int,
                     completion_tokens: int,
                     metadata: Optional[Dict[str, Any]] = None) -> TokenUsage:
        """
        记录Token使用情况
        """
        input_cost, output_cost, total_cost = self.calculate_cost(
            model_name, prompt_tokens, completion_tokens
        )
        
        usage = TokenUsage(
            request_id=request_id,
            scenario=scenario,
            model_name=model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost,
            metadata=metadata or {}
        )
        
        self.usage_history.append(usage)
        return usage
    
    def get_scenario_stats(self, scenario: str) -> Dict[str, Any]:
        """获取指定场景的统计数据"""
        scenario_usages = [u for u in self.usage_history if u.scenario == scenario]
        
        if not scenario_usages:
            return {
                "scenario": scenario,
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost": 0,
                "avg_tokens_per_request": 0,
                "avg_cost_per_request": 0
            }
        
        total_tokens = sum(u.total_tokens for u in scenario_usages)
        total_cost = sum(u.total_cost for u in scenario_usages)
        
        return {
            "scenario": scenario,
            "total_requests": len(scenario_usages),
            "total_prompt_tokens": sum(u.prompt_tokens for u in scenario_usages),
            "total_completion_tokens": sum(u.completion_tokens for u in scenario_usages),
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 4),
            "avg_tokens_per_request": round(total_tokens / len(scenario_usages), 2),
            "avg_cost_per_request": round(total_cost / len(scenario_usages), 6)
        }
    
    def get_daily_stats(self, target_date: Optional[date] = None) -> Dict[str, Any]:
        """获取指定日期的统计数据"""
        if target_date is None:
            target_date = date.today()
        
        date_str = target_date.isoformat()
        daily_usages = [
            u for u in self.usage_history
            if date.fromtimestamp(u.timestamp).isoformat() == date_str
        ]
        
        return {
            "date": date_str,
            "total_requests": len(daily_usages),
            "total_tokens": sum(u.total_tokens for u in daily_usages),
            "total_cost": round(sum(u.total_cost for u in daily_usages), 4),
            "breakdown_by_scenario": self._breakdown_by_scenario(daily_usages)
        }
    
    def get_model_stats(self, model_name: str) -> Dict[str, Any]:
        """获取指定模型的统计数据"""
        model_usages = [u for u in self.usage_history if u.model_name == model_name]
        
        return {
            "model_name": model_name,
            "total_requests": len(model_usages),
            "total_tokens": sum(u.total_tokens for u in model_usages),
            "total_cost": round(sum(u.total_cost for u in model_usages), 4)
        }
    
    def _breakdown_by_scenario(self, usages: List[TokenUsage]) -> Dict[str, Dict[str, Any]]:
        """按场景分组统计"""
        breakdown = {}
        for usage in usages:
            scenario = usage.scenario
            if scenario not in breakdown:
                breakdown[scenario] = {
                    "requests": 0,
                    "tokens": 0,
                    "cost": 0
                }
            breakdown[scenario]["requests"] += 1
            breakdown[scenario]["tokens"] += usage.total_tokens
            breakdown[scenario]["cost"] += usage.total_cost
        
        for scenario in breakdown:
            breakdown[scenario]["cost"] = round(breakdown[scenario]["cost"], 4)
        
        return breakdown
    
    def get_overall_stats(self) -> Dict[str, Any]:
        """获取整体统计数据"""
        if not self.usage_history:
            return {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost": 0,
                "scenarios": {}
            }
        
        scenarios = {}
        for scenario in set(u.scenario for u in self.usage_history):
            scenarios[scenario] = self.get_scenario_stats(scenario)
        
        return {
            "total_requests": len(self.usage_history),
            "total_prompt_tokens": sum(u.prompt_tokens for u in self.usage_history),
            "total_completion_tokens": sum(u.completion_tokens for u in self.usage_history),
            "total_tokens": sum(u.total_tokens for u in self.usage_history),
            "total_cost": round(sum(u.total_cost for u in self.usage_history), 4),
            "scenarios": scenarios,
            "models": self._get_model_breakdown()
        }
    
    def _get_model_breakdown(self) -> Dict[str, Dict[str, Any]]:
        """按模型分组统计"""
        breakdown = {}
        for usage in self.usage_history:
            model = usage.model_name
            if model not in breakdown:
                breakdown[model] = {
                    "requests": 0,
                    "tokens": 0,
                    "cost": 0
                }
            breakdown[model]["requests"] += 1
            breakdown[model]["tokens"] += usage.total_tokens
            breakdown[model]["cost"] += usage.total_cost
        
        for model in breakdown:
            breakdown[model]["cost"] = round(breakdown[model]["cost"], 4)
        
        return breakdown
    
    def set_daily_budget(self, budget: float, target_date: Optional[date] = None):
        """设置日预算"""
        if target_date is None:
            target_date = date.today()
        self.daily_budget[target_date.isoformat()] = budget
    
    def set_scenario_budget(self, scenario: str, budget: float):
        """设置场景预算"""
        self.scenario_budget[scenario] = budget
    
    def check_daily_budget(self, target_date: Optional[date] = None) -> tuple[bool, float, float]:
        """
        检查日预算是否超支
        
        Returns:
            (is_over_budget, current_cost, budget)
        """
        if target_date is None:
            target_date = date.today()
        
        date_str = target_date.isoformat()
        daily_stats = self.get_daily_stats(target_date)
        current_cost = daily_stats["total_cost"]
        budget = self.daily_budget.get(date_str, float('inf'))
        
        if budget == float('inf'):
            return False, current_cost, budget
        
        return current_cost > budget, current_cost, budget
    
    def check_scenario_budget(self, scenario: str) -> tuple[bool, float, float]:
        """检查场景预算是否超支"""
        scenario_stats = self.get_scenario_stats(scenario)
        current_cost = scenario_stats["total_cost"]
        budget = self.scenario_budget.get(scenario, float('inf'))
        
        if budget == float('inf'):
            return False, current_cost, budget
        
        return current_cost > budget, current_cost, budget
    
    def export_report(self, filepath: str, format: str = "json"):
        """导出成本报告"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "overall_stats": self.get_overall_stats(),
            "daily_stats": self.get_daily_stats(),
            "recent_usages": [u.to_dict() for u in self.usage_history[-50:]]
        }
        
        if format == "json":
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
    
    def estimate_scenario_cost(self, scenario: str, input_text: str, model_name: str = "gpt-3.5-turbo") -> Dict[str, Any]:
        """
        估算某个场景的调用成本
        
        Returns:
            包含预估Token和成本的字典
        """
        estimated_input_tokens = self.estimate_tokens(input_text)
        
        # 根据场景估算输出Token长度
        scenario_output_estimates = {
            "S11": 3000,  # PRD初稿，内容较多
            "S12": 1500,  # 风险识别
            "S13": 2500,  # 立项报告
            "S14": 1000,  # 会议纪要
            "S15": 1500,  # 周报
            "S16": 2000,  # 月报
            "S17": 2000,  # 健康度评估
            "S18": 2000,  # 验收报告
            "S19": 1500,  # 复盘经验
            "S20": 1500,  # 经验推荐
        }
        
        estimated_output_tokens = scenario_output_estimates.get(scenario, 1000)
        
        input_cost, output_cost, total_cost = self.calculate_cost(
            model_name, estimated_input_tokens, estimated_output_tokens
        )
        
        return {
            "scenario": scenario,
            "model_name": model_name,
            "estimated_input_tokens": estimated_input_tokens,
            "estimated_output_tokens": estimated_output_tokens,
            "estimated_total_tokens": estimated_input_tokens + estimated_output_tokens,
            "estimated_input_cost": input_cost,
            "estimated_output_cost": output_cost,
            "estimated_total_cost": total_cost
        }


# 全局单例
_global_cost_tracker = CostTracker()


def get_cost_tracker() -> CostTracker:
    """获取全局成本追踪器实例"""
    return _global_cost_tracker
