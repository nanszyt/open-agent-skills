"""
Agent Skills Sync & Manager Utility (技能双向同步与管理工具)

在「本仓库」与「本地 Agent 运行时」之间双向同步技能。

支持的运行时（技能根目录）：
  agents  ~/.agents/skills          DSH (DeepSeek Harness)、Antigravity 工作区级
  claude  ~/.claude/skills          Claude Code / Claude 客户端
  gemini  ~/.gemini/config/skills   Antigravity 全局级

目标目录解析优先级：
  --target-dir  >  --workspace  >  --target  >  自动探测
  自动探测：按 agents → claude → gemini 顺序，取第一个已存在的目录；
  都不存在时回落到 ~/.agents/skills（DSH 默认位置）并自动创建。
"""

import argparse
import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_SKILLS = os.path.join(REPO_ROOT, 'skills')

# User Global Config Directory
USER_HOME = os.path.expanduser('~')

# 各 Agent 运行时的全局技能目录
TARGET_PRESETS = {
    'agents': os.path.join(USER_HOME, '.agents', 'skills'),
    'claude': os.path.join(USER_HOME, '.claude', 'skills'),
    'gemini': os.path.join(USER_HOME, '.gemini', 'config', 'skills'),
}

# 自动探测顺序：DSH / Antigravity 工作区 → Claude Code → Antigravity 全局
DETECT_ORDER = ('agents', 'claude', 'gemini')

# 向后兼容：旧版本把全局目录硬编码为 Antigravity 全局路径
GLOBAL_SKILLS = TARGET_PRESETS['gemini']

COPY_IGNORE = shutil.ignore_patterns('__pycache__', '*.pyc', 'slides_preview', '*.tmp')


# --------------------------------------------------------------------------- #
# 路径解析
# --------------------------------------------------------------------------- #

def expand_path(path):
    """展开 ~ / 环境变量并转为绝对路径。"""
    return os.path.abspath(os.path.expandvars(os.path.expanduser(path)))


def detect_target():
    """自动探测目标目录，返回 (目录, 说明)。"""
    for key in DETECT_ORDER:
        path = TARGET_PRESETS[key]
        if os.path.isdir(path):
            return path, f"自动探测：命中 {key}（{path} 已存在）"
    path = TARGET_PRESETS['agents']
    return path, f"自动探测：未发现任何运行时目录，回落到 agents（{path}）"


def resolve_paths(args):
    """按优先级解析安装目标目录与导入源目录，返回 (target_dir, source_dir, note)。"""
    if args.target_dir:
        d = expand_path(args.target_dir)
        return d, d, f"--target-dir（{d}）"
    if args.workspace:
        d = os.path.join(expand_path(args.workspace), '.agents', 'skills')
        return d, d, f"--workspace（{d}）"
    if args.target and args.target != 'auto':
        d = TARGET_PRESETS[args.target]
        return d, d, f"--target {args.target}（{d}）"
    d, note = detect_target()
    return d, d, note


# --------------------------------------------------------------------------- #
# 技能枚举
# --------------------------------------------------------------------------- #

def list_skills(root):
    if not root or not os.path.exists(root):
        return []
    return [d for d in sorted(os.listdir(root)) if os.path.isdir(os.path.join(root, d))]


def list_repo_skills():
    return list_skills(REPO_SKILLS)


# --------------------------------------------------------------------------- #
# 状态展示
# --------------------------------------------------------------------------- #

def show_runtimes():
    print("\n本机运行时目录：")
    for key in DETECT_ORDER:
        path = TARGET_PRESETS[key]
        mark = "✔ 存在" if os.path.isdir(path) else "  不存在"
        print(f"  {key:<7} {mark:<8} {path}")


def show_status(target_dir=None, note=""):
    repo_list = set(list_repo_skills())
    installed = set(list_skills(target_dir))
    all_skills = sorted(repo_list.union(installed))

    if target_dir:
        print(f"\n目标目录: {target_dir}")
        if note:
            print(f"解析方式: {note}")

    print(f"\n{'SKILL NAME':<30} | {'IN REPO':<10} | {'INSTALLED':<18}")
    print("-" * 65)
    for s in all_skills:
        in_repo = "✔ Yes" if s in repo_list else "  No"
        in_global = "✔ Installed" if s in installed else "  Not Installed"
        print(f"{s:<30} | {in_repo:<10} | {in_global:<18}")
    print(f"\nTotal Repo Skills: {len(repo_list)} | Total Installed: {len(installed)}\n")


# --------------------------------------------------------------------------- #
# 复制
# --------------------------------------------------------------------------- #

