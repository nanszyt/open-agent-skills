## 变更说明

> **语言规范提醒**：本仓库统一使用**简体中文**进行技术交流、Commit 记录与 PR 评审，请使用简体中文填写以下内容。

### 关联 Issue
- Fixes #
- Closes #

### 变更背景与内容概述
<!-- 请简要说明发起此 PR 的背景原因，以及本次变更的核心内容（如新增了什么技能、解决了什么兼容性或格式问题） -->

- 

### 变更分类
- [ ] 🚀 新增技能 (New Skill)
- [ ] ⚡ 技能增强或 Prompt 调优 (Skill Enhancement)
- [ ] 🐛 技能缺陷修复 (Bugfix)
- [ ] 📝 文档补充或更新 (Docs)
- [ ] 🛠️ 自动化打包与 CI/CD 流水线 (Infra/CI)
- [ ] 🎨 结构或工具脚本重构 (Refactor)

### 影响范围
- [ ] 技能目录 (`skills/<skill-name>`)
- [ ] 安装与同步脚本 (`scripts/sync.py`, `scripts/validate.py`, `scripts/package_skills.py`)
- [ ] 技能脚手架与规范 (`spec/`, `template/`)
- [ ] 自动化流水线与 Git 规范 (`.github/`, `.githooks/`)
- [ ] 项目文档 (`README.md`, `CONTRIBUTING.md`, `AGENTS.md`)

### 验证与质量自检清单
<!-- 发起 PR 前请务必在本地逐项核对并勾选 -->

- [ ] **分支规范**：当前分支基于 `main` 切出，分支名称全小写（如 `feat/<skill-name>`、`fix/<issue-name>`），严禁直接向 `main` 发起推送
- [ ] **合规性校验**：本地运行 `python scripts/validate.py` 全部通过
- [ ] **规范 Frontmatter**：新增或修改的技能 `SKILL.md` 包含规范的 YAML frontmatter（`name` 与目录名严格一致，且包含清晰的 `description`）
- [ ] **体积控制**：提交的文件中无任何单文件超过 15MB 的二进制大文件（大文件请走 Release 附件）
- [ ] **跨平台兼容**：文件名均符合 Windows / macOS / Linux 规范（无非法字符 `: * ? " < > |` 及 Windows 保留设备名）
- [ ] **实际体验**：已在 Antigravity / Claude / Cursor 等智能体平台中手工测试过该技能的唤醒与执行效果
