---
name: agent-porter
description: AI Agent 配置迁移工具 - 导出、蒸馏、导入 Agent 配置（支持 Hermes、Claude Code、Codex、OpenCode）
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [agent, migration, export, import, portability, distillation]
    related_skills: []
---

# Agent Porter - AI Agent 配置迁移技能

将一个 AI Agent 的配置蒸馏后迁移到另一个 Agent，实现"Agent 认知传承"。

## 核心功能

1. **导出 (export)** - 从当前 Agent 提取配置并蒸馏
2. **导入 (import)** - 将配置导入到目标 Agent
3. **预览 (preview)** - 查看蒸馏后的效果

---

## 使用方式

### 导出配置

```
用户请求: "导出我的 Agent 配置"
或: "我要迁移到 Claude Code，帮我导出配置"
```

执行流程：
1. 读取当前 Agent 配置
2. 识别敏感信息并询问处理方式
3. 蒸馏精简各组件
4. 生成 `agent-export.yaml`

### 导入配置

```
用户请求: "导入 Agent 配置到 Hermes"
或: "把这个配置文件导入到 Claude Code"
```

执行流程：
1. 解析 `agent-export.yaml`
2. 转换为目标平台格式
3. 写入目标位置
4. 提示配置敏感信息

---

## 支持的平台

| 平台 | 导出支持 | 导入支持 | 配置目录 |
|------|----------|----------|----------|
| Hermes | ✅ | ✅ | ~/.hermes/ |
| Claude Code | ✅ | ✅ | ~/.claude/ |
| Codex | ✅ | ✅ | ~/.codex/ |
| OpenCode | ✅ | ✅ | ~/.config/opencode/ |

---

## 导出文件格式

```yaml
# agent-export.yaml

format_version: "1.0"
exported_at: "2024-04-26T..."
source_agent: "hermes"

# ========== 用户画像（~50行）==========
user:
  identity:
    name: "..."
    email: "..."
    role: "..."
    
  preferences:
    response_style: "..."
    language: "..."
    auto_approve: true/false
    
  current_work:
    project: "..."
    focus: "..."
    
# ========== 记忆（~100行）==========
memory:
  environment:
    - key: "..."
      value: "..."
      
  project_knowledge:
    - key: "..."
      value: "..."
      
  key_lessons:
    - key: "..."
      lesson: "..."
      
# ========== 人格设定（~50行）==========
persona:
  content: "..."
  
# ========== 技能（每项~80行）==========
skills:
  - name: "..."
    description: "..."
    core_logic: "..."
    
# ========== 平台特定信息 ==========
platform_notes:
  source_platform_only:
    - "..."  # 仅源平台有效，不迁移
```

---

## 蒸馏粒度标准

基于 Claude Code 官方建议（<200行）和 Hermes 配置限制：

| 组件 | 目标大小 | 保留内容 |
|------|----------|----------|
| user_profile | ~50行 / ~1KB | 身份 + 核心偏好 + 当前项目 |
| memory | ~100行 / ~2KB | 环境知识 + 项目约定 + 关键经验 |
| persona | ~50行 / ~1KB | 核心性格（去掉注释/示例） |
| per skill | ~80行 / ~2KB | 核心逻辑 + 关键步骤 + 注意事项 |

**总目标**: ~500行 / ~10KB（一个屏幕可看完）

---

## 敏感信息处理

### 识别规则

**必定敏感**:
- API Keys / Tokens
- 密码
- 私钥 / SSH Keys
- 数据库连接字符串

**可能敏感**:
- 邮箱地址
- 手机号码
- 服务器地址
- 项目路径
- 用户名

### 处理流程

```
发现敏感信息 → 首次询问用户选择：
  
  [A] 包含明文 - 导出文件保留明文（需妥善保管）
  [B] 包含占位符 - 用 ***REDACTED*** 替代，导入时手动填写
  [C] 跳过此项 - 不导出，新 Agent 重新录入
  [D] 全部跳过此类 - 跳过所有同类型敏感信息
  
后续同类敏感信息 → 自动应用相同策略，并告知用户
```

