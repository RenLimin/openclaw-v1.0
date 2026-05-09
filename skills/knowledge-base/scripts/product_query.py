#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标准产品/服务清单查询接口
用于合同履约义务拆分、合同审核时自动匹配标准产品定义
"""
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

DATA_DIR = Path(__file__).parent.parent / 'data' / 'standard-products'


class ProductQueryEngine:
    """产品查询引擎"""
    
    def __init__(self):
        self._load_data()
        
    def _load_data(self):
        """加载所有YAML数据"""
        # 产品主清单
        with open(DATA_DIR / 'product-list.yaml', 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            self.products = data.get('products', [])
            self.product_lines = data.get('product_lines', [])
            self.version = data.get('version', '1.0')
            self.total_products = data.get('total_products', 0)
            
        # 匹配规则
        with open(DATA_DIR / 'matching-rules.yaml', 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            self.category_keywords = data.get('category_keywords', {})
            self.match_threshold = data.get('match_threshold', 0.6)
            self.product_code_pattern = data.get('product_code_pattern', r'AS-[A-Z0-9\-]+')
            
        # 偏差规则
        with open(DATA_DIR / 'deviation-rules.yaml', 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            self.deviation_types = {d['code']: d for d in data.get('deviation_types', [])}
            self.risk_scoring = data.get('risk_scoring', {})
            self.review_templates = data.get('review_advice_templates', {})
        
        # 构建索引
        self._build_indexes()
        print(f"✅ 产品查询引擎加载完成，共 {self.total_products} 个产品")
    
    def _build_indexes(self):
        """构建各种查询索引"""
        # 产品编码索引
        self.code_index = {p['product_code']: p for p in self.products if p.get('product_code')}
        # ID索引
        self.id_index = {p['id']: p for p in self.products if p.get('id')}
        # 产品线索引
        self.line_index = {}
        for p in self.products:
            line = p.get('product_line', '其他')
            if line not in self.line_index:
                self.line_index[line] = []
            self.line_index[line].append(p)
        # 类别索引
        self.category_index = {}
        for p in self.products:
            cat = p.get('product_category', '其他')
            if cat not in self.category_index:
                self.category_index[cat] = []
            self.category_index[cat].append(p)
    
    # ==========================================
    # 查询接口
    # ==========================================
    
    def get_by_code(self, product_code: str) -> Optional[Dict]:
        """按产品编码精确查询"""
        return self.code_index.get(product_code.strip().upper())
    
    def get_by_id(self, product_id: int) -> Optional[Dict]:
        """按ID精确查询"""
        return self.id_index.get(int(product_id))
    
    def get_by_product_line(self, product_line: str) -> List[Dict]:
        """按产品线查询"""
        return self.line_index.get(product_line, [])
    
    def get_by_category(self, category: str) -> List[Dict]:
        """按产品类别查询"""
        return self.category_index.get(category, [])
    
    def search_by_keyword(self, keyword: str, limit: int = 10) -> List[Dict]:
        """按关键词模糊搜索产品"""
        keyword = keyword.lower()
        results = []
        for p in self.products:
            # 在多个字段中搜索
            search_fields = [
                p.get('product_name', ''),
                p.get('product_model', ''),
                p.get('service_name', ''),
                p.get('service_description', ''),
                p.get('product_code', ''),
            ]
            for field in search_fields:
                if field and keyword in str(field).lower():
                    results.append(p)
                    break
        return results[:limit]
    
    def match_contract_product(self, contract_content: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
        """从合同文本中智能匹配标准产品（用于履约义务拆分/合同审核）"""
        matches = []
        
        # 1. 先尝试匹配产品编码（最精确）
        product_codes = re.findall(self.product_code_pattern, contract_content, re.IGNORECASE)
        for code in product_codes:
            product = self.get_by_code(code)
            if product:
                matches.append((product, 1.0))  # 100%置信度
        
        # 2. 关键词匹配
        contract_lower = contract_content.lower()
        for p in self.products:
            score = 0.0
            # 产品名称权重最高
            name = str(p.get('product_name', '')).lower()
            model = str(p.get('product_model', '')).lower()
            service = str(p.get('service_description', '')).lower()
            
            # 简单字符串匹配计分
            name_words = set(name.split())
            model_words = set(model.split())
            contract_words = set(contract_lower.split())
            
            name_match = len(name_words & contract_words) / max(len(name_words), 1)
            model_match = len(model_words & contract_words) / max(len(model_words), 1)
            
            score = (name_match * 0.5 + model_match * 0.3 + min(len(service) / 500, 0.2))
            
            if score >= self.match_threshold:
                matches.append((p, score))
        
        # 去重 + 按分数排序
        seen_codes = set()
        unique_matches = []
        for p, score in sorted(matches, key=lambda x: -x[1]):
            code = p.get('product_code')
            if code not in seen_codes:
                seen_codes.add(code)
                unique_matches.append((p, score))
        
        return unique_matches[:top_k]
    
    def check_deviation(self, contract_term: str, product: Dict) -> Dict[str, Any]:
        """检查合同条款与标准产品的偏差（用于合同审核）"""
        deviations = []
        total_risk_score = 0
        
        product_desc = str(product.get('service_description', ''))
        product_price = product.get('unit_price', 0)
        
        # 1. 价格偏差检查（从合同条款中提取价格，简单实现）
        price_matches = re.findall(r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:元|圆|￥|RMB)', contract_term)
        for price_str in price_matches:
            try:
                price = float(price_str.replace(',', ''))
                if product_price and abs(price - product_price) / product_price > 0.15:
                    deviation = self.deviation_types['PRICE_DEVIATION'].copy()
                    deviation['actual_value'] = price
                    deviation['standard_value'] = product_price
                    deviation['diff_percent'] = abs(price - product_price) / product_price * 100
                    deviations.append(deviation)
                    total_risk_score += self.risk_scoring.get(deviation['risk_level'], 5)
            except:
                pass
        
        # 2. 服务范围偏差（简单关键词比对）
        required_keywords = ['交付', '验收', '维保', '保修', '支持', '服务']
        for kw in required_keywords:
            if kw in contract_term and kw not in product_desc:
                deviation = self.deviation_types['SCOPE_DEVIATION'].copy()
                deviation['missing_keyword'] = kw
                deviations.append(deviation)
                total_risk_score += self.risk_scoring.get(deviation['risk_level'], 5)
                break
        
        # 3. 定制化检查
        if '定制' in contract_term or '开发' in contract_term:
            deviation = self.deviation_types['CUSTOMIZATION_REQUIRED'].copy()
            deviations.append(deviation)
            total_risk_score += self.risk_scoring.get(deviation['risk_level'], 5)
        
        # 风险分级
        if total_risk_score >= 10:
            risk_level = '高风险'
        elif total_risk_score >= 5:
            risk_level = '中风险'
        else:
            risk_level = '低风险'
        
        return {
            'has_deviation': len(deviations) > 0,
            'risk_level': risk_level,
            'risk_score': total_risk_score,
            'deviations': deviations,
            'review_advice': self.review_templates.get(risk_level, ''),
        }
    
    def get_all_product_lines(self) -> List[str]:
        """获取所有产品线列表"""
        return list(self.line_index.keys())
    
    def get_all_categories(self) -> List[str]:
        """获取所有产品类别列表"""
        return list(self.category_index.keys())
    
    def stats(self) -> Dict:
        """获取统计信息"""
        return {
            'version': self.version,
            'total_products': self.total_products,
            'product_lines': len(self.line_index),
            'categories': len(self.category_index),
        }


def main():
    """命令行测试"""
    engine = ProductQueryEngine()
    
    print("\n📊 产品库统计:")
    stats = engine.stats()
    for k, v in stats.items():
        print(f"  {k}: {v}")
    
    print("\n🔍 产品线列表:")
    for line in engine.get_all_product_lines()[:10]:
        print(f"  - {line} ({len(engine.get_by_product_line(line))}个产品)")
    
    print("\n🔍 搜索测试: '全渠道应用安全监测'")
    results = engine.search_by_keyword('全渠道应用安全监测', limit=3)
    for p in results:
        print(f"  - {p['product_code']}: {p['product_name']} ({p['product_model']})")
    
    print("\n✅ 产品查询引擎测试通过！")


if __name__ == '__main__':
    main()
