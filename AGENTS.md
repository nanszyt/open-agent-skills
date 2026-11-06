# AGENTS.md

> 本文件是**针对各类型 AI Agent（Antigravity、Claude Code、Cursor、Codex 等）的操作索引与协作规范**。当 Agent 在本代码库中工作时，必须严格遵守以下规范。

---

## 项目定位

**Open Agent Skills**：公开开源的 AI Agent 技能集合与分发中心，基于 Anthropic Agent Skills Standard 构建，支持 Google Antigravity、Claude Code、Cursor、Codex 等主流智能体。

---

## 常用命令与校验入口

```bash
# 1. 校验全仓技能合规性（提交与 PR 前必跑）
python scripts/validate.py

# 2. 本地测试单个技能打包（生成 dist/<skill>.zip）
python scripts/package_skills.py --skill hose-ppt

# 3. 本地安装/同步技能
python scripts/sync.py --install hose-ppt
```

---

## 协作铁律（详见 CONTRIBUTING.md）

1. **分支管理**：
   - **严禁**直接在 `main` / `master` 分支上开发或执行 `git commit`。
   - **严禁**向远程 `origin/main` 执行 `git push`。
   - 所有改动必须新建**全小写特性分支**（如 `feat/<skill-name>`、`fix/<issue-name>`、`docs/<doc-name>`），然后发起 Pull Request 经由 CI 校验合入。
2. **分支命名**：
   - 必须且只能全小写（短横线或斜杠分隔）。禁止混用大写字母（规避 Windows NTFS / macOS 大小写不敏感冲突）。
3. **Commit 规范**：
   - 遵循 Conventional Commits：`<type>(<scope>): <简体中文说明>`。
   - 允许的 type：`feat`, `fix`, `skill`, `docs`, `ci`, `infra`, `refactor`, `test`, `chore`。
4. **文件体积与字符合规**：
   - 单文件体积必须 ≤ 15MB；
   - 严禁出现 Windows 非法字符（`: * ? " < > |`）和系统保留设备名（`CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9`）。

---

## GitHub CLI 与 PR 操作规范

- **Markdown 实体先行 (Markdown-First)**：
  多行 Commit 正文或 PR 说明，一律先在本地落盘为 `.drafts/` 目录下的 `.md` 文件（如 `.drafts/commit-msg.md`、`.drafts/pr-body.md`），再使用 `git commit -F` 或 `gh pr create --body-file` 传递，严禁在命令行拼接多行内联长文本。
- **PR 模板对齐**：
  发起 PR 时必须对齐 `.github/pull_request_template.md`，并在描述中声明已经过 `python scripts/validate.py` 校验通过。
