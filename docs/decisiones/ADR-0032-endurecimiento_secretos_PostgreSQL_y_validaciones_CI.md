# ADR-0032 – Endurecimiento de gestión de secretos PostgreSQL y validaciones CI

Status: APPROVED
Date: 2026-05-31
Scope: Database
Category: SECURITY
Tags: security, secrets, postgresql
Related ADRs: ADR-0013
Supersedes: NONE
Superseded By: NONE
Validation Reference: make verify-security

## Contexto

Durante las auditorías de seguridad y gobernanza runtime se identificaron varias desviaciones relacionadas con la gestión de secretos PostgreSQL y la validación de la aplicación.

Los hallazgos principales fueron:
- Existencia de una contraseña PostgreSQL hardcodeada en el fichero .env.
- Uso incorrecto del recurso postgres_password como directorio en lugar de fichero secreto.
- Ausencia de validación automatizada completa de secretos en producción.
- Riesgo de regresiones por errores de imports o inicialización Python no detectados por CI.
- Dependencia parcial de validaciones manuales para certificar el estado de seguridad del despliegue.

Aunque la plataforma operaba correctamente, la situación introducía deuda técnica y reducía la capacidad de certificación reproducible del entorno.

## Decisión

Se adopta una estrategia de endurecimiento basada en cuatro pilares.

### 1. Gestión de secretos mediante fichero

Se elimina cualquier uso de:
  POSTGRES_PASSWORD=<valor>
en configuración persistente.

La autenticación PostgreSQL pasa a depender exclusivamente de:
  POSTGRES_PASSWORD_FILE=/run/secrets/postgres_password
siguiendo el patrón estándar soportado por la imagen oficial de PostgreSQL.

### 2. Normalización del secreto PostgreSQL

Se establece que:
  ops/services/postgres/secrets/postgres_password
debe ser un fichero real.

Se fijan los siguientes requisitos mínimos:
- fichero secreto con permisos 600
- directorio secrets con permisos 700
- propietario distinto de nobody
- ausencia de secretos hardcodeados

### 3. Auditoría automática de seguridad

Se incorpora:
  ops/services/postgres/scripts/check_postgres_secret.sh
como mecanismo oficial de validación.

La auditoría verifica:
- existencia del secreto
- permisos
- propietario
- ausencia de POSTGRES_PASSWORD hardcodeado
- presencia de POSTGRES_PASSWORD_FILE
- montaje correcto del secreto
- ausencia de wrappers inseguros

El fallo de cualquiera de estas comprobaciones provoca error explícito.

### 4. Refuerzo de validaciones CI

Se añaden nuevas verificaciones automáticas:
- compilación completa mediante python3 -m compileall src
- smoke tests de imports
- smoke tests de init_config
- validación de modos SMTP relay y auth

El objetivo es detectar tempranamente:
- errores de sintaxis
- errores de imports
- regresiones de configuración
- problemas de inicialización

## Consecuencias

Positivas:
- eliminación de secretos hardcodeados
- alineación con buenas prácticas Docker
- reducción de superficie de ataque
- validación reproducible entre CI y producción
- detección temprana de regresiones
- mejora de la trazabilidad operativa
- reducción de deuda técnica

Negativas:
- incremento moderado de controles de validación
- mayor sensibilidad de CI ante errores de configuración

## Validación

Las siguientes evidencias confirman la implantación correcta.

Producción:
  make verify-security

Resultado:
  [OK] Comprobaciones del secreto PostgreSQL superadas

CI:
- pipeline completado correctamente
- compileall ejecutado sin errores
- smoke tests superados
- init_config validado correctamente

Runtime:
- scripts PostgreSQL operativos
- imports Python resueltos correctamente
- localización automática de src implementada

## Compatibilidad

Compatible con:
ADR-0016
ADR-0018
ADR-0029
ADR-0031

Complementa los mecanismos de gobernanza y endurecimiento definidos en dichos ADR sin introducir incompatibilidades arquitectónicas.

## Estado
Aprobado.

Implementado y validado tanto en CI como en producción.
