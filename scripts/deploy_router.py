#!/usr/bin/env python3
import os
import subprocess
import sys

# ==============================================================================
#  CENTRAL CONFIGURATION
# ==============================================================================
CONFIG = {
    # 1. AWS CodeDeploy Group Names (Must match AWS Console exactly)
    "GROUP_PROD": "Rapl-Prod-Group",
    "GROUP_DEV":  "Rapl-Dev-Group",

    # 2. Server Directory Paths
    "PROD_BENCH_DIR": "/home/frappe/prod-bench",
    "DEV_BENCH_DIR":  "/home/frappe/dev-bench",

    # 3. Application Details
    "APP_NAME": "raplbaddi",          # The folder name inside 'apps/'
    "DEV_SITE_NAME": "devrapl",       # The specific site to migrate in Dev
    "DEV_BRANCH": "origin/develop",   # The branch to reset to in Dev

    # 4. Service Management
    # The supervisor group/process names to restart after dev deployment
    # Note: Ensure colons are used correctly if restarting groups
    "DEV_SUPERVISOR_PROCESSES": "frappe-bench-dev-web: frappe-bench-dev-workers:"
}
# ==============================================================================

def run_command(command, cwd=None):
    """
    Runs a shell command in a specific directory.
    If it fails, it prints the error and exits the script.
    """
    try:
        # Print clearly for CloudWatch/CodeDeploy logs
        print(f"--> Executing: {command}")
        if cwd:
            print(f"    Context: {cwd}")
        
        # flush=True ensures logs appear immediately in the AWS console
        sys.stdout.flush()

        subprocess.run(
            command,
            shell=True,
            check=True,
            cwd=cwd,
            executable='/bin/bash'
        )
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Command failed with return code {e.returncode}")
        print(f"Failed Command: {command}")
        sys.exit(1)

def main():
    # Retrieve the Deployment Group from AWS Environment Variables
    deploy_group = os.environ.get('DEPLOYMENT_GROUP_NAME')

    print("==========================================")
    print(f"Deployment Triggered for Group: {deploy_group}")
    print("==========================================\n")

    # --- LOGIC SWITCHER ---

    if deploy_group == CONFIG["GROUP_PROD"]:
        # ----------------------------------------
        # PRODUCTION LOGIC
        # ----------------------------------------
        print("Status: Starting Production Deployment (Full Update)...")

        # 1. Update Bench (Safe production update)
        run_command("bench update --patch --no-backup", cwd=CONFIG["PROD_BENCH_DIR"])

        print("\n[SUCCESS] Production Deployment Complete.")

    elif deploy_group == CONFIG["GROUP_DEV"]:
        # ----------------------------------------
        # DEV LOGIC
        # ----------------------------------------
        print("Status: Starting Dev Deployment (Rapl App Only)...")

        app_dir = os.path.join(CONFIG["DEV_BENCH_DIR"], "apps", CONFIG["APP_NAME"])

        # 1. Manual Git Pull
        # Using variables for branch and path
        run_command("git fetch --all", cwd=app_dir)
        run_command(f"git reset --hard {CONFIG['DEV_BRANCH']}", cwd=app_dir)

        # 2. Migrate ONLY the specific site
        run_command(f"bench --site {CONFIG['DEV_SITE_NAME']} migrate", cwd=CONFIG["DEV_BENCH_DIR"])

        # 3. Restart Dev Processes
        # Using variable for process names
        restart_cmd = f"sudo supervisorctl restart {CONFIG['DEV_SUPERVISOR_PROCESSES']}"
        run_command(restart_cmd, cwd=CONFIG["DEV_BENCH_DIR"])

        print("\n[SUCCESS] Dev Deployment Complete.")

    else:
        # ----------------------------------------
        # SAFETY CATCH
        # ----------------------------------------
        print(f"[ERROR] Unknown Deployment Group: {deploy_group}")
        print("Aborting to prevent accidental data loss.")
        sys.exit(1)

if __name__ == "__main__":
    main()