#!/bin/bash
/usr/local/bin/python3 -m log_ingestor.log_ip_geolocation >> /var/log/batch_ip_geolocation.log 2>&1
