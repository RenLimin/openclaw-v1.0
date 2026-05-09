# ========================================
# KSA 导入工具
# - 自动迁移现有 skills 目录中的技能
# - 从 memory 目录提取知识
# ========================================

import os
import json
import re
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

from .manager import KSAManager


class SkillImporter:
    """技能自动迁移工具"""

    def __init__(self, skills_root: str = None, manager: KSAManager = None):
        """
        初始化技能导入器
        
        Args:
            skills_root: skills 目录根路径，默认是当前目录的上级
            manager: KSA 管理器实例
        """
        if skills_root is None:
            skills_root = os.path.dirname(os.path.dirname(__file__))
        self.skills_root = skills_root
        self.manager = manager or KSAManager()

    def scan_skills(self) -> List[Dict]:
        """扫描所有技能目录"""
        skills = []
        skills_path = Path(self.skills_root)
        
        if not skills_path.exists():
            return skills
        
        for item in skills_path.iterdir():
            if item.is_dir() and not item.name.startswith('.') and item.name != 'ksa':
                skill_info = self._extract_skill_info(item)
                if skill_info:
                    skills.append(skill_info)
        
        return skills

    def _extract_skill_info(self, skill_dir: Path) -> Optional[Dict]:
        """从技能目录提取技能信息"""
        skill_info = {
            'name': skill_dir.name,
            'skill_path': str(skill_dir),
            'version': '1.0.0',
            'author': '',
            'description': '',
            'tags': [],
            'maturity': 'prototype',
            'inputs': {},
            'outputs': {},
            'limitations': '',
            'entry_point': '',
            'files': {}
        }
        
        # 读取 SKILL.md
        skill_md = skill_dir / 'SKILL.md'
        if skill_md.exists():
            skill_info['files']['SKILL.md'] = skill_md.stat().st_size
            md_content = skill_md.read_text(encoding='utf-8', errors='ignore')
            extracted = self._parse_skill_md(md_content)
            skill_info.update(extracted)
        
        # 读取 README.md
        readme_md = skill_dir / 'README.md'
        if readme_md.exists():
            skill_info['files']['README.md'] = readme_md.stat().st_size
            if not skill_info['description']:
                md_content = readme_md.read_text(encoding='utf-8', errors='ignore')
                skill_info['description'] = self._extract_first_paragraph(md_content)
        
        # 读取 requirements.txt
        requirements = skill_dir / 'requirements.txt'
        if requirements.exists():
            skill_info['files']['requirements.txt'] = requirements.stat().st_size
        
        # 读取 .skill_meta.json
        skill_meta = skill_dir / '.skill_meta.json'
        if skill_meta.exists():
            try:
                meta = json.loads(skill_meta.read_text(encoding='utf-8'))
                if 'version' in meta:
                    skill_info['version'] = meta['version']
                if 'author' in meta:
                    skill_info['author'] = meta['author']
                if 'tags' in meta:
                    skill_info['tags'].extend(meta['tags'])
                if 'maturity' in meta:
                    skill_info['maturity'] = meta['maturity']
                if 'entry_point' in meta:
                    skill_info['entry_point'] = meta['entry_point']
            except:
                pass
        
        # 查找 Python 入口文件
        for py_file in skill_dir.glob('*.py'):
            if '__init__.py' not in str(py_file):
                skill_info['entry_point'] = skill_info['entry_point'] or f"{skill_dir.name}.{py_file.stem}"
                skill_info['files'][py_file.name] = py_file.stat().st_size
                break
        
        # 根据文件名推断标签
        skill_info['tags'] = list(set(skill_info['tags']))
        inferred_tags = self._infer_tags(skill_dir.name, skill_info['description'])
        skill_info['tags'].extend(inferred_tags)
        skill_info['tags'] = list(set(skill_info['tags']))
        
        # 根据文件数量和存在时间推断成熟度
        if len(skill_info['files']) > 5 and skill_info['maturity'] == 'prototype':
            skill_info['maturity'] = 'beta'
        if 'test' in skill_info['files'] or 'tests' in skill_info['files']:
            skill_info['maturity'] = 'production'
        
        return skill_info

    def _parse_skill_md(self, content: str) -> Dict:
        """解析 SKILL.md 内容"""
        result = {
            'description': '',
            'tags': [],
            'author': '',
            'version': '1.0.0',
            'inputs': {},
            'outputs': {},
            'limitations': ''
        }
        
        # 提取描述（第一段）
        result['description'] = self._extract_first_paragraph(content)
        
        # 提取标题和内容
        lines = content.split('\n')
        current_section = None
        section_content = []
        
        for line in lines:
            if line.startswith('#'):
                if current_section and section_content:
                    section_text = '\n'.join(section_content).strip()
                    self._process_section(result, current_section, section_text)
                
                current_section = line.lstrip('#').strip().lower()
                section_content = []
            else:
                section_content.append(line)
        
        # 处理最后一段
        if current_section and section_content:
            section_text = '\n'.join(section_content).strip()
            self._process_section(result, current_section, section_text)
        
        return result

    def _process_section(self, result: Dict, section_name: str, content: str):
        """处理文档章节"""
        if not content:
            return
        
        if '描述' in section_name or 'description' in section_name:
            result['description'] = content
        elif '标签' in section_name or 'tag' in section_name:
            tags = re.findall(r'[#\-]\s*(\w+)', content)
            result['tags'].extend(tags)
        elif '作者' in section_name or 'author' in section_name:
            result['author'] = content.split('\n')[0].strip()
        elif '版本' in section_name or 'version' in section_name:
            version_match = re.search(r'(\d+\.\d+\.\d+)', content)
            if version_match:
                result['version'] = version_match.group(1)
        elif '输入' in section_name or 'input' in section_name:
            result['inputs'] = {'description': content}
        elif '输出' in section_name or 'output' in section_name:
            result['outputs'] = {'description': content}
        elif '限制' in section_name or 'limit' in section_name or 'limitation' in section_name:
            result['limitations'] = content

    def _extract_first_paragraph(self, content: str) -> str:
        """提取第一段文本"""
        lines = content.split('\n')
        paragraphs = []
        current = []
        
        for line in lines:
            if line.strip() == '' and current:
                paragraphs.append('\n'.join(current).strip())
                current = []
            elif not line.startswith('#'):
                current.append(line)
        
        if current:
            paragraphs.append('\n'.join(current).strip())
        
        for p in paragraphs:
            if p.strip() and len(p.strip()) > 10:
                return p.strip()
        
        return ''

    def _infer_tags(self, name: str, description: str) -> List[str]:
        """根据名称和描述推断标签"""
        tag_keywords = {
            'database': ['数据', '库', 'database', 'db', 'sql'],
            'project': ['项目', 'project', '任务', 'task'],
            'contract': ['合同', 'contract', '条款'],
            'analysis': ['分析', 'analysis', '统计', 'report'],
            'nlp': ['文本', '自然语言', 'nlp', '分词'],
            'rag': ['rag', '向量', '检索', 'embedding'],
            'excel': ['excel', '表格', 'xlsx'],
            'word': ['word', '文档', 'docx'],
            'pdf': ['pdf', '扫描', 'ocr'],
            'test': ['测试', 'test', '单元测试'],
            'api': ['api', '接口', 'client'],
            'email': ['邮件', 'email', 'mail'],
            'llm': ['llm', '大模型', 'gpt', 'prompt'],
            'iris': ['巡检', 'monitor'],
            'orion': ['orion', '猎户'],
            'nova': ['nova', '新星'],
            'luna': ['luna', '月亮']
        }
        
        tags = []
        text = (name + ' ' + description).lower()
        
        for tag, keywords in tag_keywords.items():
            if any(kw in text for kw in keywords):
                tags.append(tag)
        
        return tags

    def import_skills(self, skill_names: List[str] = None) -> Dict:
        """
        导入技能到 KSA 系统
        
        Args:
            skill_names: 要导入的技能名称列表，None 表示导入所有
        
        Returns:
            导入结果统计
        """
        all_skills = self.scan_skills()
        stats = {
            'total': len(all_skills),
            'imported': 0,
            'skipped': 0,
            'failed': 0,
            'skills': []
        }
        
        for skill_info in all_skills:
            if skill_names and skill_info['name'] not in skill_names:
                stats['skipped'] += 1
                continue
            
            try:
                # 检查是否已存在
                existing = self.manager.skill.list()
                existing_names = [s['name'] for s in existing]
                
                if skill_info['name'] in existing_names:
                    # 更新现有技能
                    skill_id = next(s['id'] for s in existing if s['name'] == skill_info['name'])
                    self.manager.skill.update(skill_id, **skill_info)
                else:
                    # 创建新技能
                    self.manager.skill.add(
                        name=skill_info['name'],
                        version=skill_info['version'],
                        author=skill_info['author'],
                        description=skill_info['description'],
                        tags=skill_info['tags'],
                        maturity=skill_info['maturity'],
                        inputs=skill_info['inputs'],
                        outputs=skill_info['outputs'],
                        limitations=skill_info['limitations'],
                        entry_point=skill_info['entry_point'],
                        skill_path=skill_info['skill_path']
                    )
                
                stats['imported'] += 1
                stats['skills'].append(skill_info['name'])
            except Exception as e:
                stats['failed'] += 1
                print(f"导入技能 {skill_info['name']} 失败: {e}")
        
        return stats


