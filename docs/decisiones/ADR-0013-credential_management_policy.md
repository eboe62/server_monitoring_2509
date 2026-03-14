# ADR-0013 – Credential Management Policy

Fecha: 2026-03-14
Estado: Aprobado
Contexto: server_monitoring_2602 – Simplificación del modelo de gestión de credenciales

## Contexto
Durante FASE 4 del proceso de implementación se evaluó el modelo de gestión de credenciales definido inicialmente en la arquitectura del proyecto.

La documentación contemplaba el uso de un directorio `secrets/` por micro-stack para almacenar credenciales no versionadas.

Este modelo introducía varias complejidades operativas:
- Necesidad de crear y mantener múltiples directorios `secrets/`.
- Ambigüedad sobre el mecanismo real de inyección de secretos en contenedores.
- Riesgo de divergencia entre micro-stacks.
- Sobrecarga innecesaria en un entorno **single-host sin orquestador**.

El proyecto utiliza **Docker Compose v2 en un único host** y no emplea Docker Swarm ni otros orquestadores que proporcionen gestión nativa de secretos.

En este contexto, el uso de directorios `secrets/` aporta escaso valor operativo y complica la arquitectura.

Por este motivo se decide simplificar el modelo. La carpeta secrets se crea únicamente cuando un servicio requiere credenciales externas o material sensible.
Si un servicio no requiere credenciales, la carpeta secrets no es necesaria.
Las credenciales nunca deben almacenarse en el repositorio.

## Decisión
El proyecto adopta la siguiente política oficial de gestión de credenciales:

### Mecanismo oficial
Las credenciales del sistema se gestionan **exclusivamente mediante variables de entorno** definidas en archivos `.env` locales no versionados.

Por cada micro-stack:
- Debe existir un archivo `.env.template` versionado.
- El archivo `.env` real se genera manualmente a partir de dicha plantilla.
- El archivo `.env` debe estar incluido en `.gitignore`.

Ejemplo:
```
  ops/services/postgres/
  ├ docker-compose.yaml
  ├ Dockerfile
  ├ .env.template
  ├ config/
  └ scripts/
```

El archivo `.env.template` contiene únicamente nombres de variables y valores de ejemplo.

El archivo `.env` contiene las credenciales reales y **no forma parte del repositorio**.

## Gestión de credenciales

El proyecto utiliza actualmente variables de entorno (.env) para la inyección de credenciales en tiempo de ejecución.

Estas credenciales:
- no deben versionarse en el repositorio
- deben mantenerse únicamente en el servidor
- deben cargarse mediante la directiva env_file de Docker Compose

No se utilizan actualmente:
- Docker Secrets
- gestores externos de secretos (Vault, SSM, etc.)

Por tanto no se mantienen carpetas secrets dentro del repositorio ni estructuras asociadas a Docker secrets.

Si en el futuro se adopta un gestor de secretos se introducirá mediante un ADR específico.

### Restricciones obligatorias
No se permite:
- Versionar archivos `.env` con credenciales reales.
- Incluir credenciales dentro de Dockerfiles.
- Copiar archivos `.env` dentro de imágenes Docker.
- Incluir credenciales en scripts versionados.

### Alcance
Esta política aplica a:
- Micro-Stacks (`ops/services/*`)
- Infra-Stacks (`ops/docker/*`)

### Exclusiones explícitas
No se utilizan los siguientes mecanismos:
- Docker Swarm secrets
- Kubernetes secrets
- Directorios `secrets/` dentro de micro-stacks
- Sistemas externos de gestión de secretos

Si en el futuro se adopta un orquestador o gestor de secretos dedicado, deberá formalizarse mediante un nuevo ADR.

## Consecuencias
Positivas:
- Arquitectura significativamente más simple.
- Menor fricción operativa en despliegues manuales.
- Reducción de estructura innecesaria en micro-stacks.
- Mayor claridad en el flujo de configuración.

Limitaciones aceptadas:
- Las credenciales se almacenan en archivos `.env` locales.
- No existe cifrado nativo de credenciales en repositorio.
- La seguridad depende del control de acceso al host.

Estas limitaciones se consideran aceptables en el contexto actual del proyecto:
- servidor único
- acceso SSH controlado
- repositorio privado
- entorno de aprendizaje/prototipado avanzado.

## Alternativas consideradas
### 1. Uso de directorios `secrets/` por micro-stack
Ventajas:
- Separación explícita de credenciales.

Problemas detectados:
- No existe integración nativa con Docker Compose.
- Requiere mecanismos adicionales de montaje y lectura.
- Aumenta la complejidad sin aportar beneficios claros.

Decisión: Rechazada.

### 2. Uso de Docker Swarm secrets
Ventajas:
- Gestión de secretos nativa del orquestador.
- Inyección segura en contenedores.

Problemas detectados:
- Requiere habilitar Docker Swarm.
- Introduce complejidad innecesaria para un entorno single-node.

Decisión: Rechazada.

### 3. Uso de gestor externo de secretos (Vault, SOPS, etc.)
Ventajas:
- Seguridad avanzada.
- Rotación y auditoría de credenciales.

Problemas detectados:
- Sobrecoste operativo elevado.
- Infraestructura adicional fuera del alcance actual.

Decisión: Rechazada.

## Notas
Esta decisión implica la eliminación del directorio `secrets/` de la estructura mínima obligatoria de los micro-stacks definida en el documento de implementación.

Los documentos afectados deberán actualizarse para reflejar el nuevo modelo de credenciales.

Esta política es coherente con el modelo actual del proyecto:
- Docker Compose v2
- despliegue single-host
- arquitectura IaC reproducible.

## Estado
Aceptado.