---

## 导出流程详细步骤

### Step 1: 检测当前 Agent 类型

```bash
# 检查配置目录判断 Agent 类型
test -d ~/.hermes && echo "hermes"
test -d ~/.claude && echo "claude-code"
test -d ~/.codex && echo "codex"
test -d ~/.config/opencode && echo "opencode"
```

### Step 2: 读取配置文件

根据 Agent 类型读取对应配置：

**Hermes**:
- ~/.hermes/memory.md → memory
- ~/.hermes/user.md → user_profile
- ~/.hermes/SOUL.md → persona
- ~/.hermes/skills/*/SKILL.md → skills
- ~/.hermes/config.yaml → tools/model

**Claude Code**:
- ~/.claude/CLAUDE.md → persona + memory + user
- ~/.claude/settings.json → tools/model
- ~/.claude/commands/*.md → skills

**Codex**:
- ~/.codex/instructions.md → persona
- .codex/skills/*.md → skills
- 环境变量 → model

**OpenCode**:
- ~/.config/opencode/config.json → 全部

### Step 3: 蒸馏精简

使用 AI 分析并精简内容：

1. **合并重复信息**
2. **移除已过时信息**（已完成的事项）
3. **压缩冗长描述**（保留核心要点）
4. **筛选高价值技能**（用户自定义 > 内置技能）

### Step 4: 处理敏感信息

扫描蒸馏后的内容，识别敏感信息：
- 首次发现 → 询问用户
- 后续同类 → 应用相同策略

### Step 5: 生成导出文件

写入 `~/agent-export.yaml` 或用户指定路径。

---

## 导入流程详细步骤

### Step 1: 解析导出文件

读取并验证 `agent-export.yaml` 的格式版本。

### Step 2: 确认目标平台

询问或自动检测目标 Agent 类型。

### Step 3: 格式转换

根据目标平台转换格式：

**Hermes**:
```bash
user → ~/.hermes/user.md
memory → ~/.hermes/memory.md  
persona → ~/.hermes/SOUL.md
skills → ~/.hermes/skills/{category}/{name}/SKILL.md
```

**Claude Code**:
```bash
# 合并 persona + user + memory 到 CLAUDE.md
cat persona user memory | merge_sections > ~/.claude/CLAUDE.md

# skills → commands
skills → ~/.claude/commands/{name}.md
```

**Codex**:
```bash
persona + memory → ~/.codex/instructions.md
skills → .codex/skills/{name}.md
```

**OpenCode**:
```bash
全部 → ~/.config/opencode/config.json
```

### Step 4: 处理占位符

如果存在 `***REDACTED***`，提示用户：
```
"发现敏感信息占位符，请在目标 Agent 中手动配置：
  - sudo密码: 用于执行需要root权限的命令
  - API Key: 用于访问外部服务"
```

### Step 5: 完成确认

显示导入结果，提示用户测试验证。

---

## 转换规则详解

### Hermes → Claude Code

| 源组件 | 目标组件 | 转换方式 |
|--------|----------|----------|
| SOUL.md | CLAUDE.md 首部 | 直接合并 |
| user.md | CLAUDE.md "## User" 部分 | 格式调整 |
| memory.md | CLAUDE.md "## Memory" 部分 | 精简合并 |
| skills/*/SKILL.md | commands/*.md | 移除 YAML frontmatter |
| config.yaml MCP | settings.json mcpServers | JSON 格式转换 |

### Claude Code → Hermes

| 源组件 | 目标组件 | 转换方式 |
|--------|----------|----------|
| CLAUDE.md 首部 | SOUL.md | 提取人格部分 |
| CLAUDE.md "## User" | user.md | 提取用户部分 |
| CLAUDE.md "## Memory" | memory.md | 提取记忆部分 |
| commands/*.md | skills/*/SKILL.md | 添加 YAML frontmatter |
| settings.json mcpServers | config.yaml | YAML 格式转换 |

