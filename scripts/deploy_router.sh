#!/bin/bash
set -e

APP="raplbaddi"
ARTIFACTS="/home/frappe/codedeploy-artifacts/raplbaddi"

if [ "$DEPLOYMENT_GROUP_NAME" == "Rapl-Prod-Group" ]; then
    BENCH_DIR="/home/frappe/prod-bench"
else
    BENCH_DIR="/home/frappe/dev-bench"
fi

echo "Updating code in $BENCH_DIR/apps/$APP..."
rm -rf "$BENCH_DIR/apps/$APP"
cp -r "$ARTIFACTS" "$BENCH_DIR/apps/$APP"
chown -R frappe:frappe "$BENCH_DIR/apps/$APP"

sudo -i -u frappe bash <<EOF
set -e
export NVM_DIR="\$HOME/.nvm"
[ -s "\$NVM_DIR/nvm.sh" ] && \. "\$NVM_DIR/nvm.sh"

cd $BENCH_DIR/apps/$APP

if [ ! -d ".git" ]; then
    git init
    git config user.email "deploy@bot.com"
    git config user.name "DeployBot"
    git add .
    git commit -m "Deploy artifact"
fi

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