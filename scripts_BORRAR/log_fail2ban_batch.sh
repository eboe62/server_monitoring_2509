#!/bin/bash
/usr/local/bin/python3 -m log_ingestor.log_fail2ban_batch >> /var/log/log_fail2ban_logs.log 2>&1
