# 财务报告 — {{ report_period }}

---

## 💰 核心财务指标

| 指标 | 本期金额 | 上期金额 | 环比 | 年度预算 | 预算执行率 |
|------|----------|----------|------|----------|------------|
{% for kpi in kpis %}| {{ kpi.name }} | {{ kpi.current }} | {{ kpi.previous }} | {{ kpi.mom }} | {{ kpi.budget }} | {{ kpi.budget_rate }} |
{% endfor %}

---

## 📈 利润表分析

### 营业收入
{{ revenue_analysis }}

{% if chart_revenue_breakdown %}
![收入结构图]({{ chart_revenue_breakdown }})
{% endif %}

### 成本费用
{{ cost_analysis }}

{% if chart_cost_trend %}
![成本费用趋势图]({{ chart_cost_trend }})
{% endif %}

### 盈利能力
{{ profit_analysis }}

{% if chart_profitability %}
![盈利能力对比图]({{ chart_profitability }})
{% endif %}

---

## 📊 资产负债表分析

### 资产状况
{{ asset_analysis }}

### 负债状况
{{ liability_analysis }}

{% if chart_asset_structure %}
![资产结构图]({{ chart_asset_structure }})
{% endif %}

---

## 💵 现金流量分析
{{ cashflow_analysis }}

{% if chart_cashflow %}
![现金流量图]({{ chart_cashflow }})
{% endif %}

---

## 📉 关键财务比率

| 比率类型 | 比率名称 | 本期值 | 上期值 | 行业均值 | 评价 |
|----------|----------|--------|--------|----------|------|
{% for ratio in ratios %}| {{ ratio.category }} | {{ ratio.name }} | {{ ratio.current }} | {{ ratio.previous }} | {{ ratio.industry }} | {{ ratio.assessment }} |
{% endfor %}

---

## ⚠️ 财务风险提示
{% for risk in risks %}
### {{ risk.title }}
- **风险等级**: {{ risk.level }}
- **影响范围**: {{ risk.impact }}
- **建议措施**: {{ risk.solution }}

{% endfor %}

---

## 🎯 财务预测与建议
{{ forecast_and_recommendations }}

---

**报告生成时间**: {{ generated_at }}
**报告版本**: v{{ version }}
**编制人**: {{ prepared_by }}
**审核人**: {{ reviewed_by }}
