#!/usr/bin/env python3
import os
import subprocess
import sys
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class DeploymentGroup(Enum):
    PRODUCTION = "Rapl-Prod-Group"
    DEVELOPMENT = "Rapl-Dev-Group"


@dataclass
class BenchConfig:
    path: str
    site: Optional[str] = None


@dataclass
class DeploymentConfig:
    app_name: str
    artifact_path: str
    production: BenchConfig
    development: BenchConfig


class CommandExecutor(ABC):
    @abstractmethod
    def execute(self, cmd: str, cwd: Optional[str] = None, capture_output: bool = False) -> subprocess.CompletedProcess:
        pass


class RootCommandExecutor(CommandExecutor):
    def execute(self, cmd: str, cwd: Optional[str] = None, capture_output: bool = False) -> subprocess.CompletedProcess:
        print(f"EXEC [ROOT]: {cmd}")
        return subprocess.run(
            cmd,
            shell=True,
            check=True,
            executable='/bin/bash',
            cwd=cwd,
            capture_output=capture_output,
            text=True
        )


class UserCommandExecutor(CommandExecutor):
    def __init__(self, user: str = "frappe"):
        self.user = user

    def execute(self, cmd: str, cwd: Optional[str] = None, capture_output: bool = False) -> subprocess.CompletedProcess:
        full_cmd = f"sudo -u {self.user} bash -c 'cd {cwd} && {cmd}'"
        print(f"EXEC [{self.user.upper()}]: {full_cmd}")
        return subprocess.run(
            full_cmd,
            shell=True,
            check=True,
            executable='/bin/bash',
            capture_output=capture_output,
            text=True
        )


class NvmCommandExecutor(CommandExecutor):
    def __init__(self, user: str = "frappe"):
        self.user = user
        self.nvm_load = r'export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"'

    def execute(self, cmd: str, cwd: Optional[str] = None, capture_output: bool = False) -> subprocess.CompletedProcess:
        full_cmd = f"sudo -i -u {self.user} bash -c '{self.nvm_load} && cd {cwd} && {cmd}'"
        print(f"EXEC [NVM]: {full_cmd}")
        return subprocess.run(
            full_cmd,
            shell=True,
            check=True,
            executable='/bin/bash',
            capture_output=capture_output,
            text=True
        )


class DeploymentStep(ABC):
    def __init__(self, executor: CommandExecutor, optional: bool = False):
        self.executor = executor
        self.optional = optional

    @abstractmethod
    def execute(self, config: DeploymentConfig, bench: BenchConfig) -> None:
        pass

    def safe_execute(self, config: DeploymentConfig, bench: BenchConfig) -> bool:
        try:
            self.execute(config, bench)
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Step {self.__class__.__name__} failed")
            print(f"[ERROR] Return code: {e.returncode}")
            if e.stdout:
                print(f"[STDOUT] {e.stdout}")
            if e.stderr:
                print(f"[STDERR] {e.stderr}")
            
            if self.optional:
                print(f"[WARNING] Optional step failed, continuing...")
                return True
            return False


class InstallCodeStep(DeploymentStep):
    def __init__(self, executor: CommandExecutor, root_executor: CommandExecutor):
        super().__init__(executor)
        self.root_executor = root_executor

    def execute(self, config: DeploymentConfig, bench: BenchConfig) -> None:
        target = os.path.join(bench.path, "apps", config.app_name)
        
        if os.path.exists(target):
            shutil.rmtree(target)
        
        shutil.copytree(config.artifact_path, target)
        self.root_executor.execute(f"chown -R frappe:frappe {target}")
        
        self._validate_structure(target)

    def _validate_structure(self, target: str) -> None:
        print(f"--- Validating structure in {target} ---")
        setup_path = os.path.join(target, "setup.py")
        
        if os.path.exists(setup_path):
            print(f"[OK] setup.py found")
        else:
            print(f"[ERROR] setup.py MISSING")
            subprocess.run(f"ls -la {target}", shell=True)
            raise FileNotFoundError(f"setup.py not found in {target}")


class PipInstallStep(DeploymentStep):
    def execute(self, config: DeploymentConfig, bench: BenchConfig) -> None:
        try:
            self.executor.execute(
                f"./env/bin/pip install -e apps/{config.app_name}",
                cwd=bench.path,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] pip install failed")
            print(f"[STDOUT] {e.stdout}")
            print(f"[STDERR] {e.stderr}")
            raise


