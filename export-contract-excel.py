#!/usr/bin/env python3
"""
合同条款拆分 - Excel 导出
将合同完整拆分并导出为 Excel 文件
"""
import json
import re
from pathlib import Path
from docx import Document

try:
    import pandas as pd
    print("✅ pandas 已加载")
except ImportError:
    print("❌ 请安装 pandas: pip install pandas openpyxl")
    exit(1)

print("=" * 80)
print("📄 合同条款拆分 - Excel 导出")
print("=" * 80)

# 1. 加载配置
config_path = Path(__file__).parent / 'skills/contract-clause-split/config/contract-split-config.json'
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# 2. 加载合同
test_file = '/Users/bangcle/Downloads/contract/XSZS2603090130北京聚信得仁 - 采购合同（设备）-移动应用合格平台检测设备采购项目-聚信得仁-梆梆.docx'
print(f"\n📂 处理文件: {Path(test_file).name}")

doc = Document(test_file)

# 3. 提取所有非空段落
paragraphs = []
for p in doc.paragraphs:
    text = p.text.strip()
    if text and len(text) > 5:  # 过滤短空白行
        paragraphs.append(text)

print(f"📝 提取有效段落: {len(paragraphs)} 条")

# 4. 条款分类函数
def classify_clause(text):
    for cat_key, cat_val in config['clause_categories'].items():
        for keyword in cat_val.get('keywords', []):
            if keyword in text:
                return cat_val['name'], cat_key
    return "其他条款", "other"

# 5. 风险检测函数
def check_risk(text):
    risk_levels = []
    risk_words = []
    for level, keywords in config['risk_keywords'].items():
        for kw in keywords:
            if kw in text:
                risk_levels.append(level)
                risk_words.append(kw)
    if risk_levels:
        if 'high' in risk_levels:
            return "🔴 高风险", ", ".join(risk_words)
        elif 'medium' in risk_levels:
            return "🟡 中风险", ", ".join(risk_words)
        else:
            return "🟢 低风险", ", ".join(risk_words)
    return "✅ 无风险", ""

# 6. 处理所有条款
clauses_data = []
for i, para_text in enumerate(paragraphs, 1):
    category_name, category_key = classify_clause(para_text)
    risk_level, risk_words = check_risk(para_text)
    
    clauses_data.append({
        '条款编号': i,
        '条款分类': category_name,
        '风险等级': risk_level,
        '风险关键词': risk_words,
        '条款内容': para_text,
        '字数': len(para_text)
    })

# 7. 创建 DataFrame 并导出
df = pd.DataFrame(clauses_data)

# 统计信息
print(f"\n📊 拆分统计:")
print(f"   总条款数: {len(df)}")
print(f"   分类统计:")
for cat, count in df['条款分类'].value_counts().items():
    print(f"      {cat}: {count} 条")

print(f"\n⚠️  风险统计:")
for level, count in df['风险等级'].value_counts().items():
    print(f"      {level}: {count} 条")

# 8. 导出 Excel
output_file = Path.home() / 'Downloads' / '合同条款拆分结果_聚信得仁采购合同.xlsx'

# 使用 openpyxl 引擎导出
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    # Sheet 1: 全部条款
    df.to_excel(writer, sheet_name='全部条款', index=False)
    
    # Sheet 2-13: 按分类拆分
    for cat_name in [v['name'] for v in config['clause_categories'].values()]:
        cat_df = df[df['条款分类'] == cat_name]
        if len(cat_df) > 0:
            cat_df.to_excel(writer, sheet_name=cat_name[:15], index=False)
    
    # Sheet 14: 仅风险条款
    risk_df = df[df['风险等级'] != '✅ 无风险']
    risk_df.to_excel(writer, sheet_name='风险条款汇总', index=False)

print(f"\n📥 Excel 文件已导出:")
print(f"   {output_file}")
print(f"   工作表数: {len(config['clause_categories']) + 2} 个")

# 9. 同时导出 Markdown 预览
md_file = Path.home() / 'Downloads' / '合同条款拆分结果_聚信得仁采购合同.md'
with open(md_file, 'w', encoding='utf-8') as f:
    f.write("# 合同条款拆分报告\n\n")
    f.write(f"> 合同名称: 移动应用合格平台检测设备采购项目\n")
    f.write(f"> 导出时间: 2026-04-23 16:45\n")
    f.write(f"> 总条款数: {len(df)} 条\n\n")
    
    f.write("## 📊 分类统计\n\n")
    for cat, count in df['条款分类'].value_counts().items():
        f.write(f"- {cat}: {count} 条\n")
    
    f.write("\n## ⚠️ 风险条款汇总\n\n")
    for _, row in risk_df.iterrows():
        f.write(f"### [{row['风险等级']}] 条款 {row['条款编号']}\n")
        f.write(f"> 关键词: {row['风险关键词']}\n\n")
        f.write(f"{row['条款内容'][:300]}{'...' if len(row['条款内容']) > 300 else ''}\n\n")
    
    f.write("\n## 📋 全部条款\n\n")
    for _, row in df.iterrows():
        f.write(f"### {row['条款编号']}. [{row['条款分类']}] {row['风险等级']}\n\n")
        f.write(f"{row['条款内容']}\n\n")

print(f"📄 Markdown 预览已导出:")
print(f"   {md_file}")

print("\n" + "=" * 80)
print("✅ 导出完成！正在打开 Excel 文件...")
print("=" * 80)

# 打开文件
import subprocess
subprocess.run(['open', str(output_file)])
