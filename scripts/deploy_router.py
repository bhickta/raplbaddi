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
    print(f"EXEC: {cmd}")
    subprocess.run(cmd, shell=True, check=True, executable='/bin/bash')

def run_frappe(cmd, cwd):
    # FIXED: Removed the backslash before the dot (.)
    # We use a raw string (r'...') to prevent Python from messing with special chars
    nvm_load = r'export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"'
    
    full_cmd = f"sudo -i -u frappe bash -c '{nvm_load} && cd {cwd} && {cmd}'"
    print(f"EXEC_FRAPPE: {full_cmd}")
    subprocess.run(full_cmd, shell=True, check=True, executable='/bin/bash')

def install_code(bench_path):
    target = os.path.join(bench_path, "apps", CONFIG["APP"])
    if os.path.exists(target):
        shutil.rmtree(target)
    shutil.copytree(CONFIG["ARTIFACT"], target)
    run_root(f"chown -R frappe:frappe {target}")

def main():
    group = os.environ.get('DEPLOYMENT_GROUP_NAME')
    print(f"Deploying: {group}")

    if group == CONFIG["GROUP_PROD"]:
        install_code(CONFIG["PROD_BENCH"])
        run_frappe(f"./env/bin/pip install -e apps/{CONFIG['APP']}", CONFIG["PROD_BENCH"])
        
        run_frappe("bench setup requirements", CONFIG["PROD_BENCH"])
        run_frappe("bench migrate", CONFIG["PROD_BENCH"])
        run_frappe(f"bench build --app {CONFIG['APP']}", CONFIG["PROD_BENCH"])
        run_frappe("bench restart", CONFIG["PROD_BENCH"])

    elif group == CONFIG["GROUP_DEV"]:
        install_code(CONFIG["DEV_BENCH"])
        run_frappe(f"./env/bin/pip install -e apps/{CONFIG['APP']}", CONFIG["DEV_BENCH"])

        run_frappe("bench setup requirements", CONFIG["DEV_BENCH"])
        run_frappe(f"bench --site {CONFIG['DEV_SITE']} migrate", CONFIG["DEV_BENCH"])
        run_frappe(f"bench build --app {CONFIG['APP']}", CONFIG["DEV_BENCH"])
        run_frappe("bench restart", CONFIG["DEV_BENCH"])

    else:
        sys.exit(1)

if __name__ == "__main__":
    main()