# ========================================
# KSA 命令行接口
# python -m skills.ksa [knowledge|skill|ability] [add|list|search|update]
# ========================================

import argparse
import json
import sys
from typing import Optional

from .manager import KSAManager
from .importer import SkillImporter, KnowledgeImporter, import_target_modules
from .storage import init_database


def _print_json(data):
    """格式化打印 JSON"""
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_init(args):
    """初始化数据库"""
    init_database()
    print("KSA 数据库初始化完成")


def cmd_knowledge_add(args):
    """添加知识"""
    manager = KSAManager()
    
    # 如果 --from 参数指定了文件
    if args.from_file:
        with open(args.from_file, 'r', encoding='utf-8') as f:
            content = f.read()
        name = args.name or args.from_file
    else:
        content = sys.stdin.read() if not args.content else args.content
        name = args.name or '未命名知识'
    
    result = manager.knowledge.add(
        name=name,
        content=content,
        category=args.category,
        description=args.description or '',
        tags=args.tags.split(',') if args.tags else [],
        source=args.source or '',
        confidence=args.confidence
    )
    _print_json(result)


def cmd_knowledge_list(args):
    """列出知识"""
    manager = KSAManager()
    result = manager.knowledge.list(
        category=args.category,
        tag=args.tag,
        limit=args.limit,
        offset=args.offset
    )
    _print_json(result)


def cmd_knowledge_search(args):
    """搜索知识"""
    manager = KSAManager()
    result = manager.knowledge.search(args.query, limit=args.limit)
    _print_json(result)


def cmd_knowledge_update(args):
    """更新知识"""
    manager = KSAManager()
    kwargs = {}
    if args.name:
        kwargs['name'] = args.name
    if args.description:
        kwargs['description'] = args.description
    if args.category:
        kwargs['category'] = args.category
    if args.tags:
        kwargs['tags'] = args.tags.split(',')
    if args.content:
        kwargs['content'] = args.content
    if args.confidence is not None:
        kwargs['confidence'] = args.confidence
    
    result = manager.knowledge.update(args.id, **kwargs)
    if result:
        _print_json(result)
    else:
        print(f"知识 ID={args.id} 不存在")
        sys.exit(1)


def cmd_skill_add(args):
    """添加技能"""
    manager = KSAManager()
    
    # 如果 --from 参数指定了技能目录
    if args.from_dir:
        importer = SkillImporter()
        result = importer.import_skills(skill_names=[args.from_dir])
        _print_json(result)
        return
    
    result = manager.skill.add(
        name=args.name,
        version=args.version,
        author=args.author,
        description=args.description or '',
        tags=args.tags.split(',') if args.tags else [],
        maturity=args.maturity,
        entry_point=args.entry_point or '',
        skill_path=args.skill_path or ''
    )
    _print_json(result)


def cmd_skill_list(args):
    """列出技能"""
    manager = KSAManager()
    result = manager.skill.list(
        maturity=args.maturity,
        tag=args.tag,
        limit=args.limit,
        offset=args.offset
    )
    _print_json(result)


def cmd_skill_search(args):
    """搜索/匹配技能"""
    manager = KSAManager()
    result = manager.skill.match_skills(args.query, limit=args.limit)
    _print_json(result)


def cmd_skill_update(args):
    """更新技能"""
    manager = KSAManager()
    kwargs = {}
    if args.name:
        kwargs['name'] = args.name
    if args.version:
        kwargs['version'] = args.version
    if args.description:
        kwargs['description'] = args.description
    if args.maturity:
        kwargs['maturity'] = args.maturity
    if args.tags:
        kwargs['tags'] = args.tags.split(',')
    
    result = manager.skill.update(args.id, **kwargs)
    if result:
        _print_json(result)
    else:
        print(f"技能 ID={args.id} 不存在")
        sys.exit(1)


def cmd_skill_record(args):
    """记录技能执行结果"""
    manager = KSAManager()
    success = args.success.lower() == 'true'
    result = manager.skill.record_execution(args.id, success, args.time)
    if result:
        print(f"技能执行记录已更新")
    else:
        print(f"技能 ID={args.id} 不存在")
        sys.exit(1)


def cmd_ability_add(args):
    """添加能力"""
    manager = KSAManager()
    result = manager.ability.add(
        name=args.name,
        owner=args.owner,
        description=args.description or '',
        tags=args.tags.split(',') if args.tags else [],
        max_concurrent=args.max_concurrent
    )
    _print_json(result)


