# Agent Skills Specification (智能体技能规范标准)

本规范参考 [Anthropic Agent Skills Standard](https://github.com/anthropics/skills) 与 Google Antigravity Customization Architecture，定义了 AI Agent 技能包的标准化工程格式。

---

## 1. 核心设计原则 (Design Principles)

1. **渐进式披露 (Progressive Disclosure)**：
   - 技能默认仅向模型暴露其元数据（`name` 与 `description`），不占用大量上下文空间。
   - 仅当用户的意图或任务匹配触发条件时，Agent 才会按需加载并深入阅读完整的 `SKILL.md`、`references/` 与执行脚本。
2. **自包含与可移植 (Self-Contained & Portable)**：
   - 每个技能为一个独立的目录，包含其工作流指令、静态资源模板（`resources/` 或 `assets/`）、辅助工具脚本（`scripts/`）及深度参考手册（`references/`）。
   - 技能不依赖特定工作区的隐式配置，可跨机器、跨项目、跨平台无缝复制或挂载。
3. **确定性执行 (Deterministic Execution)**：
   - 将复杂的多步推理或格式敏感的任务固化为可执行的辅助脚本，由 Agent 调用执行，避免模型在纯文本生成过程中的语法漂移与意外幻觉。

---

## 2. 目录规范 (Directory Layout)

每个技能必须放置在独立目录中，命名全小写、短横线分隔（kebab-case）：

```text
skills/<skill-name>/
├── SKILL.md                  # [必需] 核心配置文件与主指令
├── resources/                # [可选] 静态资产、模板文件 (如 .pptx, .docx, .json 等)
├── scripts/                  # [可选] 可执行辅助脚本 (Python, Shell, Node 等)
└── references/               # [可选] 详细技术手册、设计规范、API 文档
```

---

## 3. 入口文件规范 (`SKILL.md`)

`SKILL.md` 必须以合法的 YAML Frontmatter 开头，紧随 Markdown 正文：

```yaml
---
name: my-skill-name
description: "清楚说明该技能的功能与触发场景。使用第三人称，列出高频唤醒关键词。例如：Use this skill whenever creating B2B presentations in Hosea template style. Trigger when user mentions '合思', '合思PPT'..."
---

# 技能名称与核心概述

## 资产与工具索引
- [template.pptx](./resources/template.pptx)
- [tool.py](./scripts/tool.py)

## 标准执行工作流
1. 第一步：需求与大纲梳理...
2. 第二步：调用脚本生成...
3. 第三步：QA 验收核验...
```

### Frontmatter 字段要求：
* **`name`** (字符串，必填)：技能唯一标识，必须与父目录名严格一致。
* **`description`** (字符串，必填)：路由大脑的核心依据。Agent 依据该描述判断是否激活此技能。

---

## 4. 兼容性 (Cross-Platform Compatibility)

本规范产出的技能可在以下现代 Agent 运行时中完全通用：
* **Google Antigravity**（支持全局 `~/.gemini/config/skills/` 与项目级 `.agents/skills/`）
* **Claude Code / Claude.ai**（支持 `~/.claude/skills/`）
* **Codex / OpenCode / Cursor / OpenClaw**
