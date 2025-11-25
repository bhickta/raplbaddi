#!/bin/bash
# CodeDeploy Hook: AfterInstall

# --- Configuration ---
# Automatically determine the root of the app (where CodeDeploy extracted files)
# This assumes scripts/bench_deploy.sh is running from the app root or handled by appspec
APP_DIR=$(pwd) 
CONFIG_FILE="$APP_DIR/.deploy_config"
SITE_NAME="devrapl"  # Will be overridden based on BENCH_DIR
APP="raplbaddi"
NVM_INIT_SCRIPT="/home/frappe/.nvm/nvm.sh"

# Default BENCH_DIR (fallback if .deploy_config not found)
BENCH_DIR="/home/frappe/dev-bench"
VENV_ACTIVATE=""

if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
    if [ -n "$DEPLOY_BENCH_DIR" ]; then
        BENCH_DIR="$DEPLOY_BENCH_DIR"
    fi
fi

# Fallback: extract from appspec.yml if BENCH_DIR is still default
if [ "$BENCH_DIR" = "/home/frappe/dev-bench" ] && [ -f "appspec.yml" ]; then
    PARSED_DEST=$(grep "destination:" appspec.yml | head -1 | sed 's/.*destination: //g' | xargs)
    if [[ "$PARSED_DEST" == *"prod-bench"* ]]; then
        BENCH_DIR="/home/frappe/prod-bench"
        log "Detected prod-bench from appspec.yml"
    fi
fi

VENV_ACTIVATE="$BENCH_DIR/env/bin/activate"

# Determine site name based on bench directory
if [[ "$BENCH_DIR" == *"prod-bench" ]]; then
    SITE_NAME="prodrapl"
else
    SITE_NAME="devrapl"
fi

# --- Error Handling ---
set -e
log() { echo "--- $(date '+%Y-%m-%d %H:%M:%S') | $1 ---"; }

# --- 1. Load Deployment Flags ---
# Default to TRUE if file missing (Safety fallback)
RUN_BUILD="true"
RUN_MIGRATE="true"
RUN_RESTART="true"

if [ -f "$CONFIG_FILE" ]; then
    log "Loading configuration from $CONFIG_FILE"
    cat "$CONFIG_FILE"  # Debug: show what's in the config
    source "$CONFIG_FILE"
else
    log "WARNING: No .deploy_config found. Defaulting to FULL deployment."
fi

log "Plan: Build=$RUN_BUILD | Migrate=$RUN_MIGRATE | Restart=$RUN_RESTART"
log "BENCH_DIR=$BENCH_DIR | SITE_NAME=$SITE_NAME | APP=$APP"

# --- 2. Environment Setup ---
setup_env() {
    log "Setting up environment..."
    if [ -f "$NVM_INIT_SCRIPT" ]; then
        source "$NVM_INIT_SCRIPT"
        nvm use v22.21.1 || true
    fi

    if [ -f "$VENV_ACTIVATE" ]; then
        source "$VENV_ACTIVATE"
    else
        log "ERROR: Python VENV not found."
        exit 1
    fi
    
    cd "$BENCH_DIR"
}

# --- 3. Execution Steps ---

setup_env

if [ "$RUN_BUILD" == "true" ]; then
    log "Executing: Bench Build"
    bench build --app "$APP"
else
    log "Skipped: Bench Build"
fi

if [ "$RUN_MIGRATE" == "true" ]; then
    log "Executing: Bench Migrate"
    bench --site "$SITE_NAME" migrate
else
    log "Skipped: Bench Migrate"
fi

if [ "$RUN_RESTART" == "true" ]; then
    log "Executing: Bench Restart"
    # Attempt bench restart, fail over to direct supervisor if permissions allow
    bench restart || (log "Bench restart failed, trying sudo supervisorctl..." && sudo supervisorctl restart all)
else
    log "Skipped: Bench Restart"
fi

log "Deployment Complete."
exit 0
