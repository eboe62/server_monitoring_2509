#!/bin/bash
# Script para aplicar reglas SSH rate limiting

# Cargar reglas desde el archivo
iptables-restore < /etc/iptables/rules.v4

