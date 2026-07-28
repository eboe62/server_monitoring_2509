# ADR-0007 – Política oficial de entorno VS Code + WSL para proyectos Linux/DevOps

Status: APPROVED
Date: 2026-02-16
Scope: System
Category: GOVERNANCE
Tags: governance, policy, standards
Related ADRs: NONE
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

## Contexto
Durante la evolución del entorno PRO se detectaron inconsistencias derivadas de:
- Instalaciones duplicadas de extensiones (Windows vs WSL).
- Uso ocasional de Git desde Windows.
- Problemas de detección automática de repositorios en workspaces ubicados en /mnt.
- Comportamientos inconsistentes de line endings.
- Confusión operativa al abrir proyectos sin Remote-WSL activo.
Inicialmente se consideró instalar VS Code también dentro de WSL, pero esto generaba:
- Duplicidad innecesaria.
- Mayor complejidad de mantenimiento.
- Falta de separación clara entre UI y runtime.
Se decide formalizar un modelo híbrido controlado.

## Decisión
Se adopta el siguiente modelo oficial:

## Arquitectura
VS Code se instala exclusivamente en Windows.
Windows actúa únicamente como UI Host.
Ubuntu WSL2 es el entorno oficial de:
- Ejecución
- Compilación
- Git
- Tooling backend

## Apertura obligatoria
Todo proyecto Linux/DevOps deberá abrirse mediante:
  Remote – WSL → Ubuntu
La barra inferior izquierda debe indicar:
  WSL: Ubuntu
Si no aparece, el entorno se considera inválido.

## Git oficial
El Git oficial del proyecto es el instalado en WSL.
Queda prohibido:
- Ejecutar Git desde Windows para proyectos Linux/DevOps.
- Realizar commits desde entorno no WSL.
No se modifica el comportamiento estándar de Git
(core.discoverAcrossFilesystems permanece en false).

## Ubicación del código
Los proyectos se almacenan en:
  D:\WorkSpace
  Accesible en WSL como:
  /mnt/d/WorkSpace

Decisión consciente:
- Se prioriza organización centralizada.
- Se facilita backup desde Windows.
- Se acepta ligera penalización en file watchers NTFS.

## Modelo de WorkSpace
Se adopta modelo multi-root controlado cuando:
- El workspace raíz es superior al repositorio Git.
- VS Code no detecta automáticamente repositorios hijos en filesystem montado.

Ejemplo oficial:
{
    "folders": [
        {
        "name": "WorkSpace",
        "path": "WorkSpace"
        },
        {
        "name": "server_monitoring_2509",
        "path": "WorkSpace/Proyectos/VPS_DigitalOcean_2410/server_monitoring_2509"
        }
    ],
    "settings": {
        "git.autoRepositoryDetection": "subFolders",
        "git.openRepositoryInParentFolders": "never",
        "git.detectSubmodules": true,
        "files.eol": "\n",
        "search.exclude": {
        "**/node_modules": true,
        "**/__pycache__": true,
        "**/.git": false
        }
    }
}

Justificación:
- Git no cruza límites de filesystem por defecto.
- VS Code no detecta automáticamente subrepositorios bajo /mnt.
- Se prioriza estabilidad frente a automatismo.

## Clasificación de extensiones
Extensiones técnicas (Git, Docker, Python, etc.)
→ Se instalan exclusivamente en WSL.
Extensiones de interfaz (themes, iconos, UI)
→ Se instalan en Windows.

Se prohíbe la duplicación innecesaria.

## Consecuencias
Positivas:
- Separación clara UI / runtime.
- Coherencia total entre entorno local y servidor Linux.
- Eliminación de ambigüedad Git.
- Entorno reproducible.
- Control explícito de workspace.

Limitaciones aceptadas:
- Refresco menos ágil en NTFS frente a ext4.
- Necesidad de workspace multi-root en algunos casos.
- Mayor disciplina operativa.

## Riesgos controlados
- Uso accidental de Git Windows.
- Apertura del proyecto sin Remote-WSL.
- Duplicación de extensiones.
- Inconsistencias de line endings.
La política mitiga estos riesgos mediante reglas explícitas.

## Fuera de alcance:
- No afecta arquitectura Docker.
- No redefine modelo micro-stack.
- No altera política de secrets.
- No introduce pipeline CI/CD.
- No regula configuración específica de Copilot.

## Estado
Aceptado.
