# ADR-0033 – Taxonomía Oficial de Clasificación y Etiquetado de ADRs

Status: APPROVED
Date: 2026-06-17
Decision Type: GOVERNANCE
Scope: System
Category: GOVERNANCE
Tags: governance, adr, taxonomy, documentation
Related ADRs: ADR-0000, ADR-0031
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

## Contexto

Durante la Fase 1 de normalización estructural de ADRs se ha establecido una cabecera homogénea para todos los documentos de decisión arquitectónica del repositorio.

La revisión realizada ha evidenciado que los campos:

* Decision Type
* Tags

carecen de una taxonomía oficial y de un vocabulario controlado aprobado.

Sin una definición explícita, diferentes autores podrían clasificar decisiones equivalentes utilizando terminología distinta, generando inconsistencias, dificultando la búsqueda documental y reduciendo la trazabilidad histórica.

Se requiere una política común que establezca:

* Categorías oficiales de clasificación.
* Reglas de etiquetado.
* Criterios mínimos de gobernanza documental.

## Decisión

Se adopta la siguiente taxonomía oficial para el campo `Decision Type`.

### Decision Types Oficiales

#### GOVERNANCE

Decisiones relacionadas con:

* Políticas de proyecto.
* Normas documentales.
* Procesos de gobierno.
* Gestión del ciclo de vida de ADRs.

#### ARCHITECTURE

Decisiones relacionadas con:

* Diseño arquitectónico global.
* Patrones de integración.
* Fronteras entre componentes.
* Estructura lógica del sistema.

#### INFRASTRUCTURE

Decisiones relacionadas con:

* Infraestructura.
* Redes.
* Docker.
* Hosts.
* Sistemas operativos.
* Componentes operativos de plataforma.

#### RUNTIME

Decisiones relacionadas con:

* Comportamiento en ejecución.
* Procesos.
* Cron.
* Healthchecks.
* Resiliencia operativa.
* Gestión de contenedores durante runtime.

#### SECURITY

Decisiones relacionadas con:

* Hardening.
* Control de acceso.
* Gestión de privilegios.
* Segmentación defensiva.
* Protección de secretos.

#### DATABASE

Decisiones relacionadas con:

* Persistencia.
* Bases de datos.
* Estrategias de backup.
* Gestión del dato.

#### DEPLOYMENT

Decisiones relacionadas con:

* Empaquetado.
* Distribución.
* Entornos.
* Estrategias de despliegue.

#### TESTING

Decisiones relacionadas con:

* Validación.
* Testing.
* Auditoría.
* Verificación automatizada.

## Política de Tags

Los tags constituyen un vocabulario controlado.

Las etiquetas:

* se almacenarán en minúsculas;
* utilizarán formato kebab-case cuando sea necesario;
* deberán representar conceptos estables.

### Catálogo Inicial de Tags

Infraestructura:

* docker
* compose
* network
* host
* infrastructure
* deployment

Runtime:

* runtime
* cron
* healthcheck
* resilience
* container

Seguridad:

* security
* hardening
* privilege
* secrets
* authentication

Datos:

* database
* postgresql
* backup

Calidad:

* testing
* validation
* audit

Arquitectura:

* architecture
* microservices
* integration
* api

Gobernanza:

* governance
* policy
* adr
* standards

## Reglas de Gobernanza

1. Todo ADR nuevo deberá incluir un único `Decision Type`.

2. Todo ADR nuevo deberá incluir entre uno y cinco tags.

3. Los tags deberán proceder preferentemente del catálogo aprobado.

4. La creación de nuevos Decision Types requerirá un ADR específico.

5. La incorporación de nuevos tags podrá realizarse mediante actualización de este ADR o mediante ADR posterior que amplíe el vocabulario oficial.

6. La clasificación de ADRs históricos deberá realizarse mediante revisión documental explícita y no mediante inferencia automática.

## Consecuencias

Positivas:

* Homogeneidad documental.
* Mejora de trazabilidad.
* Búsqueda más eficiente.
* Gobernanza explícita del repositorio ADR.

Negativas:

* Necesidad de revisión manual inicial de ADRs históricos.
* Mantenimiento futuro del vocabulario controlado.

## Estado de Implementación

Pendiente de aprobación.

Una vez aprobado este ADR podrá iniciarse la Fase 2 de clasificación semántica de los ADRs existentes.
