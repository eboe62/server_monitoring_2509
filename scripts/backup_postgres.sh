#!/bin/bash
/usr/local/bin/python3 /opt/monitoring/log_ingestor/backup_postgres.py >> /var/log/backup_postgres.log 2>&1