def cmd_ability_list(args):
    """列出能力"""
    manager = KSAManager()
    result = manager.ability.list(
        owner=args.owner,
        tag=args.tag,
        limit=args.limit,
        offset=args.offset
    )
    _print_json(result)


def cmd_ability_search(args):
    """搜索能力"""
    manager = KSAManager()
    result = manager.ability.search(args.query, limit=args.limit)
    _print_json(result)


def cmd_ability_update(args):
    """更新能力"""
    manager = KSAManager()
    kwargs = {}
    if args.name:
        kwargs['name'] = args.name
    if args.owner:
        kwargs['owner'] = args.owner
    if args.description:
        kwargs['description'] = args.description
    if args.tags:
        kwargs['tags'] = args.tags.split(',')
    if args.max_concurrent:
        kwargs['max_concurrent'] = args.max_concurrent
    
    result = manager.ability.update(args.id, **kwargs)
    if result:
        _print_json(result)
    else:
        print(f"能力 ID={args.id} 不存在")
        sys.exit(1)


def cmd_ability_evaluate(args):
    """评估能力任务结果"""
    manager = KSAManager()
    success = args.success.lower() == 'true'
    metrics = json.loads(args.metrics) if args.metrics else None
    result = manager.ability.evaluate_task_result(args.id, success, metrics)
    if result:
        print(f"能力评估已更新")
    else:
        print(f"能力 ID={args.id} 不存在")
        sys.exit(1)


def cmd_import_skills(args):
    """导入所有技能"""
    importer = SkillImporter()
    result = importer.import_skills()
    _print_json(result)


def cmd_import_modules(args):
    """导入指定模块的技能"""
    modules = args.modules.split(',')
    result = import_target_modules(modules)
    _print_json(result)


def cmd_import_knowledge(args):
    """从 memory 目录导入知识"""
    importer = KnowledgeImporter()
    result = importer.import_knowledge()
    _print_json(result)


def cmd_stats(args):
    """显示统计信息"""
    manager = KSAManager()
    stats = manager.get_stats()
    _print_json(stats)


# ========================================
# Ontology 子命令
# ========================================

def cmd_ontology_add_entity(args):
    """添加本体实体"""
    manager = KSAManager()
    result = manager.ontology.add_entity(
        entity_type=args.entity_type,
        entity_id=args.entity_id,
        name=args.name,
        description=args.description or '',
        tags=args.tags.split(',') if args.tags else []
    )
    _print_json(result)


def cmd_ontology_add_relation(args):
    """添加实体关系"""
    manager = KSAManager()
    result = manager.ontology.add_relation(
        source_id=args.source_id,
        target_id=args.target_id,
        relation_type=args.relation_type,
        weight=args.weight
    )
    _print_json(result)


def cmd_ontology_list_entities(args):
    """列出实体"""
    manager = KSAManager()
    result = manager.ontology.list_entities(
        entity_type=args.entity_type,
        limit=args.limit
    )
    _print_json(result)


def cmd_ontology_list_relations(args):
    """列出关系"""
    manager = KSAManager()
    result = manager.ontology.list_relations(
        relation_type=args.relation_type,
        limit=args.limit
    )
    _print_json(result)


def cmd_ontology_infer(args):
    """执行推理"""
    manager = KSAManager()
    trigger = None
    if args.skill_id:
        trigger = {'type': 'skill_success_rate_changed', 'skill_id': args.skill_id}
    result = manager.ontology.infer(trigger_event=trigger)
    _print_json(result)


def cmd_ontology_recommend(args):
    """智能推荐技能"""
    manager = KSAManager()
    result = manager.ontology.recommend_skills(args.query, limit=args.limit)
    _print_json(result)


# ========================================
# Reflection 子命令
# ========================================

def cmd_reflect_analyze(args):
    """分析任务结果"""
    manager = KSAManager()
    success = args.success.lower() == 'true'
    result = manager.reflection.analyze_task_result(
        task_id=args.task_id,
        task_name=args.name or args.task_id,
        success=success,
        execution_time=args.time,
        error_message=args.error,
        skill_id=args.skill_id,
        ability_id=args.ability_id
    )
    _print_json(result)


def cmd_reflect_list(args):
    """列出复盘记录"""
    manager = KSAManager()
    result = manager.reflection.list_retrospectives(limit=args.limit)
    _print_json(result)


def cmd_reflect_stats(args):
    """反思引擎统计"""
    manager = KSAManager()
    stats = manager.reflection.get_stats()
    _print_json(stats)


