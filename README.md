# Agent Porter 🧳

**AI Agent 配置迁移工具** - 将一个 AI Agent 的配置蒸馏后迁移到另一个 Agent。

## 功能特点

- 🔄 **跨平台迁移** - 支持 Hermes、Claude Code、Codex、OpenCode
- 🎯 **智能蒸馏** - 自动精简配置，保留核心价值
- 🔐 **敏感信息处理** - 识别并安全处理敏感数据
- 📦 **单文件导出** - 生成可读的 YAML 配置文件

## 支持的平台

| 平台 | 导出 | 导入 |
|------|------|------|
| Hermes | ✅ | ✅ |
| Claude Code | ✅ | ✅ |
| Codex | ✅ | ✅ |
| OpenCode | ✅ | ✅ |

## 安装

### 作为 Hermes Skill 使用

```bash
# 复制到 Hermes skills 目录
cp -r . ~/.hermes/skills/productivity/agent-porter/
```

### 作为独立工具使用

```bash
git clone https://github.com/JohnnyChanZY/agent-porter.git
cd agent-porter
pip install pyyaml
```

## 使用方法

### 导出配置

在 Hermes 中：
```
用户: 导出我的 Agent 配置
用户: 我要迁移到 Claude Code，帮我导出
```

### 导入配置

```
用户: 把 agent-export.yaml 导入到 Claude Code
用户: 导入配置到 Hermes
```

## 导出文件格式

```yaml
# agent-export.yaml

format_version: "1.0"
source_agent: "hermes"

# 用户画像 (~50行)
user:
  identity:
    name: "..."
    email: "..."
  preferences:
    response_style: "concise"
    language: "zh-CN"

# 记忆 (~100行)
memory:
  environment:
    - key: "sudo密码"
      value: "***REDACTED***"
  project_knowledge:
    - key: "项目目录"
      value: "~/projects/"

# 人格设定 (~50行)
persona:
  content: "..."

# 技能 (每项 ~80行)
skills:
  - name: "coding-style"
    core_logic: "..."
```

## 蒸馏粒度

基于 Claude Code 官方建议（<200行）：

| 组件 | 目标大小 |
|------|----------|
| user_profile | ~50行 / ~1KB |
| memory | ~100行 / ~2KB |
| persona | ~50行 / ~1KB |
| per skill | ~80行 / ~2KB |

**总目标**: ~500行 / ~10KB

## 敏感信息处理

工具会自动识别以下类型的敏感信息：
- 🔑 凭证（密码、API Keys、Tokens）
- 👤 个人身份信息（邮箱、手机号）
- 💻 系统信息（路径、用户名）

处理策略：
- **包含明文** - 导出文件保留原值（需妥善保管）
- **包含占位符** - 用 `***REDACTED***` 替代，导入时手动填写
- **跳过此项** - 不导出，新 Agent 重新录入

## 开发状态

- [x] 基础架构设计
- [x] Hermes 导出支持
- [x] Claude Code 导入支持
- [ ] Codex 完整支持
- [ ] OpenCode 完整支持
- [ ] 交互式敏感信息处理
- [ ] 增量导出

## License

MIT
