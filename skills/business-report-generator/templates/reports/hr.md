# 人力资源报告 — {{ report_period }}

---

## 👥 人力核心指标

| 指标 | 当前值 | 上期值 | 变化 | 目标值 |
|------|--------|--------|------|--------|
{% for kpi in kpis %}| {{ kpi.name }} | {{ kpi.current }} | {{ kpi.previous }} | {{ kpi.change }} | {{ kpi.target }} |
{% endfor %}

---

## 📊 人员结构分析

### 整体编制情况
{{ headcount_analysis }}

{% if chart_headcount_trend %}
![人员数量趋势图]({{ chart_headcount_trend }})
{% endif %}

### 人员结构分布

| 维度 | 分类 | 人数 | 占比 |
|------|------|------|------|
{% for structure in staff_structures %}| {{ structure.dimension }} | {{ structure.category }} | {{ structure.count }} | {{ structure.percentage }}% |
{% endfor %}

{% if chart_staff_structure %}
![人员结构图]({{ chart_staff_structure }})
{% endif %}

---

## 🎯 招聘分析
{{ recruitment_analysis }}

| 招聘渠道 | 收到简历 | 面试人数 | 录用人数 | 到岗人数 | 转化率 |
|----------|----------|----------|----------|----------|--------|
{% for channel in recruitment_channels %}| {{ channel.name }} | {{ channel.resumes }} | {{ channel.interviews }} | {{ channel.offers }} | {{ channel.hired }} | {{ channel.conversion }}% |
{% endfor %}

{% if chart_recruitment_funnel %}
![招聘漏斗图]({{ chart_recruitment_funnel }})
{% endif %}

---

## 💫 员工异动分析

### 入职情况
{{ onboarding_analysis }}

### 离职情况
{{ turnover_analysis }}

{% if chart_turnover %}
![离职率趋势图]({{ chart_turnover }})
{% endif %}

---

## 📈 培训与发展
{{ training_analysis }}

| 培训项目 | 参训人数 | 培训时长 | 满意度 | 费用 |
|----------|----------|----------|--------|------|
{% for training in trainings %}| {{ training.name }} | {{ training.attendees }} | {{ training.hours }} | {{ training.satisfaction }} | {{ training.cost }} |
{% endfor %}

---

## 💼 绩效管理
{{ performance_analysis }}

{% if chart_performance_distribution %}
![绩效分布图]({{ chart_performance_distribution }})
{% endif %}

---

## ⚠️ 人力风险与建议
{% for risk in risks %}
### {{ risk.title }}
- **风险等级**: {{ risk.level }}
- **影响**: {{ risk.impact }}
- **建议措施**: {{ risk.solution }}

{% endfor %}

---

## 🎯 下一阶段重点工作
{% for plan in next_plans %}
- [ ] {{ plan.task }} — 负责人: {{ plan.owner }} — 完成时间: {{ plan.deadline }}
{% endfor %}

---

**报告生成时间**: {{ generated_at }}
**报告版本**: v{{ version }}
