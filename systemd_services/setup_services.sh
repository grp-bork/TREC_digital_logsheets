#!/bin/bash

# Usage: ./setup_services.sh /path/to/conda username

set -e

CONDA_PATH="$1"
USERNAME="$2"

if [[ -z "$CONDA_PATH" || -z "$USERNAME" ]]; then
    echo "Usage: $0 <conda_path> <username>"
    exit 1
fi

REPO_PATH=$(pwd)
SERVICE_DIR="$REPO_PATH/systemd_services"
SYSTEMD_DIR="/etc/systemd/system"

echo "📁 Setting up systemd services from: $SERVICE_DIR"
echo "⚙️ Using conda path: $CONDA_PATH"
echo "👤 Running under user: $USERNAME"

# Install conda env
$CONDA_PATH/bin/conda env create -y -f "$REPO_PATH/conda-env.yaml"

# Loop through all service/timer templates and install them
for template in "$SERVICE_DIR"/*.template; do
    filename=$(basename "$template" .template)
    destination="$SYSTEMD_DIR/$filename"

    echo "🛠 Generating $destination from $template"

    sed -e "s|{{REPO_PATH}}|$REPO_PATH|g" \
        -e "s|{{CONDA_PATH}}|$CONDA_PATH|g" \
        -e "s|{{USERNAME}}|$USERNAME|g" \
        "$template" | sudo tee "$destination" > /dev/null

    sudo chmod 644 "$destination"
done

# Reload systemd to pick up new files
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reexec

# Enable and start all services and timers
for unit in "$SYSTEMD_DIR"/logsheets_*.{service,timer}; do
    unitname=$(basename "$unit")
    echo "🚀 Enabling and starting $unitname"
    sudo systemctl enable "$unitname"
    sudo systemctl restart "$unitname"
done

echo "✅ All services deployed and started."
