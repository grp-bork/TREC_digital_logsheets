set -e
REPO_PATH=$(pwd)

# Loop through all timers and remove them
for template in "$REPO_PATH"/systemd_services/*.timer.template; do
    servicename=$(basename "$template" .template)

    sudo systemctl stop "$servicename"
    sudo systemctl disable "$servicename"
    sudo rm /etc/systemd/system/$servicename
done

# Loop through all services and remove them
for template in "$REPO_PATH"/systemd_services/*.service.template; do
    servicename=$(basename "$template" .template)

    sudo systemctl stop "$servicename"
    sudo systemctl disable "$servicename"
    sudo rm /etc/systemd/system/$servicename
done

sudo systemctl daemon-reexec
