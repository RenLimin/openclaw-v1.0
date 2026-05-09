# 周报 — {{ week_start }} 至 {{ week_end }}

---

## 📊 关键指标概览

| 指标 | 本周值 | 上周值 | 环比变化 | 目标值 | 完成率 |
|------|--------|--------|----------|--------|--------|
{% for kpi in kpis %}| {{ kpi.name }} | {{ kpi.current }} | {{ kpi.previous }} | {{ kpi.mom }} | {{ kpi.target }} | {{ kpi.completion_rate }} |
{% endfor %}

---

## 🔥 本周亮点
{% for highlight in highlights %}
- {{ highlight }}
{% endfor %}

## 📈 详细经营分析

### 收入分析
{{ revenue_analysis }}

{% if chart_revenue_trend %}
![收入趋势图]({{ chart_revenue_trend }})
{% endif %}

### 成本分析
{{ cost_analysis }}

{% if chart_cost_structure %}
![成本结构图]({{ chart_cost_structure }})
{% endif %}

---

## 📋 项目进度

{% for project in projects %}
### {{ project.name }}
- **状态**: {{ project.status }}
- **完成率**: {{ project.progress }}%
- **里程碑**: {{ project.milestone }}
- **问题**: {{ project.issues }}

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

## 🎯 下周计划
{% for plan in next_week_plans %}
- [ ] {{ plan.task }} — 负责人: {{ plan.owner }} — 截止: {{ plan.deadline }}
{% endfor %}

---

**报告生成时间**: {{ generated_at }}
**报告版本**: v{{ version }}