def _copy_skill(src, dst, action):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=COPY_IGNORE)
    print(f"✔ Successfully {action} -> {dst}")


def install_skill(skill_name, target_dir):
    src = os.path.join(REPO_SKILLS, skill_name)
    if not os.path.exists(src):
        print(f"Error: Skill '{skill_name}' not found in repo: {src}")
        return False

    os.makedirs(target_dir, exist_ok=True)
    _copy_skill(src, os.path.join(target_dir, skill_name), f"installed '{skill_name}'")
    return True


def install_all(target_dir):
    skills = list_repo_skills()
    print(f"Installing {len(skills)} skills to: {target_dir}")
    failed = [s for s in skills if not install_skill(s, target_dir)]
    if failed:
        print(f"⚠ {len(failed)} skill(s) failed: {', '.join(failed)}")
        return False
    print("✔ All skills installed successfully!")
    return True


def import_skill(skill_name, source_dir):
    src = os.path.join(source_dir, skill_name)
    if not os.path.exists(src):
        print(f"Error: Skill '{skill_name}' not found in source: {src}")
        return False

    os.makedirs(REPO_SKILLS, exist_ok=True)
    _copy_skill(src, os.path.join(REPO_SKILLS, skill_name),
                f"imported '{skill_name}' from local config into repo")
    return True


def import_all(source_dir):
    skills = list_skills(source_dir)
    print(f"Importing {len(skills)} local skills into repo...")
    failed = [s for s in skills if not import_skill(s, source_dir)]
    if failed:
        print(f"⚠ {len(failed)} skill(s) failed: {', '.join(failed)}")
        return False
    print("✔ All local skills imported into repo!")
    return True


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

EPILOG = """\
示例:
  python scripts/sync.py --status
  python scripts/sync.py --install-all                        # 自动探测目标目录
  python scripts/sync.py --install hose-ppt --target claude   # 装到 ~/.claude/skills
  python scripts/sync.py --install hose-ppt --target-dir "~/my-skills"
  python scripts/sync.py --install-all --workspace "C:\\path\\to\\project"
  python scripts/sync.py --import-skill my-awesome-skill --source-dir "~/.agents/skills"
"""


def main():
    parser = argparse.ArgumentParser(
        description="Agent Skills Sync Manager（仓库 ⇄ 本地运行时）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EPILOG,
    )
    parser.add_argument("--status", action="store_true", help="Show skills status between repo and local runtime")
    parser.add_argument("--install", type=str, metavar="SKILL", help="Install a specific skill from repo to runtime")
    parser.add_argument("--install-all", action="store_true", help="Install all repo skills to runtime")
    parser.add_argument("--import-skill", type=str, metavar="SKILL", help="Import a skill from runtime into repo")
    parser.add_argument("--import-all", action="store_true", help="Import all runtime skills into repo")

    parser.add_argument(
        "--target-dir", type=str, metavar="PATH",
        help="显式指定目标技能目录（最高优先级，支持 ~ 与环境变量）",
    )
    parser.add_argument(
        "--target", choices=('auto',) + DETECT_ORDER, default='auto',
        help="按运行时预置选择目标目录：agents=~/.agents/skills, claude=~/.claude/skills, "
             "gemini=~/.gemini/config/skills, auto=自动探测（默认）",
    )
    parser.add_argument(
        "--source-dir", type=str, metavar="PATH",
        help="导入时显式指定源目录（默认与目标目录相同）",
    )
    parser.add_argument(
        "--workspace", type=str, metavar="PATH",
        help="安装到指定工作区的 <PATH>/.agents/skills（团队项目级挂载，优先级低于 --target-dir）",
    )

    args = parser.parse_args()

    target_dir, source_dir, note = resolve_paths(args)
    if args.source_dir:
        source_dir = expand_path(args.source_dir)

    if args.status:
        show_runtimes()
        show_status(target_dir, note)
        return 0

    if args.install:
        if not install_skill(args.install, target_dir):
            return 1
        print(f"   目标目录: {target_dir}\n   解析方式: {note}")
        return 0

    if args.install_all:
        ok = install_all(target_dir)
        print(f"   目标目录: {target_dir}\n   解析方式: {note}")
        return 0 if ok else 1

    if args.import_skill:
        if not import_skill(args.import_skill, source_dir):
            return 1
        print(f"   源目录: {source_dir}")
        return 0

    if args.import_all:
        ok = import_all(source_dir)
        print(f"   源目录: {source_dir}")
        return 0 if ok else 1

    show_runtimes()
    show_status(target_dir, note)
    return 0


if __name__ == '__main__':
    sys.exit(main())
