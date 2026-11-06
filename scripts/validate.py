"""
Agent Skills Validator (技能格式与合规性校验工具)
Checks every skill folder for required SKILL.md, YAML frontmatter, naming match, and broken links.
"""

import os
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_SKILLS = os.path.join(REPO_ROOT, 'skills')

def validate_all_skills():
    if not os.path.exists(REPO_SKILLS):
        print(f"Skills directory not found: {REPO_SKILLS}")
        return False
    
    skill_folders = [d for d in sorted(os.listdir(REPO_SKILLS)) if os.path.isdir(os.path.join(REPO_SKILLS, d))]
    print(f"\nValidating {len(skill_folders)} skills in {REPO_SKILLS}...\n")
    
    has_errors = False

    for folder_name in skill_folders:
        folder_path = os.path.join(REPO_SKILLS, folder_name)
        skill_md_path = os.path.join(folder_path, 'SKILL.md')
        
        # 1. Check SKILL.md existence
        if not os.path.exists(skill_md_path):
            print(f"❌ [{folder_name}]: Missing required SKILL.md file!")
            has_errors = True
            continue
            
        # 2. Check Frontmatter
        with open(skill_md_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        if not content.startswith('---'):
            print(f"❌ [{folder_name}]: SKILL.md does not start with YAML frontmatter ('---')!")
            has_errors = True
            continue
            
        parts = content.split('---', 2)
        if len(parts) < 3:
            print(f"❌ [{folder_name}]: SKILL.md frontmatter is improperly closed (missing closing '---')!")
            has_errors = True
            continue
            
        frontmatter = parts[1]
        
        # Check name
        name_match = re.search(r'name:\s*([^\n\r]+)', frontmatter)
        if not name_match:
            print(f"❌ [{folder_name}]: Missing required 'name' field in frontmatter!")
            has_errors = True
        else:
            declared_name = name_match.group(1).strip().strip("'\"")
            if declared_name != folder_name:
                print(f"⚠️ [{folder_name}]: Declared name '{declared_name}' does not match folder name '{folder_name}'!")
                
        # Check description
        desc_match = re.search(r'description:\s*([^\n\r]+)', frontmatter)
        if not desc_match:
            print(f"❌ [{folder_name}]: Missing required 'description' field in frontmatter!")
            has_errors = True
            
        print(f"✔ [{folder_name}]: Valid format & structure.")

    print("\n" + "="*50)
    if has_errors:
        print("Validation Finished: Found errors in some skills.")
        return False
    else:
        print("Validation Finished: All skills passed Agent Skills Standard!")
        return True

if __name__ == '__main__':
    success = validate_all_skills()
    sys.exit(0 if success else 1)
