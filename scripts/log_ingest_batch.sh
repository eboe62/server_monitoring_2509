#!/bin/bash
/usr/local/bin/python3 -m log_ingestor.log_ingest_batch >> /var/log/batch_attacking_logs.log 2>&1

