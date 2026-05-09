"""
Orion LLM调度框架 - 结构化输出校验机制
提供JSON Schema校验、数据类型校验、自定义规则校验等功能
"""

import json
import re
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from jsonschema import validate, ValidationError, Draft7Validator


class ValidationLevel(Enum):
    """校验级别"""
    STRICT = "strict"  # 严格模式，任何错误都失败
    WARN = "warn"      # 警告模式，记录警告但不失败
    LENIENT = "lenient"  # 宽松模式，只校验关键字段


class ErrorType(Enum):
    """错误类型"""
    SCHEMA_ERROR = "schema_error"
    TYPE_ERROR = "type_error"
    FORMAT_ERROR = "format_error"
    MISSING_FIELD = "missing_field"
    VALUE_ERROR = "value_error"
    CUSTOM_RULE_ERROR = "custom_rule_error"


@dataclass
class ValidationErrorDetail:
    """校验错误详情"""
    error_type: ErrorType
    field_path: str
    message: str
    severity: str = "error"
    suggested_fix: Optional[str] = None


@dataclass
class ValidationResult:
    """校验结果"""
    is_valid: bool
    errors: List[ValidationErrorDetail]
    warnings: List[ValidationErrorDetail]
    corrected_data: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
    
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0
    
    def add_error(self, error: ValidationErrorDetail):
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: ValidationErrorDetail):
        self.warnings.append(warning)


