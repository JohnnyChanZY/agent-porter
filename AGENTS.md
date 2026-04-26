# Agent Porter

AI Agent configuration migration tool - export, distill, and import agent configs across platforms.

## What it does

Helps you migrate your AI agent configuration (memory, persona, skills) from one agent to another with intelligent distillation.

## Supported Agents

- Hermes
- Claude Code
- Codex
- OpenCode

## Install

```bash
npx skills add JohnnyChanZY/agent-porter
```

## Quick Start

```bash
# Export from current agent
python scripts/export.py export ~/agent-export.yaml

# Import to target agent
python scripts/import.py ~/agent-export.yaml claude-code
```

## Key Features

- **Distillation**: Auto-compresses config to ~500 lines total
- **Sensitive Info Handling**: Identifies credentials, PII, and system paths
- **Cross-Platform**: Works with 4+ agent platforms

## Repository

https://github.com/JohnnyChanZY/agent-porter