def main():
    parser = argparse.ArgumentParser(
        prog='python -m skills.ksa',
        description='KSA v1.1 (Knowledge/Skill/Ability + Ontology + Reflection) 管理框架 CLI'
    )
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # init 命令
    init_parser = subparsers.add_parser('init', help='初始化数据库')
    init_parser.set_defaults(func=cmd_init)

    # stats 命令
    stats_parser = subparsers.add_parser('stats', help='显示统计信息')
    stats_parser.set_defaults(func=cmd_stats)

    # ========================================
    # Knowledge 子命令
    # ========================================
    knowledge_parser = subparsers.add_parser('knowledge', help='知识管理')
    knowledge_subparsers = knowledge_parser.add_subparsers(dest='subcommand', help='知识子命令')

    # knowledge add
    k_add_parser = knowledge_subparsers.add_parser('add', help='添加知识')
    k_add_parser.add_argument('--name', help='知识名称')
    k_add_parser.add_argument('--content', help='知识内容')
    k_add_parser.add_argument('--from', dest='from_file', help='从文件读取内容')
    k_add_parser.add_argument('--category', default='factual', help='知识分类 (factual/procedural/experiential)')
    k_add_parser.add_argument('--description', help='知识描述')
    k_add_parser.add_argument('--tags', help='标签，逗号分隔')
    k_add_parser.add_argument('--source', help='知识来源')
    k_add_parser.add_argument('--confidence', type=float, default=1.0, help='置信度')
    k_add_parser.set_defaults(func=cmd_knowledge_add)

    # knowledge list
    k_list_parser = knowledge_subparsers.add_parser('list', help='列出知识')
    k_list_parser.add_argument('--category', help='按分类过滤')
    k_list_parser.add_argument('--tag', help='按标签过滤')
    k_list_parser.add_argument('--limit', type=int, default=100, help='返回数量限制')
    k_list_parser.add_argument('--offset', type=int, default=0, help='偏移量')
    k_list_parser.set_defaults(func=cmd_knowledge_list)

    # knowledge search
    k_search_parser = knowledge_subparsers.add_parser('search', help='搜索知识')
    k_search_parser.add_argument('query', help='搜索关键词')
    k_search_parser.add_argument('--limit', type=int, default=10, help='返回数量限制')
    k_search_parser.set_defaults(func=cmd_knowledge_search)

    # knowledge update
    k_update_parser = knowledge_subparsers.add_parser('update', help='更新知识')
    k_update_parser.add_argument('--id', type=int, required=True, help='知识 ID')
    k_update_parser.add_argument('--name', help='知识名称')
    k_update_parser.add_argument('--description', help='知识描述')
    k_update_parser.add_argument('--category', help='知识分类')
    k_update_parser.add_argument('--tags', help='标签，逗号分隔')
    k_update_parser.add_argument('--content', help='知识内容')
    k_update_parser.add_argument('--confidence', type=float, help='置信度')
    k_update_parser.set_defaults(func=cmd_knowledge_update)

    # ========================================
    # Skill 子命令
    # ========================================
    skill_parser = subparsers.add_parser('skill', help='技能管理')
    skill_subparsers = skill_parser.add_subparsers(dest='subcommand', help='技能子命令')

    # skill add
    s_add_parser = skill_subparsers.add_parser('add', help='添加技能')
    s_add_parser.add_argument('--name', required=True, help='技能名称')
    s_add_parser.add_argument('--from', dest='from_dir', help='从现有技能目录导入')
    s_add_parser.add_argument('--version', default='1.0.0', help='版本号')
    s_add_parser.add_argument('--author', help='作者')
    s_add_parser.add_argument('--description', help='技能描述')
    s_add_parser.add_argument('--tags', help='标签，逗号分隔')
    s_add_parser.add_argument('--maturity', default='prototype', help='成熟度 (prototype/beta/production/deprecated)')
    s_add_parser.add_argument('--entry-point', help='入口点')
    s_add_parser.add_argument('--skill-path', help='技能路径')
    s_add_parser.set_defaults(func=cmd_skill_add)

    # skill list
    s_list_parser = skill_subparsers.add_parser('list', help='列出技能')
    s_list_parser.add_argument('--maturity', help='按成熟度过滤')
    s_list_parser.add_argument('--tag', help='按标签过滤')
    s_list_parser.add_argument('--limit', type=int, default=100, help='返回数量限制')
    s_list_parser.add_argument('--offset', type=int, default=0, help='偏移量')
    s_list_parser.set_defaults(func=cmd_skill_list)

    # skill search/match
    s_search_parser = skill_subparsers.add_parser('search', help='根据任务描述匹配技能')
    s_search_parser.add_argument('query', help='任务描述')
    s_search_parser.add_argument('--limit', type=int, default=5, help='返回数量限制')
    s_search_parser.set_defaults(func=cmd_skill_search)

    # skill update
    s_update_parser = skill_subparsers.add_parser('update', help='更新技能')
    s_update_parser.add_argument('--id', type=int, required=True, help='技能 ID')
    s_update_parser.add_argument('--name', help='技能名称')
    s_update_parser.add_argument('--version', help='版本号')
    s_update_parser.add_argument('--description', help='技能描述')
    s_update_parser.add_argument('--maturity', help='成熟度')
    s_update_parser.add_argument('--tags', help='标签，逗号分隔')
    s_update_parser.set_defaults(func=cmd_skill_update)

    # skill record
    s_record_parser = skill_subparsers.add_parser('record', help='记录技能执行结果')
    s_record_parser.add_argument('--id', type=int, required=True, help='技能 ID')
    s_record_parser.add_argument('--success', required=True, help='是否成功 (true/false)')
    s_record_parser.add_argument('--time', type=float, required=True, help='执行时间（秒）')
    s_record_parser.set_defaults(func=cmd_skill_record)

    # ========================================
    # Ability 子命令
    # ========================================
    ability_parser = subparsers.add_parser('ability', help='能力管理')
    ability_subparsers = ability_parser.add_subparsers(dest='subcommand', help='能力子命令')

    # ability add
    a_add_parser = ability_subparsers.add_parser('add', help='添加能力')
    a_add_parser.add_argument('--name', required=True, help='能力名称')
    a_add_parser.add_argument('--owner', help='能力所有者')
    a_add_parser.add_argument('--description', help='能力描述')
    a_add_parser.add_argument('--tags', help='标签，逗号分隔')
    a_add_parser.add_argument('--max-concurrent', type=int, default=1, help='最大并发数')
    a_add_parser.set_defaults(func=cmd_ability_add)

    # ability list
    a_list_parser = ability_subparsers.add_parser('list', help='列出能力')
    a_list_parser.add_argument('--owner', help='按所有者过滤')
    a_list_parser.add_argument('--tag', help='按标签过滤')
    a_list_parser.add_argument('--limit', type=int, default=100, help='返回数量限制')
    a_list_parser.add_argument('--offset', type=int, default=0, help='偏移量')
    a_list_parser.set_defaults(func=cmd_ability_list)

    # ability search
    a_search_parser = ability_subparsers.add_parser('search', help='搜索能力')
    a_search_parser.add_argument('query', help='搜索关键词')
    a_search_parser.add_argument('--limit', type=int, default=5, help='返回数量限制')
    a_search_parser.set_defaults(func=cmd_ability_search)

    # ability update
    a_update_parser = ability_subparsers.add_parser('update', help='更新能力')
    a_update_parser.add_argument('--id', type=int, required=True, help='能力 ID')
    a_update_parser.add_argument('--name', help='能力名称')
    a_update_parser.add_argument('--owner', help='能力所有者')
    a_update_parser.add_argument('--description', help='能力描述')
    a_update_parser.add_argument('--tags', help='标签，逗号分隔')
    a_update_parser.add_argument('--max-concurrent', type=int, help='最大并发数')
    a_update_parser.set_defaults(func=cmd_ability_update)

    # ability evaluate
    a_eval_parser = ability_subparsers.add_parser('evaluate', help='评估能力任务结果')
    a_eval_parser.add_argument('--id', type=int, required=True, help='能力 ID')
    a_eval_parser.add_argument('--success', required=True, help='是否成功 (true/false)')
    a_eval_parser.add_argument('--metrics', help='指标 JSON')
    a_eval_parser.set_defaults(func=cmd_ability_evaluate)

    # ========================================
    # Import 子命令
    # ========================================
    import_parser = subparsers.add_parser('import', help='批量导入')
    import_subparsers = import_parser.add_subparsers(dest='import_cmd', help='导入子命令')

    import_skills = import_subparsers.add_parser('skills', help='导入所有技能')
    import_skills.set_defaults(func=cmd_import_skills)

    import_modules = import_subparsers.add_parser('modules', help='导入指定模块')
    import_modules.add_argument('modules', help='模块名，逗号分隔')
    import_modules.set_defaults(func=cmd_import_modules)

    import_knowledge = import_subparsers.add_parser('knowledge', help='从 memory 目录导入知识')
    import_knowledge.set_defaults(func=cmd_import_knowledge)

    # ========================================
    # Ontology 子命令
    # ========================================
    ontology_parser = subparsers.add_parser('ontology', help='本体知识图谱 (v1.1)')
    ontology_subparsers = ontology_parser.add_subparsers(dest='subcommand', help='Ontology 子命令')

    # ontology add-entity
    o_add_entity = ontology_subparsers.add_parser('add-entity', help='添加实体')
    o_add_entity.add_argument('--entity-type', required=True, help='实体类型 (agent/skill/knowledge/ability/task/domain)')
    o_add_entity.add_argument('--entity-id', required=True, help='外部实体 ID')
    o_add_entity.add_argument('--name', required=True, help='实体名称')
    o_add_entity.add_argument('--description', help='实体描述')
    o_add_entity.add_argument('--tags', help='标签，逗号分隔')
    o_add_entity.set_defaults(func=cmd_ontology_add_entity)

    # ontology add-relation
    o_add_relation = ontology_subparsers.add_parser('add-relation', help='添加关系')
    o_add_relation.add_argument('--source-id', type=int, required=True, help='源实体 ID')
    o_add_relation.add_argument('--target-id', type=int, required=True, help='目标实体 ID')
    o_add_relation.add_argument('--relation-type', required=True, help='关系类型')
    o_add_relation.add_argument('--weight', type=float, default=1.0, help='关系权重')
    o_add_relation.set_defaults(func=cmd_ontology_add_relation)

    # ontology list-entities
    o_list_entities = ontology_subparsers.add_parser('list-entities', help='列出实体')
    o_list_entities.add_argument('--entity-type', help='按实体类型过滤')
    o_list_entities.add_argument('--limit', type=int, default=100, help='返回数量限制')
    o_list_entities.set_defaults(func=cmd_ontology_list_entities)

    # ontology list-relations
    o_list_relations = ontology_subparsers.add_parser('list-relations', help='列出关系')
    o_list_relations.add_argument('--relation-type', help='按关系类型过滤')
    o_list_relations.add_argument('--limit', type=int, default=100, help='返回数量限制')
    o_list_relations.set_defaults(func=cmd_ontology_list_relations)

    # ontology infer
    o_infer = ontology_subparsers.add_parser('infer', help='执行推理')
    o_infer.add_argument('--skill-id', type=int, help='触发推理的技能 ID')
    o_infer.set_defaults(func=cmd_ontology_infer)

    # ontology recommend
    o_recommend = ontology_subparsers.add_parser('recommend', help='智能推荐技能')
    o_recommend.add_argument('query', help='任务描述')
    o_recommend.add_argument('--limit', type=int, default=5, help='返回数量限制')
    o_recommend.set_defaults(func=cmd_ontology_recommend)

    # ========================================
    # Reflection 子命令
    # ========================================
    reflect_parser = subparsers.add_parser('reflect', help='反思成长引擎 (v1.1)')
    reflect_subparsers = reflect_parser.add_subparsers(dest='subcommand', help='Reflection 子命令')

    # reflect analyze
    r_analyze = reflect_subparsers.add_parser('analyze', help='分析任务结果')
    r_analyze.add_argument('--task-id', required=True, help='任务 ID')
    r_analyze.add_argument('--name', help='任务名称')
    r_analyze.add_argument('--success', required=True, help='是否成功 (true/false)')
    r_analyze.add_argument('--time', type=float, help='执行时间（秒）')
    r_analyze.add_argument('--error', help='错误信息')
    r_analyze.add_argument('--skill-id', type=int, help='关联技能 ID')
    r_analyze.add_argument('--ability-id', type=int, help='关联能力 ID')
    r_analyze.set_defaults(func=cmd_reflect_analyze)

    # reflect list
    r_list = reflect_subparsers.add_parser('list', help='列出复盘记录')
    r_list.add_argument('--limit', type=int, default=100, help='返回数量限制')
    r_list.set_defaults(func=cmd_reflect_list)

    # reflect stats
    r_stats = reflect_subparsers.add_parser('stats', help='反思引擎统计')
    r_stats.set_defaults(func=cmd_reflect_stats)

    # 解析参数
    args = parser.parse_args()

    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == '__main__':
    main()
