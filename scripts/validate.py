"""
Agent Skills Validator (技能格式与跨平台合规性校验工具)
Checks every skill folder for required SKILL.md, YAML frontmatter, naming match, file size, and cross-platform safety.
"""

import os
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_SKILLS = os.path.join(REPO_ROOT, 'skills')
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15MB

WINDOWS_ILLEGAL_CHARS = set(r':*?"<>|')
WINDOWS_RESERVED_NAMES = {
    'con', 'prn', 'aux', 'nul',
    'com1', 'com2', 'com3', 'com4', 'com5', 'com6', 'com7', 'com8', 'com9',
    'lpt1', 'lpt2', 'lpt3', 'lpt4', 'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9'
}

def validate_all_skills():
    if not os.path.exists(REPO_SKILLS):
        print(f"Skills directory not found: {REPO_SKILLS}")
        return False
    
    skill_folders = [d for d in sorted(os.listdir(REPO_SKILLS)) if os.path.isdir(os.path.join(REPO_SKILLS, d))]
    print(f"\n=======================================================")
    print(f"Validating {len(skill_folders)} skills in {REPO_SKILLS}")
    print(f"=======================================================\n")
    
    has_errors = False

    for folder_name in skill_folders:
        folder_path = os.path.join(REPO_SKILLS, folder_name)
        skill_md_path = os.path.join(folder_path, 'SKILL.md')
        
        # 1. Folder naming check (lowercase & hyphens only)
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', folder_name):
            print(f"❌ [{folder_name}]: Folder name must be strictly lowercase alphanumeric with hyphens (e.g. 'hose-ppt')!")
            has_errors = True
        
        # 2. Check SKILL.md existence
        if not os.path.exists(skill_md_path):
            print(f"❌ [{folder_name}]: Missing required SKILL.md file!")
            has_errors = True
            continue
            
        # 3. Check Frontmatter format
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
                print(f"❌ [{folder_name}]: Declared name '{declared_name}' does not match folder name '{folder_name}'!")
                has_errors = True
                
        # Check description
        desc_match = re.search(r'description:\s*([^\n\r]+)', frontmatter)
        if not desc_match:
            print(f"❌ [{folder_name}]: Missing required 'description' field in frontmatter!")
            has_errors = True
        elif len(desc_match.group(1).strip()) < 10:
            print(f"⚠️ [{folder_name}]: Description is too short (< 10 chars). Please provide a more descriptive summary.")
            
        # 4. Deep check files inside skill folder (size and cross-platform compatibility)
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_full_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_full_path, folder_path)
                
                # Check file size limit (15MB)
                fsize = os.path.getsize(file_full_path)
                if fsize > MAX_FILE_SIZE:
                    size_mb = fsize / (1024 * 1024)
                    print(f"❌ [{folder_name}]: File '{rel_path}' ({size_mb:.2f} MB) exceeds 15 MB limit! Large assets must use GitHub Releases.")
                    has_errors = True
                    
                # Check Windows illegal characters
                if any(c in WINDOWS_ILLEGAL_CHARS for c in file):
                    print(f"❌ [{folder_name}]: Filename '{file}' contains illegal characters (: * ? \" < > |)!")
                    has_errors = True
                    
                # Check Windows reserved names
                base_name = os.path.splitext(file)[0].lower()
                if base_name in WINDOWS_RESERVED_NAMES:
                    print(f"❌ [{folder_name}]: Filename '{file}' uses a reserved Windows device name ({base_name})!")
                    has_errors = True

        if not has_errors:
            print(f"✔ [{folder_name}]: Valid format, frontmatter & structure.")

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
