"""
技能版本管理框架
- 版本号管理（语义化版本）
- 变更日志自动生成
- 版本回滚机制
- 技能元数据管理
"""

import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class VersionManager:
    def __init__(self, path: str):
        self.path = Path(path)
        self.meta_file = self.path / ".skill_meta.json"
        self.changelog_file = self.path / "CHANGELOG.md"
        self.meta = self._load_meta()

    def _load_meta(self) -> Dict:
        """加载元数据"""
        if self.meta_file.exists():
            with open(self.meta_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 初始化默认元数据
        return {
            "name": self.path.name,
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "versions": [],
            "checkpoints": [],
            "scores": {}
        }

    def _save_meta(self):
        """保存元数据"""
        self.meta["updated_at"] = datetime.now().isoformat()
        with open(self.meta_file, 'w', encoding='utf-8') as f:
            json.dump(self.meta, f, indent=2, ensure_ascii=False)

    def bump_version(self, part: str = "patch") -> str:
        """
        升级版本号
        part: major, minor, patch
        """
        current = self.meta["version"]
        major, minor, patch = map(int, current.split('.'))
        
        if part == "major":
            major += 1
            minor = 0
            patch = 0
        elif part == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1
        
        new_version = f"{major}.{minor}.{patch}"
        self.meta["versions"].append({
            "version": new_version,
            "timestamp": datetime.now().isoformat(),
            "previous": current
        })
        self.meta["version"] = new_version
        self._save_meta()
        
        return new_version

    def create_checkpoint(self, message: str = "") -> Dict:
        """创建版本检查点（用于回滚）"""
        checkpoint_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        version = self.meta["version"]
        
        # 创建备份目录
        backup_dir = self.path / ".checkpoints" / checkpoint_id
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 备份文件
        for file in self.path.rglob("*"):
            if file.is_file() and '.checkpoints' not in str(file):
                rel_path = file.relative_to(self.path)
                dest = backup_dir / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file, dest)
        
        checkpoint = {
            "id": checkpoint_id,
            "version": version,
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "path": str(backup_dir)
        }
        
        self.meta["checkpoints"].append(checkpoint)
        self._save_meta()
        
        return checkpoint

    def rollback(self, checkpoint_id: Optional[str] = None) -> bool:
        """回滚到指定检查点"""
        if not self.meta["checkpoints"]:
            return False
        
        if checkpoint_id:
            checkpoint = next(
                (c for c in self.meta["checkpoints"] if c["id"] == checkpoint_id),
                None
            )
        else:
            # 回滚到最近的检查点
            checkpoint = self.meta["checkpoints"][-1]
        
        if not checkpoint:
            return False
        
        backup_dir = Path(checkpoint["path"])
        
        # 恢复文件
        for file in backup_dir.rglob("*"):
            if file.is_file():
                rel_path = file.relative_to(backup_dir)
                dest = self.path / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file, dest)
        
        # 更新版本信息
        self.meta["version"] = checkpoint["version"]
        self._save_meta()
        
        return True

    def generate_changelog(self, changes: List[Dict]) -> str:
        """生成变更日志"""
        version = self.meta["version"]
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        changelog_entry = f"\n## [{version}] - {timestamp}\n\n"
        
        change_types = {
            "added": "新增",
            "changed": "变更",
            "fixed": "修复",
            "removed": "移除",
            "improved": "改进"
        }
        
        for ctype, cname in change_types.items():
            items = [c for c in changes if c.get("type") == ctype]
            if items:
                changelog_entry += f"### {cname}\n\n"
                for item in items:
                    changelog_entry += f"- {item['message']}\n"
                changelog_entry += "\n"
        
        # 写入或追加到 CHANGELOG.md
        if self.changelog_file.exists():
            with open(self.changelog_file, 'r', encoding='utf-8') as f:
                existing = f.read()
            content = changelog_entry + existing
        else:
            content = f"# CHANGELOG\n\n" + changelog_entry
        
        with open(self.changelog_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(self.changelog_file)

    def record_score(self, score_type: str, score: int, details: Dict = None):
        """记录检查评分"""
        self.meta["scores"][score_type] = {
            "score": score,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self._save_meta()

    def get_meta(self) -> Dict:
        """获取完整元数据"""
        return self.meta

    def list_checkpoints(self) -> List[Dict]:
        """列出所有检查点"""
        return self.meta.get("checkpoints", [])

    def list_versions(self) -> List[Dict]:
        """列出所有版本"""
        return self.meta.get("versions", [])

    def auto_based_on_git(self) -> List[Dict]:
        """基于 git 自动生成变更记录"""
        # 简单的 git log 分析
        changes = []
        
        # 检查是否有 git 仓库
        git_dir = self.path / ".git"
        if not git_dir.exists():
            return changes
        
        # 尝试读取 git log
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'log', '--oneline', '-n', '20'],
                cwd=self.path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        changes.append({
                            "type": "changed",
                            "message": line
                        })
        except Exception:
            pass
        
        return changes
