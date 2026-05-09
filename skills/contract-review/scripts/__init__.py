# 合同审核业务技能 - 脚本包
# 合同审核业务技能 __init__.py

from pathlib import Path

# 技能根目录
SKILL_ROOT = Path(__file__).parent.parent

# 配置文件路径
CONFIG_PATH = SKILL_ROOT / 'config' / 'config.yaml'

# 模板目录
TEMPLATES_DIR = SKILL_ROOT / 'templates'

# 测试数据目录
TEST_DATA_DIR = SKILL_ROOT / 'test_data'

__version__ = '1.0.0'
__author__ = 'Ella 🦊'
