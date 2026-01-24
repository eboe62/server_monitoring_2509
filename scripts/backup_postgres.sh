#!/bin/bash
/usr/local/bin/python3 /opt/monitoring/scripts/backup_postgres.py >> /var/log/backup_postgres.log 2>&1
