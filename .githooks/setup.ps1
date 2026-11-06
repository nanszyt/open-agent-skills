# 跨平台一键启用 Git Hooks 配置 (Windows PowerShell)
# 输出规范：终端提示一律使用英文 ASCII，避免 Windows 代码页乱码；注释可用中文。

Write-Host "[setup] Configuring Git hooks for open-agent-skills..." -ForegroundColor Cyan

# 1. 配置 Hooks 路径
git config core.hooksPath .githooks

# 2. 关闭当前仓库的 autocrlf，防止误转 CRLF
git config core.autocrlf false

# 3. 开启符号链接支持 (Symlinks)
git config core.symlinks true

if ($LASTEXITCODE -eq 0) {
    Write-Host "[setup] OK: Git hooks and Windows settings configured successfully." -ForegroundColor Green
    Write-Host "[setup] Active rules:" -ForegroundColor Yellow
    Write-Host "        - no direct commits on main/master"
    Write-Host "        - branch names must be lowercase (Windows case-insensitivity safe)"
    Write-Host "        - commit message must follow Conventional Commits (commit-msg)"
    Write-Host "        - block staged files larger than 15 MB"
    Write-Host "        - block filenames illegal or reserved on Windows"
    Write-Host "        - no direct pushes to remote main (merge via GitHub Pull Requests)"
    Write-Host "        - line endings stay LF (core.autocrlf = false)"
    Write-Host "        - symlinks enabled (core.symlinks = true)"
} else {
    Write-Host "[setup] FAILED: check that git is installed and available on PATH." -ForegroundColor Red
    exit 1
}
