#!/bin/bash
/usr/local/bin/python3 -m log_ingestor.log_kern_batch >> /var/log/batch_kern_logs.log 2>&1
