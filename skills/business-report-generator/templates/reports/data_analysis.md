# 数据分析报告 — {{ analysis_topic }}

**数据来源**: {{ data_source }}
**分析周期**: {{ analysis_period }}
**分析人员**: {{ analyst }}

---

## 📊 核心指标摘要

| 指标 | 数值 | 同比变化 | 环比变化 | 备注 |
|------|------|----------|----------|------|
{% for kpi in kpis %}| {{ kpi.name }} | {{ kpi.value }} | {{ kpi.yoy }} | {{ kpi.mom }} | {{ kpi.remark }} |
{% endfor %}

---

## 🔍 数据概览
{{ data_overview }}

### 数据质量检查
- **数据行数**: {{ row_count }}
- **数据列数**: {{ column_count }}
- **缺失值率**: {{ missing_rate }}%
- **异常值检测**: {{ anomaly_check }}

---

## 📈 趋势分析
{{ trend_analysis }}

{% if chart_trend_line %}
![趋势分析图]({{ chart_trend_line }})
{% endif %}

### 关键发现
{% for finding in trend_findings %}
- {{ finding }}
{% endfor %}

---

## 📊 对比分析
{{ comparison_analysis }}

{% if chart_comparison_bar %}
![对比分析图]({{ chart_comparison_bar }})
{% endif %}

### 组间差异
{% for diff in group_differences %}
- **{{ diff.group }}**: {{ diff.description }}
{% endfor %}

---

## 🥧 结构分析
{{ structure_analysis }}

{% if chart_structure_pie %}
![结构分析图]({{ chart_structure_pie }})
{% endif %}

### 构成占比
| 分类 | 数值 | 占比 | 同比变化 |
|------|------|------|----------|
{% for item in structure_items %}| {{ item.name }} | {{ item.value }} | {{ item.percentage }}% | {{ item.yoy }} |
{% endfor %}

---

## 🎯 相关性分析
{{ correlation_analysis }}

{% if chart_correlation_heatmap %}
![相关性热力图]({{ chart_correlation_heatmap }})
{% endif %}

### 强相关关系
{% for corr in strong_correlations %}
- **{{ corr.variable_a }}** 与 **{{ corr.variable_b }}**: 相关系数 {{ corr.coefficient }}
{% endfor %}

---

## 📉 异常与离群点分析
{{ anomaly_analysis }}

| 异常点 | 数值 | 偏离均值 | 可能原因 |
|--------|------|----------|----------|
{% for anomaly in anomalies %}| {{ anomaly.name }} | {{ anomaly.value }} | {{ anomaly.deviation }} | {{ anomaly.reason }} |
{% endfor %}

---

## 💡 洞察与建议

### 核心洞察
{% for insight in insights %}
- {{ insight }}
{% endfor %}

### 行动建议
{% for recommendation in recommendations %}
- [ ] {{ recommendation.action }} — 优先级: {{ recommendation.priority }} — 预期效果: {{ recommendation.expected }}
{% endfor %}

---

**报告生成时间**: {{ generated_at }}
**报告版本**: v{{ version }}
