#!/usr/bin/env python3
import os
import subprocess
import sys
import shutil
import datetime

# ==============================================================================
#  CONFIGURATION
# ==============================================================================
CONFIG = {
    "GROUP_PROD": "Rapl-Prod-Group",
    "GROUP_DEV":  "Rapl-Dev-Group",

    # Server Paths
    "PROD_BENCH_DIR": "/home/frappe/prod-bench",
    "DEV_BENCH_DIR":  "/home/frappe/dev-bench",
    
    # This is where CodeDeploy temporarily unzips the new code
    # MUST match the destination in appspec.yml
    "TEMP_ARTIFACT_DIR": "/home/frappe/codedeploy-artifacts/raplbaddi",

    "APP_NAME": "raplbaddi",
    "DEV_SITE_NAME": "devrapl",
    "DEV_SUPERVISOR": "frappe-bench-dev-web: frappe-bench-dev-workers:"
}
# ==============================================================================

def log(msg):
    print(f"[{datetime.datetime.now()}] {msg}")
    sys.stdout.flush()

def run_command(command, cwd=None):
    try:
        log(f"EXEC: {command}")
        subprocess.run(command, shell=True, check=True, cwd=cwd, executable='/bin/bash')
    except subprocess.CalledProcessError as e:
        log(f"[FATAL] Command failed: {e.returncode}")
        sys.exit(1)

def deploy_app_code(bench_dir):
    """
    Wipes the old app code and replaces it with the new artifact.
    """
    target_app_path = os.path.join(bench_dir, "apps", CONFIG["APP_NAME"])
    source_code_path = CONFIG["TEMP_ARTIFACT_DIR"]

    log(f"--> Replacing code in: {target_app_path}")

    # 1. Remove OLD code (Clean slate to avoid ghost files)
    if os.path.exists(target_app_path):
        shutil.rmtree(target_app_path)
    
    # 2. Move NEW code from Temp dir to Apps dir
    # We use copytree because the temp dir might contain other scripts we need later
    # or we can just move it.
    shutil.copytree(source_code_path, target_app_path)

    # 3. Fix Permissions (Crucial because CodeDeploy might write as root)
    run_command(f"chown -R frappe:frappe {target_app_path}", cwd=bench_dir)

def main():
    deploy_group = os.environ.get('DEPLOYMENT_GROUP_NAME')
    log(f"Starting Git-Less Deployment for: {deploy_group}")

    if deploy_group == CONFIG["GROUP_PROD"]:
        # --- PRODUCTION LOGIC ---
        # Note: For Prod, you usually want to be careful about wiping folders.
        # But for consistency, we replace the code.
        deploy_app_code(CONFIG["PROD_BENCH_DIR"])
        
        # Bench Update usually does a git pull, but since we updated files manually,
        # we just run requirements and migrate.
        run_command("bench setup requirements", cwd=CONFIG["PROD_BENCH_DIR"])
        run_command("bench migrate", cwd=CONFIG["PROD_BENCH_DIR"])
        
        # Optional: Build assets if JS/CSS changed
        run_command("bench build --app raplbaddi", cwd=CONFIG["PROD_BENCH_DIR"])
        
        log("[SUCCESS] Production Deployment Complete.")

    elif deploy_group == CONFIG["GROUP_DEV"]:
        # --- DEV LOGIC ---
        
        # 1. Replace Code
        deploy_app_code(CONFIG["DEV_BENCH_DIR"])

        # 2. Install Dependencies (Python reqs)
        run_command("bench setup requirements", cwd=CONFIG["DEV_BENCH_DIR"])

        # 3. Migrate DB
        run_command(f"bench --site {CONFIG['DEV_SITE_NAME']} migrate", cwd=CONFIG["DEV_BENCH_DIR"])

        # 4. Restart
        run_command(f"sudo supervisorctl restart {CONFIG['DEV_SUPERVISOR']}", cwd=CONFIG["DEV_BENCH_DIR"])

        log("[SUCCESS] Dev Deployment Complete.")

    else:
        log(f"[ERROR] Unknown Group: {deploy_group}")
        sys.exit(1)

if __name__ == "__main__":
    main()