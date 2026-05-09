"""
Orion LLM调度框架 - Prompt模板基类
包含基础数据结构和表结构定义
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
from enum import Enum


class OutputFormat(Enum):
    """LLM输出格式枚举"""
    JSON = "json"
    MARKDOWN = "markdown"
    TEXT = "text"
    XML = "xml"


@dataclass
class PromptTemplate:
    """
    Prompt模板数据结构
    
    Attributes:
        template_id: 模板ID: S11, S12等
        scenario_name: 场景名称
        system_prompt: 系统提示词
        output_format: 输出格式
        output_schema: 输出格式定义(JSON Schema)
        input_params: 输入参数说明
        example_input: 示例输入
        example_output: 示例输出
        version: 版本号
        tags: 标签列表
        created_at: 创建时间
    """
    template_id: str
    scenario_name: str
    system_prompt: str
    output_format: OutputFormat
    output_schema: Dict[str, Any]
    input_params: List[Dict[str, str]]
    example_input: Dict[str, Any]
    example_output: Dict[str, Any]
    version: str = "1.0"
    tags: List[str] = field(default_factory=list)
    created_at: str = ""


# ==================== Prompt模板表结构定义 ====================
# prompt_templates 表结构定义(SQL DDL)
PROMPT_TEMPLATES_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS prompt_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id VARCHAR(32) UNIQUE NOT NULL COMMENT '模板ID: S11, S12等',
    scenario_name VARCHAR(128) NOT NULL COMMENT '场景名称',
    system_prompt TEXT NOT NULL COMMENT '系统提示词',
    output_format VARCHAR(32) DEFAULT 'json' COMMENT '输出格式: json/markdown/text/xml',
    output_schema JSON COMMENT '输出格式定义(JSON Schema)',
    input_params JSON COMMENT '输入参数说明列表',
    example_input JSON COMMENT '示例输入',
    example_output JSON COMMENT '示例输出',
    version VARCHAR(16) DEFAULT '1.0' COMMENT '版本号',
    tags JSON COMMENT '标签列表',
    is_active TINYINT DEFAULT 1 COMMENT '是否启用',
    token_cost_estimate INTEGER DEFAULT 0 COMMENT '预估Token消耗',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_template_id (template_id),
    INDEX idx_scenario (scenario_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Prompt模板表';
"""
