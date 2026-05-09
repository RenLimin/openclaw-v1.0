"""
Orion LLM调度框架 v1.0

一个企业级的LLM应用编排框架，提供：
- Prompt模板管理（10个项目管理场景）
- 统一调用接口
- 结构化输出校验
- Token成本统计

使用方式:
    from orion import LLMClient, call_llm
    
    client = LLMClient()
    result = client.call("S11", {"raw_requirement": "..."}, enable_llm=False)
"""

from .client import LLMClient, LLMResponse, call_llm
from .templates import (
    get_template, 
    get_all_templates, 
    build_prompt,
    PromptTemplate,
    TEMPLATE_REGISTRY,
    PROMPT_TEMPLATES_TABLE_SCHEMA
)
from .validator import (
    OutputValidator,
    validate_output,
    ValidationResult,
    ValidationLevel,
    ValidationErrorDetail
)
from .cost_tracker import (
    CostTracker,
    get_cost_tracker,
    TokenUsage,
    ModelPricing,
    ModelProvider
)

__version__ = "1.0.0"
__author__ = "Orion Team"
