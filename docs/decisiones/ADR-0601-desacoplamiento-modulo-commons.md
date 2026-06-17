# ADR-0601: Estructura de Desacoplamiento de Capas mediante el Patrón Módulo-Commons

Status: APPROVED
Date: 2026-06-11
Decision Type: REVIEW_REQUIRED
Scope: System
Tags: REVIEW_REQUIRED
Related ADRs: ADR-0600, ADR-0602
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

## Contexto
Se observa que cada dominio de negocio del backend está duplicado sistemáticamente en dos subartefactos emparentados: un módulo principal (ej. `gda-agrupacion`) y un submódulo con el sufijo `-commons` (ej. `gda-agrupacion-commons`). Es necesario fijar la frontera de qué lógica reside en cada lado para evitar el acoplamiento cíclico en el árbol de Maven y la fuga de responsabilidades.

## Decisión
Adoptar el patrón de Aislamiento de Commons. Los módulos independientes de negocio solo expondrán e incluirán en su extensión `-commons` aquellos elementos que requieran ser consumidos por otros servicios del ecosistema.

En `-commons` residirán únicamente:
- DTOs de intercambio.
- Interfaces de clientes de comunicación (Feign/WebClient).
- Excepciones de dominio.
- Constantes globales del módulo.

En el módulo principal residirán:
- La lógica de negocio (Services).
- La capa de persistencia (Entities JPA/Repositories).
- Los controladores REST.
- Las configuraciones del framework.

### Excepciones de Infraestructura Autorizadas
Se autoriza una excepción al patrón de Aislamiento de Commons para microservicios destinados exclusivamente a funciones transversales, utilitarias o de soporte técnico. En estos casos, se permite centralizar estructuras de datos, contratos de intercambio o entidades ligeras en el submódulo `-commons` para optimizar la integración y el rendimiento en el monorrepo.

Ejemplo:
- `gda-log` puede incluir entidades JPA y repositorios en su submódulo `gda-log-commons` debido a su naturaleza transversal y utilitaria.

**Restricción:**
Para los módulos que procesan lógica de negocio (como `gda-persona` o `gda-agrupacion`), esta excepción queda estrictamente prohibida. El aislamiento definido en este ADR es de obligado cumplimiento para garantizar la separación de responsabilidades y evitar acoplamientos indebidos.
