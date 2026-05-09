"""
Orion LLM调度框架 - 统一调用接口
提供LLMClient类，支持规则生成和LLM调用两种模式
"""

import uuid
import json
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass

from .templates import get_template, build_prompt
from .validator import validate_output, ValidationResult, ValidationLevel
from .cost_tracker import get_cost_tracker, CostTracker


@dataclass
class LLMResponse:
    """LLM调用响应"""
    success: bool
    scenario: str
    data: Optional[Dict[str, Any]] = None
    raw_output: Optional[str] = None
    validation_result: Optional[ValidationResult] = None
    token_usage: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    is_mock: bool = False  # 是否为规则生成的模拟数据


class LLMClient:
    """
    LLM统一调用客户端
    
    特性:
    1. 支持规则生成模式(enable_llm=False)：返回模板化的占位数据
    2. 支持真实LLM调用模式(enable_llm=True)：调用大模型API
    3. 内置结构化输出校验
    4. 自动Token成本统计
    """
    
    def __init__(self, 
                 model_name: str = "gpt-3.5-turbo",
                 validation_level: ValidationLevel = ValidationLevel.STRICT,
                 auto_retry_on_validation_failure: bool = True):
        self.model_name = model_name
        self.validation_level = validation_level
        self.auto_retry = auto_retry_on_validation_failure
        self.cost_tracker: CostTracker = get_cost_tracker()
    
    def call(self, 
             scenario: str, 
             data: Dict[str, Any], 
             enable_llm: bool = False,
             validate_output: bool = True,
             **kwargs) -> LLMResponse:
        """
        统一调用入口
        
        Args:
            scenario: 场景ID，如 S11, S12 等
            data: 输入数据
            enable_llm: 是否调用真实LLM，False时返回规则生成的模拟数据
            validate_output: 是否进行输出校验
            **kwargs: 额外参数
            
        Returns:
            LLMResponse 响应对象
        """
        request_id = str(uuid.uuid4())
        
        # 获取模板
        template = get_template(scenario)
        if not template:
            return LLMResponse(
                success=False,
                scenario=scenario,
                error_message=f"未找到场景模板: {scenario}"
            )
        
        if enable_llm:
            return self._call_llm(request_id, scenario, data, template, validate_output, **kwargs)
        else:
            return self._generate_mock_output(request_id, scenario, data, template)
    
    def _generate_mock_output(self, 
                              request_id: str,
                              scenario: str, 
                              data: Dict[str, Any], 
                              template: Any) -> LLMResponse:
        """
        基于规则生成模拟输出（不调用LLM）
        根据Schema生成合理的占位数据
        """
        try:
            # 根据Schema生成模拟数据
            mock_data = self._schema_to_mock_data(template.output_schema, data, scenario)
            
            # 估算Token成本
            prompt_text = build_prompt(scenario, data) or ""
            estimated_tokens = self.cost_tracker.estimate_tokens(prompt_text)
            
            # 记录预估使用量（模拟）
            token_usage = {
                "request_id": request_id,
                "estimated_input_tokens": estimated_tokens,
                "estimated_output_tokens": self._estimate_output_tokens(scenario),
                "mode": "mock/rule-based"
            }
            
            return LLMResponse(
                success=True,
                scenario=scenario,
                data=mock_data,
                token_usage=token_usage,
                is_mock=True
            )
        except Exception as e:
            return LLMResponse(
                success=False,
                scenario=scenario,
                error_message=f"生成模拟输出失败: {str(e)}"
            )
    
    def _schema_to_mock_data(self, 
                             schema: Dict[str, Any], 
                             input_data: Dict[str, Any],
                             scenario: str) -> Dict[str, Any]:
        """
        根据JSON Schema生成模拟数据
        """
        mock_data = {}
        
        if "properties" not in schema:
            return mock_data
        
        for prop_name, prop_schema in schema["properties"].items():
            prop_type = prop_schema.get("type", "string")
            
            # 基础字段处理
            if prop_name == "project_name" and "project_data" in input_data:
                mock_data[prop_name] = input_data["project_data"].get("name", "未命名项目")
            elif prop_name == "overall_status" or prop_name == "overall_health":
                mock_data[prop_name] = "正常"
            elif prop_name == "overall_health_score":
                mock_data[prop_name] = 85
            elif prop_name == "overall_health_level":
                mock_data[prop_name] = "良好"
            elif prop_name == "acceptance_conclusion":
                mock_data[prop_name] = "验收通过"
            elif prop_name == "risk_summary" or prop_name == "executive_summary":
                mock_data[prop_name] = f"基于输入数据生成的{scenario}摘要"
            elif prop_name == "meeting_summary":
                mock_data[prop_name] = input_data.get("meeting_metadata", {}).get("title", "会议摘要")
            
            # 类型处理
            elif prop_type == "array":
                items_schema = prop_schema.get("items", {})
                if items_schema.get("type") == "object":
                    mock_data[prop_name] = [self._schema_to_mock_data(items_schema, input_data, scenario)]
                else:
                    mock_data[prop_name] = []
            
            elif prop_type == "object":
                mock_data[prop_name] = self._schema_to_mock_data(prop_schema, input_data, scenario)
            
            elif prop_type == "string":
                if "enum" in prop_schema:
                    mock_data[prop_name] = prop_schema["enum"][0]
                else:
                    mock_data[prop_name] = f"[{prop_name}]"
            
            elif prop_type in ["number", "integer"]:
                mock_data[prop_name] = 0
            
            elif prop_type == "boolean":
                mock_data[prop_name] = True
            
            else:
                mock_data[prop_name] = f"[{prop_name}]"
        
        return mock_data
    
    def _estimate_output_tokens(self, scenario: str) -> int:
        """估算输出Token数"""
        estimates = {
            "S11": 3000,  # PRD初稿
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
        return estimates.get(scenario, 1000)
    
    def _call_llm(self,
                  request_id: str,
                  scenario: str,
                  data: Dict[str, Any],
                  template: Any,
                  validate: bool = True,
                  **kwargs) -> LLMResponse:
        """
        调用真实LLM（这里是框架实现，实际调用需要接入具体LLM API）
        """
        try:
            # 构建完整Prompt
            prompt = build_prompt(scenario, data)
            if not prompt:
                return LLMResponse(
                    success=False,
                    scenario=scenario,
                    error_message="构建Prompt失败"
                )
            
            # TODO: 这里接入真实的LLM API调用
            # 例如 OpenAI、通义千问、豆包等
            # llm_output = self._call_actual_llm_api(prompt, **kwargs)
            
            # 目前框架实现：返回模拟的LLM输出
            # 在实际项目中替换为真实API调用
            llm_output = self._simulate_llm_output(scenario, data, template)
            
            # 校验输出
            validation_result = None
            if validate:
                validation_result = validate_output(llm_output, template.output_schema, self.validation_level)
                
                if not validation_result.is_valid:
                    if self.auto_retry:
                        # 可以在这里实现重试逻辑
                        pass
                    else:
                        return LLMResponse(
                            success=False,
                            scenario=scenario,
                            raw_output=llm_output,
                            validation_result=validation_result,
                            error_message="输出校验失败"
                        )
            
            # 记录Token使用
            input_tokens = self.cost_tracker.estimate_tokens(prompt)
            output_tokens = self.cost_tracker.estimate_tokens(llm_output)
            
            usage = self.cost_tracker.record_usage(
                request_id=request_id,
                scenario=scenario,
                model_name=self.model_name,
                prompt_tokens=input_tokens,
                completion_tokens=output_tokens,
                metadata={"validation_passed": validation_result.is_valid if validation_result else True}
            )
            
            # 解析输出
            try:
                parsed_data = json.loads(llm_output) if isinstance(llm_output, str) else llm_output
            except:
                parsed_data = {"raw_output": llm_output}
            
            return LLMResponse(
                success=True,
                scenario=scenario,
                data=parsed_data,
                raw_output=llm_output,
                validation_result=validation_result,
                token_usage=usage.to_dict()
            )
            
        except Exception as e:
            return LLMResponse(
                success=False,
                scenario=scenario,
                error_message=f"LLM调用失败: {str(e)}"
            )
    
    def _simulate_llm_output(self, scenario: str, data: Dict[str, Any], template: Any) -> str:
        """模拟LLM输出（框架占位实现）"""
        mock_data = self._schema_to_mock_data(template.output_schema, data, scenario)
        return json.dumps(mock_data, ensure_ascii=False, indent=2)
    
    def estimate_cost(self, scenario: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """预估调用成本"""
        prompt = build_prompt(scenario, data) or ""
        return self.cost_tracker.estimate_scenario_cost(scenario, prompt, self.model_name)
    
    def get_usage_stats(self, scenario: Optional[str] = None) -> Dict[str, Any]:
        """获取使用统计"""
        if scenario:
            return self.cost_tracker.get_scenario_stats(scenario)
        return self.cost_tracker.get_overall_stats()


# 便捷函数
def call_llm(scenario: str, 
             data: Dict[str, Any], 
             enable_llm: bool = False,
             **kwargs) -> LLMResponse:
    """
    便捷调用函数
    
    Example:
        result = call_llm("S11", {"raw_requirement": "做一个项目管理系统"}, enable_llm=False)
    """
    client = LLMClient(**kwargs)
    return client.call(scenario, data, enable_llm)
