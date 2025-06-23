# TODO on deployment
Add to THE END of /etc/sudoers to enable automatic restart on update
{{USERNAME}} ALL=(ALL) NOPASSWD: systemctl restart logsheets_process_new_submissions.service

# useful commands
sudo systemctl daemon-reexec
sudo systemctl enable mytask.service
sudo systemctl start mytask.service

# watch current logs
journalctl -u mytask -f
