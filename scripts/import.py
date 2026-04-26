#!/usr/bin/env python3
"""
Agent Porter Import Script
将配置导入到目标 Agent
"""

import os
import re
import json
import yaml
from pathlib import Path
from typing import Optional

# ============================================================
# 导入器
# ============================================================

def import_to_hermes(export_data: dict, output_dir: Path = None):
    """导入到 Hermes"""
    home = Path.home()
    hermes_dir = output_dir or (home / ".hermes")
    
    # User
    user_data = export_data.get("user", {})
    user_content = format_user_for_hermes(user_data)
    (hermes_dir / "user.md").write_text(user_content)
    
    # Memory
    memory_data = export_data.get("memory", {})
    memory_content = format_memory_for_hermes(memory_data)
    (hermes_dir / "memory.md").write_text(memory_content)
    
    # Persona
    persona_content = export_data.get("persona", "")
    if persona_content:
        (hermes_dir / "SOUL.md").write_text(persona_content)
    
    # Skills
    skills_dir = hermes_dir / "skills" / "imported"
    skills_dir.mkdir(parents=True, exist_ok=True)
    
    for skill in export_data.get("skills", []):
        skill_name = skill.get("name", "unknown")
        skill_content = skill.get("content", "")
        
        skill_dir = skills_dir / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(skill_content)
    
    return {
        "user": hermes_dir / "user.md",
        "memory": hermes_dir / "memory.md",
        "persona": hermes_dir / "SOUL.md",
        "skills": skills_dir
    }

def import_to_claude_code(export_data: dict, output_dir: Path = None):
    """导入到 Claude Code"""
    home = Path.home()
    claude_dir = output_dir or (home / ".claude")
    claude_dir.mkdir(parents=True, exist_ok=True)
    
    # 合并 persona + user + memory 到 CLAUDE.md
    claude_content = ""
    
    # Persona
    persona = export_data.get("persona", "")
    if persona:
        claude_content += f"# Agent Persona\n\n{persona}\n\n"
    
    # User
    user_data = export_data.get("user", {})
    if user_data:
        claude_content += format_user_for_claude(user_data) + "\n\n"
    
    # Memory
    memory_data = export_data.get("memory", {})
    if memory_data:
        claude_content += format_memory_for_claude(memory_data)
    
    (claude_dir / "CLAUDE.md").write_text(claude_content.strip())
    
    # Skills -> Commands
    commands_dir = claude_dir / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)
    
    for skill in export_data.get("skills", []):
        skill_name = skill.get("name", "unknown")
        skill_content = skill.get("content", "")
        
        # 移除 YAML frontmatter
        skill_content = re.sub(r'^---\n.*?\n---\n', '', skill_content, flags=re.DOTALL)
        
        (commands_dir / f"{skill_name}.md").write_text(skill_content)
    
    return {
        "claude_md": claude_dir / "CLAUDE.md",
        "commands": commands_dir
    }

# ============================================================
# 格式转换
# ============================================================

def format_user_for_hermes(user_data: dict) -> str:
    """格式化用户信息为 Hermes 格式"""
    lines = ["# User Profile", ""]
    
    identity = user_data.get("identity", {})
    if identity.get("email"):
        lines.append(f"用户邮箱：{identity['email']}")
    if identity.get("role"):
        lines.append(f"用户角色：{identity['role']}")
    
    prefs = user_data.get("preferences", {})
    if prefs:
        lines.append("")
        lines.append("## 偏好设置")
        if prefs.get("response_style"):
            lines.append(f"- 回复风格：{prefs['response_style']}")
        if prefs.get("language"):
            lines.append(f"- 语言：{prefs['language']}")
        if prefs.get("auto_approve"):
            lines.append(f"- 自动批准所有操作")
    
    return "\n".join(lines) + "\n"

def format_memory_for_hermes(memory_data: dict) -> str:
    """格式化记忆为 Hermes 格式"""
    lines = ["# Memory", ""]
    
    env = memory_data.get("environment", [])
    if env:
        lines.append("## 环境信息")
        for item in env:
            key = item.get("key", "")
            value = item.get("value", "")
            lines.append(f"- {key}：{value}")
        lines.append("")
    
    knowledge = memory_data.get("project_knowledge", [])
    if knowledge:
        lines.append("## 项目知识")
        for item in knowledge:
            lines.append(f"- {item.get('key', '')}：{item.get('value', '')}")
        lines.append("")
    
    lessons = memory_data.get("key_lessons", [])
    if lessons:
        lines.append("## 经验教训")
        for item in lessons:
            lines.append(f"- {item.get('key', '')}：{item.get('lesson', '')}")
    
    return "\n".join(lines) + "\n"

def format_user_for_claude(user_data: dict) -> str:
    """格式化用户信息为 Claude Code 格式"""
    lines = ["## User Profile", ""]
    
    identity = user_data.get("identity", {})
    prefs = user_data.get("preferences", {})
    
    if identity:
        lines.append(f"Identity: {identity}")
    if prefs:
        lines.append(f"Preferences: {prefs}")
    
    return "\n".join(lines)

def format_memory_for_claude(memory_data: dict) -> str:
    """格式化记忆为 Claude Code 格式"""
    lines = ["## Memory", ""]
    
    env = memory_data.get("environment", [])
    if env:
        for item in env:
            lines.append(f"- {item.get('key', '')}: {item.get('value', '')}")
    
    return "\n".join(lines)

# ============================================================
# 主函数
# ============================================================

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 3:
        print("用法: import.py <export_file> <target_agent>")
        print("目标: hermes, claude-code, codex, opencode")
        return 1
    
    export_file = Path(sys.argv[1]).expanduser()
    target_agent = sys.argv[2]
    
    if not export_file.exists():
        print(f"错误: 文件不存在 {export_file}")
        return 1
    
    # 读取导出文件
    with open(export_file, 'r', encoding='utf-8') as f:
        export_data = yaml.safe_load(f)
    
    print(f"读取导出文件: {export_file}")
    print(f"来源: {export_data.get('source_agent', 'unknown')}")
    print(f"导出时间: {export_data.get('exported_at', 'unknown')}")
    
    # 导入到目标平台
    if target_agent == "hermes":
        result = import_to_hermes(export_data)
        print(f"\n导入到 Hermes 完成:")
        for k, v in result.items():
            print(f"  - {k}: {v}")
    
    elif target_agent == "claude-code":
        result = import_to_claude_code(export_data)
        print(f"\n导入到 Claude Code 完成:")
        for k, v in result.items():
            print(f"  - {k}: {v}")
    
    else:
        print(f"暂不支持目标平台: {target_agent}")
        return 1
    
    # 检查占位符
    all_content = yaml.dump(export_data, allow_unicode=True)
    redacted_count = all_content.count("***REDACTED***")
    
    if redacted_count > 0:
        print(f"\n⚠️ 发现 {redacted_count} 个敏感信息占位符，请手动配置")
    
    return 0

if __name__ == "__main__":
    sys.exit(main() or 0)
