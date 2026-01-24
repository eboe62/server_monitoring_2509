#!/bin/bash
# auditoria_binarios.sh
# Auditoría de binarios fuera de control IaC

# --- CONFIGURACIÓN ---
WHITELIST=("configure_docker_limits.sh" "configura_iptables.sh")

echo "==== AUDITORÍA DE BINARIOS ===="
echo "Fecha: $(date)"
echo

# 1. Buscar binarios en /usr/local/bin fuera de whitelist
echo ">> Binarios en /usr/local/bin fuera de whitelist:"
for file in /usr/local/bin/*; do
    fname=$(basename "$file")
    if [[ ! " ${WHITELIST[@]} " =~ " ${fname} " ]]; then
        ls -lh "$file"
    fi
done
echo

# 2. Ver si están gestionados por el sistema de paquetes
echo ">> Origen de los binarios encontrados:"
for file in /usr/local/bin/*; do
    fname=$(basename "$file")
    if [[ ! " ${WHITELIST[@]} " =~ " ${fname} " ]]; then
        if command -v rpm &>/dev/null; then
            rpm -qf "$file" 2>/dev/null || echo "No pertenece a ningún paquete: $file"
        elif command -v dpkg &>/dev/null; then
            dpkg -S "$file" 2>/dev/null || echo "No pertenece a ningún paquete: $file"
        fi
    fi
done
echo

# 3. Binarios grandes sospechosos
echo ">> Binarios mayores a 5MB:"
find /usr/local/bin /opt -type f -executable -size +5M -exec ls -lh {} \;
echo

# 4. Ejecutables recientes en /usr/bin
echo ">> Binarios modificados en /usr/bin en los últimos 30 días:"
find /usr/bin -type f -user root -mtime -30 -exec ls -lh {} \;
echo

echo "==== FIN DE AUDITORÍA ===="

