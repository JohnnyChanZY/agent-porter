# Agent Porter

**AI Agent 配置迁移工具** - 将一个 AI Agent 的配置蒸馏后迁移到另一个 Agent。

[![Install with skills.sh](https://img.shields.io/badge/install%20with-skills.sh-blue)](https://skills.sh)

## 安装

```bash
# 通过 skills.sh 安装
npx skills add JohnnyChanZY/agent-porter

# 或克隆仓库
git clone https://github.com/JohnnyChanZY/agent-porter.git
cd agent-porter
pip install pyyaml
```

## 功能

- 🔄 **跨平台迁移** - 支持 Hermes、Claude Code、Codex、OpenCode
- 🎯 **智能蒸馏** - 自动精简配置，保留核心价值
- 🔐 **敏感信息处理** - 识别并安全处理敏感数据
- 📦 **单文件导出** - 生成可读的 YAML 配置文件

## 快速开始

### 导出配置

```bash
python scripts/export.py export ~/agent-export.yaml
```

### 导入配置

```bash
# 导入到 Claude Code
python scripts/import.py ~/agent-export.yaml claude-code

# 导入到 Hermes
python scripts/import.py ~/agent-export.yaml hermes
```

## 支持的平台

| 平台 | 导出 | 导入 | 配置目录 |
|------|------|------|----------|
| Hermes | ✅ | ✅ | ~/.hermes/ |
| Claude Code | ✅ | ✅ | ~/.claude/ |
| Codex | ✅ | ✅ | ~/.codex/ |
| OpenCode | ✅ | ✅ | ~/.config/opencode/ |

## 导出内容

自动蒸馏以下组件：

| 组件 | 大小目标 | 内容 |
|------|----------|------|
| user_profile | ~50行 | 身份信息 + 核心偏好 + 当前项目 |
| memory | ~100行 | 环境知识 + 项目约定 + 关键经验 |
| persona | ~50行 | 核心性格设定 |
| skills | ~80行/个 | 核心逻辑 + 关键步骤 |

## 敏感信息处理

自动识别并处理：

- 🔑 **凭证类** - 密码、API Keys、Tokens
- 👤 **个人身份** - 邮箱、手机号
- 💻 **系统信息** - 文件路径、用户名

首次发现时询问处理方式，后续同类信息自动应用相同策略。

## 目录结构

```
agent-porter/
├── skills/
│   └── agent-porter/
│       └── SKILL.md      # skills.sh 格式
├── scripts/
│   ├── export.py         # 导出脚本
│   └── import.py         # 导入脚本
├── README.md
├── AGENTS.md
└── LICENSE
```

## License

MIT
