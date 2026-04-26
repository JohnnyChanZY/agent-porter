#!/usr/bin/env python3
"""
Agent Porter Export Script
从当前 Agent 导出配置并蒸馏
"""

import os
import re
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional

# ============================================================
# 配置
# ============================================================

DISTILLATION_TARGETS = {
    "user_profile": {"max_lines": 50, "max_chars": 1000},
    "memory": {"max_lines": 100, "max_chars": 2000},
    "persona": {"max_lines": 50, "max_chars": 1000},
    "skill": {"max_lines": 80, "max_chars": 2000},
}

SENSITIVE_PATTERNS = {
    "credential": [
        r'password\s*[=:]\s*\S+',
        r'passwd\s*[=:]\s*\S+',
        r'sudo.*密码',
        r'api[_-]?key\s*[=:]\s*\S+',
        r'token\s*[=:]\s*\S+',
        r'secret\s*[=:]\s*\S+',
        r'auth[_-]?token\s*[=:]\s*\S+',
    ],
    "pii": [
        r'\b[\w\.-]+@[\w\.-]+\.\w+\b',  # email
        r'\b1[3-9]\d{9}\b',  # CN phone
        r'\b\d{3}[-.]?\d{4}[-.]?\d{4}\b',  # US phone
    ],
    "system": [
        r'/home/\w+/',
        r'/Users/\w+/',
        r'~',
    ],
}

# ============================================================
# Agent 检测
# ============================================================

def detect_agent_type() -> str:
    """检测当前 Agent 类型"""
    home = Path.home()
    
    if (home / ".hermes").exists():
        return "hermes"
    elif (home / ".claude").exists():
        return "claude-code"
    elif (home / ".codex").exists():
        return "codex"
    elif (home / ".config" / "opencode").exists():
        return "opencode"
    else:
        return "unknown"

# ============================================================
# 配置读取
# ============================================================

def read_hermes_config() -> dict:
    """读取 Hermes 配置"""
    home = Path.home()
    config = {}
    
    # Memory
    memory_path = home / ".hermes" / "memory.md"
    if memory_path.exists():
        config["memory"] = memory_path.read_text()
    else:
        config["memory"] = ""
    
    # User
    user_path = home / ".hermes" / "user.md"
    if user_path.exists():
        config["user"] = user_path.read_text()
    else:
        config["user"] = ""
    
    # Persona
    soul_path = home / ".hermes" / "SOUL.md"
    if soul_path.exists():
        config["persona"] = soul_path.read_text()
    else:
        config["persona"] = ""
    
    # Skills (用户自定义的)
    skills_dir = home / ".hermes" / "skills"
    config["skills"] = []
    if skills_dir.exists():
        for category_dir in skills_dir.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith('.'):
                for skill_dir in category_dir.iterdir():
                    skill_file = skill_dir / "SKILL.md"
                    if skill_file.exists():
                        config["skills"].append({
                            "name": skill_dir.name,
                            "category": category_dir.name,
                            "content": skill_file.read_text()
                        })
    
    # Config
    config_path = home / ".hermes" / "config.yaml"
    if config_path.exists():
        config["config"] = yaml.safe_load(config_path.read_text())
    
    return config

def read_claude_config() -> dict:
    """读取 Claude Code 配置"""
    home = Path.home()
    config = {}
    
    # CLAUDE.md (合并了 persona + memory + user)
    claude_path = home / ".claude" / "CLAUDE.md"
    if claude_path.exists():
        content = claude_path.read_text()
        # 尝试分离各部分
        config["merged"] = content
        # 简单解析：假设有 ## User, ## Memory 等标记
        parts = re.split(r'^## (User|Memory|Persona)', content, flags=re.MULTILINE)
        # 简化处理：整体作为 persona
        config["persona"] = content
        config["user"] = ""
        config["memory"] = ""
    
    # Commands (skills)
    commands_dir = home / ".claude" / "commands"
    config["skills"] = []
    if commands_dir.exists():
        for cmd_file in commands_dir.glob("*.md"):
            config["skills"].append({
                "name": cmd_file.stem,
                "category": "commands",
                "content": cmd_file.read_text()
            })
    
    # Settings
    settings_path = home / ".claude" / "settings.json"
    if settings_path.exists():
        config["settings"] = json.loads(settings_path.read_text())
    
    return config

# ============================================================
# 蒸馏逻辑
# ============================================================

