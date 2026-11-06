"""
Automated Skill Packager (技能自动化独立打包工具)
Packages each skill in skills/ into an independent downloadable zip file containing 1-click installers.
Used by GitHub Actions and local developers.
"""

import os
import sys
import shutil
import zipfile
import argparse
import tempfile
import re

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(REPO_ROOT, 'skills')

INSTALL_BAT_TPL = """@echo off
chcp 65001 >nul
echo ========================================================
echo   {skill_name} 智能体技能一键安装程序 (Windows)
echo ========================================================
echo.
set "TARGET=%USERPROFILE%\\.gemini\\config\\skills\\{skill_name}"

echo 正在部署至: %TARGET% ...
if not exist "%USERPROFILE%\\.gemini\\config\\skills" (
    mkdir "%USERPROFILE%\\.gemini\\config\\skills"
)
if exist "%TARGET%" (
    rmdir /s /q "%TARGET%"
)
mkdir "%TARGET%"
xcopy /s /e /y "%~dp0{skill_name}\\*" "%TARGET%\\" >nul

echo.
echo ========================================================
echo   [SUCCESS] 安装成功！
echo   现在可以在 Antigravity 中直接使用该技能。
echo ========================================================
echo.
pause
"""

INSTALL_SH_TPL = """#!/bin/bash
TARGET="$HOME/.gemini/config/skills/{skill_name}"
echo "========================================================"
echo "  {skill_name} Agent Skill Installer (macOS / Linux)"
echo "========================================================"
mkdir -p "$HOME/.gemini/config/skills"
if [ -d "$TARGET" ]; then
    rm -rf "$TARGET"
fi
mkdir -p "$TARGET"

DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
cp -R "$DIR/{skill_name}/"* "$TARGET/"

echo "========================================================"
echo "  [SUCCESS] Installed successfully to $TARGET"
echo "========================================================"
"""

def extract_skill_metadata(skill_path):
    skill_md = os.path.join(skill_path, 'SKILL.md')
    desc = "No description provided."
    if os.path.exists(skill_md):
        with open(skill_md, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        m = re.search(r'description:\s*["\']?([^"\']+)["\']?', content)
        if m:
            desc = m.group(1).strip()
    return desc

def package_all_skills(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    skills = [d for d in sorted(os.listdir(SKILLS_DIR)) if os.path.isdir(os.path.join(SKILLS_DIR, d))]
    
    print(f"Packaging {len(skills)} skills into {out_dir}...")
    release_items = []

    for s_name in skills:
        s_src = os.path.join(SKILLS_DIR, s_name)
        zip_name = f"{s_name}.zip"
        zip_path = os.path.join(out_dir, zip_name)
        
        # Build in tempdir
        with tempfile.TemporaryDirectory() as tmp:
            # 1. install.bat
            bat_path = os.path.join(tmp, "install.bat")
            with open(bat_path, "w", encoding="utf-8-sig") as f:
                f.write(INSTALL_BAT_TPL.format(skill_name=s_name))
                
            # 2. install.sh
            sh_path = os.path.join(tmp, "install.sh")
            with open(sh_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(INSTALL_SH_TPL.format(skill_name=s_name))
                
            # 3. copy skill folder
            dest_skill_folder = os.path.join(tmp, s_name)
            shutil.copytree(
                s_src, dest_skill_folder,
                ignore=shutil.ignore_patterns('__pycache__', '*.pyc', 'slides_preview', '*.tmp')
            )
            
            # 4. create zip
            if os.path.exists(zip_path):
                os.remove(zip_path)
            with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
                for root, _, files in os.walk(tmp):
                    for file in files:
                        full_p = os.path.join(root, file)
                        rel_p = os.path.relpath(full_p, tmp)
                        z.write(full_p, rel_p)
                        
        size_kb = os.path.getsize(zip_path) / 1024.0
        desc = extract_skill_metadata(s_src)
        print(f"✔ Packaged: {zip_name} ({size_kb:.1f} KB)")
        release_items.append({"name": s_name, "zip": zip_name, "size": f"{size_kb:.1f} KB", "desc": desc})

    # Generate RELEASE_NOTES.md
    notes_path = os.path.join(out_dir, "RELEASE_NOTES.md")
    with open(notes_path, "w", encoding="utf-8") as f:
        f.write("# 📦 Agent Skills 独立安装包自动发布\n\n")
        f.write("本发布由 GitHub Actions 自动化构建。每个技能均已打包为独立的绿色免配置安装包，内附 Windows `install.bat` 与 macOS/Linux `install.sh`。\n\n")
        f.write("### 技能下载列表 (Downloads)\n\n")
        f.write("| 技能名称 | 独立下载包 | 文件大小 | 简介 |\n")
        f.write("|---|---|---|---|\n")
        for item in release_items:
            f.write(f"| **`{item['name']}`** | [⬇️ 下载 `{item['zip']}`](https://github.com/nanszyt/open-agent-skills/releases/download/latest/{item['zip']}) | {item['size']} | {item['desc'][:70]}... |\n")
        f.write("\n### 安装使用说明\n")
        f.write("1. 下载对应技能的 `.zip` 文件；\n")
        f.write("2. 解压后：\n")
        f.write("   - **Windows**：双击运行 `install.bat`\n")
        f.write("   - **macOS / Linux**：终端执行 `bash install.sh`\n")
        f.write("3. 重新打开 Antigravity 或任何支持 Agent Skills 的平台即可自动唤醒使用。\n")

    print(f"✔ Generated Release Notes: {notes_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Package Skills")
    parser.add_argument("--output-dir", "-o", default=os.path.join(REPO_ROOT, 'dist'), help="Output directory")
    args = parser.parse_args()
    package_all_skills(args.output_dir)
