#!/usr/bin/env python3
import os
import subprocess
import sys
import shutil
import datetime

CONFIG = {
    "GROUP_PROD": "Rapl-Prod-Group",
    "GROUP_DEV":  "Rapl-Dev-Group",
    "PROD_BENCH": "/home/frappe/prod-bench",
    "DEV_BENCH":  "/home/frappe/dev-bench",
    "ARTIFACT":   "/home/frappe/codedeploy-artifacts/raplbaddi",
    "APP":        "raplbaddi",
    "DEV_SITE":   "devrapl"
}

def run_root(cmd):
    # Runs commands as Root
    print(f"EXEC [ROOT]: {cmd}")
    subprocess.run(cmd, shell=True, check=True, executable='/bin/bash')

def run_pip(cmd, cwd):
    # Runs pip/python commands (Simple, no NVM needed)
    # We use 'sudo -u frappe' directly without -i to avoid loading heavy shell profiles
    full_cmd = f"sudo -u frappe bash -c 'cd {cwd} && {cmd}'"
    print(f"EXEC_PIP: {full_cmd}")
    subprocess.run(full_cmd, shell=True, check=True, executable='/bin/bash')

def run_build(cmd, cwd):
    # Runs bench build (Complex, NEEDS NVM for Node/Yarn)
    # Only use this for the 'build' step
    nvm_load = r'export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"'
    full_cmd = f"sudo -i -u frappe bash -c '{nvm_load} && cd {cwd} && {cmd}'"
    print(f"EXEC_BUILD: {full_cmd}")
    subprocess.run(full_cmd, shell=True, check=True, executable='/bin/bash')

def install_code(bench_path):
    target = os.path.join(bench_path, "apps", CONFIG["APP"])
    
    # 1. Clean Wipe & Copy
    if os.path.exists(target):
        shutil.rmtree(target)
    shutil.copytree(CONFIG["ARTIFACT"], target)
    
    # 2. Fix Permissions
    run_root(f"chown -R frappe:frappe {target}")
    
    # 3. DEBUG: Check if setup.py exists (Common failure point)
    print(f"--- Checking files in {target} ---")
    if os.path.exists(os.path.join(target, "setup.py")):
        print(f"[OK] setup.py found in {target}")
    else:
        print(f"[ERROR] setup.py MISSING in {target}. Check your Zip file structure!")
        subprocess.run(f"ls -la {target}", shell=True) # List files to debug

def main():
    group = os.environ.get('DEPLOYMENT_GROUP_NAME')
    print(f"Deploying: {group}")

    if group == CONFIG["GROUP_PROD"]:
        install_code(CONFIG["PROD_BENCH"])
        
        # 1. Python Install (Simple)
        run_pip(f"./env/bin/pip install -e apps/{CONFIG['APP']}", CONFIG["PROD_BENCH"])
        run_pip("bench setup requirements", CONFIG["PROD_BENCH"])
        run_pip("bench migrate", CONFIG["PROD_BENCH"])
        
        # 2. JS Build (Complex - Needs NVM)
        run_build(f"bench build --app {CONFIG['APP']}", CONFIG["PROD_BENCH"])
        
        run_pip("bench restart", CONFIG["PROD_BENCH"])

    elif group == CONFIG["GROUP_DEV"]:
        install_code(CONFIG["DEV_BENCH"])

        # 1. Python Install (Simple)
        run_pip(f"./env/bin/pip install -e apps/{CONFIG['APP']}", CONFIG["DEV_BENCH"])
        run_pip("bench setup requirements", CONFIG["DEV_BENCH"])
        run_pip(f"bench --site {CONFIG['DEV_SITE']} migrate", CONFIG["DEV_BENCH"])
        
        # 2. JS Build (Complex - Needs NVM)
        run_build(f"bench build --app {CONFIG['APP']}", CONFIG["DEV_BENCH"])
        
        run_pip("bench restart", CONFIG["DEV_BENCH"])

    else:
        sys.exit(1)

if __name__ == "__main__":
    main()