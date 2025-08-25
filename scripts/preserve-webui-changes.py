#!/usr/bin/env python3
"""
Smart WebUI preservation script for MCPO updates.
This script automatically re-applies WebUI modifications to main.py after upstream merges.
"""

import re
import sys
import os
from pathlib import Path

def backup_webui_changes(main_py_path):
    """Extract and backup current WebUI modifications"""
    print("📦 Backing up current WebUI modifications...")
    
    with open(main_py_path, 'r') as f:
        content = f.read()
    
    webui_changes = {
        'has_webui_import': 'from mcpo.utils.web_interface import create_web_interface_router' in content,
        'has_webui_router': 'create_web_interface_router(' in content,
        'import_location': None,
        'router_location': None
    }
    
    # Find where the import is located
    if webui_changes['has_webui_import']:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'from mcpo.utils.web_interface import create_web_interface_router' in line:
                webui_changes['import_location'] = i
                break
    
    # Find where the router is added
    if webui_changes['has_webui_router']:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'create_web_interface_router(' in line:
                webui_changes['router_location'] = i
                break
    
    return webui_changes

def apply_webui_modifications(main_py_path, force=False):
    """Apply WebUI modifications to main.py"""
    print(f"🔧 Applying WebUI modifications to {main_py_path}...")
    
    with open(main_py_path, 'r') as f:
        content = f.read()
    
    modified = False
    
    # 1. Add WebUI import if not present
    webui_import = "from mcpo.utils.web_interface import create_web_interface_router"
    if webui_import not in content:
        print("  ➕ Adding WebUI import...")
        
        # Strategy 1: Add after other mcpo.utils imports
        utils_import_pattern = r'(from mcpo\.utils\.[^\s]+ import [^\n]+)'
        matches = list(re.finditer(utils_import_pattern, content))
        
        if matches:
            # Add after the last mcpo.utils import
            last_match = matches[-1]
            insert_pos = last_match.end()
            content = content[:insert_pos] + '\n' + webui_import + content[insert_pos:]
            modified = True
            print("    ✅ Added after existing mcpo.utils imports")
        else:
            # Strategy 2: Add after mcpo imports section
            mcpo_import_pattern = r'(from mcpo[^\n]*\n)(?!\s*from mcpo)'
            if re.search(mcpo_import_pattern, content):
                content = re.sub(mcpo_import_pattern, r'\1' + webui_import + '\n', content)
                modified = True
                print("    ✅ Added after mcpo imports section")
            else:
                # Strategy 3: Add after all imports
                import_end_pattern = r'(\nimport [^\n]*\n)(?!\s*(?:import|from))'
                if re.search(import_end_pattern, content):
                    content = re.sub(import_end_pattern, r'\1\n' + webui_import + '\n', content)
                    modified = True
                    print("    ✅ Added after all imports")
                else:
                    print("    ❌ Could not find suitable location for import")
    else:
        print("  ✅ WebUI import already present")
    
    # 2. Add WebUI router integration if not present
    webui_router_lines = [
        "    # Add web interface router",
        "    web_router = create_web_interface_router(config_path=config_path)",
        "    main_app.include_router(web_router)"
    ]
    webui_router_code = '\n'.join(webui_router_lines)
    
    if 'create_web_interface_router(' not in content or 'main_app.include_router(web_router)' not in content:
        print("  ➕ Adding WebUI router integration...")
        
        # Strategy 1: Add after CORS middleware setup
        cors_pattern = r'(main_app\.add_middleware\(\s*CORSMiddleware[^}]+}\s*\))'
        cors_match = re.search(cors_pattern, content, re.DOTALL)
        
        if cors_match:
            insert_pos = cors_match.end()
            # Find the end of the line
            while insert_pos < len(content) and content[insert_pos] != '\n':
                insert_pos += 1
            content = content[:insert_pos] + '\n\n' + webui_router_code + content[insert_pos:]
            modified = True
            print("    ✅ Added after CORS middleware")
        else:
            # Strategy 2: Add after API key middleware
            api_key_pattern = r'(if api_key and strict_auth:\s*main_app\.add_middleware\(APIKeyMiddleware[^\n]*\))'
            api_key_match = re.search(api_key_pattern, content, re.DOTALL)
            
            if api_key_match:
                insert_pos = api_key_match.end()
                while insert_pos < len(content) and content[insert_pos] != '\n':
                    insert_pos += 1
                content = content[:insert_pos] + '\n\n' + webui_router_code + content[insert_pos:]
                modified = True
                print("    ✅ Added after API key middleware")
            else:
                # Strategy 3: Add before headers processing
                headers_pattern = r'(\s+headers = kwargs\.get\("headers"\))'
                headers_match = re.search(headers_pattern, content)
                
                if headers_match:
                    content = content[:headers_match.start()] + '\n' + webui_router_code + '\n' + content[headers_match.start():]
                    modified = True
                    print("    ✅ Added before headers processing")
                else:
                    print("    ❌ Could not find suitable location for router integration")
    else:
        print("  ✅ WebUI router integration already present")
    
    if modified:
        # Write the modified content
        with open(main_py_path, 'w') as f:
            f.write(content)
        print(f"✅ Successfully applied WebUI modifications to {main_py_path}")
    else:
        print("✅ No modifications needed - WebUI integration already present")
    
    return modified

def verify_webui_integration(main_py_path):
    """Verify that WebUI integration is properly applied"""
    print(f"🔍 Verifying WebUI integration in {main_py_path}...")
    
    with open(main_py_path, 'r') as f:
        content = f.read()
    
    checks = {
        'import': 'from mcpo.utils.web_interface import create_web_interface_router' in content,
        'router_creation': 'create_web_interface_router(' in content,
        'router_include': 'main_app.include_router(web_router)' in content,
        'webui_file': os.path.exists('src/mcpo/utils/web_interface.py')
    }
    
    print("  Verification results:")
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"    {status} {check.replace('_', ' ').title()}: {'PASS' if result else 'FAIL'}")
    
    all_passed = all(checks.values())
    if all_passed:
        print("✅ All WebUI integration checks passed!")
    else:
        print("❌ Some WebUI integration checks failed!")
        
    return all_passed

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 preserve-webui-changes.py <command> [options]")
        print("Commands:")
        print("  apply - Apply WebUI modifications to main.py")
        print("  verify - Verify WebUI integration")
        print("  backup - Backup current WebUI modifications")
        sys.exit(1)
    
    command = sys.argv[1]
    main_py_path = "src/mcpo/main.py"
    
    if not os.path.exists(main_py_path):
        print(f"❌ {main_py_path} not found!")
        sys.exit(1)
    
    if command == "apply":
        force = "--force" in sys.argv
        modified = apply_webui_modifications(main_py_path, force)
        if modified:
            verify_webui_integration(main_py_path)
        sys.exit(0 if modified or verify_webui_integration(main_py_path) else 1)
    
    elif command == "verify":
        success = verify_webui_integration(main_py_path)
        sys.exit(0 if success else 1)
    
    elif command == "backup":
        changes = backup_webui_changes(main_py_path)
        print("Backup result:", changes)
        sys.exit(0)
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()