### 其他平台转换

类似逻辑，根据各平台配置结构调整。

---

## Pitfalls / 注意事项

1. **敏感信息安全**
   - 导出文件可能包含敏感信息，提醒用户妥善保管
   - 不要将导出文件上传到公开位置

2. **平台差异**
   - 某些功能在目标平台可能不支持（如 Hermes 的 cron 功能）
   - MCP 服务器配置需要重新验证兼容性

3. **技能兼容性**
   - 技能中的命令可能依赖特定工具（如 hermes_tools）
   - 需要检查并调整依赖

4. **模型差异**
   - Prompt 在不同模型上效果可能不同
   - 导入后可能需要微调

5. **路径差异**
   - 文件路径可能因系统不同而失效
   - 需要检查并调整路径

---

## 示例对话

**导出场景**:
```
用户: 我要迁移到 Claude Code，帮我导出 Hermes 配置

Agent: 
好的，我来帮你导出 Hermes 配置。

正在读取配置文件...
- memory.md: 1857字符
- user.md: 553字符
- SOUL.md: 537字符
- 自定义技能: 3个

正在蒸馏精简...
- 已移除已完成的事项（毕设论文已完成）
- 已合并重复的用户偏好信息
- 已压缩冗长的技能文档

⚠️ 发现敏感信息:
  
1. sudo 密码: "password"
   类型: credential
   
请选择处理方式:
[A] 包含明文 - 导出文件保留明文
[B] 包含占位符 - 用 ***REDACTED*** 替代
[C] 跳过此项 - 不导出
[D] 全部跳过此类 - 跳过所有密码类信息

用户: B

Agent:
已选择"包含占位符"。后续所有密码类敏感信息将自动应用此策略。

继续扫描...
  
2. 用户邮箱: JohnnyChenZhuoyi@hotmail.com
   类型: pii (个人身份信息)
   
请选择处理方式:
[A] 包含明文
[B] 包含占位符
[C] 跳过此项
[D] 全部跳过此类

用户: A

Agent:
已选择"包含明文"。后续所有邮箱类信息将保留原值。

完成！导出文件已生成: ~/agent-export.yaml

蒸馏后大小: 8.5KB（约450行）
原始大小: 约15KB

你可以查看文件内容，确认无误后再导入到 Claude Code。
```

**导入场景**:
```
用户: 把 ~/agent-export.yaml 导入到 Claude Code

Agent:
好的，我来导入配置到 Claude Code。

正在解析导出文件...
- 格式版本: 1.0
- 来源: Hermes
- 导出时间: 2024-04-26

正在转换格式...
- 合并 persona + user + memory → ~/.claude/CLAUDE.md
- 转换技能 → ~/.claude/commands/
- 转换 MCP 配置 → ~/.claude/settings.json

⚠️ 发现占位符需要手动配置:
- sudo密码: 用于执行需要root权限的命令
- API Key (如果需要): 用于访问外部服务

已完成导入！

写入位置:
- ~/.claude/CLAUDE.md (358行)
- ~/.claude/commands/ (3个文件)
- ~/.claude/settings.json (已更新 MCP 配置)

建议:
1. 启动 Claude Code 测试基本功能
2. 手动配置敏感信息
3. 检查技能命令的兼容性
```

---

## 验证步骤

导出后验证:
```bash
# 检查文件格式
python -c "import yaml; yaml.safe_load(open('~/agent-export.yaml'))"

# 检查大小
wc -l ~/agent-export.yaml
wc -c ~/agent-export.yaml
```

导入后验证:
```bash
# 根据目标平台检查文件是否存在
test -f ~/.claude/CLAUDE.md && echo "Claude Code 配置已写入"
test -f ~/.hermes/memory.md && echo "Hermes 配置已写入"
```