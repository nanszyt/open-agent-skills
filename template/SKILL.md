---
name: my-new-skill
description: "Use this skill whenever user asks to [action/workflow]. Trigger when user mentions '[keyword1]', '[keyword2]', or '[keyword3]'."
---

# 新技能模板 (Skill Starter Template)

简要描述本 Skill 的设计目标、适用业务场景以及它解决的核心痛点。

---

## 资产与工具索引

- **核心执行脚本**：[example.py](./scripts/example.py)
- **技术规范参考**：[guide.md](./references/guide.md)

---

## 标准执行工作流 (Standard Workflow)

### 第 1 步：分析输入与准备上下文
详细列出 Agent 在执行此技能前需收集的信息或确认的前提条件。

### 第 2 步：调用工具执行核心任务
说明具体的命令或脚本调用方式：
```bash
python scripts/example.py --input data.json
```

### 第 3 步：结果校验与质量核验 (QA Checklist)
- [ ] 检查项 1：产出物格式是否合规
- [ ] 检查项 2：关键指标与内容是否完整