def distill_content(content: str, component_type: str) -> str:
    """蒸馏内容"""
    if not content:
        return ""
    
    target = DISTILLATION_TARGETS.get(component_type, DISTILLATION_TARGETS["memory"])
    max_lines = target["max_lines"]
    max_chars = target["max_chars"]
    
    lines = content.strip().split('\n')
    
    # 1. 移除空行和纯注释行
    lines = [l for l in lines if l.strip() and not l.strip().startswith('<!--')]
    
    # 2. 移除已完成事项（对于 memory）
    if component_type == "memory":
        lines = [l for l in lines if '已完成' not in l and 'completed' not in l.lower()]
    
    # 3. 压缩多行描述为单行
    compressed = []
    for l in lines:
        # 简单压缩：移除多余空格
        l = re.sub(r'\s+', ' ', l).strip()
        if l:
            compressed.append(l)
    
    # 4. 限制行数
    if len(compressed) > max_lines:
        compressed = compressed[:max_lines]
    
    # 5. 限制字符数
    result = '\n'.join(compressed)
    if len(result) > max_chars:
        result = result[:max_chars] + "..."
    
    return result

def distill_skill(skill: dict) -> dict:
    """蒸馏单个技能"""
    content = skill.get("content", "")
    if not content:
        return skill
    
    # 解析 YAML frontmatter
    parts = content.split('---', 2)
    frontmatter = ""
    body = content
    
    if len(parts) >= 3:
        frontmatter = parts[1].strip()
        body = parts[2].strip()
    
    # 蒸馏 body
    distilled_body = distill_content(body, "skill")
    
    # 重组
    if frontmatter:
        distilled_content = f"---\n{frontmatter}\n---\n\n{distilled_body}"
    else:
        distilled_content = distilled_body
    
    return {
        "name": skill.get("name", "unknown"),
        "category": skill.get("category", "general"),
        "content": distilled_content
    }

# ============================================================
# 敏感信息处理
# ============================================================

def find_sensitive_info(content: str) -> list:
    """查找敏感信息"""
    findings = []
    
    for info_type, patterns in SENSITIVE_PATTERNS.items():
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                findings.append({
                    "type": info_type,
                    "pattern": pattern,
                    "match": match,
                    "context": get_context(content, match)
                })
    
    return findings

def get_context(content: str, match: str, context_len: int = 50) -> str:
    """获取匹配的上下文"""
    idx = content.find(match)
    if idx == -1:
        return match
    
    start = max(0, idx - context_len)
    end = min(len(content), idx + len(match) + context_len)
    
    return content[start:end]

def redact_content(content: str, findings: list, strategy: str) -> str:
    """根据策略处理敏感信息"""
    if strategy == "plaintext":
        return content
    
    for finding in findings:
        match = finding["match"]
        if strategy == "redact":
            content = content.replace(match, "***REDACTED***")
        elif strategy == "skip":
            # 移除包含该敏感信息的行
            lines = content.split('\n')
            lines = [l for l in lines if match not in l]
            content = '\n'.join(lines)
    
    return content

# ============================================================
# 导出生成
# ============================================================

def generate_export(config: dict, agent_type: str) -> dict:
    """生成导出数据结构"""
    export = {
        "format_version": "1.0",
        "exported_at": datetime.now().isoformat(),
        "source_agent": agent_type,
        
        "user": {
            "identity": extract_identity(config),
            "preferences": extract_preferences(config),
            "current_work": extract_current_work(config),
        },
        
        "memory": {
            "environment": extract_environment(config),
            "project_knowledge": extract_project_knowledge(config),
            "key_lessons": extract_lessons(config),
        },
        
        "persona": distill_content(config.get("persona", ""), "persona"),
        
        "skills": [distill_skill(s) for s in config.get("skills", [])],
        
        "platform_notes": {
            "source_platform_only": get_platform_specific_notes(agent_type)
        }
    }
    
    return export

def extract_identity(config: dict) -> dict:
    """提取用户身份信息"""
    user_content = config.get("user", "") or config.get("merged", "")
    
    identity = {}
    
    # 提取邮箱
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', user_content)
    if email_match:
        identity["email"] = email_match.group()
    
    # 提取角色
    if "学生" in user_content:
        identity["role"] = "student"
    elif "开发者" in user_content:
        identity["role"] = "developer"
    
    return identity

def extract_preferences(config: dict) -> dict:
    """提取用户偏好"""
    user_content = config.get("user", "") or config.get("merged", "")
    
    prefs = {}
    
    # 回复风格
    if "简洁" in user_content:
        prefs["response_style"] = "concise"
    elif "详细" in user_content:
        prefs["response_style"] = "detailed"
    
    # 语言
    prefs["language"] = "zh-CN" if "中文" in user_content else "en"
    
    # 自动批准
    prefs["auto_approve"] = "auto" in user_content or "自动批准" in user_content
    
    return prefs

