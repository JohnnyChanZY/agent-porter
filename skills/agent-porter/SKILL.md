---
name: agent-porter
description: AI Agent configuration migration tool - Export, distill, and import agent configs across platforms (Hermes, Claude Code, Codex, OpenCode, etc.)
---

# Agent Porter 🧳

AI Agent 配置迁移工具 - 将一个 AI Agent 的配置蒸馏后迁移到另一个 Agent。

## When to Use This Skill

Use this skill when the user:

- Wants to migrate from one AI agent to another (e.g., Hermes → Claude Code)
- Needs to backup their agent configuration
- Wants to export their agent's memory, persona, and skills
- Is setting up a new agent and wants to transfer existing knowledge
- Asks about "agent portability" or "config migration"

## Quick Start

### Export Configuration

```bash
# Export from current agent
npx skills add JohnnyChanZY/agent-porter
python scripts/export.py export ~/agent-export.yaml
```

### Import Configuration

```bash
# Import to target agent
python scripts/import.py ~/agent-export.yaml claude-code
```

## Supported Platforms

| Platform | Export | Import | Config Directory |
|----------|--------|--------|------------------|
| Hermes | ✅ | ✅ | ~/.hermes/ |
| Claude Code | ✅ | ✅ | ~/.claude/ |
| Codex | ✅ | ✅ | ~/.codex/ |
| OpenCode | ✅ | ✅ | ~/.config/opencode/ |

## What Gets Exported

The skill exports and distills these components:

1. **User Profile** (~50 lines) - Identity, preferences, current work focus
2. **Memory** (~100 lines) - Environment knowledge, project conventions, key lessons
3. **Persona** (~50 lines) - Agent personality and behavior settings
4. **Skills** (~80 lines each) - Selected high-value skills

## Distillation

The skill automatically distills configuration to keep it concise:

- Based on Claude Code's recommendation (<200 lines per file)
- Removes redundant and outdated information
- Compresses verbose descriptions
- Filters high-value skills only

## Sensitive Information Handling

The skill identifies and handles sensitive data:

| Type | Examples | Handling Options |
|------|----------|------------------|
| Credential | passwords, API keys, tokens | Redact / Skip / Keep |
| PII | email, phone numbers | Redact / Skip / Keep |
| System | file paths, usernames | Keep / Modify |

First encounter prompts user for choice, subsequent same-type info uses same strategy.

## Export File Format

```yaml
# agent-export.yaml

format_version: "1.0"
source_agent: "hermes"

user:
  identity: { name, email, role }
  preferences: { style, language, auto_approve }
  current_work: { project, focus }

memory:
  environment: [ { key, value, type } ]
  project_knowledge: [ { key, value } ]
  key_lessons: [ { key, lesson } ]

persona:
  content: "..."

skills:
  - name: "..."
    core_logic: "..."

platform_notes:
  source_platform_only: [ "..." ]
```

## Import Process

1. Parse `agent-export.yaml`
2. Convert format for target platform
3. Write to target locations
4. Prompt for sensitive info configuration

### Platform-Specific Conversion

**Hermes → Claude Code**:
- SOUL.md + user.md + memory.md → CLAUDE.md (merged)
- skills/*/SKILL.md → commands/*.md (remove frontmatter)

**Claude Code → Hermes**:
- CLAUDE.md → SOUL.md + user.md + memory.md (split)
- commands/*.md → skills/*/SKILL.md (add frontmatter)

## Installation

### As a standalone tool

```bash
git clone https://github.com/JohnnyChanZY/agent-porter.git
cd agent-porter
pip install pyyaml
```

### Via skills.sh

```bash
npx skills add JohnnyChanZY/agent-porter
```

## Examples

### Export with sensitive info handling

```
User: Export my Hermes config

Agent: 
Reading configuration...
  - memory: 1857 chars
  - user: 553 chars  
  - persona: 537 chars
  - skills: 3 custom skills

Distilling...
  - Removed completed items
  - Merged duplicate preferences
  - Compressed verbose skill docs

⚠️ Found sensitive info:
  1. [credential] sudo password: "password"
  
Choose handling:
  [A] Keep plaintext
  [B] Use placeholder (***REDACTED***)
  [C] Skip this item
  [D] Skip all credentials

User: B

Agent:
Selected "placeholder". All credentials will use this strategy.

Export complete: ~/agent-export.yaml
Size: 8.5KB (~450 lines)
```

### Import to Claude Code

```
User: Import to Claude Code

Agent:
Parsing export file...
  - Source: Hermes
  - Version: 1.0

Converting format...
  - Merging persona + user + memory → ~/.claude/CLAUDE.md
  - Converting skills → ~/.claude/commands/

⚠️ Found 1 placeholder requiring manual config:
  - sudo password: for root commands

Import complete!
Test with: claude
```

## Repository

https://github.com/JohnnyChanZY/agent-porter