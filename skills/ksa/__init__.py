# ========================================
# KSA (Knowledge/Skill/Ability) 管理框架
# 作为整个交付系统的核心基础设施
# ========================================

from .models import Knowledge, Skill, Ability, KnowledgeCategory, SkillMaturity
from .storage import KSAStorage, get_default_storage, init_database
from .manager import KSAManager, KSAKnowledgeManager, KSASkillManager, KSAAbilityManager
from .importer import SkillImporter, KnowledgeImporter, import_target_modules

__version__ = '1.0.0'
__all__ = [
    'Knowledge', 'Skill', 'Ability',
    'KnowledgeCategory', 'SkillMaturity',
    'KSAStorage', 'get_default_storage', 'init_database',
    'KSAManager', 'KSAKnowledgeManager', 'KSASkillManager', 'KSAAbilityManager',
    'SkillImporter', 'KnowledgeImporter', 'import_target_modules',
]
