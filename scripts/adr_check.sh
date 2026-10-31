#!/bin/bash
# Compara las ADR versionadas en docs/decisiones con el repositorio central
# de documentación IA (ADR-0035 §2.2). Solo compara ficheros versionados;
# las copias de trabajo ignoradas ("* copy*") no cuentan. No modifica nada.
# Uso: scripts/adr_check.sh [directorio del clon central, por defecto ai-docs]

AI_DOCS_DIR="${1:-ai-docs}"

if [ ! -d "$AI_DOCS_DIR/.git" ]; then
    echo "[ABORT] Falta $AI_DOCS_DIR/ (make ai-setup)"
    exit 1
fi

rc=0

# Central -> local: toda ADR central existe en local y es idéntica
while IFS= read -r -d '' path; do
    f="${path#decisiones/}"
    if [ ! -f "docs/decisiones/$f" ]; then
        echo "[FAIL] Falta en local:   $f"; rc=1
    elif ! cmp -s "$AI_DOCS_DIR/$path" "docs/decisiones/$f"; then
        echo "[FAIL] Distinta:         $f"; rc=1
    fi
done < <(git -C "$AI_DOCS_DIR" ls-files -z decisiones)

# Local -> central: toda ADR versionada en local existe en el central
while IFS= read -r -d '' path; do
    f="${path#docs/decisiones/}"
    if ! git -C "$AI_DOCS_DIR" ls-files --error-unmatch "decisiones/$f" >/dev/null 2>&1; then
        echo "[FAIL] Falta en central: $f"; rc=1
    fi
done < <(git ls-files -z docs/decisiones)

if [ "$rc" -eq 0 ]; then
    echo "[OK] docs/decisiones idéntico a $AI_DOCS_DIR/decisiones ($(git -C "$AI_DOCS_DIR" rev-parse --short HEAD))"
fi
exit "$rc"
