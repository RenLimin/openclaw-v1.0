# {{ year }}年{{ month }}月 经营月报

---

## 📊 关键指标概览

| 指标 | 本月实际 | 上月实际 | 环比 | 去年同期 | 同比 | 年度目标 | 完成率 |
|------|----------|----------|------|----------|------|----------|--------|
{% for kpi in kpis %}| {{ kpi.name }} | {{ kpi.current }} | {{ kpi.previous }} | {{ kpi.mom }} | {{ kpi.last_year }} | {{ kpi.yoy }} | {{ kpi.target }} | {{ kpi.completion_rate }} |
{% endfor %}

---

## 🔥 本月亮点
{% for highlight in highlights %}
- {{ highlight }}
{% endfor %}

## 📈 经营业绩分析

### 收入分析
{{ revenue_analysis }}

{% if chart_revenue_trend %}
![月度收入趋势图]({{ chart_revenue_trend }})
{% endif %}

{% if chart_revenue_comparison %}
![收入同比对比图]({{ chart_revenue_comparison }})
{% endif %}

### 利润分析
{{ profit_analysis }}

{% if chart_profit_margin %}
![利润率趋势图]({{ chart_profit_margin }})
{% endif %}

### 成本分析
{{ cost_analysis }}

{% if chart_cost_structure %}
![成本结构图]({{ chart_cost_structure }})
{% endif %}

---

## 📋 业务部门表现

{% for dept in departments %}
### {{ dept.name }}
- **业绩**: {{ dept.performance }}
- **排名**: {{ dept.rank }}
- **贡献度**: {{ dept.contribution }}%

{% endfor %}

---

## 🚧 项目进展汇总

| 项目名称 | 状态 | 进度 | 本月产出 |
|----------|------|------|----------|
{% for project in projects %}| {{ project.name }} | {{ project.status }} | {{ project.progress }}% | {{ project.output }} |
{% endfor %}

---

## ⚠️ 问题与风险
{% for risk in risks %}
### {{ risk.title }}
- **等级**: {{ risk.level }}
- **影响**: {{ risk.impact }}
- **对策**: {{ risk.solution }}

{% endfor %}

---

## 🎯 下月工作计划
{% for plan in next_month_plans %}
- [ ] {{ plan.task }} — 负责人: {{ plan.owner }} — 预期成果: {{ plan.expected }}
{% endfor %}

---

**报告生成时间**: {{ generated_at }}
**报告版本**: v{{ version }}