class OutputValidator:
    """结构化输出校验器"""
    
    def __init__(self, level: ValidationLevel = ValidationLevel.STRICT):
        self.level = level
        self.custom_rules = {}
    
    def validate(self, data: Union[str, Dict[str, Any]], schema: Dict[str, Any]) -> ValidationResult:
        """
        主校验入口
        
        Args:
            data: 待校验的数据，可以是JSON字符串或字典
            schema: JSON Schema定义
            
        Returns:
            ValidationResult 校验结果
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        
        # 1. 解析JSON字符串
        parsed_data, parse_errors = self._parse_json(data)
        if parse_errors:
            for err in parse_errors:
                result.add_error(err)
            return result
        
        # 2. JSON Schema校验
        schema_errors = self._validate_schema(parsed_data, schema)
        for err in schema_errors:
            result.add_error(err)
        
        # 3. 业务规则校验
        business_errors = self._validate_business_rules(parsed_data, schema)
        for err in business_errors:
            result.add_error(err)
        
        # 4. 自动修复尝试
        if not result.is_valid and self.level != ValidationLevel.STRICT:
            corrected = self._auto_correct(parsed_data, schema, result.errors)
            if corrected:
                result.corrected_data = corrected
        
        return result
    
    def _parse_json(self, data: Union[str, Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], List[ValidationErrorDetail]]:
        """解析JSON字符串"""
        errors = []
        
        if isinstance(data, dict):
            return data, errors
        
        if not isinstance(data, str):
            errors.append(ValidationErrorDetail(
                error_type=ErrorType.TYPE_ERROR,
                field_path="",
                message=f"期望字符串或字典类型，实际得到{type(data).__name__}"
            ))
            return None, errors
        
        try:
            # 尝试提取JSON内容（处理可能的Markdown代码块包裹）
            json_str = self._extract_json_from_text(data)
            parsed = json.loads(json_str)
            return parsed, errors
        except json.JSONDecodeError as e:
            errors.append(ValidationErrorDetail(
                error_type=ErrorType.FORMAT_ERROR,
                field_path="",
                message=f"JSON解析失败: {str(e)}",
                suggested_fix="请检查JSON格式是否正确，确保没有语法错误"
            ))
            return None, errors
    
    def _extract_json_from_text(self, text: str) -> str:
        """从文本中提取JSON内容（处理Markdown代码块）"""
        # 匹配 ```json ... ``` 格式
        json_block_pattern = r'```json\s*([\s\S]*?)\s*```'
        match = re.search(json_block_pattern, text)
        if match:
            return match.group(1)
        
        # 匹配 ``` ... ``` 格式
        generic_block_pattern = r'```\s*([\s\S]*?)\s*```'
        match = re.search(generic_block_pattern, text)
        if match:
            return match.group(1)
        
        # 尝试找到最外层的 {}
        brace_start = text.find('{')
        brace_end = text.rfind('}')
        if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
            return text[brace_start:brace_end + 1]
        
        return text
    
    def _validate_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> List[ValidationErrorDetail]:
        """JSON Schema校验"""
        errors = []
        
        try:
            validate(instance=data, schema=schema)
        except ValidationError as e:
            # 转换为我们的错误格式
            validator = Draft7Validator(schema)
            for error in validator.iter_errors(data):
                field_path = ".".join(str(p) for p in error.path) if error.path else "root"
                
                suggested_fix = self._get_suggested_fix(error)
                
                errors.append(ValidationErrorDetail(
                    error_type=ErrorType.SCHEMA_ERROR,
                    field_path=field_path,
                    message=error.message,
                    suggested_fix=suggested_fix
                ))
        
        return errors
    
    def _get_suggested_fix(self, error: ValidationError) -> Optional[str]:
        """根据错误类型提供修复建议"""
        if "is not of type" in error.message:
            return f"请确保该字段类型为{error.validator_value}"
        elif "is a required property" in error.message:
            return "请添加这个必填字段"
        elif "is not one of" in error.message:
            return f"请从允许的值中选择: {error.validator_value}"
        elif "is too long" in error.message:
            return f"请缩短内容到{error.validator_value}字符以内"
        elif "is too short" in error.message:
            return f"请增加内容长度至少到{error.validator_value}字符"
        return None
    
    def _validate_business_rules(self, data: Dict[str, Any], schema: Dict[str, Any]) -> List[ValidationErrorDetail]:
        """业务规则校验"""
        errors = []
        
        # 校验枚举值
        errors.extend(self._validate_enum_values(data, schema))
        
        # 校验日期格式
        errors.extend(self._validate_date_formats(data))
        
        # 校验邮箱格式
        errors.extend(self._validate_email_formats(data))
        
        return errors
    
    def _validate_enum_values(self, data: Dict[str, Any], schema: Dict[str, Any], path: str = "") -> List[ValidationErrorDetail]:
        """递归校验枚举值"""
        errors = []
        
        if "properties" in schema:
            for prop_name, prop_schema in schema["properties"].items():
                current_path = f"{path}.{prop_name}" if path else prop_name
                
                if prop_name in data:
                    prop_value = data[prop_name]
                    
                    # 校验枚举
                    if "enum" in prop_schema and prop_value not in prop_schema["enum"]:
                        errors.append(ValidationErrorDetail(
                            error_type=ErrorType.VALUE_ERROR,
                            field_path=current_path,
                            message=f"值'{prop_value}'不在允许的枚举值中: {prop_schema['enum']}",
                            suggested_fix=f"请从以下值中选择: {', '.join(prop_schema['enum'])}"
                        ))
                    
                    # 递归校验对象属性
                    if prop_schema.get("type") == "object" and isinstance(prop_value, dict):
                        errors.extend(self._validate_enum_values(prop_value, prop_schema, current_path))
                    
                    # 递归校验数组项
                    if prop_schema.get("type") == "array" and isinstance(prop_value, list):
                        item_schema = prop_schema.get("items", {})
                        for i, item in enumerate(prop_value):
                            item_path = f"{current_path}[{i}]"
                            if isinstance(item, dict) and "properties" in item_schema:
                                errors.extend(self._validate_enum_values(item, item_schema, item_path))
        
        return errors
    
    def _validate_date_formats(self, data: Dict[str, Any], path: str = "") -> List[ValidationErrorDetail]:
        """校验日期格式"""
        errors = []
        date_pattern = r'^\d{4}-\d{2}-\d{2}( \d{2}:\d{2}(:\d{2})?)?$'
        
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            
            if isinstance(value, str) and key in ["date", "deadline", "created_at", "updated_at", "start_date", "end_date"]:
                if not re.match(date_pattern, value):
                    errors.append(ValidationErrorDetail(
                        error_type=ErrorType.FORMAT_ERROR,
                        field_path=current_path,
                        message=f"日期格式不正确: {value}",
                        suggested_fix="请使用 YYYY-MM-DD 或 YYYY-MM-DD HH:MM 格式"
                    ))
            
            elif isinstance(value, dict):
                errors.extend(self._validate_date_formats(value, current_path))
            
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        errors.extend(self._validate_date_formats(item, f"{current_path}[{i}]"))
        
        return errors
    
    def _validate_email_formats(self, data: Dict[str, Any], path: str = "") -> List[ValidationErrorDetail]:
        """校验邮箱格式"""
        errors = []
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            
            if isinstance(value, str) and "email" in key.lower():
                if not re.match(email_pattern, value):
                    errors.append(ValidationErrorDetail(
                        error_type=ErrorType.FORMAT_ERROR,
                        field_path=current_path,
                        message=f"邮箱格式不正确: {value}",
                        suggested_fix="请使用标准邮箱格式: user@domain.com"
                    ))
            
            elif isinstance(value, dict):
                errors.extend(self._validate_email_formats(value, current_path))
            
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        errors.extend(self._validate_email_formats(item, f"{current_path}[{i}]"))
        
        return errors
    
    def _auto_correct(self, data: Dict[str, Any], schema: Dict[str, Any], errors: List[ValidationErrorDetail]) -> Optional[Dict[str, Any]]:
        """自动修复尝试"""
        corrected = data.copy()
        
        for error in errors:
            # 修复缺失字段（填充默认值）
            if error.error_type == ErrorType.SCHEMA_ERROR and "is a required property" in error.message:
                field_name = error.field_path
                self._set_default_value(corrected, field_name, schema)
        
        return corrected
    
    def _set_default_value(self, data: Dict[str, Any], field_path: str, schema: Dict[str, Any]):
        """为缺失字段设置默认值"""
        parts = field_path.split('.')
        current = data
        current_schema = schema
        
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {}
            current = current[part]
            if "properties" in current_schema and part in current_schema["properties"]:
                current_schema = current_schema["properties"][part]
        
        field_name = parts[-1]
        
        # 根据schema类型设置默认值
        if "properties" in current_schema and field_name in current_schema["properties"]:
            field_schema = current_schema["properties"][field_name]
            field_type = field_schema.get("type", "string")
            
            if field_type == "string":
                current[field_name] = ""
            elif field_type == "array":
                current[field_name] = []
            elif field_type == "object":
                current[field_name] = {}
            elif field_type == "number" or field_type == "integer":
                current[field_name] = 0
            elif field_type == "boolean":
                current[field_name] = False
    
    def register_custom_rule(self, rule_name: str, rule_func):
        """注册自定义校验规则"""
        self.custom_rules[rule_name] = rule_func


# 便捷函数
def validate_output(data: Union[str, Dict[str, Any]], schema: Dict[str, Any], level: ValidationLevel = ValidationLevel.STRICT) -> ValidationResult:
    """便捷的校验函数"""
    validator = OutputValidator(level=level)
    return validator.validate(data, schema)