class KnowledgeImporter:
    """从 memory 目录提取知识"""

    def __init__(self, memory_root: str = None, manager: KSAManager = None):
        if memory_root is None:
            memory_root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'memory')
        self.memory_root = memory_root
        self.manager = manager or KSAManager()

    def scan_memory_files(self) -> List[Dict]:
        """扫描 memory 目录下的所有文件"""
        knowledge_items = []
        memory_path = Path(self.memory_root)
        
        if not memory_path.exists():
            return knowledge_items
        
        for ext in ['*.md', '*.txt', '*.json']:
            for file in memory_path.rglob(ext):
                if file.is_file():
                    k_info = self._extract_knowledge_from_file(file)
                    if k_info:
                        knowledge_items.append(k_info)
        
        return knowledge_items

    def _extract_knowledge_from_file(self, file: Path) -> Optional[Dict]:
        """从文件中提取知识"""
        try:
            content = file.read_text(encoding='utf-8', errors='ignore')
            if not content.strip():
                return None
            
            # 确定知识类别
            category = 'experiential'  # 默认经验类
            if '笔记' in file.name or 'note' in file.name.lower():
                category = 'factual'
            elif '教程' in file.name or '指南' in file.name or 'guide' in file.name.lower():
                category = 'procedural'
            
            # 提取标题
            title = file.stem
            first_line = content.split('\n')[0].strip()
            if first_line.startswith('#'):
                title = first_line.lstrip('#').strip()
            
            # 提取标签
            tags = []
            tag_matches = re.findall(r'#(\w+)', content)
            tags.extend(tag_matches)
            
            # 根据目录添加标签
            relative = file.relative_to(self.memory_root)
            tags.extend([p.lower() for p in relative.parts[:-1]])
            
            return {
                'name': title,
                'content': content,
                'category': category,
                'description': self._extract_first_paragraph(content),
                'source': str(file),
                'tags': list(set(tags))
            }
        except Exception as e:
            print(f"处理文件 {file} 失败: {e}")
            return None

    def _extract_first_paragraph(self, content: str) -> str:
        """提取第一段文本"""
        lines = content.split('\n')
        paragraphs = []
        current = []
        
        for line in lines:
            if line.strip() == '' and current:
                paragraphs.append('\n'.join(current).strip())
                current = []
            elif not line.startswith('#'):
                current.append(line)
        
        if current:
            paragraphs.append('\n'.join(current).strip())
        
        for p in paragraphs:
            if p.strip() and len(p.strip()) > 10:
                return p.strip()[:500]  # 限制长度
        
        return ''

    def import_knowledge(self) -> Dict:
        """导入知识到 KSA 系统"""
        knowledge_items = self.scan_memory_files()
        stats = {
            'total': len(knowledge_items),
            'imported': 0,
            'failed': 0,
            'items': []
        }
        
        for k_info in knowledge_items:
            try:
                self.manager.knowledge.add(
                    name=k_info['name'],
                    content=k_info['content'],
                    category=k_info['category'],
                    description=k_info['description'],
                    tags=k_info['tags'],
                    source=k_info['source']
                )
                stats['imported'] += 1
                stats['items'].append(k_info['name'])
            except Exception as e:
                stats['failed'] += 1
                print(f"导入知识 {k_info['name']} 失败: {e}")
        
        return stats


def import_target_modules(module_names: List[str]) -> Dict:
    """
    导入指定模块的技能
    
    Args:
        module_names: 模块名称列表，如 ['database', 'orion', 'nova', 'luna', 'vet']
    
    Returns:
        导入结果
    """
    importer = SkillImporter()
    all_skills = importer.scan_skills()
    
    # 匹配目标模块
    target_skills = []
    for skill in all_skills:
        skill_name_lower = skill['name'].lower()
        for module in module_names:
            module_lower = module.lower()
            if module_lower in skill_name_lower:
                target_skills.append(skill['name'])
                break
    
    target_skills = list(set(target_skills))
    result = importer.import_skills(skill_names=target_skills)
    
    # 也导入知识
    knowledge_importer = KnowledgeImporter()
    knowledge_result = knowledge_importer.import_knowledge()
    
    return {
        'skills': result,
        'knowledge': knowledge_result
    }
