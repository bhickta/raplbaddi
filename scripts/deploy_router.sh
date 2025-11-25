#!/bin/bash
set -e

# Configuration
APP="raplbaddi"
ARTIFACTS="/home/frappe/codedeploy-artifacts/raplbaddi"

# Determine Bench Path
if [ "$DEPLOYMENT_GROUP_NAME" == "Rapl-Prod-Group" ]; then
    BENCH_DIR="/home/frappe/prod-bench"
else
    BENCH_DIR="/home/frappe/dev-bench"
fi

# 1. Root Steps: Update Code & Permissions
echo "Updating code in $BENCH_DIR/apps/$APP..."
rm -rf "$BENCH_DIR/apps/$APP"
cp -r "$ARTIFACTS" "$BENCH_DIR/apps/$APP"
chown -R frappe:frappe "$BENCH_DIR/apps/$APP"

# 2. Frappe Steps: Bench Commands
# We use a Heredoc (<<EOF) to run this block as the 'frappe' user
sudo -i -u frappe bash <<EOF
set -e
export NVM_DIR="\$HOME/.nvm"
[ -s "\$NVM_DIR/nvm.sh" ] && \. "\$NVM_DIR/nvm.sh"

cd $BENCH_DIR

echo "Installing Python Dependencies..."
./env/bin/pip install -e apps/$APP

echo "Running Bench Setup..."
bench setup requirements

echo "Migrating..."
bench migrate

echo "Building Assets..."
bench build --app $APP

echo "Restarting..."
bench restart
EOF

echo "Deployment Complete."