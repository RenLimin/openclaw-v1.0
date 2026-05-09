#!/usr/bin/env python3
"""
数据校验模块
============
负责CSV数据加载、格式校验、类型转换
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any

logger = logging.getLogger(__name__)


class DataValidator:
    """数据校验器"""
    
    # 预期的文件和列名配置
    EXPECTED_FILES = {
        '签约项目统计': {
            'prefix': '周报-签约项目统计',
            'expected_rows': None,  # 运行时验证
            'required_columns': [
                'BI履约ID', '最终用户名称', '客户名称', '责任销售（履约项）',
                '责任销售所属团队', '负责人', '所属项目', '项目类型(概览)',
                '项目状态', '立项日期', '基线-预估结项日期', '实际结项日期',
                '销售合同编号', '合同名称', '直签或代理', '合同归档日期',
                '合同起始日期', '合同结束日期', '交付服务开始日期', '交付服务结束日期',
                '合同验收条款', '验收时点', '验收方式', '标题', '标准产品/服务序号',
                '履约类型', '所属产线', '状态', '履约项异常/变更备注',
                '履约项优先级', '预估交付完成日期', '预算-预估交付完成日期',
                '交付邮件发送日期', '实际服务/授权开始日期', '实际服务/授权结束日期',
                '预估验收完成日期', '预算-预估验收完成日期', '备注', 'PMO备注',
                'ID', '事业部（区域）', '事业部负责人', '异常报备日期',
                '预估异常处置完成日期', '异常归档日期', '异常影响情况',
                '异常项目-类别', '异常项目-处置方案', '异常处置方案-影响',
                '交付说明（异常履约项统计类别）', '交付说明（履约项交付情况、合同交付条款）',
                '交付中心反馈', '营销中心反馈', '项目异常内容', '预估金额'
            ]
        },
        'POC提前实施': {
            'prefix': 'POC&提前实施统计',
            'expected_rows': None,
            'required_columns': []  # 动态获取
        },
        '异常处置': {
            'prefix': '签约项目异常处置',
            'expected_rows': None,
            'required_columns': []  # 动态获取
        },
        '确收': {
            'prefix': '确收凭证交接-确收',
            'expected_rows': None,
            'required_columns': []  # 动态获取
        },
        '验收': {
            'prefix': '确收凭证交接-验收',
            'expected_rows': None,
            'required_columns': []  # 动态获取
        }
    }
    
    def __init__(self, data_dir: str, month_prefix: str):
        """
        初始化数据校验器
        
        Args:
            data_dir: 数据目录路径
            month_prefix: 月份前缀，如 '202602'
        """
        self.data_dir = Path(data_dir)
        self.month_prefix = month_prefix
        self.dataframes: Dict[str, pd.DataFrame] = {}
        self.validation_report: Dict[str, Any] = {
            'success': True,
            'errors': [],
            'warnings': [],
            'files': {}
        }
    
    def load_all_csv(self) -> Dict[str, pd.DataFrame]:
        """加载所有CSV文件"""
        logger.info("开始加载CSV文件...")
        
        for file_key, config in self.EXPECTED_FILES.items():
            try:
                # 查找匹配的文件
                pattern = f"{self.month_prefix}*{config['prefix']}*.csv"
                matching_files = list(self.data_dir.glob(pattern))
                
                if not matching_files:
                    self.validation_report['errors'].append(
                        f"未找到文件: {file_key} (pattern: {pattern})"
                    )
                    self.validation_report['success'] = False
                    continue
                
                file_path = matching_files[0]
                logger.info(f"加载 {file_key}: {file_path.name}")
                
                # 读取CSV
                df = pd.read_csv(file_path, dtype=str, low_memory=False)
                
                # 存储原始行数（含表头）
                row_count = len(df)
                self.validation_report['files'][file_key] = {
                    'filename': file_path.name,
                    'rows': row_count,
                    'columns': len(df.columns.tolist()),
                    'column_names': df.columns.tolist()
                }
                
                logger.info(f"  行数: {row_count}, 列数: {len(df.columns)}")
                
                self.dataframes[file_key] = df
                
            except Exception as e:
                error_msg = f"加载 {file_key} 失败: {str(e)}"
                logger.error(error_msg)
                self.validation_report['errors'].append(error_msg)
                self.validation_report['success'] = False
        
        return self.dataframes
    
    def validate_row_counts(self, expected_signing_rows: int = None) -> bool:
        """验证行数"""
        logger.info("验证行数...")
        
        if '签约项目统计' in self.dataframes:
            df = self.dataframes['签约项目统计']
            actual_rows = len(df)
            
            if expected_signing_rows:
                if actual_rows != expected_signing_rows:
                    warning = f"签约项目统计行数不符: 预期 {expected_signing_rows}, 实际 {actual_rows}"
                    logger.warning(warning)
                    self.validation_report['warnings'].append(warning)
                    self.validation_report['files']['签约项目统计']['expected_rows'] = expected_signing_rows
                    self.validation_report['files']['签约项目统计']['row_match'] = False
                else:
                    logger.info(f"✓ 签约项目统计行数验证通过: {actual_rows}")
                    self.validation_report['files']['签约项目统计']['row_match'] = True
            else:
                logger.info(f"  签约项目统计行数: {actual_rows} (未设置预期值)")
        
        return True
    
    def validate_columns(self) -> bool:
        """验证列名"""
        logger.info("验证列名...")
        
        for file_key, config in self.EXPECTED_FILES.items():
            if file_key not in self.dataframes:
                continue
                
            df = self.dataframes[file_key]
            actual_columns = set(df.columns.tolist())
            required_columns = config['required_columns']
            
            if required_columns:
                missing_columns = set(required_columns) - actual_columns
                if missing_columns:
                    error = f"{file_key} 缺少列: {missing_columns}"
                    logger.error(error)
                    self.validation_report['errors'].append(error)
                    self.validation_report['success'] = False
                else:
                    logger.info(f"✓ {file_key} 列名验证通过")
        
        return self.validation_report['success']
    
    def convert_data_types(self) -> bool:
        """转换数据类型（日期、数值等）"""
        logger.info("转换数据类型...")
        
        date_columns = [
            '立项日期', '基线-预估结项日期', '实际结项日期', '合同归档日期',
            '合同起始日期', '合同结束日期', '交付服务开始日期', '交付服务结束日期',
            '交付邮件发送日期', '实际服务/授权开始日期', '实际服务/授权结束日期',
            '预估验收完成日期', '预算-预估验收完成日期', '异常报备日期',
            '预估异常处置完成日期', '异常归档日期'
        ]
        
        numeric_columns = ['预估金额']
        
        for file_key, df in self.dataframes.items():
            for col in date_columns:
                if col in df.columns:
                    try:
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                    except Exception as e:
                        logger.debug(f"列 {col} 日期转换失败: {e}")
            
            for col in numeric_columns:
                if col in df.columns:
                    try:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    except Exception as e:
                        logger.debug(f"列 {col} 数值转换失败: {e}")
        
        return True
    
    def remove_empty_rows(self) -> Dict[str, int]:
        """移除空行，返回各文件移除的行数"""
        removed_counts = {}
        
        for file_key, df in self.dataframes.items():
            original_count = len(df)
            # 移除全为空的行
            df_cleaned = df.dropna(how='all')
            cleaned_count = len(df_cleaned)
            removed = original_count - cleaned_count
            
            if removed > 0:
                logger.info(f"  {file_key}: 移除 {removed} 行空行")
                self.dataframes[file_key] = df_cleaned
                removed_counts[file_key] = removed
        
        return removed_counts
    
    def run_validation(self, expected_signing_rows: int = None) -> Dict[str, Any]:
        """运行完整校验流程"""
        logger.info("=" * 60)
        logger.info("开始数据校验流程")
        logger.info("=" * 60)
        
        # 1. 加载所有CSV
        self.load_all_csv()
        
        if not self.dataframes:
            logger.error("没有成功加载任何数据文件")
            return self.validation_report
        
        # 2. 验证行数
        self.validate_row_counts(expected_signing_rows)
        
        # 3. 验证列名
        self.validate_columns()
        
        # 4. 移除空行
        self.remove_empty_rows()
        
        # 5. 转换数据类型
        self.convert_data_types()
        
        # 输出摘要
        logger.info("=" * 60)
        if self.validation_report['success']:
            logger.info("✓ 数据校验完成")
        else:
            logger.warning("⚠ 数据校验完成，但存在错误")
        
        for file_key, info in self.validation_report['files'].items():
            logger.info(f"  {file_key}: {info['rows']} 行 x {info['columns']} 列")
        
        if self.validation_report['warnings']:
            logger.info(f"警告数: {len(self.validation_report['warnings'])}")
        if self.validation_report['errors']:
            logger.error(f"错误数: {len(self.validation_report['errors'])}")
        
        logger.info("=" * 60)
        
        return self.validation_report
    
    def get_dataframe(self, name: str) -> pd.DataFrame:
        """获取指定的DataFrame"""
        return self.dataframes.get(name)
    
    def get_all_dataframes(self) -> Dict[str, pd.DataFrame]:
        """获取所有DataFrame"""
        return self.dataframes
