#!/bin/sh
# 跨平台一键启用 Git Hooks 配置
# 适用环境：macOS / Linux / Windows Git Bash
# 输出规范：终端提示一律使用英文 ASCII，避免 Windows 代码页乱码；注释可用中文。

echo "[setup] Configuring Git hooks for open-agent-skills..."
git config core.hooksPath .githooks
git config core.autocrlf false
git config core.symlinks true

if [ $? -eq 0 ]; then
    echo "[setup] OK: Git hooks and line endings configured successfully."
    echo "        core.hooksPath = $(git config core.hooksPath)"
    echo "[setup] Active rules:"
    echo "        - no direct commits on main/master"
    echo "        - branch names must be lowercase (Windows case-insensitivity safe)"
    echo "        - commit message must follow Conventional Commits (commit-msg)"
    echo "        - block staged files larger than 15 MB"
    echo "        - block filenames illegal or reserved on Windows"
    echo "        - no direct pushes to remote main (merge via GitHub Pull Requests)"
    echo "        - line endings stay LF (core.autocrlf = false)"
    echo "        - symlinks enabled (core.symlinks = true)"
else
    echo "[setup] FAILED: check that git is installed and available on PATH."
    exit 1
fi
