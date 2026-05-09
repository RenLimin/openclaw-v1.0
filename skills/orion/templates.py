"""
Orion LLM调度框架 - Prompt模板管理 (已重构)
包含基类定义和完整模板注册表

注意：模板已按编号范围拆分为:
- templates_base.py: 基类和表结构定义
- templates_s11_s15.py: S11-S15模板 (需求分析、风险管理、立项、会议纪要、周报)
- templates_s16_s20.py: S16-S20模板 (月报、健康度评估、验收、复盘、经验推荐)
"""

from typing import Dict, Any, Optional

# 导入基类
from .templates_base import (
    OutputFormat,
    PromptTemplate,
    PROMPT_TEMPLATES_TABLE_SCHEMA,
)

# 导入S11-S15模板
from .templates_s11_s15 import (
    TEMPLATE_S11,
    TEMPLATE_S12,
    TEMPLATE_S13,
    TEMPLATE_S14,
    TEMPLATE_S15,
    TEMPLATES_S11_S15,
)

# 导入S16-S20模板
from .templates_s16_s20 import (
    TEMPLATE_S16,
    TEMPLATE_S17,
    TEMPLATE_S18,
    TEMPLATE_S19,
    TEMPLATE_S20,
    TEMPLATES_S16_S20,
)


# ==================== 完整模板注册表 ====================
TEMPLATE_REGISTRY: Dict[str, PromptTemplate] = {
    **TEMPLATES_S11_S15,
    **TEMPLATES_S16_S20,
}


def get_template(template_id: str) -> Optional[PromptTemplate]:
    """
    获取指定ID的Prompt模板
    
    Args:
        template_id: 模板ID (如 "S11", "S12")
        
    Returns:
        Optional[PromptTemplate]: 找到的模板对象，未找到则返回None
    """
    return TEMPLATE_REGISTRY.get(template_id)


def get_all_templates() -> Dict[str, PromptTemplate]:
    """
    获取所有可用的模板
    
    Returns:
        Dict[str, PromptTemplate]: 完整的模板字典
    """
    return TEMPLATE_REGISTRY


def build_prompt(template_id: str, data: Dict[str, Any]) -> Optional[str]:
    """
    根据模板和输入数据构建完整的Prompt
    
    Args:
        template_id: 模板ID
        data: 输入数据字典
        
    Returns:
        Optional[str]: 构建完成的Prompt，模板不存在则返回None
    """
    template = get_template(template_id)
    if not template:
        return None
    
    system_prompt = template.system_prompt
    
    # 添加输入数据到用户prompt
    user_prompt = f"\n\n输入数据:\n"
    for key, value in data.items():
        user_prompt += f"{key}: {value}\n"
    
    # 添加输出格式要求
    user_prompt += f"\n请严格按照以下JSON格式输出:\n"
    user_prompt += f"输出Schema: {template.output_schema}\n"
    
    return f"{system_prompt}\n\n{user_prompt}"