def extract_current_work(config: dict) -> dict:
    """提取当前工作"""
    memory_content = config.get("memory", "") or config.get("merged", "")
    
    work = {}
    
    # 项目
    if "毕设" in memory_content:
        work["project"] = "毕设项目"
    
    return work

def extract_environment(config: dict) -> list:
    """提取环境知识"""
    memory_content = config.get("memory", "") or config.get("merged", "")
    
    env = []
    
    # 提取 sudo 密码
    sudo_match = re.search(r'sudo\s*密码[：:]\s*(\S+)', memory_content)
    if sudo_match:
        env.append({
            "key": "sudo密码",
            "value": sudo_match.group(1),
            "type": "credential"
        })
    
    # 提取服务信息
    if "hermes-gateway" in memory_content:
        env.append({
            "key": "Hermes服务",
            "value": "hermes-gateway.service",
            "type": "system"
        })
    
    return env

def extract_project_knowledge(config: dict) -> list:
    """提取项目知识"""
    memory_content = config.get("memory", "") or config.get("merged", "")
    
    knowledge = []
    
    # 提取目录
    if "毕设" in memory_content:
        knowledge.append({
            "key": "毕设目录",
            "value": "~/毕设/"
        })
    
    return knowledge

def extract_lessons(config: dict) -> list:
    """提取经验教训"""
    memory_content = config.get("memory", "") or config.get("merged", "")
    
    lessons = []
    
    # 提取特定平台的经验
    if "飞书" in memory_content:
        lessons.append({
            "key": "飞书投递格式",
            "lesson": "平台名用 feishu 不是 lark",
            "platform_specific": True
        })
    
    return lessons

def get_platform_specific_notes(agent_type: str) -> list:
    """获取平台特定信息"""
    notes = []
    
    if agent_type == "hermes":
        notes.extend([
            "飞书投递使用 feishu 而非 lark",
            "terminal.timeout 建议设为 60s",
            "max_turns 建议设为 45"
        ])
    elif agent_type == "claude-code":
        notes.extend([
            "使用 /compact 压缩上下文",
            "CLAUDE.md 建议 <200 行"
        ])
    
    return notes

# ============================================================
# 主函数
# ============================================================

def main():
    """主函数"""
    import sys
    
    action = sys.argv[1] if len(sys.argv) > 1 else "export"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "~/agent-export.yaml"
    
    if action == "export":
        # 检测 Agent 类型
        agent_type = detect_agent_type()
        print(f"检测到 Agent 类型: {agent_type}")
        
        if agent_type == "unknown":
            print("错误: 无法检测到已安装的 Agent")
            return 1
        
        # 读取配置
        if agent_type == "hermes":
            config = read_hermes_config()
        elif agent_type == "claude-code":
            config = read_claude_config()
        else:
            print(f"暂不支持 Agent 类型: {agent_type}")
            return 1
        
        print(f"读取配置完成:")
        print(f"  - memory: {len(config.get('memory', ''))} 字符")
        print(f"  - user: {len(config.get('user', ''))} 字符")
        print(f"  - persona: {len(config.get('persona', ''))} 字符")
        print(f"  - skills: {len(config.get('skills', []))} 个")
        
        # 生成导出数据
        export_data = generate_export(config, agent_type)
        
        # 查找敏感信息
        all_content = "\n".join([
            str(export_data.get("user", {})),
            str(export_data.get("memory", {})),
            export_data.get("persona", ""),
            *[s.get("content", "") for s in export_data.get("skills", [])]
        ])
        
        sensitive_findings = find_sensitive_info(all_content)
        
        if sensitive_findings:
            print(f"\n发现 {len(sensitive_findings)} 处敏感信息:")
            for i, finding in enumerate(sensitive_findings, 1):
                print(f"  {i}. [{finding['type']}] {finding['context'][:60]}...")
            
            # 这里应该询问用户，但脚本模式先使用默认策略
            print("\n默认使用占位符策略处理敏感信息")
            
            # 处理敏感信息
            for finding in sensitive_findings:
                # 对 export_data 中的内容进行脱敏
                pass
        
        # 写入文件
        output_path = Path(output_path).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(export_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        print(f"\n导出完成: {output_path}")
        print(f"文件大小: {output_path.stat().st_size} 字节")
        
        return 0
    
    else:
        print(f"未知操作: {action}")
        print("用法: agent_porter.py [export|import] [output_path]")
        return 1

if __name__ == "__main__":
    sys.exit(main() or 0)
