# useful commands
sudo systemctl daemon-reexec
sudo systemctl enable mytask.service
sudo systemctl start mytask.service

# watch current logs
journalctl -u mytask -f
