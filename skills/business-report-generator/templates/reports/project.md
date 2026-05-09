# 项目报告 — {{ project_name }}

**项目编号**: {{ project_code }}
**项目经理**: {{ project_manager }}
**报告周期**: {{ report_period }}
**项目状态**: {{ project_status }}

---

## 📊 关键指标概览

| 指标 | 当前值 | 目标值 | 偏差 | 偏差率 |
|------|--------|--------|------|--------|
{% for kpi in kpis %}| {{ kpi.name }} | {{ kpi.current }} | {{ kpi.target }} | {{ kpi.variance }} | {{ kpi.variance_rate }} |
{% endfor %}

---

## 🔥 项目亮点
{% for highlight in highlights %}
- {{ highlight }}
{% endfor %}

## 📈 进度分析

### 整体进度
{{ progress_analysis }}

{% if chart_progress_timeline %}
![项目进度时间线]({{ chart_progress_timeline }})
{% endif %}

### 里程碑达成情况

| 里程碑 | 计划完成 | 实际完成 | 状态 | 延期原因 |
|--------|----------|----------|------|----------|
{% for milestone in milestones %}| {{ milestone.name }} | {{ milestone.plan_date }} | {{ milestone.actual_date }} | {{ milestone.status }} | {{ milestone.reason }} |
{% endfor %}

---

## 💰 成本分析
{{ cost_analysis }}

{% if chart_cost_burn %}
![成本燃尽图]({{ chart_cost_burn }})
{% endif %}

---

## 👥 团队资源

| 角色 | 投入人数 | 计划工时 | 实际工时 | 利用率 |
|------|----------|----------|----------|--------|
{% for resource in resources %}| {{ resource.role }} | {{ resource.headcount }} | {{ resource.plan_hours }} | {{ resource.actual_hours }} | {{ resource.utilization }}% |
{% endfor %}

---

## 🐛 问题与风险
{% for risk in risks %}
### {{ risk.title }}
- **等级**: {{ risk.level }}
- **发生概率**: {{ risk.probability }}%
- **影响范围**: {{ risk.impact }}
- **对策**: {{ risk.solution }}
- **负责人**: {{ risk.owner }}

{% endfor %}

---

## 🎯 下一阶段计划
{% for plan in next_plans %}
- [ ] {{ plan.task }} — 负责人: {{ plan.owner }} — 截止: {{ plan.deadline }}
{% endfor %}

---

**报告生成时间**: {{ generated_at }}
**报告版本**: v{{ version }}
