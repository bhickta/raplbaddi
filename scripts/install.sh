#!/bin/bash
set -e

# =========================
# CONFIG
# =========================
ARTIFACT_DIR="/home/frappe/codedeploy-artifacts/raplbaddi"
# =========================

cd $ARTIFACT_DIR
echo "--> wrapper: Invoking Python Deployment Router..."
python3 scripts/deploy_router.py#!/bin/bash
set -e

# Set the context to where CodeDeploy dropped the files
cd /home/frappe/codedeploy-artifacts/raplbaddi

echo "--> wrapper: Invoking Python Deployment Router..."
python3 scripts/deploy_router.py