class SetupRequirementsStep(DeploymentStep):
    def execute(self, config: DeploymentConfig, bench: BenchConfig) -> None:
        try:
            result = self.executor.execute(
                "bench setup requirements",
                cwd=bench.path,
                capture_output=True
            )
            if result.stdout:
                print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] bench setup requirements failed")
            print(f"[STDOUT] {e.stdout}")
            print(f"[STDERR] {e.stderr}")
            raise


class MigrateStep(DeploymentStep):
    def execute(self, config: DeploymentConfig, bench: BenchConfig) -> None:
        cmd = f"bench --site {bench.site} migrate" if bench.site else "bench migrate"
        try:
            result = self.executor.execute(cmd, cwd=bench.path, capture_output=True)
            if result.stdout:
                print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Migration failed")
            print(f"[STDOUT] {e.stdout}")
            print(f"[STDERR] {e.stderr}")
            raise


class BuildStep(DeploymentStep):
    def execute(self, config: DeploymentConfig, bench: BenchConfig) -> None:
        try:
            result = self.executor.execute(
                f"bench build --app {config.app_name}",
                cwd=bench.path,
                capture_output=True
            )
            if result.stdout:
                print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Build failed")
            print(f"[STDOUT] {e.stdout}")
            print(f"[STDERR] {e.stderr}")
            raise


class RestartStep(DeploymentStep):
    def execute(self, config: DeploymentConfig, bench: BenchConfig) -> None:
        try:
            result = self.executor.execute("bench restart", cwd=bench.path, capture_output=True)
            if result.stdout:
                print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Restart failed")
            print(f"[STDOUT] {e.stdout}")
            print(f"[STDERR] {e.stderr}")
            raise


class DeploymentPipeline:
    def __init__(self, steps: List[DeploymentStep]):
        self.steps = steps

    def execute(self, config: DeploymentConfig, bench: BenchConfig) -> None:
        for i, step in enumerate(self.steps, 1):
            print(f"\n=== Step {i}/{len(self.steps)}: {step.__class__.__name__} ===")
            if not step.safe_execute(config, bench):
                raise RuntimeError(f"Pipeline failed at step: {step.__class__.__name__}")


class DeploymentPipelineFactory:
    @staticmethod
    def create_standard_pipeline() -> DeploymentPipeline:
        root_executor = RootCommandExecutor()
        user_executor = UserCommandExecutor()
        nvm_executor = NvmCommandExecutor()

        return DeploymentPipeline([
            InstallCodeStep(user_executor, root_executor),
            PipInstallStep(user_executor),
            SetupRequirementsStep(nvm_executor),
            MigrateStep(user_executor),
            BuildStep(nvm_executor),
            RestartStep(user_executor)
        ])


class DeploymentOrchestrator:
    def __init__(self, config: DeploymentConfig, pipeline: DeploymentPipeline):
        self.config = config
        self.pipeline = pipeline

    def deploy(self, group_name: str) -> None:
        print(f"Deploying: {group_name}")
        
        try:
            group = DeploymentGroup(group_name)
        except ValueError:
            print(f"Unknown deployment group: {group_name}")
            sys.exit(1)

        bench = self._get_bench_config(group)
        
        try:
            self.pipeline.execute(self.config, bench)
            print("\n=== Deployment completed successfully ===")
        except Exception as e:
            print(f"\n=== Deployment failed: {e} ===")
            sys.exit(1)

    def _get_bench_config(self, group: DeploymentGroup) -> BenchConfig:
        if group == DeploymentGroup.PRODUCTION:
            return self.config.production
        elif group == DeploymentGroup.DEVELOPMENT:
            return self.config.development
        else:
            raise ValueError(f"Unsupported deployment group: {group}")


def main():
    config = DeploymentConfig(
        app_name="raplbaddi",
        artifact_path="/home/frappe/codedeploy-artifacts/raplbaddi",
        production=BenchConfig(path="/home/frappe/prod-bench"),
        development=BenchConfig(
            path="/home/frappe/dev-bench",
            site="devrapl"
        )
    )

    pipeline = DeploymentPipelineFactory.create_standard_pipeline()
    orchestrator = DeploymentOrchestrator(config, pipeline)

    group_name = os.environ.get('DEPLOYMENT_GROUP_NAME')
    if not group_name:
        print("DEPLOYMENT_GROUP_NAME environment variable not set")
        sys.exit(1)

    orchestrator.deploy(group_name)


if __name__ == "__main__":
    main()