#!/usr/bin/env python3
import os
import subprocess
import sys
import shutil
from dataclasses import dataclass

@dataclass
class BenchConfig:
    path: str
    site: str = None

@dataclass
class DeploymentConfig:
    app_name: str
    artifact_path: str
    production: BenchConfig
    development: BenchConfig

def run_command(cmd, user="frappe", cwd=None, use_nvm=False):
    prefix = f"sudo -u {user} bash -c"
    
    if use_nvm:
        # Use sudo -i to get full login environment
        prefix = f"sudo -i -u {user} bash -c"
        
        # KEY FIX: Use semicolons (;) so it doesn't stop if NVM warns us.
        # Check for bench and node locations for debugging.
        nvm_load = (
            'export NVM_DIR="$HOME/.nvm"; '
            '[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"; '
            'echo "DEBUG: Node is $(which node)"; '
            'echo "DEBUG: Bench is $(which bench)"; '
        )
        cmd = f"{nvm_load} {cmd}"
    
    full_cmd = f"{prefix} 'cd {cwd or '.'} && {cmd}'"
    print(f"EXEC: {full_cmd}")

    try:
        result = subprocess.run(
            full_cmd,
            shell=True,
            check=True,
            executable='/bin/bash',
            capture_output=True,
            text=True
        )
        print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Command failed with return code {e.returncode}")
        print("--- STDOUT ---")
        print(e.stdout)
        print("--- STDERR ---")
        print(e.stderr)
        print("--------------\n")
        sys.exit(1)

class DeploymentStep:
    def execute(self, config, bench):
        raise NotImplementedError

class InstallCodeStep(DeploymentStep):
    def execute(self, config, bench):
        target = os.path.join(bench.path, "apps", config.app_name)
        if os.path.exists(target):
            shutil.rmtree(target)
        shutil.copytree(config.artifact_path, target)
        
        subprocess.run(f"chown -R frappe:frappe {target}", shell=True, check=True)
        
        if not os.path.exists(os.path.join(target, "setup.py")):
            raise FileNotFoundError(f"setup.py not found in {target}")

class PipInstallStep(DeploymentStep):
    def execute(self, config, bench):
        run_command(
            f"./env/bin/pip install -e apps/{config.app_name}",
            cwd=bench.path
        )

class SetupRequirementsStep(DeploymentStep):
    def execute(self, config, bench):
        run_command(
            "bench setup requirements",
            cwd=bench.path,
            use_nvm=True
        )

class MigrateStep(DeploymentStep):
    def execute(self, config, bench):
        cmd = f"bench --site {bench.site} migrate" if bench.site else "bench migrate"
        run_command(cmd, cwd=bench.path)

class BuildStep(DeploymentStep):
    def execute(self, config, bench):
        run_command(
            f"bench build --app {config.app_name}",
            cwd=bench.path,
            use_nvm=True
        )

class RestartStep(DeploymentStep):
    def execute(self, config, bench):
        run_command("bench restart", cwd=bench.path)

class ClearCacheStep(DeploymentStep):
    def execute(self, config, bench):
        cmd = f"bench --site {bench.site} clear-cache" if bench.site else "bench clear-cache"
        try:
            run_command(cmd, cwd=bench.path)
        except subprocess.CalledProcessError:
            print("[WARN] Clear cache failed, ignoring...")

def get_bench_config(config, group_name):
    if group_name == "Rapl-Prod-Group":
        return config.production
    elif group_name == "Rapl-Dev-Group":
        return config.development
    else:
        raise ValueError(f"Unknown group: {group_name}")

def main():
    config = DeploymentConfig(
        app_name="raplbaddi",
        artifact_path="/home/frappe/codedeploy-artifacts/raplbaddi",
        production=BenchConfig(path="/home/frappe/prod-bench"),
        development=BenchConfig(path="/home/frappe/dev-bench", site="devrapl")
    )

    group_name = os.environ.get('DEPLOYMENT_GROUP_NAME')
    if not group_name:
        print("DEPLOYMENT_GROUP_NAME environment variable not set")
        # Default to dev for testing if needed, or exit
        sys.exit(1)

    try:
        bench = get_bench_config(config, group_name)
        print(f"Deploying {config.app_name} to {group_name}...")

        steps = [
            InstallCodeStep(),
            PipInstallStep(),
            SetupRequirementsStep(),
            MigrateStep(),
            BuildStep(),
            ClearCacheStep(),
            RestartStep()
        ]

        for step in steps:
            print(f"\n=== Running {step.__class__.__name__} ===")
            step.execute(config, bench)
            
        print("\n=== Deployment Successful ===")

    except Exception as e:
        print(f"\n=== Deployment Failed: {e} ===")
        sys.exit(1)

if __name__ == "__main__":
    main()